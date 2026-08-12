"""
--- モジュール gairaigo の単体テスト ---
"""

from checks import gairaigo

"""
-- 関数 run のテスト --
1. 正常: 外来語長音辞書の語（末尾に長音がない）を含む場合、findingが追加される
2. 正常: 語の直後に長音「ー」が続く場合（正しい表記）、findingsに追加されない
3. 正常: 該当語がない場合、findingsに追加されない
"""


def test_gairaigo_run_detects_missing_chouon():
    """1. 正常: 外来語長音辞書の語（末尾に長音がない）を含む場合、findingが追加される"""
    findings = []

    gairaigo.run("ユーザ登録を行う。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "gairaigo-chouon-ユーザ"
    assert findings[0]["category"] == "外来語の表記"
    assert findings[0]["level"] == "注意"
    assert findings[0]["source"] == "Ⅰ-3エ"


def test_gairaigo_run_correct_chouon_appends_nothing():
    """2. 正常: 語の直後に長音「ー」が続く場合（正しい表記）、findingsに追加されない"""
    findings = []

    gairaigo.run("ユーザー登録を行う。", findings)

    assert findings == []


def test_gairaigo_run_no_match_appends_nothing():
    """3. 正常: 該当語がない場合、findingsに追加されない"""
    findings = []

    gairaigo.run("該当する語がない文章です。", findings)

    assert findings == []
