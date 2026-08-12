"""
--- モジュール kousei の単体テスト ---
"""

from checks import kousei

"""
-- 関数 run のテスト --
1. 正常: 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない
2. 正常: 戻り値はNoneである
"""


def test_kousei_run_appends_nothing():
    """1. 正常: 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない"""
    findings = []

    kousei.run("何らかの文書テキスト。", findings)

    assert findings == []


def test_kousei_run_returns_none():
    """2. 正常: 戻り値はNoneである"""
    result = kousei.run("何らかの文書テキスト。", [])

    assert result is None
