"""
--- モジュール buntai の単体テスト ---
"""

from checks import buntai

"""
-- 関数 check_jotai_keitai_kongou のテスト --
1. 正常: です・ます体とである・だ体が両方存在する場合、1件のfindingが追加される
2. 正常: です・ます体のみの場合、findingsに追加されない
3. 正常: である・だ体のみの場合、findingsに追加されない
4. 正常: どちらも存在しない場合、findingsに追加されない
"""


def test_buntai_check_jotai_keitai_kongou_detects_mix():
    """1. 正常: です・ます体とである・だ体が両方存在する場合、1件のfindingが追加される"""
    findings = []

    buntai.check_jotai_keitai_kongou("これはペンです。それは机である。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "style-mix"
    assert findings[0]["category"] == "文体・文の書き方"
    assert findings[0]["level"] == "要修正"


def test_buntai_check_jotai_keitai_kongou_keitai_only_appends_nothing():
    """2. 正常: です・ます体のみの場合、findingsに追加されない"""
    findings = []

    buntai.check_jotai_keitai_kongou("これはペンです。それは机です。", findings)

    assert findings == []


def test_buntai_check_jotai_keitai_kongou_jotai_only_appends_nothing():
    """3. 正常: である・だ体のみの場合、findingsに追加されない"""
    findings = []

    buntai.check_jotai_keitai_kongou("これはペンである。それは机だ。", findings)

    assert findings == []


def test_buntai_check_jotai_keitai_kongou_neither_appends_nothing():
    """4. 正常: どちらも存在しない場合、findingsに追加されない"""
    findings = []

    buntai.check_jotai_keitai_kongou("見出しのみの文書", findings)

    assert findings == []


"""
-- 関数 check_surubeki のテスト --
1. 正常: 「（漢字/ひらがな）するべき」が1箇所ある場合、1件のfindingが追加される
2. 正常: 複数箇所ある場合、マッチ数だけfindingsに追加される
3. 正常: 該当パターンがない場合、findingsに追加されない
"""


def test_buntai_check_surubeki_detects_single_match():
    """1. 正常: 「（漢字/ひらがな）するべき」が1箇所ある場合、1件のfindingが追加される"""
    findings = []

    buntai.check_surubeki("これは対応するべきだ。", findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "style-surubeki"
    assert findings[0]["level"] == "注意"
    assert findings[0]["suggestion"] == "「するべき」→「すべき」"


def test_buntai_check_surubeki_counts_each_occurrence():
    """2. 正常: 複数箇所ある場合、マッチ数だけfindingsに追加される"""
    findings = []

    buntai.check_surubeki("対応するべきだ。次に確認するべきだ。", findings)

    assert len(findings) == 2


def test_buntai_check_surubeki_no_match_appends_nothing():
    """3. 正常: 該当パターンがない場合、findingsに追加されない"""
    findings = []

    buntai.check_surubeki("これは対応すべきだ。", findings)

    assert findings == []


"""
-- 関数 check_sentence_length のテスト --
1. 正常: limit以下の文のみの場合、findingsに追加されない
2. 正常: limitを超える文がある場合、1件のfindingが追加される
3. 正常: excerptが40字を超える場合、40字+「…」に切り詰められる
4. 正常: limit引数を指定した場合、その値が閾値として使われる
5. 正常: 空白文字は文字数カウントから除外される
"""


def test_buntai_check_sentence_length_within_limit_appends_nothing():
    """1. 正常: limit以下の文のみの場合、findingsに追加されない"""
    findings = []

    buntai.check_sentence_length("短い文です。", findings)

    assert findings == []


def test_buntai_check_sentence_length_over_limit_appends_one():
    """2. 正常: limitを超える文がある場合、1件のfindingが追加される"""
    findings = []
    long_sentence = "あ" * 61 + "。"

    buntai.check_sentence_length(long_sentence, findings)

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "sentence-length"
    assert findings[0]["level"] == "参考"


def test_buntai_check_sentence_length_truncates_excerpt_over_40_chars():
    """3. 正常: excerptが40字を超える場合、40字+「…」に切り詰められる"""
    findings = []
    long_sentence = "あ" * 61 + "。"

    buntai.check_sentence_length(long_sentence, findings)

    assert findings[0]["excerpt"] == "あ" * 40 + "…"


def test_buntai_check_sentence_length_respects_custom_limit():
    """4. 正常: limit引数を指定した場合、その値が閾値として使われる"""
    findings = []

    buntai.check_sentence_length("これは短い文です。", findings, limit=5)

    assert len(findings) == 1


def test_buntai_check_sentence_length_ignores_whitespace_in_count():
    """5. 正常: 空白文字は文字数カウントから除外される"""
    findings = []
    # 61字の非空白文字 + 大量の空白。空白を除けば61字なので超過するはず。
    sentence = ("あ" * 61) + (" " * 100) + "。"

    buntai.check_sentence_length(sentence, findings, limit=60)

    assert len(findings) == 1


"""
-- 関数 run のテスト --
1. 正常: 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる
"""


def test_buntai_run_calls_all_checks():
    """1. 正常: 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる"""
    findings = []
    text = "これはペンです。それは机である。対応するべきだ。" + ("あ" * 61) + "。"

    buntai.run(text, findings)

    rule_ids = {f["rule_id"] for f in findings}
    assert "style-mix" in rule_ids
    assert "style-surubeki" in rule_ids
    assert "sentence-length" in rule_ids
