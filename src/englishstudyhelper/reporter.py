"""
分析結果をレポートとして出力するモジュール
"""
from email.policy import default
from typing import List, Dict, Optional, Tuple
import textwrap

from .word import Word
from .config import get_config
from .dictionary import get_dictionary, Dictionary


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


def generate_and_save_report(words: List[Word], output_path: str, option='') -> None:
    """
    レポートを生成してファイルに保存する（互換用のヘルパー）。
    現在は generate_report で行リストを作り、save_report でヘッダー付きで保存する。
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
        output_path (str): 出力ファイルのパス
        option (str): オプション（例: "no_translation"）
    """
    rows = generate_report(words, option)
    save_report(rows, output_path)


def is_irregular_verb(word: str, dictionary: Dictionary) -> bool:
    """
    動詞が不規則変化かどうかを判定する
    
    Args:
        word (str): 動詞
        dictionary (Dictionary): 辞書オブジェクト
    
    Returns:
        bool: 不規則変化の場合はTrue
    """
    # 不規則変化の動詞の辞書
    irregular_verbs = {
        'be', 'have', 'do', 'say', 'make', 'go', 'take', 'come', 'see', 'get',
        'know', 'give', 'find', 'think', 'tell', 'become', 'leave', 'feel',
        'put', 'bring', 'begin', 'keep', 'hold', 'write', 'run', 'stand',
        'meet', 'sit', 'speak', 'let', 'set', 'send', 'pay', 'hear', 'mean',
        'lose', 'read', 'fall', 'lead', 'understand', 'buy', 'win', 'teach',
        'catch', 'choose', 'grow', 'wear', 'drive', 'break', 'show', 'throw',
        'build', 'spend', 'draw', 'fly', 'sell', 'rise', 'swim', 'forget',
        'cut', 'sing', 'hang', 'shake', 'ride', 'feed', 'beat', 'lie', 'lay',
        'shoot', 'sleep', 'wake', 'cost', 'hit', 'hurt', 'split', 'spread',
        'shut', 'stick', 'sting', 'strike', 'swear', 'sweep', 'swing', 'tear',
        'bend', 'bet', 'bite', 'blow', 'burn', 'burst', 'cast', 'deal', 'dig',
        'dream', 'drink', 'eat', 'fight', 'freeze', 'hide', 'kneel', 'lean',
        'leap', 'lend', 'light', 'seek', 'shine', 'sink', 'slide', 'smell',
        'spell', 'spill', 'spit', 'steal', 'weep', 'wind'
    }
    
    # 動詞の原形を取得
    base_form = dictionary._get_verb_infinitive(word)
    
    # 原形が不規則変化の動詞リストに含まれるかチェック
    return base_form in irregular_verbs


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
    base_form = word
    
    # 品詞タグに基づいて原形を取得
    if pos in ['VBD', 'VBN']:  # 過去形または過去分詞
        base_form = dictionary._get_verb_infinitive(word)
    elif pos == 'VBG':  # 現在分詞/動名詞
        base_form = dictionary._get_verb_infinitive_from_ing(word)
    elif pos == 'VBZ':  # 三人称単数現在
        base_form = dictionary._get_verb_infinitive_from_third_person(word)
    
    # 不規則変化の動詞の過去形と過去分詞形のマッピング
    irregular_verb_forms = {
        'be': ('was/were', 'been'),
        'have': ('had', 'had'),
        'do': ('did', 'done'),
        'say': ('said', 'said'),
        'make': ('made', 'made'),
        'go': ('went', 'gone'),
        'take': ('took', 'taken'),
        'come': ('came', 'come'),
        'see': ('saw', 'seen'),
        'get': ('got', 'got/gotten'),
        'know': ('knew', 'known'),
        'give': ('gave', 'given'),
        'find': ('found', 'found'),
        'think': ('thought', 'thought'),
        'tell': ('told', 'told'),
        'become': ('became', 'become'),
        'leave': ('left', 'left'),
        'feel': ('felt', 'felt'),
        'put': ('put', 'put'),
        'bring': ('brought', 'brought'),
        'begin': ('began', 'begun'),
        'keep': ('kept', 'kept'),
        'hold': ('held', 'held'),
        'write': ('wrote', 'written'),
        'run': ('ran', 'run'),
        'stand': ('stood', 'stood'),
        'meet': ('met', 'met'),
        'sit': ('sat', 'sat'),
        'speak': ('spoke', 'spoken'),
        'let': ('let', 'let'),
        'set': ('set', 'set'),
        'send': ('sent', 'sent'),
        'pay': ('paid', 'paid'),
        'hear': ('heard', 'heard'),
        'mean': ('meant', 'meant'),
        'lose': ('lost', 'lost'),
        'read': ('read', 'read'),
        'fall': ('fell', 'fallen'),
        'lead': ('led', 'led'),
        'understand': ('understood', 'understood'),
        'buy': ('bought', 'bought'),
        'win': ('won', 'won'),
        'teach': ('taught', 'taught'),
        'catch': ('caught', 'caught'),
        'choose': ('chose', 'chosen'),
        'grow': ('grew', 'grown'),
        'wear': ('wore', 'worn'),
        'drive': ('drove', 'driven'),
        'break': ('broke', 'broken'),
        'show': ('showed', 'shown'),
        'throw': ('threw', 'thrown'),
        'build': ('built', 'built'),
        'spend': ('spent', 'spent'),
        'draw': ('drew', 'drawn'),
        'fly': ('flew', 'flown'),
        'sell': ('sold', 'sold'),
        'rise': ('rose', 'risen'),
        'swim': ('swam', 'swum'),
        'forget': ('forgot', 'forgotten'),
        'cut': ('cut', 'cut'),
        'sing': ('sang', 'sung'),
        'hang': ('hung', 'hung'),
        'shake': ('shook', 'shaken'),
        'ride': ('rode', 'ridden'),
        'feed': ('fed', 'fed'),
        'beat': ('beat', 'beaten'),
        'lie': ('lay', 'lain'),
        'lay': ('laid', 'laid'),
        'shoot': ('shot', 'shot'),
        'sleep': ('slept', 'slept'),
        'wake': ('woke', 'woken'),
        'cost': ('cost', 'cost'),
        'hit': ('hit', 'hit'),
        'hurt': ('hurt', 'hurt'),
        'split': ('split', 'split'),
        'spread': ('spread', 'spread'),
        'shut': ('shut', 'shut'),
        'stick': ('stuck', 'stuck'),
        'sting': ('stung', 'stung'),
        'strike': ('struck', 'struck'),
        'swear': ('swore', 'sworn'),
        'sweep': ('swept', 'swept'),
        'swing': ('swung', 'swung'),
        'tear': ('tore', 'torn'),
        'bend': ('bent', 'bent'),
        'bet': ('bet', 'bet'),
        'bite': ('bit', 'bitten'),
        'blow': ('blew', 'blown'),
        'burn': ('burned/burnt', 'burned/burnt'),
        'burst': ('burst', 'burst'),
        'cast': ('cast', 'cast'),
        'deal': ('dealt', 'dealt'),
        'dig': ('dug', 'dug'),
        'dream': ('dreamed/dreamt', 'dreamed/dreamt'),
        'drink': ('drank', 'drunk'),
        'eat': ('ate', 'eaten'),
        'fight': ('fought', 'fought'),
        'freeze': ('froze', 'frozen'),
        'hide': ('hid', 'hidden'),
        'kneel': ('knelt', 'knelt'),
        'lean': ('leaned/leant', 'leaned/leant'),
        'leap': ('leaped/leapt', 'leaped/leapt'),
        'lend': ('lent', 'lent'),
        'light': ('lit', 'lit'),
        'seek': ('sought', 'sought'),
        'shine': ('shone', 'shone'),
        'sink': ('sank', 'sunk'),
        'slide': ('slid', 'slid'),
        'smell': ('smelled/smelt', 'smelled/smelt'),
        'spell': ('spelled/spelt', 'spelled/spelt'),
        'spill': ('spilled/spilt', 'spilled/spilt'),
        'spit': ('spat', 'spat'),
        'steal': ('stole', 'stolen'),
        'weep': ('wept', 'wept'),
        'wind': ('wound', 'wound')
    }
    
    # 不規則変化の動詞の場合
    if base_form in irregular_verb_forms:
        past_tense, past_participle = irregular_verb_forms[base_form]
    else:
        # 規則変化の動詞の場合
        if base_form.endswith('e'):
            past_tense = base_form + 'd'
            past_participle = base_form + 'd'
        elif base_form.endswith('y') and base_form[-2] not in ['a', 'e', 'i', 'o', 'u']:
            past_tense = base_form[:-1] + 'ied'
            past_participle = base_form[:-1] + 'ied'
        elif (len(base_form) > 1 and 
              base_form[-1] not in ['a', 'e', 'i', 'o', 'u', 'y', 'w'] and 
              base_form[-2] in ['a', 'e', 'i', 'o', 'u']):
            past_tense = base_form + base_form[-1] + 'ed'
            past_participle = base_form + base_form[-1] + 'ed'
        else:
            past_tense = base_form + 'ed'
            past_participle = base_form + 'ed'
    
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


def generate_verb_report(words: List[Word]) -> Tuple[List[str], List[str]]:
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
    irregular_rows: List[str] = []
    regular_rows: List[str] = []
    
    # 処理済みの動詞の原形を記録するセット
    processed_base_forms = set()
    
    for verb in verbs:
        # 動詞の原形、過去形、過去分詞形を取得
        base_form, past_tense, past_participle = get_verb_forms(verb.text, verb.pos, dictionary)
        
        # 既に処理済みの原形はスキップ
        if base_form in processed_base_forms:
            continue
        
        # 処理済みとしてマーク
        processed_base_forms.add(base_form)
        
        # 動詞の日本語訳を取得
        translation = dictionary.get_word_translation(base_form, 'VB') or "未登録"
        
        row = f"| {base_form} | {past_tense} | {past_participle} | {translation} |"
        
        # 不規則変化かどうかを判定
        if is_irregular_verb(verb.text, dictionary):
            irregular_rows.append(row)
        else:
            regular_rows.append(row)
    
    # アルファベット順に整列
    irregular_rows = sorted(irregular_rows)
    regular_rows = sorted(regular_rows)
    
    return irregular_rows, regular_rows


def save_verb_report(irregular_rows: List[str], regular_rows: List[str], output_path: str) -> None:
    """
    動詞レポートをファイルに保存する（見出しとテーブルヘッダーはこのタイミングで付与）
    
    Args:
        irregular_rows (List[str]): 不規則動詞の行
        regular_rows (List[str]): 規則動詞の行
        output_path (str): 出力ファイルのパス
    """
    parts: List[str] = []
    parts.append("## 不規則動詞")
    parts.append(generate_verb_report_table_header())
    parts.extend(irregular_rows)
    parts.append("")
    parts.append("## 一般動詞")
    parts.append(generate_verb_report_table_header())
    parts.extend(regular_rows)
    content = "\n".join(parts)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


def generate_and_save_verb_report(words: List[Word], output_path: str) -> None:
    """
    動詞レポートを生成してファイルに保存する
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
        output_path (str): 出力ファイルのパス
    """
    irregular_rows, regular_rows = generate_verb_report(words)
    save_verb_report(irregular_rows, regular_rows, output_path)


def generate_full_report(words: List[Word], title: str, option: str = '') -> List[str]:
    """
    1つのファイル分の統合レポート本文を生成する（見出し含む行リスト）
    
    構成:
      # {title}
      
      ## 出現単語表
      <table header>
      <rows>
      
      ## 動詞一覧
      ### 不規則動詞
      <verb table header>
      <irregular rows>
      
      ### 一般動詞
      <verb table header>
      <regular rows>
    """
    rows = generate_report(words, option)
    irregular_rows, regular_rows = generate_verb_report(words)
    parts: List[str] = []
    parts.append(f"# {title}")
    parts.append("")
    parts.append("## 出現単語表")
    parts.append(generate_table_header())
    parts.extend(rows)
    parts.append("")
    parts.append("## 動詞一覧")
    parts.append("### 不規則動詞")
    parts.append(generate_verb_report_table_header())
    parts.extend(irregular_rows)
    parts.append("")
    parts.append("### 一般動詞")
    parts.append(generate_verb_report_table_header())
    parts.extend(regular_rows)
    return parts


def save_full_report(lines: List[str], output_path: str) -> None:
    content = "\n".join(lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)