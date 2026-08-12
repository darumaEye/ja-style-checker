"""
--- モジュール kanji_kana の単体テスト ---
"""

from checks.kanji_kana import (
    JOYO_KANJI,
    _load_joyo_kanji,
    check_hyougai_kanji_char_level,
    run,
)

"""
-- 関数 _load_joyo_kanji のテスト --
1. 正常: 戻り値がfrozensetであり、既知の常用漢字（「愛」等）が含まれる
2. 正常: 件数が常用漢字表の字数（2,136字）と一致する
"""


def test_kanji_kana__load_joyo_kanji_returns_frozenset_containing_known_kanji():
    """1. 正常: 戻り値がfrozensetであり、既知の常用漢字（「愛」等）が含まれる"""
    result = _load_joyo_kanji()

    assert isinstance(result, frozenset)
    assert "愛" in result


def test_kanji_kana__load_joyo_kanji_has_2136_entries():
    """2. 正常: 件数が常用漢字表の字数（2,136字）と一致する"""
    result = _load_joyo_kanji()

    assert len(result) == 2136


"""
-- 関数 check_hyougai_kanji_char_level のテスト --
1. 正常: 常用漢字表にない漢字が含まれる場合、findingが追加される（レベル参考）
2. 正常: 常用漢字のみの場合、findingsに追加されない
3. 正常: 「々」は検出対象外
4. 正常: 同じ表外漢字が複数回出現する場合、出現ごとに個別のfindingが追加される（rule_idは同じになる）
"""


def test_kanji_kana_check_hyougai_kanji_char_level_detects_non_joyo_kanji():
    """1. 正常: 常用漢字表にない漢字が含まれる場合、findingが追加される（レベル参考）"""
    findings = []
    assert "薔" not in JOYO_KANJI

    check_hyougai_kanji_char_level("薔薇の花が咲いた。", findings)

    assert len(findings) >= 1
    assert all(f["level"] == "参考" for f in findings)
    assert all(f["category"] == "漢字・かなの使い方" for f in findings)


def test_kanji_kana_check_hyougai_kanji_char_level_joyo_only_appends_nothing():
    """2. 正常: 常用漢字のみの場合、findingsに追加されない"""
    findings = []

    check_hyougai_kanji_char_level("愛と安全を大切にする。", findings)

    assert findings == []


def test_kanji_kana_check_hyougai_kanji_char_level_ignores_odoriji():
    """3. 正常: 「々」は検出対象外"""
    findings = []

    check_hyougai_kanji_char_level("人々が集まる。", findings)

    assert findings == []


def test_kanji_kana_check_hyougai_kanji_char_level_repeats_finding_per_occurrence():
    """4. 正常: 同じ表外漢字が複数回出現する場合、出現ごとに個別のfindingが追加される（rule_idは同じになる）"""
    findings = []

    check_hyougai_kanji_char_level("薔と薔", findings)

    assert len(findings) == 2
    assert findings[0]["rule_id"] == findings[1]["rule_id"] == "hyougai-kanji-char-薔"


"""
-- 関数 run のテスト --
1. 正常: 表外漢字・GAIJI_DICT・KANA_KAKI_DICT・HOJO_DOUSHI_PATTERNSそれぞれの検出条件を
   満たすtextを渡すと、対応するrule_idがすべてfindingsに含まれる
2. 正常: GAIJI_DICTの語に含まれる表外文字は、check_hyougai_kanji_char_levelでも
   文字単位で重複して検出される（仕様上の既知の重複。Claude側でまとめる想定）
"""


def test_kanji_kana_run_calls_all_checks():
    """1. 正常: 表外漢字・GAIJI_DICT・KANA_KAKI_DICT・HOJO_DOUSHI_PATTERNSそれぞれの検出条件を
    満たすtextを渡すと、対応するrule_idがすべてfindingsに含まれる
    """
    findings = []
    text = "薔薇が咲いた。憂鬱な気分だ。従って中止する。て下さい。"

    run(text, findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert any(r.startswith("hyougai-kanji-char-") for r in rule_ids)
    assert "gaiji-憂鬱" in rule_ids
    assert "kanakaki-従って" in rule_ids
    assert "hojo-doushi-て下さい" in rule_ids


def test_kanji_kana_run_gaiji_dict_word_duplicates_char_level_finding():
    """2. 正常: GAIJI_DICTの語に含まれる表外文字は、check_hyougai_kanji_char_levelでも
    文字単位で重複して検出される（仕様上の既知の重複。Claude側でまとめる想定）
    """
    findings = []
    assert "竄" not in JOYO_KANJI

    run("データを改竄した。", findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert "gaiji-改竄" in rule_ids
    assert "hyougai-kanji-char-竄" in rule_ids
