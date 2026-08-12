"""
--- モジュール kigou の単体テスト ---
"""

from checks import kigou

"""
-- 関数 check_touten_kongou のテスト --
1. 正常: 「、」と「，」が両方存在する場合、「，」の出現数だけfindingが追加される
2. 正常: 「、」のみの場合、findingsに追加されない
3. 正常: 「，」のみの場合、findingsに追加されない
4. 正常: どちらもない場合、findingsに追加されない
"""


def test_kigou_check_touten_kongou_detects_mix():
    """1. 正常: 「、」と「，」が両方存在する場合、「，」の出現数だけfindingが追加される"""
    findings = []

    kigou.check_touten_kongou("これは、テストである，確認する，終わり。", findings)

    assert len(findings) == 2
    assert findings[0]["rule_id"] == "punct-touten-mix"
    assert findings[0]["category"] == "符号・句読点"
    assert findings[0]["level"] == "要修正"


def test_kigou_check_touten_kongou_touten_only_appends_nothing():
    """2. 正常: 「、」のみの場合、findingsに追加されない"""
    findings = []

    kigou.check_touten_kongou("これは、テストである。", findings)

    assert findings == []


def test_kigou_check_touten_kongou_comma_only_appends_nothing():
    """3. 正常: 「，」のみの場合、findingsに追加されない"""
    findings = []

    kigou.check_touten_kongou("これは，テストである。", findings)

    assert findings == []


def test_kigou_check_touten_kongou_neither_appends_nothing():
    """4. 正常: どちらもない場合、findingsに追加されない"""
    findings = []

    kigou.check_touten_kongou("これはテストである。", findings)

    assert findings == []


"""
-- 関数 check_kuten_piriodo のテスト --
1. 正常: 「．」があり前後が数字でない場合、findingが追加される
2. 正常: 小数点（前後が数字）の場合、findingsに追加されない
3. 正常: 「．」がない場合、findingsに追加されない
"""


def test_kigou_check_kuten_piriodo_detects_non_decimal_period():
    """1. 正常: 「．」があり前後が数字でない場合、findingが追加される"""
    findings = []

    kigou.check_kuten_piriodo("これはテストである．", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "punct-kuten-piriodo"
    assert findings[0]["level"] == "要修正"


def test_kigou_check_kuten_piriodo_decimal_point_appends_nothing():
    """2. 正常: 小数点（前後が数字）の場合、findingsに追加されない"""
    findings = []

    kigou.check_kuten_piriodo("3．14は円周率である。", findings)

    assert findings == []


def test_kigou_check_kuten_piriodo_no_match_appends_nothing():
    """3. 正常: 「．」がない場合、findingsに追加されない"""
    findings = []

    kigou.check_kuten_piriodo("これはテストである。", findings)

    assert findings == []


"""
-- 関数 check_gikaku_fugou_zenhan のテスト --
1. 正常: 「？」の直後に文字が続く場合、findingが追加される
2. 正常: 「！」の直後に文字が続く場合、findingが追加される
3. 正常: 「？」の直後が全角スペースの場合、findingsに追加されない
4. 正常: 「？」が文末（直後に何もない）の場合、findingsに追加されない
"""


def test_kigou_check_gikaku_fugou_zenhan_detects_after_question_mark():
    """1. 正常: 「？」の直後に文字が続く場合、findingが追加される"""
    findings = []

    kigou.check_gikaku_fugou_zenhan("本当？大丈夫か確認する。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "punct-gikaku-space"
    assert findings[0]["level"] == "参考"


def test_kigou_check_gikaku_fugou_zenhan_detects_after_exclamation_mark():
    """2. 正常: 「！」の直後に文字が続く場合、findingが追加される"""
    findings = []

    kigou.check_gikaku_fugou_zenhan("危ない！注意して。", findings)

    assert len(findings) == 1


def test_kigou_check_gikaku_fugou_zenhan_full_width_space_appends_nothing():
    """3. 正常: 「？」の直後が全角スペースの場合、findingsに追加されない"""
    findings = []

    kigou.check_gikaku_fugou_zenhan("本当？　大丈夫か確認する。", findings)

    assert findings == []


def test_kigou_check_gikaku_fugou_zenhan_end_of_text_appends_nothing():
    """4. 正常: 「？」が文末（直後に何もない）の場合、findingsに追加されない"""
    findings = []

    kigou.check_gikaku_fugou_zenhan("本当？", findings)

    assert findings == []


"""
-- 関数 run のテスト --
1. 正常: 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる
"""


def test_kigou_run_calls_all_checks():
    """1. 正常: 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる"""
    findings = []
    text = "これは、テストである，確認。3．14ではない．本当？大丈夫か。"

    kigou.run(text, findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert "punct-touten-mix" in rule_ids
    assert "punct-kuten-piriodo" in rule_ids
    assert "punct-gikaku-space" in rule_ids
