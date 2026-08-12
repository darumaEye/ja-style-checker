"""
# checks パッケージ

機械判定層のチェック関数を、`koyobun_rules.md` の8カテゴリに対応するモジュールに
分割して束ねるパッケージ。

## インターフェース

- 各モジュールは `run(text, findings)` を公開する。
- `mechanical_check.py` はこのパッケージの `run_all_checks()` だけを呼び出す。
"""

from . import (
    buntai,
    gairaigo,
    kanji_kana,
    kigou,
    kousei,
    okurigana,
    suuji,
    yougo,
)

# koyobun_rules.md のカテゴリ番号順
_MODULES = [
    kanji_kana,  # 1. 漢字・かなの使い方
    okurigana,  # 2. 送り仮名
    gairaigo,  # 3. 外来語の表記
    suuji,  # 4. 数字の使い方
    kigou,  # 5. 符号・句読点の使い方
    yougo,  # 6. 用語の使い方
    buntai,  # 7. 文体・文の書き方
    kousei,  # 8. 文書構成・見出し
]


def run_all_checks(text: str) -> list[dict[str, str]]:
    """全チェックモジュールを `text` に対して実行し、検出結果のリストを返す。"""
    findings: list[dict[str, str]] = []
    for module in _MODULES:
        module.run(text, findings)
    return findings
