"""
分析結果をレポートとして出力するモジュール
"""
import textwrap
from typing import List, Dict, Optional, Tuple

from .config import get_config
from .dictionary import get_dictionary, Dictionary
from .word import Word


def format_table_row(word: Word, translation: Optional[str], pos_translation: str, example: str) -> str:
    """
    表の行をフォーマットする
    
    Args:
        word (Word): 単語オブジェクト
        translation (Optional[str]): 単語の日本語訳
        pos_translation (str): 品詞の日本語訳
        example (str): 例文
    
    Returns:
        str: フォーマットされた表の行
    """
    # 単語の日本語訳がない場合は空文字列を使用
    translation = translation or "未登録"

    # 例文が長い場合は省略
    example_wrapped = textwrap.shorten(example, width=60, placeholder="...")

    return f"| {word.text:<15} | {word.count:<8} | {translation:<20} | {pos_translation:<15} | {example_wrapped:<60} |"


def generate_table_header() -> str:
    """
    表のヘッダーを生成する
    
    Returns:
        str: 表のヘッダー
    """
    header = "| 語句             | 出現回数 | 意味・説明             | 品詞             | 例文                                                         |"
    separator = "|-----------------|----------|------------------------|------------------|--------------------------------------------------------------|"
    return f"{header}\n{separator}"


def generate_report(words: List[Word], option: str) -> List[str]:
    """
    単語リストからレポートの行（ヘッダー除く）を生成する
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
        option (str): オプション（例: "no_translation"）
    
    Returns:
        List[str]: 表の行（ヘッダーは含まない）
    """
    config = get_config()
    dictionary = get_dictionary()

    rows: List[str] = []

    # 各単語の行を生成
    for word in words:
        # 単語の日本語訳を取得
        translation = dictionary.get_word_translation(word.text, word.pos)

        # no_translationオプションが指定されている場合、翻訳が None の場合のみ出力
        if option == "no_translation" and translation is not None:
            continue

        # 品詞の日本語訳を取得
        pos_translation = config.get_pos_translation(word.pos)

        # 例文を1つ取得（最初の例文を使用）
        example = word.examples[0] if word.examples else ""

        # 行をフォーマットして追加
        row = format_table_row(word, translation, pos_translation, example)
        rows.append(row)

    return rows


def save_report(rows: List[str], output_path: str) -> None:
    """
    レポートをファイルに保存する（ヘッダー行をこのタイミングで追加）
    
    Args:
        rows (List[str]): テーブルの行（ヘッダーは含まない）
        output_path (str): 出力ファイルのパス
    """
    header = generate_table_header()
    content = "\n".join([header] + rows)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)



def get_verb_forms(word: str, pos: str, dictionary: Dictionary) -> Tuple[str, str, str]:
    """
    動詞の原形、過去形、過去分詞形を取得する
    
    Args:
        word (str): 動詞
        pos (str): 品詞タグ
        dictionary (Dictionary): 辞書オブジェクト
    
    Returns:
        Tuple[str, str, str]: (原形, 過去形, 過去分詞形)
    """
    # 動詞の原形を取得
    try:
        base_form = dictionary.inflector.Search(word)[0][0]
    except Exception as e:
        print('Inflector failed for word:', word, 'pos:', pos)
        raise e
    v_info = dictionary.inflector.InflectVerb(base_form)

    if 'vp' not in v_info or 'vx' not in v_info:
        # 品詞の誤判定などで動詞情報が取得できない場合は None を返す
        return ('', '', '')

    try:
        # 動詞の過去形
        past_tense = v_info['vp'][0]
        # 動詞の過去分詞形
        past_participle = v_info['vx'][0]
    except (KeyError, IndexError) as e:
        print('maybe it\'s not verb: word:', word, 'pos:', pos, 'v_info:', v_info)
        raise e

    return (base_form, past_tense, past_participle)


def generate_verb_report_table_header() -> str:
    """
    動詞レポートの表のヘッダーを生成する
    
    Returns:
        str: 表のヘッダー
    """
    header = "| 原型 | 過去形 | 過去分詞形 | 意味・説明 |"
    separator = "|------|------|----------|----------|"
    return f"{header}\n{separator}"


def generate_verb_report(words: List[Word]) -> List[str]:
    """
    動詞リストからレポートの各行（ヘッダー除く）を生成する
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
    
    Returns:
        Tuple[List[str], List[str]]: (不規則動詞の行リスト, 規則動詞の行リスト)
    """
    dictionary = get_dictionary()

    # 動詞のみをフィルタリング
    verb_pos_tags = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    verbs = [word for word in words if word.pos in verb_pos_tags]

    # 動詞を規則変化と不規則変化に分類（行として格納）
    regular_rows: List[str] = []

    # 処理済みの動詞の原形を記録するセット
    processed_base_forms = set()

    for verb in verbs:
        # 動詞の原形、過去形、過去分詞形を取得
        base_form, past_tense, past_participle = get_verb_forms(verb.text, verb.pos, dictionary)

        # base_form が '' の場合(品詞の誤判定)はスキップ
        if base_form == '':
            continue

        # 既に処理済みの原形はスキップ
        if base_form in processed_base_forms:
            continue

        # 処理済みとしてマーク
        processed_base_forms.add(base_form)

        # 動詞の日本語訳を取得
        translation = dictionary.get_word_translation(base_form, 'VB') or "未登録"

        row = f"| {base_form} | {past_tense} | {past_participle} | {translation} |"

        regular_rows.append(row)

    # アルファベット順に整列
    regular_rows = sorted(regular_rows)

    return regular_rows


def save_full_report(lines: List[str], output_path: str) -> None:
    content = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

from typing import Any


def escape_md_cell(s: str) -> str:
    """
    Markdown テーブル用セルのエスケープ。
    '|' を '\|' に、連続改行は '<br>' に。
    None は '' 扱い。
    """
    if s is None:
        return ""
    # Ensure string
    s = str(s)
    # Normalize newlines to <br>
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse multiple newlines to single <br> between content
    s = s.replace("\n\n", "\n").replace("\n", "<br>")
    # Escape pipes
    s = s.replace("|", "\\|")
    return s


def format_grammar_points_table(items: List[Dict[str, Any]]) -> List[str]:
    """
    文法・構文ポイントの JSON 配列を Markdown テーブル行（文字列リスト）に整形して返す。
    先頭にヘッダ行を含める。
    並びは 'no' 数値昇順。
    """
    lines: List[str] = []
    lines.append("## 文法・構文のポイント解説")
    lines.append("")
    lines.append("| No | 例文 (英) | 構文・文法タイトル | 形 (form) | 解説 (要点) | 日本語訳 |")
    lines.append("|---:|---|---|---|---|---|")

    def _key(x):
        try:
            return int(str(x.get("no", "0")).strip())
        except Exception:
            return 0

    for it in sorted(items, key=_key):
        no = escape_md_cell(str(it.get("no", "")).strip())
        eng = escape_md_cell(str(it.get("eng", "")).strip())
        ttl = escape_md_cell(str(it.get("title", "")).strip())
        frm = escape_md_cell(str(it.get("form", "")).strip())
        expv = it.get("exp", [])
        if isinstance(expv, list):
            exp_join = "<br>".join("・" + escape_md_cell(str(e).strip()) for e in expv if str(e).strip())
        else:
            exp_join = escape_md_cell(str(expv or "").strip())
        jpn = escape_md_cell(str(it.get("jpn", "")).strip())
        lines.append(f"| {no} | {eng} | {ttl} | {frm} | {exp_join} | {jpn} |")

    return lines


def generate_full_report_with_grammar(
        words: List['Word'],
        title: str,
        option: str,
        grammar_points: Optional[List[Dict[str, Any]]]
) -> List[str]:
    """
    既存の「出現単語表」「動詞一覧」に加えて、
    grammar_points があれば「文法・構文のポイント解説」セクションを末尾に追加して返す。
    """
    rows = generate_report(words, option)
    verb_rows = generate_verb_report(words)
    parts: List[str] = []
    parts.append(f"# {title}")
    parts.append("")
    parts.append("## 出現単語表")
    parts.append(generate_table_header())
    parts.extend(rows)
    parts.append("")
    parts.append("## 動詞一覧")
    parts.append(generate_verb_report_table_header())
    parts.extend(verb_rows)
    if grammar_points:
        parts.append("")
        parts.extend(format_grammar_points_table(grammar_points))
    return parts
