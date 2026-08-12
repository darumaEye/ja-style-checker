"""
# 用語の使い方（要領 Ⅱ）

用語の使い方に関する機械判定。
"""

import re

from .common import Category, Level, add, check_dictionary

# 重言（Ⅱ-5ウ）
JUGON_DICT = {
    "違和感を感じる": "違和感を覚える／違和感がある",
    "各都道府県ごとに": "各都道府県で／都道府県ごとに",
    "第１日目": "第1日／1日目",
    "第1日目": "第1日／1日目",
    "従来から": "従来／以前から",
    "まず最初に": "まず／最初に",
    "被害を被る": "被害を受ける",
    "後で後悔する": "後悔する",
    "馬から落馬": "落馬",
}

# 冗長表現（Ⅱ-5ウ）
JOCHOU_DICT = {
    "することができる": "できる",
    "することが可能である": "できる",
    "することが可能となる": "できるようになる",
}


def check_oyobi_narabini(text, findings):
    """「並びに（ならびに）」が「及び（および）」と対応しているかチェック（Ⅱ-1）。
    漢字表記・仮名書き（Ⅰ-1(3)オで認められる解説・広報等の仮名書き）の双方を対象とする。"""
    for line in text.split("\n"):
        for sentence in re.split(r"。", line):
            has_narabini = "並びに" in sentence or "ならびに" in sentence
            has_oyobi = "及び" in sentence or "および" in sentence
            if has_narabini and not has_oyobi:
                ctx = sentence.strip()[:60]
                add(
                    findings,
                    "term-narabini",
                    Category.YOUGO,
                    Level.WARNING,
                    ctx,
                    "「並びに／ならびに」は「及び／および」と対で使うのが原則です。対応する語がなければ「と」等に言い換えるか、対応する語を補ってください。",
                    "Ⅱ-1",
                )


def check_moshikuha_matawa(text, findings):
    """「若しくは（もしくは）」が「又は（または）」と対応しているかチェック（Ⅱ-1）"""
    for line in text.split("\n"):
        for sentence in re.split(r"。", line):
            has_moshikuha = "若しくは" in sentence or "もしくは" in sentence
            has_matawa = "又は" in sentence or "または" in sentence
            if has_moshikuha and not has_matawa:
                ctx = sentence.strip()[:60]
                add(
                    findings,
                    "term-moshikuha",
                    Category.YOUGO,
                    Level.WARNING,
                    ctx,
                    "「若しくは／もしくは」は「又は／または」と対で使うのが原則です。対応する語がなければ「か」等に言い換えるか、対応する語を補ってください。",
                    "Ⅱ-1",
                )


def check_toori(text: str, findings: list[dict[str, str]]) -> None:
    """様態を表す「通り」の仮名書きチェック（Ⅰ-1(3)ア）。大通り等の固有語は除外。

    注：`koyobun_rules.md`の表記上は「6. 用語の使い方」欄に掲載されているが、
    出力する`category`は元の`mechanical_check.py`の実装どおり「漢字・かなの使い方」
    のまま変更していない（動作を変えないため）。
    """
    for m in re.finditer(r"の通り", text):
        ctx = text[max(0, m.start() - 10) : m.end() + 10]
        if "大通り" in ctx:
            continue
        add(
            findings,
            "kana-toori",
            Category.KANJI_KANA,
            Level.WARNING,
            ctx,
            "「の通り」→「のとおり」（様態を表す場合は仮名書き）",
            "Ⅰ-1(3)ア",
        )


def run(text, findings):
    """このカテゴリの全チェックを実行する。"""
    check_oyobi_narabini(text, findings)
    check_moshikuha_matawa(text, findings)
    check_toori(text, findings)
    check_dictionary(
        text, findings, JUGON_DICT, "jugon", Category.YOUGO, Level.WARNING, "Ⅱ-5ウ"
    )
    check_dictionary(
        text, findings, JOCHOU_DICT, "jochou", Category.YOUGO, Level.INFO, "Ⅱ-5ウ"
    )
