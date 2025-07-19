#!/usr/bin/env python3
"""
辞書検索機能の改善をテストするスクリプト
"""
from src.englishstudyhelper.dictionary import get_dictionary

def test_translation_formatting():
    """
    翻訳結果のフォーマット機能をテストする
    """
    print("=== 翻訳結果のフォーマット機能のテスト ===")
    dictionary = get_dictionary()
    
    # 複数の訳語がある単語の例
    words = ["water", "run", "book", "good"]
    
    for word in words:
        print(f"\n単語: {word}")
        
        # デフォルト（最大3つの訳語）
        translation = dictionary.get_word_translation(word)
        print(f"デフォルト（最大3つの訳語）:\n{translation}")
        
        # 最大1つの訳語
        translation = dictionary.get_word_translation(word, max_translations=1)
        print(f"最大1つの訳語:\n{translation}")
        
        # 最大5つの訳語
        translation = dictionary.get_word_translation(word, max_translations=5)
        print(f"最大5つの訳語:\n{translation}")

def test_word_stemming():
    """
    原型推測機能をテストする
    """
    print("\n=== 原型推測機能のテスト ===")
    dictionary = get_dictionary()
    
    # 名詞の複数形
    plural_nouns = [
        ("books", "NNS"),
        ("children", "NNS"),
        ("mice", "NNS"),
        ("boxes", "NNS"),
        ("cities", "NNS")
    ]
    
    print("\n名詞の複数形:")
    for word, pos in plural_nouns:
        translation = dictionary.get_word_translation(word, part_of_speech=pos)
        print(f"{word} ({pos}) -> {translation}")
    
    # 動詞の活用形
    verb_forms = [
        ("running", "VBG"),  # 現在分詞/動名詞
        ("ran", "VBD"),      # 過去形
        ("runs", "VBZ"),     # 三人称単数現在
        ("played", "VBD"),   # 過去形
        ("playing", "VBG"),  # 現在分詞/動名詞
        ("plays", "VBZ"),    # 三人称単数現在
        ("gone", "VBN"),     # 過去分詞
        ("written", "VBN"),  # 過去分詞
        ("took", "VBD"),     # 過去形
        ("taking", "VBG")    # 現在分詞/動名詞
    ]
    
    print("\n動詞の活用形:")
    for word, pos in verb_forms:
        translation = dictionary.get_word_translation(word, part_of_speech=pos)
        print(f"{word} ({pos}) -> {translation}")
    
    # 形容詞の比較級
    adjective_forms = [
        ("better", "JJR"),   # 比較級
        ("bigger", "JJR"),   # 比較級
        ("happier", "JJR"),  # 比較級
        ("more", "JJR"),     # 比較級
        ("worse", "JJR")     # 比較級
    ]
    
    print("\n形容詞の比較級:")
    for word, pos in adjective_forms:
        translation = dictionary.get_word_translation(word, part_of_speech=pos)
        print(f"{word} ({pos}) -> {translation}")

if __name__ == "__main__":
    test_translation_formatting()
    test_word_stemming()