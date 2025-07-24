"""
分析結果をレポートとして出力するモジュール
"""
from email.policy import default
from typing import List, Dict, Optional
import textwrap

from .word import Word
from .config import get_config
from .dictionary import get_dictionary


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


def generate_report(words: List[Word], option: str) -> str:
    """
    単語リストからレポートを生成する
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
        option (str): オプション（例: "no_translation"）
    
    Returns:
        str: レポート
    """
    config = get_config()
    dictionary = get_dictionary()
    
    # 表のヘッダーを生成
    report = [generate_table_header()]
    
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
        report.append(row)
    
    # レポートを文字列として結合
    return "\n".join(report)


def save_report(report: str, output_path: str) -> None:
    """
    レポートをファイルに保存する
    
    Args:
        report (str): レポート
        output_path (str): 出力ファイルのパス
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def generate_and_save_report(words: List[Word], output_path: str, option='') -> None:
    """
    レポートを生成してファイルに保存する
    
    Args:
        words (List[Word]): 単語オブジェクトのリスト
        output_path (str): 出力ファイルのパス
        option (str): オプション（例: "no_translation"）
    """
    report = generate_report(words, option)
    save_report(report, output_path)