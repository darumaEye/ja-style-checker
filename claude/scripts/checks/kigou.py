"""
# 符号・句読点の使い方（要領 Ⅰ-5、Ⅰ-6）

符号・句読点の使い方に関する機械判定。

## 未実装

- 「「々」は複合語の切れ目では使わない」（Ⅰ-6イ）、「段落冒頭は1字下げる」（Ⅰ-6ア）は
  `koyobun_rules.md`上に項目があるが、現状は未実装（前者は判断区分）。
"""

import re

from .common import Category, Level, add


def check_touten_kongou(text, findings):
    """読点の「、」「，」混在チェック（Ⅰ-5(1)ア）"""
    has_ten = "、" in text
    has_comma = "，" in text
    if has_ten and has_comma:
        for m in re.finditer("，", text):
            ctx = text[max(0, m.start() - 10) : m.start() + 10]
            add(
                findings,
                "punct-touten-mix",
                Category.KIGOU,
                Level.ERROR,
                ctx,
                "「，」を「、」に統一する",
                "Ⅰ-5(1)ア",
            )


def check_kuten_piriodo(text, findings):
    """句点「．」の使用チェック（Ⅰ-5(1)ア）。数値の小数点は除外する。"""
    for m in re.finditer(r"．", text):
        start, end = m.start(), m.end()
        before = text[max(0, start - 1) : start]
        after = text[end : end + 1]
        if before.isdigit() and after.isdigit():
            continue  # 小数点は対象外
        ctx = text[max(0, start - 10) : end + 10]
        add(
            findings,
            "punct-kuten-piriodo",
            Category.KIGOU,
            Level.ERROR,
            ctx,
            "「．」を「。」に統一する",
            "Ⅰ-5(1)ア",
        )


def check_gikaku_fugou_zenhan(text, findings):
    """疑問符・感嘆符の後スペースチェック（Ⅰ-5(2)ア）"""
    for m in re.finditer(r"[？！][^\s　？！。\n]", text):
        ctx = text[max(0, m.start() - 10) : m.end() + 10]
        add(
            findings,
            "punct-gikaku-space",
            Category.KIGOU,
            Level.INFO,
            ctx,
            "疑問符・感嘆符の後に文が続く場合は1文字分（全角）空けます。",
            "Ⅰ-5(2)ア",
        )


def run(text, findings):
    """このカテゴリの全チェックを実行する。"""
    check_touten_kongou(text, findings)
    check_kuten_piriodo(text, findings)
    check_gikaku_fugou_zenhan(text, findings)
