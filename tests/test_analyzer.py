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
        
        # 単語の出現回数を確認
        if 'is_VBZ' in word_dict:
            is_word = word_dict['is_VBZ']
            self.assertEqual(is_word.count, 1)
    
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


    def test_words_with_different_pos(self):
        """
        同じ単語が異なる品詞で登場する文を正しく分析できるかテスト
        """
        # テスト用のテキスト（同じ単語が異なる品詞で登場する文）
        test_text = (
            # play: 動詞と名詞
            "I play soccer every day. We watched a play at the theater. "
            # run: 動詞と名詞
            "She can run fast. I went for a run this morning. "
            # watch: 動詞と名詞
            "I watch TV after dinner. This is a new watch. "
            # light: 名詞と形容詞
            "Turn on the light. This bag is very light. "
            # book: 名詞と動詞
            "I read a good book. I want to book a room. "
            # face: 名詞と動詞
            "He has a kind face. Let's face the problem. "
            # close: 動詞と形容詞
            "Please close the door. We are very close friends. "
            # love: 名詞と動詞
            "Her love for animals is strong. I love this movie. "
            # walk: 名詞と動詞
            "Let's go for a walk. I walk to school. "
            # open: 動詞と形容詞
            "Open the window, please. The store is open. "
            # dance: 動詞と名詞
            "I like to dance. That was a great dance!"
        )
        
        # テキストを分析
        word_dict = analyze_text(test_text)
        
        # 同じ単語が異なる品詞で正しく識別されているか確認
        # play: 動詞と名詞
        self.assertIn('play_VBP', word_dict)  # 動詞
        self.assertIn('play_NN', word_dict)   # 名詞
        self.assertEqual(word_dict['play_VBP'].text, 'play')
        self.assertEqual(word_dict['play_NN'].text, 'play')
        self.assertEqual(word_dict['play_VBP'].pos, 'VBP')
        self.assertEqual(word_dict['play_NN'].pos, 'NN')
        self.assertIn('I play soccer every day.', word_dict['play_VBP'].examples)
        self.assertIn('We watched a play at the theater.', word_dict['play_NN'].examples)
        
        # run: 動詞と名詞
        self.assertIn('run_VB', word_dict)    # 動詞
        self.assertIn('run_NN', word_dict)    # 名詞
        self.assertEqual(word_dict['run_VB'].text, 'run')
        self.assertEqual(word_dict['run_NN'].text, 'run')
        self.assertEqual(word_dict['run_VB'].pos, 'VB')
        self.assertEqual(word_dict['run_NN'].pos, 'NN')
        self.assertIn('She can run fast.', word_dict['run_VB'].examples)
        self.assertIn('I went for a run this morning.', word_dict['run_NN'].examples)
        
        # watch: 動詞と名詞
        self.assertIn('watch_VBP', word_dict)  # 動詞
        self.assertIn('watch_NN', word_dict)   # 名詞
        self.assertEqual(word_dict['watch_VBP'].text, 'watch')
        self.assertEqual(word_dict['watch_NN'].text, 'watch')
        self.assertEqual(word_dict['watch_VBP'].pos, 'VBP')
        self.assertEqual(word_dict['watch_NN'].pos, 'NN')
        self.assertIn('I watch TV after dinner.', word_dict['watch_VBP'].examples)
        self.assertIn('This is a new watch.', word_dict['watch_NN'].examples)
        
        # light: 名詞と形容詞
        self.assertIn('light_NN', word_dict)   # 名詞
        self.assertIn('light_JJ', word_dict)   # 形容詞
        self.assertEqual(word_dict['light_NN'].text, 'light')
        self.assertEqual(word_dict['light_JJ'].text, 'light')
        self.assertEqual(word_dict['light_NN'].pos, 'NN')
        self.assertEqual(word_dict['light_JJ'].pos, 'JJ')
        self.assertIn('Turn on the light.', word_dict['light_NN'].examples)
        self.assertIn('This bag is very light.', word_dict['light_JJ'].examples)
        
        # book: 名詞のみ（NLTKは "book a room" の "book" も名詞として認識）
        self.assertIn('book_NN', word_dict)   # 名詞
        self.assertEqual(word_dict['book_NN'].text, 'book')
        self.assertEqual(word_dict['book_NN'].pos, 'NN')
        self.assertIn('I read a good book.', word_dict['book_NN'].examples)
        self.assertIn('I want to book a room.', word_dict['book_NN'].examples)
        
        # face: 名詞と動詞
        self.assertIn('face_NN', word_dict)   # 名詞
        self.assertIn('face_VB', word_dict)   # 動詞
        self.assertEqual(word_dict['face_NN'].text, 'face')
        self.assertEqual(word_dict['face_VB'].text, 'face')
        self.assertEqual(word_dict['face_NN'].pos, 'NN')
        self.assertEqual(word_dict['face_VB'].pos, 'VB')
        self.assertIn('He has a kind face.', word_dict['face_NN'].examples)
        self.assertIn("Let's face the problem.", word_dict['face_VB'].examples)
        
        # close: 動詞と形容詞
        self.assertIn('close_VB', word_dict)   # 動詞
        self.assertIn('close_JJ', word_dict)   # 形容詞
        self.assertEqual(word_dict['close_VB'].text, 'close')
        self.assertEqual(word_dict['close_JJ'].text, 'close')
        self.assertEqual(word_dict['close_VB'].pos, 'VB')
        self.assertEqual(word_dict['close_JJ'].pos, 'JJ')
        self.assertIn('Please close the door.', word_dict['close_VB'].examples)
        self.assertIn('We are very close friends.', word_dict['close_JJ'].examples)
        
        # love: 名詞と動詞
        self.assertIn('love_NN', word_dict)   # 名詞
        self.assertIn('love_VBP', word_dict)  # 動詞
        self.assertEqual(word_dict['love_NN'].text, 'love')
        self.assertEqual(word_dict['love_VBP'].text, 'love')
        self.assertEqual(word_dict['love_NN'].pos, 'NN')
        self.assertEqual(word_dict['love_VBP'].pos, 'VBP')
        self.assertIn('Her love for animals is strong.', word_dict['love_NN'].examples)
        self.assertIn('I love this movie.', word_dict['love_VBP'].examples)
        
        # walk: 名詞と動詞
        self.assertIn('walk_NN', word_dict)   # 名詞
        self.assertIn('walk_VBP', word_dict)  # 動詞
        self.assertEqual(word_dict['walk_NN'].text, 'walk')
        self.assertEqual(word_dict['walk_VBP'].text, 'walk')
        self.assertEqual(word_dict['walk_NN'].pos, 'NN')
        self.assertEqual(word_dict['walk_VBP'].pos, 'VBP')
        self.assertIn("Let's go for a walk.", word_dict['walk_NN'].examples)
        self.assertIn('I walk to school.', word_dict['walk_VBP'].examples)
        
        # open: 動詞と形容詞
        self.assertIn('open_VB', word_dict)   # 動詞
        self.assertIn('open_JJ', word_dict)   # 形容詞
        self.assertEqual(word_dict['open_VB'].text, 'open')
        self.assertEqual(word_dict['open_JJ'].text, 'open')
        self.assertEqual(word_dict['open_VB'].pos, 'VB')
        self.assertEqual(word_dict['open_JJ'].pos, 'JJ')
        self.assertIn('Open the window, please.', word_dict['open_VB'].examples)
        self.assertIn('The store is open.', word_dict['open_JJ'].examples)
        
        # dance: 動詞と名詞
        self.assertIn('dance_VB', word_dict)   # 動詞
        self.assertIn('dance_NN', word_dict)   # 名詞
        self.assertEqual(word_dict['dance_VB'].text, 'dance')
        self.assertEqual(word_dict['dance_NN'].text, 'dance')
        self.assertEqual(word_dict['dance_VB'].pos, 'VB')
        self.assertEqual(word_dict['dance_NN'].pos, 'NN')
        self.assertIn('I like to dance.', word_dict['dance_VB'].examples)
        self.assertIn('That was a great dance!', word_dict['dance_NN'].examples)


if __name__ == '__main__':
    unittest.main()