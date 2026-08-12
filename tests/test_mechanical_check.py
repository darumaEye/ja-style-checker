"""
--- モジュール mechanical_check の単体テスト ---
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent.parent / "claude" / "scripts" / "mechanical_check.py"

"""
-- 関数 main のテスト --
1. 正常: 検出対象を含むファイルを渡すと、findingsのJSON配列が標準出力に出力される
2. 正常: 検出対象がない（空文字列の）ファイルを渡すと、空のJSON配列が標準出力に出力される
3. 異常: 引数を渡さない場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する
4. 異常: 引数を2つ以上渡した場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する
"""


def _run_cli(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        capture_output=True,
        text=True,
    )


def test_mechanical_check_main_outputs_findings_json(tmp_path):
    """1. 正常: 検出対象を含むファイルを渡すと、findingsのJSON配列が標準出力に出力される"""
    target = tmp_path / "sample.txt"
    target.write_text("１と1が混在する。", encoding="utf-8")

    result = _run_cli([str(target)])

    assert result.returncode == 0
    findings = json.loads(result.stdout)
    assert isinstance(findings, list)
    assert len(findings) >= 1
    assert findings[0]["rule_id"] == "number-width-mix"


def test_mechanical_check_main_empty_file_outputs_empty_array(tmp_path):
    """2. 正常: 検出対象がない（空文字列の）ファイルを渡すと、空のJSON配列が標準出力に出力される"""
    target = tmp_path / "empty.txt"
    target.write_text("", encoding="utf-8")

    result = _run_cli([str(target)])

    assert result.returncode == 0
    assert json.loads(result.stdout) == []


def test_mechanical_check_main_no_args_exits_with_usage_error():
    """3. 異常: 引数を渡さない場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する"""
    result = _run_cli([])

    assert result.returncode == 1
    assert "使い方" in result.stderr


def test_mechanical_check_main_too_many_args_exits_with_usage_error(tmp_path):
    """4. 異常: 引数を2つ以上渡した場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する"""
    target = tmp_path / "sample.txt"
    target.write_text("テスト", encoding="utf-8")

    result = _run_cli([str(target), "extra"])

    assert result.returncode == 1
    assert "使い方" in result.stderr
