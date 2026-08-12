"""
# 数字の使い方（要領 Ⅰ-4）

数字の使い方に関する機械判定。

## 未実装

- 「横書きでは算用数字を使う」（漢数字→算用数字への変換）、
  「兆・億・万は漢字、千・百は算用数字」（Ⅰ-4ウ）は`koyobun_rules.md`上は
  機械判定可能とされているが、現状は未実装。
"""

import re

from .common import Category, Level, add, check_pattern_dict

# 「か所」「か月」表記（Ⅰ-4ケ）
KASHO_PATTERNS = [
    (re.compile(r"(\d+)ヶ所"), r"\1か所"),
    (re.compile(r"(\d+)ヵ所"), r"\1か所"),
    (re.compile(r"(\d+)カ所"), r"\1か所"),
    (re.compile(r"(\d+)ヶ月"), r"\1か月"),
    (re.compile(r"(\d+)ヵ月"), r"\1か月"),
    (re.compile(r"(\d+)カ月"), r"\1か月"),
]


def check_zenkaku_hankaku_suuji(text, findings):
    """数字の全角・半角混在チェック（Ⅰ-4エ）"""
    has_zenkaku = bool(re.search(r"[０-９]", text))
    has_hankaku = bool(re.search(r"[0-9]", text))
    if has_zenkaku and has_hankaku:
        add(
            findings,
            "number-width-mix",
            Category.SUUJI,
            Level.WARNING,
            "（文書全体）",
            "全角数字と半角数字が混在しています。文書内でどちらかに統一してください。",
            "Ⅰ-4エ",
        )


def check_comma_kugiri(text, findings):
    """4桁以上の数字のコンマ区切りチェック（Ⅰ-4イ）。年・電話番号・郵便番号は除外する。"""
    for m in re.finditer(r"(?<!\d)(\d{4,})(?!\d)", text):
        num = m.group(1)
        start, end = m.start(), m.end()
        after = text[end : end + 3]
        before = text[max(0, start - 3) : start]
        # 年（2024年 等）、電話番号やハイフン付き番号、既にコンマがある場合は除外
        if after.startswith("年"):
            continue
        if "-" in before or "-" in after or "‐" in before or "‐" in after:
            continue
        if "," in before[-1:] or "," in after[:1]:
            continue
        ctx = text[max(0, start - 10) : end + 10]
        formatted = "{:,}".format(int(num))
        add(
            findings,
            "number-comma",
            Category.SUUJI,
            Level.ERROR,
            ctx,
            f"{num} → {formatted}（3桁ごとにコンマ区切り）",
            "Ⅰ-4イ",
        )


def run(text, findings):
    """このカテゴリの全チェックを実行する。"""
    check_zenkaku_hankaku_suuji(text, findings)
    check_comma_kugiri(text, findings)
    check_pattern_dict(
        text, findings, KASHO_PATTERNS, "kasho", Category.SUUJI, Level.INFO, "Ⅰ-4ケ"
    )
