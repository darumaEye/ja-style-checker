"""
# 外来語の表記（要領 Ⅰ-3）

外来語の表記に関する機械判定。

## 未実装

- 「一つの文書内で第1表・第2表の表記を混在させない」（Ⅰ-3ウ）は
  `koyobun_rules.md`上は機械判定可能とされているが、現状は未実装。
"""

from .common import Category, Level, check_dictionary

# 外来語長音（Ⅰ-3エ）※語末以外の誤爆を避けるため簡易的に完全一致語で判定
GAIRAIGO_CHOUON_DICT = {
    "コンピュータ": "コンピューター",
    "サーバ": "サーバー",
    "プリンタ": "プリンター",
    "ブラウザ": "ブラウザー",
    "ユーザ": "ユーザー",
    "フォルダ": "フォルダー",
}


def run(text, findings):
    """このカテゴリの全チェックを実行する。"""
    check_dictionary(
        text,
        findings,
        GAIRAIGO_CHOUON_DICT,
        "gairaigo-chouon",
        Category.GAIRAIGO,
        Level.WARNING,
        "Ⅰ-3エ",
        exclude_if_followed_by={"ー"},
    )
