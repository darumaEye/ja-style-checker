"""
--- モジュール okurigana の単体テスト ---
"""

from checks import okurigana

"""
-- 関数 run のテスト --
1. 正常: 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない
2. 正常: 戻り値はNoneである
"""


def test_okurigana_run_appends_nothing():
    """1. 正常: 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない"""
    findings = []

    okurigana.run("何らかの文書テキスト。", findings)

    assert findings == []


def test_okurigana_run_returns_none():
    """2. 正常: 戻り値はNoneである"""
    result = okurigana.run("何らかの文書テキスト。", [])

    assert result is None
