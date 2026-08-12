#!/usr/bin/env python3
"""
ルールファイル（正本・人間向け）から、Claudeが読むべき行だけを自動抽出し、
軽量な「<元ファイル名>.generated.md」を `claude/references/` に生成する。

出力ファイル名は固定の命名規則に従う（呼び出し側が名前を決めない）。
    koyobun_rules.md → koyobun_rules.generated.md
    company_rules.md → company_rules.generated.md

生成物は自動生成物であり、手動編集しない。編集はすべて正本（例：
koyobun_rules.md）に対して行い、本スクリプトを再実行して更新する。

抽出方針:
- 種別が「判断」で始まる行のみを残す（「機械」「機械（辞書）」
  「機械（文字数）」は、スクリプトが既に実装済みのため、Claudeが
  読む必要がない）
- 見出し（## カテゴリ名）は、判断行が1件でも残るカテゴリのみ残す
- 種別列を持たない表・セクション（凡例、厳格モード表、説明文のみの
  セクション等）はそのまま引き継ぐ
- 種別列自体が存在しないルールファイル（例：company_rules.mdが
  まだ表形式になっていない場合）は、全文をそのまま引き継ぐ

使い方:
    python3 make_generated_md.py <正本のmdファイルパス>
"""

import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DST_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "claude", "references")

TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
SEPARATOR_ROW_RE = re.compile(r"^\|[\s\-:|]+\|\s*$")


def is_table_row(line):
    """行がMarkdown表のデータ行・ヘッダー行か判定する（区切り行は除く）。"""
    return bool(TABLE_ROW_RE.match(line)) and not SEPARATOR_ROW_RE.match(line)


def is_separator_row(line):
    """行がMarkdown表の区切り行（|---|---|等）か判定する。"""
    return bool(SEPARATOR_ROW_RE.match(line))


def split_cells(line):
    """Markdown表の1行を、先頭・末尾の"|"を除いてセルのリストに分割する。"""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [c.strip() for c in inner.split("|")]


def build_judgment_view(source_text):
    """正本のMarkdown全文から、判断行のみを残した抽出版の全文を生成する。"""
    lines = source_text.split("\n")
    out_lines = []
    i = 0
    n = len(lines)

    # ヘッダー部分（# タイトル 〜 最初の "## " 見出し手前）はそのまま引き継ぐ
    while i < n and not lines[i].startswith("## "):
        out_lines.append(lines[i])
        i += 1

    while i < n:
        if lines[i].startswith("## "):
            heading_line = lines[i]
            block = [lines[i]]
            i += 1
            # 見出し直後、次の "## " までを1ブロックとして収集
            while i < n and not lines[i].startswith("## "):
                block.append(lines[i])
                i += 1

            filtered_block = filter_block(block, heading_line)
            if filtered_block is not None:
                out_lines.extend(filtered_block)
        else:
            out_lines.append(lines[i])
            i += 1

    return "\n".join(out_lines)


def filter_block(block, heading_line):
    """1つの '## ...' セクション（表を含む）を判断行のみにフィルタする。
    判断行が1件も無ければセクションごと落とす（凡例・厳格モード表など
    ルール表以外のセクションは常に残す）。
    """
    header = heading_line.strip()

    # 凡例・拡張予定など、ルール表以外のセクションはそのまま残す
    if "凡例" in header or "今後の拡張予定" in header:
        return block

    kept_lines = []
    table_lines = [l for l in block if is_table_row(l)]

    if not table_lines:
        # 表が無いセクション（説明文のみ等）はそのまま残す
        return block

    header_row = None
    separator_row = None
    data_rows = []
    for l in block:
        if is_separator_row(l):
            separator_row = l
            continue
        if is_table_row(l):
            if header_row is None:
                header_row = l
            else:
                data_rows.append(l)

    if header_row is None:
        return block

    header_cells = split_cells(header_row)
    try:
        type_col_index = header_cells.index("種別")
    except ValueError:
        type_col_index = None

    kept_data_rows = []
    for row in data_rows:
        cells = split_cells(row)
        if type_col_index is not None and type_col_index < len(cells):
            cell_value = cells[type_col_index]
            if cell_value.startswith("判断"):
                kept_data_rows.append(row)
        else:
            # 種別列が無い表（例：厳格モード表）は、
            # ルール名に「及び」「並びに」「若しくは」等の判断系語がなくても
            # そのまま残す（厳格モード表は判断行を含むため個別に扱う）
            kept_data_rows.append(row)

    if not kept_data_rows:
        return None  # このカテゴリは判断行が無いので丸ごと省く

    non_table_lines_before_table = []
    for l in block:
        if is_table_row(l):
            break
        non_table_lines_before_table.append(l)

    kept_lines.extend(non_table_lines_before_table)
    kept_lines.append(header_row)
    if separator_row:
        kept_lines.append(separator_row)
    kept_lines.extend(kept_data_rows)
    kept_lines.append("")

    return kept_lines


def main():
    """コマンドライン引数で指定された正本ファイルから抽出版を生成し、
    <正本のstem>.generated.md として `claude/references/` に書き出す。"""
    if len(sys.argv) != 2:
        print(
            "使い方: python3 make_generated_md.py <正本のmdファイルパス>",
            file=sys.stderr,
        )
        sys.exit(1)

    src_path = sys.argv[1]
    src_stem = os.path.splitext(os.path.basename(src_path))[0]
    dst_path = os.path.join(DST_DIR, f"{src_stem}.generated.md")

    with open(src_path, "r", encoding="utf-8") as f:
        source_text = f.read()

    view = build_judgment_view(source_text)

    src_name = os.path.basename(src_path)
    script_name = os.path.basename(__file__)
    notice = (
        "<!--\n"
        "  このファイルは自動生成物です。手動編集しないでください。\n"
        f"  正本は {src_name} です。編集はそちらに対して行い、\n"
        f"  scripts/{script_name} を再実行してください（package.shが自動で行います）。\n"
        "  抽出条件：種別が「判断」で始まる行のみを収録（機械判定層は\n"
        "  scripts/mechanical_check.py が実装済みのため、Claudeが読む\n"
        "  必要はありません）。\n"
        "-->\n\n"
    )

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(notice + view)

    print(f"生成しました: {dst_path}")


if __name__ == "__main__":
    main()
