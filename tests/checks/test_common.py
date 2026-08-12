"""
--- モジュール common の単体テスト ---
"""

import re

import pytest

from checks.common import Category, Level, add, check_dictionary, check_pattern_dict

"""
-- 関数 add のテスト --
1. 正常: findingsが空のとき、指定した内容の辞書が1件追加される
2. 正常: 既存のfindingsがある場合、末尾に追加され既存要素は変化しない
3. 正常: excerptの前後の空白（半角・全角スペース、タブ、改行）が除去され、
   空白のみの場合は空文字列になる
4. 正常: rule_id・suggestion・sourceは前後の空白を除去せずそのまま追加される
5. 正常: category・levelに渡したEnumメンバーのvalue（文字列）が格納される
6. 異常: category・levelにEnumでない値を渡すと、AttributeErrorが送出される
7. 正常: 戻り値はNoneである
8. 正常: 呼び出し前後で同一のfindingsオブジェクト（id）が変更される
9. 正常: 複数回呼び出すと、呼び出し順にfindingsへ追加される
"""


def test_common_add_appends_to_empty_findings():
    """1. 正常: findingsが空のとき、指定した内容の辞書が1件追加される"""
    findings = []

    add(findings, "r1", Category.KANJI_KANA, Level.WARNING, "抜粋", "提案", "出典")

    assert len(findings) == 1
    assert findings[0] == {
        "rule_id": "r1",
        "category": "漢字・かなの使い方",
        "level": "注意",
        "excerpt": "抜粋",
        "suggestion": "提案",
        "source": "出典",
    }


def test_common_add_preserves_existing_entries():
    """2. 正常: 既存のfindingsがある場合、末尾に追加され既存要素は変化しない"""
    existing = {
        "rule_id": "r0",
        "category": "用語の使い方",
        "level": "参考",
        "excerpt": "既存",
        "suggestion": "既存提案",
        "source": "既存出典",
    }
    findings = [existing]

    add(findings, "r1", Category.KANJI_KANA, Level.WARNING, "抜粋", "提案", "出典")

    assert len(findings) == 2
    assert findings[0] == existing
    assert findings[1]["rule_id"] == "r1"


@pytest.mark.parametrize(
    "excerpt, expected",
    [
        ("抜粋", "抜粋"),
        ("  抜粋  ", "抜粋"),
        ("　抜粋\t\n", "抜粋"),
        ("   ", ""),
        ("", ""),
    ],
)
def test_common_add_strips_excerpt_whitespace(excerpt, expected):
    """3. 正常: excerptの前後の空白（半角・全角スペース、タブ、改行）が除去され、
    空白のみの場合は空文字列になる
    """
    findings = []

    add(findings, "r1", Category.KANJI_KANA, Level.WARNING, excerpt, "提案", "出典")

    assert findings[0]["excerpt"] == expected


def test_common_add_does_not_strip_other_fields():
    """4. 正常: rule_id・suggestion・sourceは前後の空白を除去せずそのまま追加される"""
    findings = []

    add(
        findings,
        "r1",
        Category.KANJI_KANA,
        Level.WARNING,
        "抜粋",
        "  提案  ",
        "  出典  ",
    )

    assert findings[0]["suggestion"] == "  提案  "
    assert findings[0]["source"] == "  出典  "


@pytest.mark.parametrize("category", list(Category))
@pytest.mark.parametrize("level", list(Level))
def test_common_add_stores_enum_value_as_str(category, level):
    """5. 正常: category・levelに渡したEnumメンバーのvalue（文字列）が格納される"""
    findings = []

    add(findings, "r1", category, level, "抜粋", "提案", "出典")

    assert findings[0]["category"] == category.value
    assert findings[0]["level"] == level.value
    assert type(findings[0]["category"]) is str
    assert type(findings[0]["level"]) is str


@pytest.mark.parametrize("bad_arg", ["category", "level"])
def test_common_add_non_enum_category_or_level_raises_error(bad_arg):
    """6. 異常: category・levelにEnumでない値を渡すと、AttributeErrorが送出される"""
    findings = []
    kwargs = {"category": Category.KANJI_KANA, "level": Level.WARNING}
    kwargs[bad_arg] = "生の文字列"

    with pytest.raises(AttributeError):
        add(findings, "r1", kwargs["category"], kwargs["level"], "抜粋", "提案", "出典")


def test_common_add_returns_none():
    """7. 正常: 戻り値はNoneである"""
    findings = []

    result = add(
        findings, "r1", Category.KANJI_KANA, Level.WARNING, "抜粋", "提案", "出典"
    )

    assert result is None


def test_common_add_mutates_list_in_place():
    """8. 正常: 呼び出し前後で同一のfindingsオブジェクト（id）が変更される"""
    findings = []
    findings_id = id(findings)

    add(findings, "r1", Category.KANJI_KANA, Level.WARNING, "抜粋", "提案", "出典")

    assert id(findings) == findings_id


def test_common_add_appends_multiple_calls_in_order():
    """9. 正常: 複数回呼び出すと、呼び出し順にfindingsへ追加される"""
    findings = []

    add(findings, "r1", Category.KANJI_KANA, Level.WARNING, "1件目", "提案1", "出典1")
    add(findings, "r2", Category.YOUGO, Level.INFO, "2件目", "提案2", "出典2")

    assert [f["rule_id"] for f in findings] == ["r1", "r2"]
    assert [f["excerpt"] for f in findings] == ["1件目", "2件目"]


"""
-- 関数 check_dictionary のテスト --
1. 正常: 辞書内の語がtextに1つ含まれる場合、対応する内容のfindingが1件追加される
2. 正常: 辞書のvalueがNoneのエントリは検出されない
3. 正常: 同じ語が複数回出現する場合、出現数だけfindingsに追加される
4. 正常: textに辞書のどの語も含まれない場合、findingsに追加されない
5. 正常: exclude_if_followed_byを指定し、直後の文字が集合に含まれる場合は除外される
6. 正常: exclude_if_followed_byを指定していても、直後の文字が集合に含まれなければ検出される
"""


def test_common_check_dictionary_detects_single_match():
    """1. 正常: 辞書内の語がtextに1つ含まれる場合、対応する内容のfindingが1件追加される"""
    findings = []

    check_dictionary(
        "従って結論を述べる。",
        findings,
        {"従って": "したがって"},
        "kanakaki",
        Category.KANJI_KANA,
        Level.WARNING,
        "Ⅰ-1(3)",
    )

    assert len(findings) == 1
    assert findings[0]["rule_id"] == "kanakaki-従って"
    assert findings[0]["category"] == "漢字・かなの使い方"
    assert findings[0]["level"] == "注意"
    assert findings[0]["suggestion"] == "「従って」→「したがって」"
    assert findings[0]["source"] == "Ⅰ-1(3)"


def test_common_check_dictionary_skips_none_value_entries():
    """2. 正常: 辞書のvalueがNoneのエントリは検出されない"""
    findings = []

    check_dictionary(
        "並びに関係者各位",
        findings,
        {"並びに": None},
        "kanakaki",
        Category.KANJI_KANA,
        Level.WARNING,
        "Ⅰ-1(3)",
    )

    assert findings == []


def test_common_check_dictionary_counts_each_occurrence():
    """3. 正常: 同じ語が複数回出現する場合、出現数だけfindingsに追加される"""
    findings = []

    check_dictionary(
        "従って前者、従って後者。",
        findings,
        {"従って": "したがって"},
        "kanakaki",
        Category.KANJI_KANA,
        Level.WARNING,
        "Ⅰ-1(3)",
    )

    assert len(findings) == 2


def test_common_check_dictionary_no_match_appends_nothing():
    """4. 正常: textに辞書のどの語も含まれない場合、findingsに追加されない"""
    findings = []

    check_dictionary(
        "該当する語がない文章です。",
        findings,
        {"従って": "したがって"},
        "kanakaki",
        Category.KANJI_KANA,
        Level.WARNING,
        "Ⅰ-1(3)",
    )

    assert findings == []


def test_common_check_dictionary_excludes_when_followed_by_excluded_char():
    """5. 正常: exclude_if_followed_byを指定し、直後の文字が集合に含まれる場合は除外される"""
    findings = []

    check_dictionary(
        "ユーザー登録",
        findings,
        {"ユーザ": "ユーザー"},
        "gairaigo-chouon",
        Category.GAIRAIGO,
        Level.WARNING,
        "Ⅰ-3エ",
        exclude_if_followed_by={"ー"},
    )

    assert findings == []


def test_common_check_dictionary_detects_when_not_followed_by_excluded_char():
    """6. 正常: exclude_if_followed_byを指定していても、直後の文字が集合に含まれなければ検出される"""
    findings = []

    check_dictionary(
        "ユーザ登録",
        findings,
        {"ユーザ": "ユーザー"},
        "gairaigo-chouon",
        Category.GAIRAIGO,
        Level.WARNING,
        "Ⅰ-3エ",
        exclude_if_followed_by={"ー"},
    )

    assert len(findings) == 1


"""
-- 関数 check_pattern_dict のテスト --
1. 正常: パターンにマッチする文字列がある場合、1件のfindingが追加される
2. 正常: 複数箇所にマッチする場合、マッチ数だけ追加される
3. 正常: マッチしない場合、findingsに追加されない
4. 正常: suggestionにパターン置換後の文字列が含まれる
5. 正常: 複数のパターンを渡した場合、それぞれのパターンで検出される
"""


def test_common_check_pattern_dict_detects_single_match():
    """1. 正常: パターンにマッチする文字列がある場合、1件のfindingが追加される"""
    findings = []

    check_pattern_dict(
        "3ヶ所を確認する。",
        findings,
        [(re.compile(r"(\d+)ヶ所"), r"\1か所")],
        "kasho",
        Category.SUUJI,
        Level.INFO,
        "Ⅰ-4ケ",
    )

    assert len(findings) == 1
    assert findings[0]["category"] == "数字の使い方"
    assert findings[0]["level"] == "参考"
    assert findings[0]["source"] == "Ⅰ-4ケ"


def test_common_check_pattern_dict_counts_each_match():
    """2. 正常: 複数箇所にマッチする場合、マッチ数だけ追加される"""
    findings = []

    check_pattern_dict(
        "3ヶ所と5ヶ所を確認する。",
        findings,
        [(re.compile(r"(\d+)ヶ所"), r"\1か所")],
        "kasho",
        Category.SUUJI,
        Level.INFO,
        "Ⅰ-4ケ",
    )

    assert len(findings) == 2


def test_common_check_pattern_dict_no_match_appends_nothing():
    """3. 正常: マッチしない場合、findingsに追加されない"""
    findings = []

    check_pattern_dict(
        "マッチしない文章です。",
        findings,
        [(re.compile(r"(\d+)ヶ所"), r"\1か所")],
        "kasho",
        Category.SUUJI,
        Level.INFO,
        "Ⅰ-4ケ",
    )

    assert findings == []


def test_common_check_pattern_dict_suggestion_contains_replacement():
    """4. 正常: suggestionにパターン置換後の文字列が含まれる"""
    findings = []

    check_pattern_dict(
        "3ヶ所を確認する。",
        findings,
        [(re.compile(r"(\d+)ヶ所"), r"\1か所")],
        "kasho",
        Category.SUUJI,
        Level.INFO,
        "Ⅰ-4ケ",
    )

    assert findings[0]["suggestion"] == "「3ヶ所」→「3か所」"
    assert findings[0]["rule_id"] == "kasho-3ヶ所"


def test_common_check_pattern_dict_applies_all_given_patterns():
    """5. 正常: 複数のパターンを渡した場合、それぞれのパターンで検出される"""
    findings = []

    check_pattern_dict(
        "3ヶ所と2ヶ月を確認する。",
        findings,
        [
            (re.compile(r"(\d+)ヶ所"), r"\1か所"),
            (re.compile(r"(\d+)ヶ月"), r"\1か月"),
        ],
        "kasho",
        Category.SUUJI,
        Level.INFO,
        "Ⅰ-4ケ",
    )

    assert len(findings) == 2
    assert {f["suggestion"] for f in findings} == {
        "「3ヶ所」→「3か所」",
        "「2ヶ月」→「2か月」",
    }
