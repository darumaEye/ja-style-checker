"""
--- モジュール checks の単体テスト ---
"""

from checks import run_all_checks

"""
-- 関数 run_all_checks のテスト --
1. 正常: 各カテゴリの検出条件を満たすtextを渡すと、複数カテゴリの検出結果が
   findingsに含まれる
2. 正常: 検出対象がない場合、空リストが返る
3. 正常: 戻り値が辞書のリストであり、各要素が期待するキーを持つ
4. 正常: 呼び出しごとに独立したリストが返る（前回呼び出しの結果を引き継がない）
5. 正常: 空文字列を渡しても例外は発生せず、空リストが返る
"""


def test_init_run_all_checks_detects_across_categories():
    """1. 正常: 各カテゴリの検出条件を満たすtextを渡すと、複数カテゴリの検出結果が
    findingsに含まれる
    """
    text = "薔薇が咲いた。１と1が混在。会員並びに関係者に通知する。"

    findings = run_all_checks(text)

    categories = {f["category"] for f in findings}
    assert "漢字・かなの使い方" in categories
    assert "数字の使い方" in categories
    assert "用語の使い方" in categories


def test_init_run_all_checks_no_detection_returns_empty_list():
    """2. 正常: 検出対象がない場合、空リストが返る"""
    findings = run_all_checks("特に問題のない普通の文章です。")

    assert findings == []


def test_init_run_all_checks_returns_list_of_dicts_with_expected_keys():
    """3. 正常: 戻り値が辞書のリストであり、各要素が期待するキーを持つ"""
    findings = run_all_checks("薔薇が咲いた。")

    assert isinstance(findings, list)
    assert len(findings) >= 1
    expected_keys = {"rule_id", "category", "level", "excerpt", "suggestion", "source"}
    assert set(findings[0].keys()) == expected_keys


def test_init_run_all_checks_returns_independent_list_per_call():
    """4. 正常: 呼び出しごとに独立したリストが返る（前回呼び出しの結果を引き継がない）"""
    first = run_all_checks("薔薇が咲いた。")
    second = run_all_checks("特に問題のない普通の文章です。")

    assert len(first) >= 1
    assert second == []


def test_init_run_all_checks_empty_text_returns_empty_list():
    """5. 正常: 空文字列を渡しても例外は発生せず、空リストが返る"""
    findings = run_all_checks("")

    assert findings == []
