#!/usr/bin/env python3
"""
関数一覧とテストの`docstring`を読み取り、テスト実装状況を表として出力する。

対象は `claude/scripts/`・`scripts/` 以下のソースと `tests/` 以下のテストコード。

## テストケースの記法

テスト側の`docstring`に以下の記法でケースを書いておくと、関数ごとのテスト件数と
ケース一覧を集計できる。

```python
\"\"\"
--- モジュール/クラス <名前> の単体テスト ---

-- 関数 <名前> のテスト --
1. 正常: 正しく〜される
2. 異常: 〜した場合、エラーになる
\"\"\"
```

同じ (ファイル, クラス, 関数, ケース番号) の記載が複数箇所にある場合
（マスタ一覧と各テスト関数の`docstring`への再掲など）は1件にまとめて数える。

## 使い方

```
python3 report_test_status.py           # 標準出力
python3 report_test_status.py -o 出力名  # ファイル出力
```
"""

import argparse
import ast
import io
import re
import sys
import tokenize
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC_DIRS = [ROOT / "claude" / "scripts", ROOT / "scripts"]
TESTS_DIR = ROOT / "tests"

# テスト不要な特殊関数
NO_TEST_NEEDED = frozenset()

RE_HEADER = re.compile(r"^-+\s*(?:モジュール|クラス)\s+(\S+)\s+の.*テスト\s*-+$")
RE_FN_HEADER = re.compile(r"^-+\s*関数\s+(\S+)\s+のテスト\s*-+$")
RE_CASE = re.compile(r"^(\d+)\.\s*(正常|異常):\s*(.*)$")


def parse_functions(path: Path) -> list[dict]:
    """
    ソースファイルから、テスト対象になる関数（モジュール直下・クラス内の
    `def`/`async def`）を抽出する。関数内で定義されたローカル関数は対象外。

    各関数を `{'class_name', 'match_key', 'fn', 'vis', 'file'}` の辞書として返す。
    `class_name` は表示用（モジュール直下なら `None`）。
    `match_key` はテストdocstringとの突き合わせ用（クラス名、なければ
    モジュール名。`__init__.py` の場合はパッケージ名＝親ディレクトリ名）。
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    module_name = path.parent.name if path.name == "__init__.py" else path.stem

    functions: list[dict] = []

    def visit_body(body: list[ast.stmt], class_name: str | None) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit_body(node.body, node.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = node.name
                if name.startswith("__") and name.endswith("__"):
                    vis = "public"
                elif name.startswith("_"):
                    vis = "private"
                else:
                    vis = "public"
                functions.append(
                    {
                        "class_name": class_name,
                        "match_key": (
                            class_name if class_name is not None else module_name
                        ),
                        "fn": name,
                        "vis": vis,
                        "file": path.name,
                    }
                )

    visit_body(tree.body, None)
    return functions


def extract_doc_lines(path: Path) -> list[str]:
    """
    ファイル内の文字列リテラル文（docstringおよび、import文の後などに置かれた
    注記用の文字列リテラル）と `#` コメントの中身を、ファイル中の出現順に
    1行ずつ並べて返す。

    docstringに限定せず「式文として置かれた文字列リテラル」全般を対象に
    することで、モジュール先頭のdocstring以外の場所に書かれたテストケース
    一覧も拾えるようにしている。
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    entries: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            for offset, line in enumerate(node.value.value.splitlines()):
                entries.append((node.lineno + offset, line))

    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            entries.append((token.start[0], token.string.lstrip("#").strip()))

    entries.sort(key=lambda x: x[0])
    return [line for _, line in entries]


def collect_test_cases(files: list[Path]) -> list[dict]:
    """
    docstringのテストケース記法を読み取り、テストケース一覧を返す。
    各ケースを `{'file', 'class_name', 'fn', 'num', 'type', 'desc'}` として返す。
    説明が複数行にまたがる場合、次のケース行・見出し行・空行が現れるまでの
    行を継続行として同じケースの説明に連結する。
    """
    cases: list[dict] = []
    seen: set[tuple] = set()

    for path in files:
        current_class: str | None = None
        current_fn: str | None = None
        active_case: dict | None = None

        for line in extract_doc_lines(path):
            stripped = line.strip()

            match_header = RE_HEADER.match(stripped)
            if match_header:
                current_class = match_header.group(1)
                current_fn = None
                active_case = None
                continue

            match_fn_header = RE_FN_HEADER.match(stripped)
            if match_fn_header:
                current_fn = match_fn_header.group(1)
                active_case = None
                continue

            if not stripped:
                active_case = None
                continue

            if current_class is None or current_fn is None:
                continue

            match_case = RE_CASE.match(stripped)
            if match_case:
                num = int(match_case.group(1))
                key = (path.name, current_class, current_fn, num)
                if key in seen:
                    active_case = None
                    continue
                seen.add(key)

                active_case = {
                    "file": path.name,
                    "class_name": current_class,
                    "fn": current_fn,
                    "num": num,
                    "type": match_case.group(2),
                    "desc": match_case.group(3).strip(),
                }
                cases.append(active_case)
                continue

            if active_case is not None:
                active_case["desc"] = f"{active_case['desc']} {stripped}".strip()

    return cases


def collect_test_counts(files: list[Path]) -> dict[tuple[str, str], int]:
    """`(class_name, fn)` → テストケース件数 のマップを返す。"""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for case in collect_test_cases(files):
        counts[(case["class_name"], case["fn"])] += 1
    return dict(counts)


def build_status_section(src_paths: list[Path], test_paths: list[Path]) -> str:
    """テスト実装状況セクションをマークダウンとして生成する。"""
    all_functions: list[dict] = []
    for p in src_paths:
        all_functions.extend(parse_functions(p))

    test_counts = collect_test_counts(test_paths)

    by_file: dict[str, list[dict]] = defaultdict(list)
    for fn_info in all_functions:
        by_file[fn_info["file"]].append(fn_info)

    lines: list[str] = ["# 1. テスト実装状況\n"]
    lines.append("- 表の ⚠️ 未実装 行を優先して対応してください。\n")
    total = untested = 0

    for filename in sorted(by_file):
        fns = by_file[filename]
        lines.append(f"## {filename}\n")
        lines.append("| クラス | 関数 | 可視性 | テスト件数 | 状況 |")
        lines.append("|---|---|---|---|---|")

        for fn in fns:
            name = fn["fn"]
            class_name = fn["class_name"] or "(module)"
            vis = fn["vis"]

            if name in NO_TEST_NEEDED:
                lines.append(f"| {class_name} | {name} | {vis} | - | N/A |")
                continue

            count = test_counts.get((fn["match_key"], name), 0)
            count_str = f"{count}件" if count else "-"

            total += 1
            if count == 0:
                status = "⚠️ 未実装"
                untested += 1
            else:
                status = "✅"

            lines.append(f"| {class_name} | {name} | {vis} | {count_str} | {status} |")

        lines.append("")

    tested = total - untested
    pct = int(100 * tested / total) if total > 0 else 0
    lines.insert(1, f"- **実装済み: {tested} / {total} ({pct}%)**\n")

    return "\n".join(lines)


def build_test_case_section(test_paths: list[Path]) -> str:
    """テストケース一覧セクションをマークダウンとして生成する。"""
    all_cases = collect_test_cases(test_paths)

    groups: dict[tuple[str, str, str], list[dict]] = {}
    for case in all_cases:
        key = (case["file"], case["class_name"], case["fn"])
        groups.setdefault(key, []).append(case)

    lines: list[str] = ["# 2. テストケース一覧\n"]
    lines.append("- 種別が正常のみ、または異常のみの関数がないか確認してください。\n")
    lines.append(
        "- ケース番号が連続しているか確認してください"
        "（番号の飛びは削除済みケースまたは記載漏れの可能性があります）。\n"
    )
    lines.append(
        "- 一覧に記載されたケースに対応するテスト関数（def test_*）が"
        "実際に存在するか確認してください。\n"
    )

    for (file, class_name, fn), cases in groups.items():
        lines.append(f"## {file} — {class_name}::{fn}\n")
        lines.append("| # | 種別 | 説明 |")
        lines.append("|---|---|---|")
        for case in sorted(cases, key=lambda c: c["num"]):
            lines.append(f"| {case['num']} | {case['type']} | {case['desc']} |")
        lines.append("")

    return "\n".join(lines)


def build_report() -> str:
    src_paths = sorted(p for d in SRC_DIRS for p in d.rglob("*.py"))
    test_paths = sorted(TESTS_DIR.rglob("*.py"))
    status = build_status_section(src_paths, test_paths)
    cases = build_test_case_section(test_paths)
    return status + "\n\n" + cases


def main() -> None:
    parser = argparse.ArgumentParser(description="テスト実装状況管理表を生成する。")
    parser.add_argument(
        "-o",
        "--output",
        metavar="ファイル",
        help="出力先ファイルパス（省略時は標準出力）",
    )
    args = parser.parse_args()

    report = build_report()

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(report + "\n", encoding="utf-8")
        print(f"出力しました: {out_path}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
