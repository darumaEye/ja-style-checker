"""
# common モジュール

全カテゴリ共通のヘルパー関数。

## 関数

- `add()`: 検出結果1件を `findings` リストに追加する。
- `check_dictionary()`: 置換辞書ベースの検出を行う。
- `check_pattern_dict()`: 正規表現パターンベースの検出を行う。

各カテゴリモジュールはこのモジュールをインポートして使う。
`category` / `level` は、呼び出し側で必ず `Category` / `Level` のメンバーを渡す。`rules_checklist.md` の凡例にない値を渡すと、実行時に `ValueError` となる。
"""

import re
from enum import Enum


class Category(str, Enum):
    """検出結果の分類。 `koyobun_rules.md` の8カテゴリに、社内ルール・
    個人ルール・案件ルール由来の指摘のための値を加えたもの。

    KANJI_KANA 〜 KOUSEI: 要領（ `koyobun_rules.md` ）由来の8カテゴリ
    COMPANY_RULE: 社内ルール（ `company_rules.md` ）由来の指摘に使う。
        `company_rules.md` がカテゴリ表を持つようになった場合、その
        カテゴリに要領の8分類が流用できるならそちらを使ってよいが、
        要領の分類に収まらない社内独自の観点はこちらを使う。
    USER_RULE: Claude Projectのプロジェクト知識にある `user_rules.md`
        （個人ルール）由来の指摘に使う。
    PROJECT_RULE: Claude Projectのプロジェクト知識にある `project_rules.md`
        （案件独自ルール）由来の指摘に使う。
    """

    KANJI_KANA = "漢字・かなの使い方"
    OKURIGANA = "送り仮名"
    GAIRAIGO = "外来語の表記"
    SUUJI = "数字の使い方"
    KIGOU = "符号・句読点"
    YOUGO = "用語の使い方"
    BUNTAI = "文体・文の書き方"
    KOUSEI = "文書構成・見出し"
    COMPANY_RULE = "社内ルール"
    USER_RULE = "個人ルール"
    PROJECT_RULE = "案件ルール"


class Level(str, Enum):
    """指摘の対応レベル。 `koyobun_rules.md` の凡例で定義されている3段階。"""

    ERROR = "要修正"
    WARNING = "注意"
    INFO = "参考"


def add(
    findings: list[dict[str, str]],
    rule_id: str,
    category: Category,
    level: Level,
    excerpt: str,
    suggestion: str,
    source: str,
) -> None:
    """検出結果1件を `findings` リストに追加する共通ヘルパー。"""
    findings.append(
        {
            "rule_id": rule_id,
            "category": category.value,
            "level": level.value,
            "excerpt": excerpt.strip(),
            "suggestion": suggestion,
            "source": source,
        }
    )


def check_dictionary(
    text: str,
    findings: list[dict[str, str]],
    dictionary: dict[str, str | None],
    rule_id_prefix: str,
    category: Category,
    level: Level,
    source: str,
    exclude_if_followed_by: str | None = None,
) -> None:
    """置換辞書（ `bad` → `good` ）に基づき、 `text` から該当語を検出して `findings` に追加する。

    `good` が `None` のエントリはスキップする（対応関係チェック等、別関数で個別処理するため）。
    `exclude_if_followed_by` を指定すると、該当語の直後がその文字集合に含まれる場合は
    誤検出として除外する（例：「ユーザ」+「ー」＝「ユーザー」は正しい表記）。
    """
    for bad, good in dictionary.items():
        if good is None:
            continue
        for m in re.finditer(re.escape(bad), text):
            if exclude_if_followed_by:
                after = text[m.end() : m.end() + 1]
                if after in exclude_if_followed_by:
                    continue  # 例：「ユーザ」+「ー」＝「ユーザー」は正しい表記なので除外
            ctx = text[max(0, m.start() - 10) : m.end() + 10]
            add(
                findings,
                f"{rule_id_prefix}-{bad}",
                category,
                level,
                ctx,
                f"「{bad}」→「{good}」",
                source,
            )


def check_pattern_dict(
    text: str,
    findings: list[dict[str, str]],
    patterns: list[tuple[re.Pattern[str], str]],
    rule_id_prefix: str,
    category: Category,
    level: Level,
    source: str,
) -> None:
    """(正規表現, 置換文字列)のリストに基づき、 `text` から該当箇所を検出して `findings` に追加する。"""
    for pattern, replacement in patterns:
        for m in pattern.finditer(text):
            ctx = text[max(0, m.start() - 10) : m.end() + 10]
            suggestion = pattern.sub(replacement, m.group(0))
            add(
                findings,
                f"{rule_id_prefix}-{m.group(0)}",
                category,
                level,
                ctx,
                f"「{m.group(0)}」→「{suggestion}」",
                source,
            )
