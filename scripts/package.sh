#!/usr/bin/env bash
# koetsu スキルのパッケージングスクリプト
#
# 1. テストを実行する（失敗時はここで止まる）
# 2. テスト実装状況表（tests/test_status_report.md）を更新する
# 3. rule-sources/ 配下の各ルールファイル（正本）から、対応する
#    「<元ファイル名>.generated.md」（軽量版）を claude/references/ に再生成する
# 4. 同じ軽量版を gemini/knowledge/ にもコピーする（Gemini Gemの「知識」用。
#    正本は rule-sources/ の1つだけで、claude向け・gemini向けの2箇所に複製する）
# 5. claude/ ディレクトリのみを zip にまとめる（アップロード対象はclaude/だけなので、
#    rule-sources/・gemini/・tests/・.venv/等リポジトリの他の部分は含めない）
#
# ルールファイルを編集したら、アップロードの前に必ずこのスクリプトを再実行すること。
# 「*.generated.md」を手動編集しても、次回実行時に上書きされる。
#
# 新しいルールファイルを追加する場合は、下の RULE_FILES に1行足すだけでよい
# （出力ファイル名は make_generated_md.py が自動で決める）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$REPO_DIR/claude"
GEMINI_KNOWLEDGE_DIR="$REPO_DIR/gemini/knowledge"
ZIP_NAME="$(basename "$REPO_DIR").zip"

RULE_FILES=(
  "$REPO_DIR/rule-sources/koyobun_rules.md"
  "$REPO_DIR/rule-sources/company_rules.md"
)

echo "== 1. テストを実行 =="
(cd "$REPO_DIR" && python3 -m pytest)

echo "== 2. テスト実装状況表を更新 =="
python3 "$SCRIPT_DIR/report_test_status.py" -o "$REPO_DIR/tests/test_status_report.md"

echo "== 3. 各ルールファイルの軽量版（*.generated.md）を生成 =="
for f in "${RULE_FILES[@]}"; do
  python3 "$SCRIPT_DIR/make_generated_md.py" "$f"
done

echo "== 4. gemini/knowledge/ にも軽量版をコピー =="
mkdir -p "$GEMINI_KNOWLEDGE_DIR"
cp "$CLAUDE_DIR"/references/*.generated.md "$GEMINI_KNOWLEDGE_DIR/"

echo "== 5. zip を作成 =="
cd "$REPO_DIR"
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" "$(basename "$CLAUDE_DIR")" \
  -x "*__pycache__*" "*.pyc" "*.DS_Store" \
  > /dev/null
echo "生成しました: $REPO_DIR/$ZIP_NAME"
