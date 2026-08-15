"""
--- モジュール report_test_status の単体テスト ---
"""

import subprocess
import sys
from pathlib import Path

from report_test_status import (
    build_report,
    build_status_section,
    build_test_case_section,
    collect_test_cases,
    collect_test_counts,
    extract_doc_lines,
    parse_functions,
)

SCRIPT_PATH = Path(__file__).parent.parent / "scripts" / "report_test_status.py"

"""
-- 関数 parse_functions のテスト --
1. 正常: モジュール直下の関数は、class_nameがNone・match_keyがモジュール名になる
2. 正常: クラス内の関数は、class_nameがクラス名になる
3. 正常: 関数内で定義されたローカル関数は対象外
4. 正常: 先頭がアンダースコア1つの関数はvis="private"になる
5. 正常: ダンダーメソッドはvis="public"になる
6. 正常: __init__.pyの場合、match_keyは親ディレクトリ名になる
"""


def test_report_test_status_parse_functions_module_level_function(tmp_path):
    """1. 正常: モジュール直下の関数は、class_nameがNone・match_keyがモジュール名になる"""
    f = tmp_path / "sample_module.py"
    f.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = parse_functions(f)

    assert len(result) == 1
    assert result[0]["fn"] == "foo"
    assert result[0]["class_name"] is None
    assert result[0]["match_key"] == "sample_module"


def test_report_test_status_parse_functions_method_in_class(tmp_path):
    """2. 正常: クラス内の関数は、class_nameがクラス名になる"""
    f = tmp_path / "sample_module.py"
    f.write_text("class Foo:\n    def bar(self):\n        pass\n", encoding="utf-8")

    result = parse_functions(f)

    assert len(result) == 1
    assert result[0]["fn"] == "bar"
    assert result[0]["class_name"] == "Foo"
    assert result[0]["match_key"] == "Foo"


def test_report_test_status_parse_functions_ignores_local_functions(tmp_path):
    """3. 正常: 関数内で定義されたローカル関数は対象外"""
    f = tmp_path / "sample_module.py"
    f.write_text(
        "def outer():\n    def inner():\n        pass\n    return inner\n",
        encoding="utf-8",
    )

    result = parse_functions(f)

    assert [fn["fn"] for fn in result] == ["outer"]


def test_report_test_status_parse_functions_single_underscore_is_private(tmp_path):
    """4. 正常: 先頭がアンダースコア1つの関数はvis="private"になる"""
    f = tmp_path / "sample_module.py"
    f.write_text("def _helper():\n    pass\n", encoding="utf-8")

    result = parse_functions(f)

    assert result[0]["vis"] == "private"


def test_report_test_status_parse_functions_dunder_method_is_public(tmp_path):
    """5. 正常: ダンダーメソッドはvis="public"になる"""
    f = tmp_path / "sample_module.py"
    f.write_text(
        "class Foo:\n    def __init__(self):\n        pass\n", encoding="utf-8"
    )

    result = parse_functions(f)

    assert result[0]["vis"] == "public"


def test_report_test_status_parse_functions_init_py_uses_parent_dir_as_match_key(
    tmp_path,
):
    """6. 正常: __init__.pyの場合、match_keyは親ディレクトリ名になる"""
    pkg_dir = tmp_path / "mypackage"
    pkg_dir.mkdir()
    f = pkg_dir / "__init__.py"
    f.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = parse_functions(f)

    assert result[0]["match_key"] == "mypackage"


"""
-- 関数 extract_doc_lines のテスト --
1. 正常: モジュールdocstringの各行が抽出される
2. 正常: 関数docstringの各行も抽出される
3. 正常: #コメントの中身も抽出される
4. 正常: 複数の文字列リテラル文・コメントが、ファイル中の出現順に並ぶ
"""


def test_report_test_status_extract_doc_lines_module_docstring(tmp_path):
    """1. 正常: モジュールdocstringの各行が抽出される"""
    f = tmp_path / "sample_module.py"
    f.write_text('"""line1\nline2"""\n', encoding="utf-8")

    result = extract_doc_lines(f)

    assert result == ["line1", "line2"]


def test_report_test_status_extract_doc_lines_function_docstring(tmp_path):
    """2. 正常: 関数docstringの各行も抽出される"""
    f = tmp_path / "sample_module.py"
    f.write_text('def foo():\n    """関数の説明"""\n    pass\n', encoding="utf-8")

    result = extract_doc_lines(f)

    assert "関数の説明" in result


def test_report_test_status_extract_doc_lines_comment_content(tmp_path):
    """3. 正常: #コメントの中身も抽出される"""
    f = tmp_path / "sample_module.py"
    f.write_text("x = 1  # これはコメント\n", encoding="utf-8")

    result = extract_doc_lines(f)

    assert "これはコメント" in result


def test_report_test_status_extract_doc_lines_ordered_by_appearance(tmp_path):
    """4. 正常: 複数の文字列リテラル文・コメントが、ファイル中の出現順に並ぶ"""
    f = tmp_path / "sample_module.py"
    f.write_text(
        '"""先頭のdocstring"""\n' "# 次のコメント\n" '"""\n浮いた文字列リテラル\n"""\n',
        encoding="utf-8",
    )

    result = extract_doc_lines(f)

    assert result.index("先頭のdocstring") < result.index("次のコメント")
    assert result.index("次のコメント") < result.index("浮いた文字列リテラル")


"""
-- 関数 collect_test_cases のテスト --
1. 正常: 見出し行に続くケース行が正しく抽出される
2. 正常: 継続行（次のケース行・見出し行・空行が現れるまで）が同じケースの説明に連結される
3. 正常: 同じ(file, class, fn, num)の重複記載は1件にまとめられる
4. 正常: 見出しが無い状態のケース行は無視される
"""


def test_report_test_status_collect_test_cases_extracts_basic_case(tmp_path):
    """1. 正常: 見出し行に続くケース行が正しく抽出される"""
    f = tmp_path / "test_sample.py"
    f.write_text(
        '"""\n'
        "--- モジュール sample の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 何かが起きる\n"
        '"""\n',
        encoding="utf-8",
    )

    result = collect_test_cases([f])

    assert len(result) == 1
    assert result[0]["class_name"] == "sample"
    assert result[0]["fn"] == "foo"
    assert result[0]["num"] == 1
    assert result[0]["type"] == "正常"
    assert result[0]["desc"] == "何かが起きる"


def test_report_test_status_collect_test_cases_joins_continuation_lines(tmp_path):
    """2. 正常: 継続行（次のケース行・見出し行・空行が現れるまで）が同じケースの説明に連結される"""
    f = tmp_path / "test_sample.py"
    f.write_text(
        '"""\n'
        "--- モジュール sample の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 長い説明が\n"
        "   複数行にまたがる場合\n"
        '"""\n',
        encoding="utf-8",
    )

    result = collect_test_cases([f])

    assert result[0]["desc"] == "長い説明が 複数行にまたがる場合"


def test_report_test_status_collect_test_cases_deduplicates_same_case(tmp_path):
    """3. 正常: 同じ(file, class, fn, num)の重複記載は1件にまとめられる"""
    f = tmp_path / "test_sample.py"
    f.write_text(
        '"""\n'
        "--- モジュール sample の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 最初の記載\n"
        '"""\n\n'
        "def test_foo_case1():\n"
        '    """1. 正常: 最初の記載"""\n'
        "    pass\n",
        encoding="utf-8",
    )

    result = collect_test_cases([f])

    assert len(result) == 1


def test_report_test_status_collect_test_cases_ignores_case_without_header(tmp_path):
    """4. 正常: 見出しが無い状態のケース行は無視される"""
    f = tmp_path / "test_sample.py"
    f.write_text('"""\n1. 正常: 見出しの前にあるケース\n"""\n', encoding="utf-8")

    result = collect_test_cases([f])

    assert result == []


"""
-- 関数 collect_test_counts のテスト --
1. 正常: (class_name, fn)ごとのケース件数を正しく集計する
"""


def test_report_test_status_collect_test_counts_counts_per_function(tmp_path):
    """1. 正常: (class_name, fn)ごとのケース件数を正しく集計する"""
    f = tmp_path / "test_sample.py"
    f.write_text(
        '"""\n'
        "--- モジュール sample の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 1件目\n"
        "2. 正常: 2件目\n"
        '"""\n',
        encoding="utf-8",
    )

    result = collect_test_counts([f])

    assert result[("sample", "foo")] == 2


"""
-- 関数 build_status_section のテスト --
1. 正常: テストが存在する関数は状況が✅になり、件数が表示される
2. 正常: テストが存在しない関数は状況が⚠️未実装になる
3. 正常: 実装済み件数・全体件数・パーセンテージが正しく計算される
"""


def test_report_test_status_build_status_section_marks_tested_function(tmp_path):
    """1. 正常: テストが存在する関数は状況が✅になり、件数が表示される"""
    src = tmp_path / "sample_module.py"
    src.write_text("def foo():\n    pass\n", encoding="utf-8")
    test_f = tmp_path / "test_sample_module.py"
    test_f.write_text(
        '"""\n'
        "--- モジュール sample_module の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 何か\n"
        '"""\n',
        encoding="utf-8",
    )

    result = build_status_section([src], [test_f])

    assert "| (module) | foo | public | 1件 | ✅ |" in result


def test_report_test_status_build_status_section_marks_untested_function(tmp_path):
    """2. 正常: テストが存在しない関数は状況が⚠️未実装になる"""
    src = tmp_path / "sample_module.py"
    src.write_text("def foo():\n    pass\n", encoding="utf-8")

    result = build_status_section([src], [])

    assert "⚠️ 未実装" in result


def test_report_test_status_build_status_section_computes_percentage(tmp_path):
    """3. 正常: 実装済み件数・全体件数・パーセンテージが正しく計算される"""
    src = tmp_path / "sample_module.py"
    src.write_text("def foo():\n    pass\n\n\ndef bar():\n    pass\n", encoding="utf-8")
    test_f = tmp_path / "test_sample_module.py"
    test_f.write_text(
        '"""\n'
        "--- モジュール sample_module の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "1. 正常: 何か\n"
        '"""\n',
        encoding="utf-8",
    )

    result = build_status_section([src], [test_f])

    assert "実装済み: 1 / 2 (50%)" in result


"""
-- 関数 build_test_case_section のテスト --
1. 正常: ケースが(file, class, fn)ごとにグループ化され、番号順に並ぶ
"""


def test_report_test_status_build_test_case_section_groups_and_orders_cases(tmp_path):
    """1. 正常: ケースが(file, class, fn)ごとにグループ化され、番号順に並ぶ"""
    f = tmp_path / "test_sample.py"
    f.write_text(
        '"""\n'
        "--- モジュール sample の単体テスト ---\n\n"
        "-- 関数 foo のテスト --\n"
        "2. 正常: 2番目\n"
        "1. 正常: 1番目\n"
        '"""\n',
        encoding="utf-8",
    )

    result = build_test_case_section([f])

    assert result.index("1番目") < result.index("2番目")


"""
-- 関数 build_report のテスト --
1. 正常: テスト実装状況セクションとテストケース一覧セクションを、空行区切りで連結した文字列を返す
"""


def test_report_test_status_build_report_concatenates_both_sections():
    """1. 正常: テスト実装状況セクションとテストケース一覧セクションを、空行区切りで連結した文字列を返す"""
    result = build_report()

    assert result.startswith("# 1. テスト実装状況")
    assert "\n\n# 2. テストケース一覧" in result


"""
-- 関数 main のテスト --
1. 正常: 引数なしで実行すると、標準出力にレポートが出力される
2. 正常: -oオプションでファイルパスを指定すると、そのファイルにレポートが書き出される
"""


def _run_cli(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_report_test_status_main_prints_report_to_stdout():
    """1. 正常: 引数なしで実行すると、標準出力にレポートが出力される"""
    result = _run_cli([])

    assert result.returncode == 0
    assert "# 1. テスト実装状況" in result.stdout


def test_report_test_status_main_writes_report_to_file(tmp_path):
    """2. 正常: -oオプションでファイルパスを指定すると、そのファイルにレポートが書き出される"""
    out_path = tmp_path / "status.md"

    result = _run_cli(["-o", str(out_path)])

    assert result.returncode == 0
    assert out_path.exists()
    assert "# 1. テスト実装状況" in out_path.read_text(encoding="utf-8")
