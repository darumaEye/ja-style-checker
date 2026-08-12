"""
# 文体・文の書き方（要領 Ⅲ-1、Ⅲ-3）

文体・文の書き方に関する機械判定。

## 未実装

- 「同じ助詞の連続使用を避ける」（Ⅲ-3キ）は`koyobun_rules.md`上は機械判定可能と
  されているが、現状は未実装。
"""

import re

from .common import Category, Level, add


def check_jotai_keitai_kongou(text, findings):
    """常体・敬体混在チェック（Ⅲ-1イ）"""
    has_keitai = bool(re.search(r"(です|ます)。", text))
    has_jotai = bool(re.search(r"(である|だ)。", text))
    if has_keitai and has_jotai:
        add(
            findings,
            "style-mix",
            Category.BUNTAI,
            Level.ERROR,
            "（文書全体）",
            "「です・ます」体と「である・だ」体が混在しています。原則としてどちらかに統一してください（引用・箇条書内は例外）。",
            "Ⅲ-1イ",
        )


def check_surubeki(text, findings):
    """「するべき」→「すべき」チェック（Ⅲ-1オ）"""
    # NOTE: [一-\u9fffぁ-ん] は「漢字またはひらがな1字」を表す。
    for m in re.finditer(r"[一-\u9fffぁ-ん]するべき", text):
        ctx = text[max(0, m.start() - 10) : m.end() + 10]
        add(
            findings,
            "style-surubeki",
            Category.BUNTAI,
            Level.WARNING,
            ctx,
            "「するべき」→「すべき」",
            "Ⅲ-1オ",
        )


def check_sentence_length(text, findings, limit=60):
    """一文の長さチェック（Ⅲ-3ア）。
    行（見出し等、句点のない行）をまたいで文を連結しないよう、
    改行ごとに区切ってから句点で文を切り出す。"""
    for line in text.split("\n"):
        for sentence in re.split(r"。", line):
            s = sentence.strip()
            length = len(re.sub(r"\s", "", s))
            if length > limit:
                add(
                    findings,
                    "sentence-length",
                    Category.BUNTAI,
                    Level.INFO,
                    (s[:40] + "…") if len(s) > 40 else s,
                    f"一文が{length}字あります。50〜60字を超えたら分割を検討してください。",
                    "Ⅲ-3ア",
                )


def run(text, findings):
    """このカテゴリの全チェックを実行する。"""
    check_jotai_keitai_kongou(text, findings)
    check_surubeki(text, findings)
    check_sentence_length(text, findings)
