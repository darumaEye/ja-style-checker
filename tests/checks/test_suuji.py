"""
--- モジュール suuji の単体テスト ---
"""

from checks import suuji

"""
-- 関数 check_zenkaku_hankaku_suuji のテスト --
1. 正常: 全角数字と半角数字が両方存在する場合、1件のfindingが追加される
2. 正常: 全角数字のみの場合、findingsに追加されない
3. 正常: 半角数字のみの場合、findingsに追加されない
"""


def test_suuji_check_zenkaku_hankaku_suuji_detects_mix():
    """1. 正常: 全角数字と半角数字が両方存在する場合、1件のfindingが追加される"""
    findings = []

    suuji.check_zenkaku_hankaku_suuji("１と1が混在する。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "number-width-mix"
    assert findings[0]["category"] == "数字の使い方"
    assert findings[0]["level"] == "注意"


def test_suuji_check_zenkaku_hankaku_suuji_zenkaku_only_appends_nothing():
    """2. 正常: 全角数字のみの場合、findingsに追加されない"""
    findings = []

    suuji.check_zenkaku_hankaku_suuji("１２３のみ。", findings)

    assert findings == []


def test_suuji_check_zenkaku_hankaku_suuji_hankaku_only_appends_nothing():
    """3. 正常: 半角数字のみの場合、findingsに追加されない"""
    findings = []

    suuji.check_zenkaku_hankaku_suuji("123のみ。", findings)

    assert findings == []


"""
-- 関数 check_comma_kugiri のテスト --
1. 正常: 4桁以上の数字にコンマがない場合、findingが追加される（3桁区切りのsuggestion付き）
2. 正常: 直後が「年」の場合（西暦等）、findingsに追加されない
3. 正常: 前後にハイフンがある場合（電話番号等）、findingsに追加されない
4. 正常: 既にコンマ区切りがある場合、findingsに追加されない
5. 正常: 3桁以下の数字は対象外
"""


def test_suuji_check_comma_kugiri_detects_missing_comma():
    """1. 正常: 4桁以上の数字にコンマがない場合、findingが追加される（3桁区切りのsuggestion付き）"""
    findings = []

    suuji.check_comma_kugiri("予算は12345円です。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "number-comma"
    assert findings[0]["level"] == "要修正"
    assert findings[0]["suggestion"] == "12345 → 12,345（3桁ごとにコンマ区切り）"


def test_suuji_check_comma_kugiri_year_appends_nothing():
    """2. 正常: 直後が「年」の場合（西暦等）、findingsに追加されない"""
    findings = []

    suuji.check_comma_kugiri("2024年に開催された。", findings)

    assert findings == []


def test_suuji_check_comma_kugiri_hyphenated_appends_nothing():
    """3. 正常: 前後にハイフンがある場合（電話番号等）、findingsに追加されない"""
    findings = []

    suuji.check_comma_kugiri("電話番号は0120-1234-5678です。", findings)

    assert findings == []


def test_suuji_check_comma_kugiri_already_comma_separated_appends_nothing():
    """4. 正常: 既にコンマ区切りがある場合、findingsに追加されない"""
    findings = []

    suuji.check_comma_kugiri("予算は12,345円です。", findings)

    assert findings == []


def test_suuji_check_comma_kugiri_three_digits_appends_nothing():
    """5. 正常: 3桁以下の数字は対象外"""
    findings = []

    suuji.check_comma_kugiri("在庫は123個です。", findings)

    assert findings == []


"""
-- 関数 run のテスト --
1. 正常: 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる
"""


def test_suuji_run_calls_all_checks():
    """1. 正常: 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる"""
    findings = []
    text = "１と1が混在。予算は12345円。3ヶ所を確認する。"

    suuji.run(text, findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert "number-width-mix" in rule_ids
    assert "number-comma" in rule_ids
    assert "kasho-3ヶ所" in rule_ids
