"""
テキスト分析を行うモジュール
"""
import re
import ssl
from typing import Dict, List, Tuple

import nltk

from . import dictionary, word
from .config import get_config
from .word import Word

# SSLの証明書検証を無効化（開発環境用）
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


def ensure_nltk_resources():
    """必要なNLTKリソースをダウンロードする"""
    resources = [
        'punkt',
        'averaged_perceptron_tagger',
        'punkt_tab',
        'averaged_perceptron_tagger_eng',
    ]

    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            try:
                nltk.download(resource)
            except Exception as e:
                print(f"警告: {resource}のダウンロードに失敗しました: {e}")


# 起動時にリソースを確認
ensure_nltk_resources()


def read_text_file(file_path: str) -> str:
    """
    テキストファイルを読み込む
    
    Args:
        file_path (str): テキストファイルのパス
    
    Returns:
        str: ファイルの内容
    
    Raises:
        FileNotFoundError: ファイルが見つからない場合
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")


def clean_text(text: str) -> str:
    """
    テキストをクリーニングする
    
    Args:
        text (str): 元のテキスト
    
    Returns:
        str: クリーニングされたテキスト
    """
    # バックスラッシュを削除
    text = text.replace('\\', '')

    # 複数の空白を1つの空白に置換
    text = re.sub(r'\s+', ' ', text)

    return text


def extract_sentences(text: str) -> List[str]:
    """
    テキストから文を抽出する
    
    Args:
        text (str): テキスト
    
    Returns:
        List[str]: 文のリスト
    """
    # NLTKのsentence tokenizerを使用
    sentences = nltk.sent_tokenize(text)

    # 空の文や記号のみの文を除外
    sentences = [s.strip() for s in sentences if s.strip() and not all(c in '.,;:!?"\'()[]{}' for c in s.strip())]

    return sentences


def tokenize_and_tag(sentence: str) -> List[Tuple[str, str]]:
    """
    文をトークン化し、品詞タグを付ける
    
    Args:
        sentence (str): 文
    
    Returns:
        List[Tuple[str, str]]: (単語, 品詞タグ) のリスト
    """
    # 単語に分割
    tokens = nltk.word_tokenize(sentence)

    # 品詞タグ付け
    tagged_tokens = nltk.pos_tag(tokens)

    return tagged_tokens


def analyze_text(text: str) -> Dict[str, Word]:
    """
    テキストを分析し、単語の出現回数と例文を収集する
    
    Args:
        text (str): 分析するテキスト
    
    Returns:
        Dict[str, Word]: 単語オブジェクトの辞書 (キーは "単語_品詞")
    """
    # テキストをクリーニング
    cleaned_text = clean_text(text)

    # 文を抽出
    sentences = extract_sentences(cleaned_text)

    # 単語を収集
    word_dict = {}

    for sentence in sentences:
        # 文をトークン化し、品詞タグを付ける
        tagged_tokens = tokenize_and_tag(sentence)

        # 各単語を処理
        for token, pos in tagged_tokens:
            # 記号や数字は除外
            if not token.isalpha():
                continue

            # 単語と品詞の組み合わせのキーを作成
            word_key = f"{token.lower()}_{pos}"

            # 辞書に単語を追加または更新
            if word_key not in word_dict:
                word = token.lower()
                org = dictionary.get_dictionary().get_word_base_form(word, pos)
                word_dict[word_key] = Word(text=word, org=org, pos=pos)

            # 出現回数をインクリメント
            word_dict[word_key].increment_count()

            # 例文を追加
            word_dict[word_key].add_example(sentence)

    return word_dict


def filter_words(word_dict: Dict[str, Word]) -> Dict[str, Word]:
    """
    単語を除外条件に基づいてフィルタリングする
    
    Args:
        word_dict (Dict[str, Word]): 単語オブジェクトの辞書
    
    Returns:
        Dict[str, Word]: フィルタリングされた単語オブジェクトの辞書
    """
    config = get_config()
    filtered_dict = {}

    for word_key, word_obj in word_dict.items():
        # 除外すべき単語かどうかを判定
        if not config.should_exclude_word(word_obj.text, word_obj.pos):
            filtered_dict[word_key] = word_obj

    return filtered_dict


def sort_words_by_count(word_dict: Dict[str, Word]) -> List[Word]:
    """
    単語を出現回数順にソートする
    
    Args:
        word_dict (Dict[str, Word]): 単語オブジェクトの辞書
    
    Returns:
        List[Word]: 出現回数順にソートされた単語オブジェクトのリスト
    """
    return sorted(word_dict.values(), key=lambda w: w.count, reverse=True)

def sort_words_by_dict(word_dict: Dict[str, Word]) -> List[Word]:
    """
    単語を辞書順にソートする

    Args:
        word_dict (Dict[str, Word]): 単語オブジェクトの辞書
    Returns:
        List[Word]: 辞書順にソートされた単語オブジェクトのリスト
    """
    return sorted(word_dict.values(), key=lambda w: w.text)

def analyze_file(file_path: str) -> List[Word]:
    """
    ファイルを分析し、フィルタリングされた単語リストを返す
    
    Args:
        file_path (str): 分析するファイルのパス
    
    Returns:
        List[Word]: フィルタリングされ、出現回数順にソートされた単語オブジェクトのリスト
    """
    # ファイルを読み込む
    text = read_text_file(file_path)

    # テキストを分析
    word_dict = analyze_text(text)

    # 単語をフィルタリング
    filtered_dict = filter_words(word_dict)

    # 単語を辞書順にソート
    sorted_words = sort_words_by_dict(filtered_dict)

    return sorted_words
