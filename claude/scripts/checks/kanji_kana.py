"""
# 漢字・かなの使い方（要領 Ⅰ-1）

漢字・かなの使い方に関する機械判定。
"""

import re
from pathlib import Path

from .common import Category, Level, add, check_dictionary, check_pattern_dict

_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_joyo_kanji() -> frozenset[str]:
    """常用漢字表（平成22年内閣告示第2号）の本表2,136字をtxtファイルから読み込む。

    出典：文化庁「常用漢字表」告示別表（法令・告示のため著作権の対象外）。
    許容字体5字（餌・遡・遜・謎・餅の異体字）は本表の通用字体のみ収録。
    データ本体は`data/joyo_kanji.txt`（1行1字）。
    """
    path = _DATA_DIR / "joyo_kanji.txt"
    with open(path, "r", encoding="utf-8") as f:
        return frozenset(line.strip() for line in f if line.strip())


JOYO_KANJI = _load_joyo_kanji()


# 常用漢字表外・表外音訓の言い換え例（Ⅰ-1(2)）
GAIJI_DICT: dict[str, str] = {
    "憂鬱": "憂うつ",
    "改竄": "改ざん",
    "颯爽": "さっそう",
    "杜撰": "ずさん",
    "毀損": "き損",
    "漏洩": "漏えい",
    "破綻": "破たん",
    "蔓延": "まん延",
    "斡旋": "あっせん",
    "石鹸": "せっけん",
    "拘泥": "こだわる",
    "捏造": "ねつ造",
    "毀誉褒貶": "評価",
    "活かす": "生かす",
}

# 接続詞・補助語のかな書き（Ⅰ-1(3)）
KANA_KAKI_DICT: dict[str, str | None] = {
    "従って": "したがって",
    "但し": "ただし",
    "但書": "ただし書",
    "即ち": "すなわち",
    "尚": "なお",
    "又": "また",
    "或いは": "あるいは",
    "並びに": None,  # 及びとの対応チェックで別途処理（yougo.py）
}

# 補助動詞のかな書き（Ⅰ-1(3)）
HOJO_DOUSHI_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"て下さい"), "てください"),
    (re.compile(r"て頂[くきけ]"), "ていただく（活用に応じて）"),
    (re.compile(r"て行く"), "ていく"),
    (re.compile(r"て来る"), "てくる"),
    (re.compile(r"て見る"), "てみる"),
    (re.compile(r"て欲しい"), "てほしい"),
    (re.compile(r"て良い"), "てよい"),
]


def check_hyougai_kanji_char_level(text: str, findings: list[dict[str, str]]) -> None:
    """常用漢字表にない漢字（表外漢字）を、辞書に頼らず文字単位で網羅的に検出する（Ⅰ-1(2)）。

    `GAIJI_DICT` は「知っている語だけ」しか拾えないが、この関数は常用漢字表
    2,136字との照合なので、辞書に載っていない表外漢字も含めて検出できる。
    ただし以下の限界がある。
    - 固有名詞（人名・地名）は常用漢字表の適用対象外（Ⅰ-1ウ）だが、
      本関数はそれを判別できないため、レベルは「参考」に留める。
    - 表内の漢字でも、採用されていない音訓（表外音訓）による誤用は検出できない
      （読み方の判定が必要なため、形態素解析なしでは対応できない。今後の課題）。
    - `GAIJI_DICT` で既に個別の指摘が出ている語は、重複指摘になる場合がある
      （ `SKILL.md` の手順どおり、Claude側で重複をまとめる）。
    """
    # NOTE: [\u4e00-\u9fff] はCJK統合漢字ブロックを表す。
    kanji_pattern = re.compile(r"[\u4e00-\u9fff々]")
    seen_at = set()
    for m in kanji_pattern.finditer(text):
        ch = m.group(0)
        if ch == "々":
            continue  # 踊り字は別ルール（Ⅰ-6イ、kigou.py）で扱う
        if ch in JOYO_KANJI:
            continue
        pos = m.start()
        if pos in seen_at:
            continue
        seen_at.add(pos)
        ctx = text[max(0, pos - 10) : pos + 10]
        add(
            findings,
            f"hyougai-kanji-char-{ch}",
            Category.KANJI_KANA,
            Level.INFO,
            ctx,
            f"「{ch}」は常用漢字表にない漢字です。固有名詞でなければ、仮名書きか言い換えを検討してください。",
            "Ⅰ-1(2)",
        )


def run(text: str, findings: list[dict[str, str]]) -> None:
    """このカテゴリの全チェックを実行する。"""
    check_hyougai_kanji_char_level(text, findings)
    check_dictionary(
        text, findings, GAIJI_DICT, "gaiji", Category.KANJI_KANA, Level.ERROR, "Ⅰ-1(2)"
    )
    check_dictionary(
        text,
        findings,
        KANA_KAKI_DICT,
        "kanakaki",
        Category.KANJI_KANA,
        Level.WARNING,
        "Ⅰ-1(3)",
    )
    check_pattern_dict(
        text,
        findings,
        HOJO_DOUSHI_PATTERNS,
        "hojo-doushi",
        Category.KANJI_KANA,
        Level.ERROR,
        "Ⅰ-1(3)",
    )
