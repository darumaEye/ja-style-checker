"""
--- モジュール yougo の単体テスト ---
"""

from checks import yougo

"""
-- 関数 check_oyobi_narabini のテスト --
1. 正常: 「並びに」があり「及び」がない文の場合、findingが追加される
2. 正常: 「並びに」と「及び」が両方ある場合、findingsに追加されない
3. 正常: 「並びに」がない場合、findingsに追加されない
4. 正常: 仮名書き「ならびに」でも検出される
"""


def test_yougo_check_oyobi_narabini_detects_unpaired_narabini():
    """1. 正常: 「並びに」があり「及び」がない文の場合、findingが追加される"""
    findings = []

    yougo.check_oyobi_narabini("会員並びに関係者に通知する。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "term-narabini"
    assert findings[0]["category"] == "用語の使い方"
    assert findings[0]["level"] == "注意"


def test_yougo_check_oyobi_narabini_paired_with_oyobi_appends_nothing():
    """2. 正常: 「並びに」と「及び」が両方ある場合、findingsに追加されない"""
    findings = []

    yougo.check_oyobi_narabini("会員及び関係者並びに来賓に通知する。", findings)

    assert findings == []


def test_yougo_check_oyobi_narabini_no_narabini_appends_nothing():
    """3. 正常: 「並びに」がない場合、findingsに追加されない"""
    findings = []

    yougo.check_oyobi_narabini("会員に通知する。", findings)

    assert findings == []


def test_yougo_check_oyobi_narabini_detects_kana_form():
    """4. 正常: 仮名書き「ならびに」でも検出される"""
    findings = []

    yougo.check_oyobi_narabini("会員ならびに関係者に通知する。", findings)

    assert len(findings) == 1


"""
-- 関数 check_moshikuha_matawa のテスト --
1. 正常: 「若しくは」があり「又は」がない場合、findingが追加される
2. 正常: 「若しくは」と「又は」が両方ある場合、findingsに追加されない
3. 正常: 「若しくは」がない場合、findingsに追加されない
"""


def test_yougo_check_moshikuha_matawa_detects_unpaired_moshikuha():
    """1. 正常: 「若しくは」があり「又は」がない場合、findingが追加される"""
    findings = []

    yougo.check_moshikuha_matawa("Aさん若しくはBさんが担当する。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "term-moshikuha"
    assert findings[0]["level"] == "注意"


def test_yougo_check_moshikuha_matawa_paired_with_matawa_appends_nothing():
    """2. 正常: 「若しくは」と「又は」が両方ある場合、findingsに追加されない"""
    findings = []

    yougo.check_moshikuha_matawa("Aさん又はBさん若しくはCさんが担当する。", findings)

    assert findings == []


def test_yougo_check_moshikuha_matawa_no_moshikuha_appends_nothing():
    """3. 正常: 「若しくは」がない場合、findingsに追加されない"""
    findings = []

    yougo.check_moshikuha_matawa("Aさんが担当する。", findings)

    assert findings == []


"""
-- 関数 check_toori のテスト --
1. 正常: 「の通り」がある場合、findingが追加される（カテゴリは「漢字・かなの使い方」のまま）
2. 正常: 「大通り」は除外される
3. 正常: 「の通り」がない場合、findingsに追加されない
"""


def test_yougo_check_toori_detects_youtai_no_toori():
    """1. 正常: 「の通り」がある場合、findingが追加される（カテゴリは「漢字・かなの使い方」のまま）"""
    findings = []

    yougo.check_toori("指示の通り進める。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "kana-toori"
    assert findings[0]["category"] == "漢字・かなの使い方"
    assert findings[0]["level"] == "注意"


def test_yougo_check_toori_excludes_oodoori():
    """2. 正常: 「大通り」は除外される"""
    findings = []

    yougo.check_toori("駅前の大通りを進む。", findings)

    assert findings == []


def test_yougo_check_toori_no_match_appends_nothing():
    """3. 正常: 「の通り」がない場合、findingsに追加されない"""
    findings = []

    yougo.check_toori("指示どおりに進める。", findings)

    assert findings == []


"""
-- 関数 run のテスト --
1. 正常: 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる
"""


def test_yougo_run_calls_all_checks():
    """1. 正常: 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる"""
    findings = []
    text = (
        "会員並びに関係者に通知する。Aさん若しくはBさんが担当する。"
        "指示の通り進める。違和感を感じる。することができる。"
    )

    yougo.run(text, findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert "term-narabini" in rule_ids
    assert "term-moshikuha" in rule_ids
    assert "kana-toori" in rule_ids
    assert "jugon-違和感を感じる" in rule_ids
    assert "jochou-することができる" in rule_ids
