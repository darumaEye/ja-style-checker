#!/usr/bin/env python3
"""
# 公用文要領ベースの機械判定チェッカー

「新しい『公用文作成の要領』に向けて」（令和3年3月 文化審議会国語分科会）のうち、
文脈判断を伴わず正規表現・辞書で一意に検出できるルールのみを対象とする。
専門用語の言い換え要否、文体の親しみやすさ、一文の論点整理など判断が
必要な項目はルールファイルの「判断」区分としてClaude側が扱う。

実体は `checks/` パッケージにルールファイルの8カテゴリ単位で分割されている
（`checks/kanji_kana.py`, `checks/okurigana.py` 等）。このファイルはCLIとして
呼び出すためのエントリーポイント。

## 使い方

```
python3 mechanical_check.py <対象テキストファイル>
```

## 出力

標準出力にJSON配列。各要素は以下の形式。

```json
{
    "rule_id": "...",
    "category": "...",
    "level": "要修正 | 注意 | 参考",
    "excerpt": "該当箇所の抜粋",
    "suggestion": "修正案",
    "source": "要領の該当箇所"
}
```

## 注意

- 検出に用いる辞書は例示レベルであり、実運用で拡充されていくことを前提とする。
- 固有名詞・引用部分・コードやURLなどはここでは除外していない。
  「引用（「」内）は直接引用以外にも広く使われる」「固有名詞は正規表現では
  判定できない」など文脈判断が必要なため、除外は`SKILL.md`の指示に基づき
  Claude側（AI判断層）で行う。
"""

import json
import sys

from checks import run_all_checks


def main():
    """コマンドライン引数で指定されたファイルを読み込み、チェック結果をJSONで標準出力に出力する。"""
    if len(sys.argv) != 2:
        print(
            "使い方: python3 mechanical_check.py <対象テキストファイル>",
            file=sys.stderr,
        )
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    findings = run_all_checks(text)
    print(json.dumps(findings, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
