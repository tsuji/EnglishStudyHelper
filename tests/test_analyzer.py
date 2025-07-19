"""
テキスト分析機能のテスト
"""
import unittest
import os
import tempfile
from src.englishstudyhelper.word import Word
from src.englishstudyhelper.analyzer import (
    clean_text,
    extract_sentences,
    tokenize_and_tag,
    analyze_text,
    filter_words,
    sort_words_by_count,
    read_text_file
)


class TestAnalyzer(unittest.TestCase):
    """
    テキスト分析機能のテストケース
    """
    
    def setUp(self):
        """
        テスト前の準備
        """
        # テスト用のテキストファイルを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.text_path = os.path.join(self.temp_dir.name, 'test_text.txt')
        
        # テスト用のテキスト
        self.test_text = (
            "This is a test. It has multiple sentences.\n"
            "The rabbit felt soft. Kipper went to play with Anna."
        )
        
        # テキストファイルを書き込む
        with open(self.text_path, 'w', encoding='utf-8') as f:
            f.write(self.test_text)
    
    def tearDown(self):
        """
        テスト後のクリーンアップ
        """
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    def test_read_text_file(self):
        """
        テキストファイル読み込みのテスト
        """
        # ファイルを読み込む
        text = read_text_file(self.text_path)
        
        # 読み込んだテキストが正しいか確認
        self.assertEqual(text, self.test_text)
        
        # 存在しないファイルの場合、例外が発生することを確認
        with self.assertRaises(FileNotFoundError):
            read_text_file(os.path.join(self.temp_dir.name, 'non_existent.txt'))
    
    def test_clean_text(self):
        """
        テキストクリーニングのテスト
        """
        # バックスラッシュを含むテキスト
        text_with_backslash = "This is a test.\\ It has backslashes.\\"
        cleaned = clean_text(text_with_backslash)
        self.assertEqual(cleaned, "This is a test. It has backslashes.")
        
        # 複数の空白を含むテキスト
        text_with_spaces = "This   has   multiple    spaces."
        cleaned = clean_text(text_with_spaces)
        self.assertEqual(cleaned, "This has multiple spaces.")
    
    def test_extract_sentences(self):
        """
        文抽出のテスト
        """
        # 複数の文を含むテキスト
        text = "This is the first sentence. This is the second. And this is the third!"
        sentences = extract_sentences(text)
        
        # 正しく文が抽出されているか確認
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], "This is the first sentence.")
        self.assertEqual(sentences[1], "This is the second.")
        self.assertEqual(sentences[2], "And this is the third!")
        
        # 空の文は除外される
        text_with_empty = "First.  . Third."
        sentences = extract_sentences(text_with_empty)
        self.assertEqual(len(sentences), 2)
        self.assertEqual(sentences[0], "First.")
        self.assertEqual(sentences[1], "Third.")
    
    def test_tokenize_and_tag(self):
        """
        トークン化と品詞タグ付けのテスト
        """
        # 単純な文
        sentence = "The cat sat on the mat."
        tokens = tokenize_and_tag(sentence)
        
        # トークンと品詞タグのペアが正しく取得できているか確認
        self.assertIsInstance(tokens, list)
        self.assertTrue(all(isinstance(t, tuple) and len(t) == 2 for t in tokens))
        
        # 特定のトークンと品詞タグを確認
        self.assertIn(('The', 'DT'), tokens)
        self.assertIn(('cat', 'NN'), tokens)
        self.assertIn(('sat', 'VBD'), tokens)
    
    def test_analyze_text(self):
        """
        テキスト分析のテスト
        """
        # テキストを分析
        word_dict = analyze_text(self.test_text)
        
        # 単語辞書が正しく作成されているか確認
        self.assertIsInstance(word_dict, dict)
        
        # 特定の単語が含まれているか確認
        self.assertIn('test_NN', word_dict)
        self.assertIn('rabbit_NN', word_dict)
        
        # 単語オブジェクトの内容を確認
        test_word = word_dict['test_NN']
        self.assertEqual(test_word.text, 'test')
        self.assertEqual(test_word.pos, 'NN')
        self.assertEqual(test_word.count, 1)
        self.assertIn('This is a test.', test_word.examples)
        
        # 複数回出現する単語の出現回数を確認
        if 'is_VBZ' in word_dict:
            is_word = word_dict['is_VBZ']
            self.assertEqual(is_word.count, 2)
    
    def test_filter_words(self):
        """
        単語フィルタリングのテスト
        """
        # テスト用の単語辞書を作成
        word_dict = {
            'test_NN': Word(text='test', pos='NN', count=1),
            'the_DT': Word(text='the', pos='DT', count=3),
            'is_VBZ': Word(text='is', pos='VBZ', count=2),
            'rabbit_NN': Word(text='rabbit', pos='NN', count=1),
            'anna_NNP': Word(text='anna', pos='NNP', count=1)
        }
        
        # 単語をフィルタリング
        filtered_dict = filter_words(word_dict)
        
        # 除外されるべき単語が除外されているか確認
        self.assertIn('test_NN', filtered_dict)
        self.assertIn('rabbit_NN', filtered_dict)
        self.assertNotIn('the_DT', filtered_dict)  # 定冠詞は除外
        self.assertNotIn('is_VBZ', filtered_dict)  # be動詞は除外
        self.assertNotIn('anna_NNP', filtered_dict)  # 固有名詞は除外
    
    def test_sort_words_by_count(self):
        """
        単語の出現回数順ソートのテスト
        """
        # テスト用の単語辞書を作成
        word_dict = {
            'test_NN': Word(text='test', pos='NN', count=1),
            'rabbit_NN': Word(text='rabbit', pos='NN', count=3),
            'play_VB': Word(text='play', pos='VB', count=2)
        }
        
        # 単語を出現回数順にソート
        sorted_words = sort_words_by_count(word_dict)
        
        # 正しくソートされているか確認
        self.assertEqual(len(sorted_words), 3)
        self.assertEqual(sorted_words[0].text, 'rabbit')  # 最も多い
        self.assertEqual(sorted_words[1].text, 'play')    # 2番目
        self.assertEqual(sorted_words[2].text, 'test')    # 最も少ない


if __name__ == '__main__':
    unittest.main()