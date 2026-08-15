"""
--- モジュール make_generated_md の単体テスト ---
"""

import subprocess
import sys
from pathlib import Path

from make_generated_md import (
    build_judgment_view,
    filter_block,
    is_separator_row,
    is_table_row,
    split_cells,
)

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "make_generated_md.py"
DST_DIR = Path(__file__).parent.parent / "claude" / "references"

"""
-- 関数 is_table_row のテスト --
1. 正常: 通常のテーブル行は真を返す
2. 正常: 区切り行は偽を返す
3. 正常: テーブル行でない文字列は偽を返す
"""


def test_make_generated_md_is_table_row_detects_data_row():
    """1. 正常: 通常のテーブル行は真を返す"""
    assert is_table_row("| ルール | 種別 | レベル |") is True


def test_make_generated_md_is_table_row_rejects_separator_row():
    """2. 正常: 区切り行は偽を返す"""
    assert is_table_row("|---|---|---|") is False


def test_make_generated_md_is_table_row_rejects_non_table_line():
    """3. 正常: テーブル行でない文字列は偽を返す"""
    assert is_table_row("これは表ではない行です。") is False


"""
-- 関数 is_separator_row のテスト --
1. 正常: 区切り行（位置指定のコロン付き含む）は真を返す
2. 正常: 通常のデータ行は偽を返す
"""


def test_make_generated_md_is_separator_row_detects_separator():
    """1. 正常: 区切り行（位置指定のコロン付き含む）は真を返す"""
    assert is_separator_row("|---|:---:|---:|") is True


def test_make_generated_md_is_separator_row_rejects_data_row():
    """2. 正常: 通常のデータ行は偽を返す"""
    assert is_separator_row("| ルール | 種別 |") is False


"""
-- 関数 split_cells のテスト --
1. 正常: 先頭・末尾の「|」を除き、セルごとに分割してstripした文字列のリストを返す
"""


def test_make_generated_md_split_cells_splits_and_strips():
    """1. 正常: 先頭・末尾の「|」を除き、セルごとに分割してstripした文字列のリストを返す"""
    result = split_cells("|  ルール  | 種別 | レベル |")

    assert result == ["ルール", "種別", "レベル"]


"""
-- 関数 filter_block のテスト --
1. 正常: 見出しに「凡例」を含む場合、ブロックをそのまま返す
2. 正常: 見出しに「今後の拡張予定」を含む場合、ブロックをそのまま返す
3. 正常: 表を含まないブロック（説明文のみ）はそのまま返す
4. 正常: 種別列を持つ表では、「判断」で始まる行だけが残る
5. 正常: 判断行が1件も無い場合はNoneを返す
6. 正常: 種別列が無い表は、全データ行がそのまま残る
"""


def test_make_generated_md_filter_block_keeps_legend_section():
    """1. 正常: 見出しに「凡例」を含む場合、ブロックをそのまま返す"""
    block = ["## 凡例", "", "- 種別の説明"]

    result = filter_block(block, "## 凡例")

    assert result == block


def test_make_generated_md_filter_block_keeps_future_extension_section():
    """2. 正常: 見出しに「今後の拡張予定」を含む場合、ブロックをそのまま返す"""
    block = ["## 今後の拡張予定", "", "- 予定項目"]

    result = filter_block(block, "## 今後の拡張予定")

    assert result == block


def test_make_generated_md_filter_block_keeps_section_without_table():
    """3. 正常: 表を含まないブロック（説明文のみ）はそのまま返す"""
    block = ["## 1. 説明のみのセクション", "", "表を持たない説明文です。"]

    result = filter_block(block, "## 1. 説明のみのセクション")

    assert result == block


def test_make_generated_md_filter_block_keeps_only_judgment_rows():
    """4. 正常: 種別列を持つ表では、「判断」で始まる行だけが残る"""
    block = [
        "## 1. カテゴリ",
        "",
        "| ルール | 種別 | レベル |",
        "|---|---|---|",
        "| 機械的なルール | 機械 | 要修正 |",
        "| 判断が必要なルール | 判断 | 参考 |",
    ]

    result = filter_block(block, "## 1. カテゴリ")

    assert result is not None
    assert not any("機械的なルール" in line for line in result)
    assert any("判断が必要なルール" in line for line in result)


def test_make_generated_md_filter_block_returns_none_when_no_judgment_rows():
    """5. 正常: 判断行が1件も無い場合はNoneを返す"""
    block = [
        "## 1. カテゴリ",
        "",
        "| ルール | 種別 | レベル |",
        "|---|---|---|",
        "| 機械的なルール | 機械 | 要修正 |",
    ]

    result = filter_block(block, "## 1. カテゴリ")

    assert result is None


def test_make_generated_md_filter_block_keeps_all_rows_without_type_column():
    """6. 正常: 種別列が無い表は、全データ行がそのまま残る"""
    block = [
        "## 厳格モード表",
        "",
        "| ルール | 適用 |",
        "|---|---|",
        "| 何らかのルール | 厳格モードのみ |",
    ]

    result = filter_block(block, "## 厳格モード表")

    assert result is not None
    assert any("何らかのルール" in line for line in result)


"""
-- 関数 build_judgment_view のテスト --
1. 正常: 最初の見出しより前のヘッダー部分はそのまま引き継がれる
2. 正常: 判断行が0件のセクションは出力から除外される
3. 正常: 複数セクションを含む場合、各セクションが独立してフィルタされる
"""


def test_make_generated_md_build_judgment_view_keeps_header_before_first_heading():
    """1. 正常: 最初の見出しより前のヘッダー部分はそのまま引き継がれる"""
    source = "# タイトル\n\n出典：どこか\n\n## 1. カテゴリ\n\n説明文のみ。\n"

    result = build_judgment_view(source)

    assert result.startswith("# タイトル\n\n出典：どこか")


def test_make_generated_md_build_judgment_view_drops_section_with_no_judgment_rows():
    """2. 正常: 判断行が0件のセクションは出力から除外される"""
    source = (
        "# タイトル\n\n"
        "## 1. 機械のみのカテゴリ\n\n"
        "| ルール | 種別 |\n|---|---|\n| 機械ルール | 機械 |\n"
    )

    result = build_judgment_view(source)

    assert "1. 機械のみのカテゴリ" not in result


def test_make_generated_md_build_judgment_view_filters_each_section_independently():
    """3. 正常: 複数セクションを含む場合、各セクションが独立してフィルタされる"""
    source = (
        "# タイトル\n\n"
        "## 1. 機械のみ\n\n"
        "| ルール | 種別 |\n|---|---|\n| 機械ルール | 機械 |\n\n"
        "## 2. 判断あり\n\n"
        "| ルール | 種別 |\n|---|---|\n| 判断ルール | 判断 |\n"
    )

    result = build_judgment_view(source)

    assert "1. 機械のみ" not in result
    assert "2. 判断あり" in result
    assert "判断ルール" in result


"""
-- 関数 main のテスト --
1. 正常: 正本ファイルを渡すと、対応する.generated.mdがclaude/references/に生成される
2. 異常: 引数の数が1つでない場合、使い方メッセージを標準エラーに出力し終了コード1で終了する
"""


def _run_cli(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_make_generated_md_main_generates_output_file(tmp_path):
    """1. 正常: 正本ファイルを渡すと、対応する.generated.mdがclaude/references/に生成される"""
    src = tmp_path / "_test_fixture_rules.md"
    src.write_text(
        "# テスト用ルール\n\n"
        "## 1. カテゴリ\n\n"
        "| ルール | 種別 |\n|---|---|\n| 判断ルール | 判断 |\n",
        encoding="utf-8",
    )
    dst = DST_DIR / "_test_fixture_rules.generated.md"

    try:
        result = _run_cli([str(src)])

        assert result.returncode == 0
        assert dst.exists()
        assert "判断ルール" in dst.read_text(encoding="utf-8")
    finally:
        dst.unlink(missing_ok=True)


def test_make_generated_md_main_wrong_arg_count_exits_with_usage_error():
    """2. 異常: 引数の数が1つでない場合、使い方メッセージを標準エラーに出力し終了コード1で終了する"""
    result = _run_cli([])

    assert result.returncode == 1
    assert "使い方" in result.stderr
