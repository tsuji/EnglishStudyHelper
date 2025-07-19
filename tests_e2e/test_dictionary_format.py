#!/usr/bin/env python3
"""
辞書検索機能のフォーマットをテストするスクリプト
"""
from src.englishstudyhelper.dictionary import get_dictionary

def test_dictionary_format():
    """
    辞書検索機能のフォーマットをテストする
    """
    print("=== 辞書検索機能のフォーマットテスト ===")
    dictionary = get_dictionary()
    
    # テスト用の単語リスト
    words = [
        "test",
        "example",
        "book",
        "run",
        "water",
        "good"
    ]
    
    for word in words:
        # 通常の検索
        translation = dictionary.get_word_translation(word)
        print(f"\n単語: {word}")
        print(f"翻訳: {translation}")
        
        # max_translationsを指定した検索
        translation = dictionary.get_word_translation(word, max_translations=2)
        print(f"翻訳 (max_translations=2): {translation}")
        
        # 品詞を指定した検索
        if word == "run":
            # 動詞の過去形
            translation = dictionary.get_word_translation("ran", part_of_speech="VBD")
            print(f"翻訳 (ran, part_of_speech=VBD): {translation}")
        
        if word == "book":
            # 名詞の複数形
            translation = dictionary.get_word_translation("books", part_of_speech="NNS")
            print(f"翻訳 (books, part_of_speech=NNS): {translation}")
        
        if word == "good":
            # 形容詞の比較級
            translation = dictionary.get_word_translation("better", part_of_speech="JJR")
            print(f"翻訳 (better, part_of_speech=JJR): {translation}")

if __name__ == "__main__":
    test_dictionary_format()