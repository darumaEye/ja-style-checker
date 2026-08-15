# 1. テスト実装状況

- **実装済み: 40 / 40 (100%)**

- 表の ⚠️ 未実装 行を優先して対応してください。

## __init__.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | run_all_checks | public | 5件 | ✅ |

## buntai.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | check_jotai_keitai_kongou | public | 4件 | ✅ |
| (module) | check_surubeki | public | 3件 | ✅ |
| (module) | check_sentence_length | public | 5件 | ✅ |
| (module) | run | public | 1件 | ✅ |

## common.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | add | public | 9件 | ✅ |
| (module) | check_dictionary | public | 6件 | ✅ |
| (module) | check_pattern_dict | public | 5件 | ✅ |

## gairaigo.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | run | public | 3件 | ✅ |

## kanji_kana.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | _load_joyo_kanji | private | 2件 | ✅ |
| (module) | check_hyougai_kanji_char_level | public | 4件 | ✅ |
| (module) | run | public | 2件 | ✅ |

## kigou.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | check_touten_kongou | public | 4件 | ✅ |
| (module) | check_kuten_piriodo | public | 3件 | ✅ |
| (module) | check_gikaku_fugou_zenhan | public | 4件 | ✅ |
| (module) | run | public | 1件 | ✅ |

## kousei.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | run | public | 2件 | ✅ |

## make_generated_md.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | is_table_row | public | 3件 | ✅ |
| (module) | is_separator_row | public | 2件 | ✅ |
| (module) | split_cells | public | 1件 | ✅ |
| (module) | build_judgment_view | public | 3件 | ✅ |
| (module) | filter_block | public | 6件 | ✅ |
| (module) | main | public | 2件 | ✅ |

## mechanical_check.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | main | public | 4件 | ✅ |

## okurigana.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | run | public | 2件 | ✅ |

## report_test_status.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | parse_functions | public | 6件 | ✅ |
| (module) | extract_doc_lines | public | 4件 | ✅ |
| (module) | collect_test_cases | public | 4件 | ✅ |
| (module) | collect_test_counts | public | 1件 | ✅ |
| (module) | build_status_section | public | 3件 | ✅ |
| (module) | build_test_case_section | public | 1件 | ✅ |
| (module) | build_report | public | 1件 | ✅ |
| (module) | main | public | 2件 | ✅ |

## suuji.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | check_zenkaku_hankaku_suuji | public | 3件 | ✅ |
| (module) | check_comma_kugiri | public | 5件 | ✅ |
| (module) | run | public | 1件 | ✅ |

## yougo.py

| クラス | 関数 | 可視性 | テスト件数 | 状況 |
|---|---|---|---|---|
| (module) | check_oyobi_narabini | public | 4件 | ✅ |
| (module) | check_moshikuha_matawa | public | 3件 | ✅ |
| (module) | check_toori | public | 3件 | ✅ |
| (module) | run | public | 1件 | ✅ |


# 2. テストケース一覧

- 種別が正常のみ、または異常のみの関数がないか確認してください。

- ケース番号が連続しているか確認してください（番号の飛びは削除済みケースまたは記載漏れの可能性があります）。

- 一覧に記載されたケースに対応するテスト関数（def test_*）が実際に存在するか確認してください。

## test_buntai.py — buntai::check_jotai_keitai_kongou

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | です・ます体とである・だ体が両方存在する場合、1件のfindingが追加される |
| 2 | 正常 | です・ます体のみの場合、findingsに追加されない |
| 3 | 正常 | である・だ体のみの場合、findingsに追加されない |
| 4 | 正常 | どちらも存在しない場合、findingsに追加されない |

## test_buntai.py — buntai::check_surubeki

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「（漢字/ひらがな）するべき」が1箇所ある場合、1件のfindingが追加される |
| 2 | 正常 | 複数箇所ある場合、マッチ数だけfindingsに追加される |
| 3 | 正常 | 該当パターンがない場合、findingsに追加されない |

## test_buntai.py — buntai::check_sentence_length

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | limit以下の文のみの場合、findingsに追加されない |
| 2 | 正常 | limitを超える文がある場合、1件のfindingが追加される |
| 3 | 正常 | excerptが40字を超える場合、40字+「…」に切り詰められる |
| 4 | 正常 | limit引数を指定した場合、その値が閾値として使われる |
| 5 | 正常 | 空白文字は文字数カウントから除外される |

## test_buntai.py — buntai::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる |

## test_common.py — common::add

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | findingsが空のとき、指定した内容の辞書が1件追加される |
| 2 | 正常 | 既存のfindingsがある場合、末尾に追加され既存要素は変化しない |
| 3 | 正常 | excerptの前後の空白（半角・全角スペース、タブ、改行）が除去され、 空白のみの場合は空文字列になる |
| 4 | 正常 | rule_id・suggestion・sourceは前後の空白を除去せずそのまま追加される |
| 5 | 正常 | category・levelに渡したEnumメンバーのvalue（文字列）が格納される |
| 6 | 異常 | category・levelにEnumでない値を渡すと、AttributeErrorが送出される |
| 7 | 正常 | 戻り値はNoneである |
| 8 | 正常 | 呼び出し前後で同一のfindingsオブジェクト（id）が変更される |
| 9 | 正常 | 複数回呼び出すと、呼び出し順にfindingsへ追加される |

## test_common.py — common::check_dictionary

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 辞書内の語がtextに1つ含まれる場合、対応する内容のfindingが1件追加される |
| 2 | 正常 | 辞書のvalueがNoneのエントリは検出されない |
| 3 | 正常 | 同じ語が複数回出現する場合、出現数だけfindingsに追加される |
| 4 | 正常 | textに辞書のどの語も含まれない場合、findingsに追加されない |
| 5 | 正常 | exclude_if_followed_byを指定し、直後の文字が集合に含まれる場合は除外される |
| 6 | 正常 | exclude_if_followed_byを指定していても、直後の文字が集合に含まれなければ検出される |

## test_common.py — common::check_pattern_dict

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | パターンにマッチする文字列がある場合、1件のfindingが追加される |
| 2 | 正常 | 複数箇所にマッチする場合、マッチ数だけ追加される |
| 3 | 正常 | マッチしない場合、findingsに追加されない |
| 4 | 正常 | suggestionにパターン置換後の文字列が含まれる |
| 5 | 正常 | 複数のパターンを渡した場合、それぞれのパターンで検出される |

## test_gairaigo.py — gairaigo::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 外来語長音辞書の語（末尾に長音がない）を含む場合、findingが追加される |
| 2 | 正常 | 語の直後に長音「ー」が続く場合（正しい表記）、findingsに追加されない |
| 3 | 正常 | 該当語がない場合、findingsに追加されない |

## test_init.py — checks::run_all_checks

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 各カテゴリの検出条件を満たすtextを渡すと、複数カテゴリの検出結果が findingsに含まれる |
| 2 | 正常 | 検出対象がない場合、空リストが返る |
| 3 | 正常 | 戻り値が辞書のリストであり、各要素が期待するキーを持つ |
| 4 | 正常 | 呼び出しごとに独立したリストが返る（前回呼び出しの結果を引き継がない） |
| 5 | 正常 | 空文字列を渡しても例外は発生せず、空リストが返る |

## test_kanji_kana.py — kanji_kana::_load_joyo_kanji

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 戻り値がfrozensetであり、既知の常用漢字（「愛」等）が含まれる |
| 2 | 正常 | 件数が常用漢字表の字数（2,136字）と一致する |

## test_kanji_kana.py — kanji_kana::check_hyougai_kanji_char_level

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 常用漢字表にない漢字が含まれる場合、findingが追加される（レベル参考） |
| 2 | 正常 | 常用漢字のみの場合、findingsに追加されない |
| 3 | 正常 | 「々」は検出対象外 |
| 4 | 正常 | 同じ表外漢字が複数回出現する場合、出現ごとに個別のfindingが追加される（rule_idは同じになる） |

## test_kanji_kana.py — kanji_kana::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 表外漢字・GAIJI_DICT・KANA_KAKI_DICT・HOJO_DOUSHI_PATTERNSそれぞれの検出条件を 満たすtextを渡すと、対応するrule_idがすべてfindingsに含まれる |
| 2 | 正常 | GAIJI_DICTの語に含まれる表外文字は、check_hyougai_kanji_char_levelでも 文字単位で重複して検出される（仕様上の既知の重複。Claude側でまとめる想定） |

## test_kigou.py — kigou::check_touten_kongou

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「、」と「，」が両方存在する場合、「，」の出現数だけfindingが追加される |
| 2 | 正常 | 「、」のみの場合、findingsに追加されない |
| 3 | 正常 | 「，」のみの場合、findingsに追加されない |
| 4 | 正常 | どちらもない場合、findingsに追加されない |

## test_kigou.py — kigou::check_kuten_piriodo

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「．」があり前後が数字でない場合、findingが追加される |
| 2 | 正常 | 小数点（前後が数字）の場合、findingsに追加されない |
| 3 | 正常 | 「．」がない場合、findingsに追加されない |

## test_kigou.py — kigou::check_gikaku_fugou_zenhan

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「？」の直後に文字が続く場合、findingが追加される |
| 2 | 正常 | 「！」の直後に文字が続く場合、findingが追加される |
| 3 | 正常 | 「？」の直後が全角スペースの場合、findingsに追加されない |
| 4 | 正常 | 「？」が文末（直後に何もない）の場合、findingsに追加されない |

## test_kigou.py — kigou::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 3つのチェック関数すべてが呼び出され、対応するrule_idがfindingsに含まれる |

## test_kousei.py — kousei::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない |
| 2 | 正常 | 戻り値はNoneである |

## test_okurigana.py — okurigana::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 未実装（何もしない）ため、どのようなtextを渡してもfindingsに何も追加されない |
| 2 | 正常 | 戻り値はNoneである |

## test_suuji.py — suuji::check_zenkaku_hankaku_suuji

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 全角数字と半角数字が両方存在する場合、1件のfindingが追加される |
| 2 | 正常 | 全角数字のみの場合、findingsに追加されない |
| 3 | 正常 | 半角数字のみの場合、findingsに追加されない |

## test_suuji.py — suuji::check_comma_kugiri

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 4桁以上の数字にコンマがない場合、findingが追加される（3桁区切りのsuggestion付き） |
| 2 | 正常 | 直後が「年」の場合（西暦等）、findingsに追加されない |
| 3 | 正常 | 前後にハイフンがある場合（電話番号等）、findingsに追加されない |
| 4 | 正常 | 既にコンマ区切りがある場合、findingsに追加されない |
| 5 | 正常 | 3桁以下の数字は対象外 |

## test_suuji.py — suuji::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる |

## test_yougo.py — yougo::check_oyobi_narabini

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「並びに」があり「及び」がない文の場合、findingが追加される |
| 2 | 正常 | 「並びに」と「及び」が両方ある場合、findingsに追加されない |
| 3 | 正常 | 「並びに」がない場合、findingsに追加されない |
| 4 | 正常 | 仮名書き「ならびに」でも検出される |

## test_yougo.py — yougo::check_moshikuha_matawa

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「若しくは」があり「又は」がない場合、findingが追加される |
| 2 | 正常 | 「若しくは」と「又は」が両方ある場合、findingsに追加されない |
| 3 | 正常 | 「若しくは」がない場合、findingsに追加されない |

## test_yougo.py — yougo::check_toori

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 「の通り」がある場合、findingが追加される（カテゴリは「漢字・かなの使い方」のまま） |
| 2 | 正常 | 「大通り」は除外される |
| 3 | 正常 | 「の通り」がない場合、findingsに追加されない |

## test_yougo.py — yougo::run

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 検出条件を満たすtextを渡すと対応するrule_idがすべてfindingsに含まれる |

## test_make_generated_md.py — make_generated_md::is_table_row

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 通常のテーブル行は真を返す |
| 2 | 正常 | 区切り行は偽を返す |
| 3 | 正常 | テーブル行でない文字列は偽を返す |

## test_make_generated_md.py — make_generated_md::is_separator_row

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 区切り行（位置指定のコロン付き含む）は真を返す |
| 2 | 正常 | 通常のデータ行は偽を返す |

## test_make_generated_md.py — make_generated_md::split_cells

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 先頭・末尾の「|」を除き、セルごとに分割してstripした文字列のリストを返す |

## test_make_generated_md.py — make_generated_md::filter_block

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 見出しに「凡例」を含む場合、ブロックをそのまま返す |
| 2 | 正常 | 見出しに「今後の拡張予定」を含む場合、ブロックをそのまま返す |
| 3 | 正常 | 表を含まないブロック（説明文のみ）はそのまま返す |
| 4 | 正常 | 種別列を持つ表では、「判断」で始まる行だけが残る |
| 5 | 正常 | 判断行が1件も無い場合はNoneを返す |
| 6 | 正常 | 種別列が無い表は、全データ行がそのまま残る |

## test_make_generated_md.py — make_generated_md::build_judgment_view

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 最初の見出しより前のヘッダー部分はそのまま引き継がれる |
| 2 | 正常 | 判断行が0件のセクションは出力から除外される |
| 3 | 正常 | 複数セクションを含む場合、各セクションが独立してフィルタされる |

## test_make_generated_md.py — make_generated_md::main

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 正本ファイルを渡すと、対応する.generated.mdがclaude/references/に生成される |
| 2 | 異常 | 引数の数が1つでない場合、使い方メッセージを標準エラーに出力し終了コード1で終了する |

## test_mechanical_check.py — mechanical_check::main

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 検出対象を含むファイルを渡すと、findingsのJSON配列が標準出力に出力される |
| 2 | 正常 | 検出対象がない（空文字列の）ファイルを渡すと、空のJSON配列が標準出力に出力される |
| 3 | 異常 | 引数を渡さない場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する |
| 4 | 異常 | 引数を2つ以上渡した場合、使い方メッセージが標準エラーに出力され、終了コード1で終了する |

## test_report_test_status.py — report_test_status::parse_functions

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | モジュール直下の関数は、class_nameがNone・match_keyがモジュール名になる |
| 2 | 正常 | クラス内の関数は、class_nameがクラス名になる |
| 3 | 正常 | 関数内で定義されたローカル関数は対象外 |
| 4 | 正常 | 先頭がアンダースコア1つの関数はvis="private"になる |
| 5 | 正常 | ダンダーメソッドはvis="public"になる |
| 6 | 正常 | __init__.pyの場合、match_keyは親ディレクトリ名になる |

## test_report_test_status.py — report_test_status::extract_doc_lines

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | モジュールdocstringの各行が抽出される |
| 2 | 正常 | 関数docstringの各行も抽出される |
| 3 | 正常 | #コメントの中身も抽出される |
| 4 | 正常 | 複数の文字列リテラル文・コメントが、ファイル中の出現順に並ぶ |

## test_report_test_status.py — report_test_status::collect_test_cases

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 見出し行に続くケース行が正しく抽出される |
| 2 | 正常 | 継続行（次のケース行・見出し行・空行が現れるまで）が同じケースの説明に連結される |
| 3 | 正常 | 同じ(file, class, fn, num)の重複記載は1件にまとめられる |
| 4 | 正常 | 見出しが無い状態のケース行は無視される |

## test_report_test_status.py — report_test_status::collect_test_counts

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | (class_name, fn)ごとのケース件数を正しく集計する |

## test_report_test_status.py — report_test_status::build_status_section

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | テストが存在する関数は状況が✅になり、件数が表示される |
| 2 | 正常 | テストが存在しない関数は状況が⚠️未実装になる |
| 3 | 正常 | 実装済み件数・全体件数・パーセンテージが正しく計算される |

## test_report_test_status.py — report_test_status::build_test_case_section

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | ケースが(file, class, fn)ごとにグループ化され、番号順に並ぶ |

## test_report_test_status.py — report_test_status::build_report

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | テスト実装状況セクションとテストケース一覧セクションを、空行区切りで連結した文字列を返す |

## test_report_test_status.py — report_test_status::main

| # | 種別 | 説明 |
|---|---|---|
| 1 | 正常 | 引数なしで実行すると、標準出力にレポートが出力される |
| 2 | 正常 | -oオプションでファイルパスを指定すると、そのファイルにレポートが書き出される |

