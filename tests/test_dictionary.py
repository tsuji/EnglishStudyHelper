"""
辞書検索機能のテスト
"""
import unittest
import os
import sqlite3
import tempfile
from src.englishstudyhelper.dictionary import Dictionary, get_dictionary


class TestDictionary(unittest.TestCase):
    """
    辞書検索機能のテストケース
    """
    
    def setUp(self):
        """
        テスト前の準備
        """
        # テスト用の一時ディレクトリを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_ejdict.sqlite3')
        
        # テスト用のDBを作成
        self._create_test_db()
        
    def tearDown(self):
        """
        テスト後のクリーンアップ
        """
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    def _create_test_db(self):
        """
        テスト用のDBを作成する
        """
        # DBに接続
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # テーブルを作成
        cursor.execute('''
        CREATE TABLE items (
            item_id INTEGER PRIMARY KEY,
            word TEXT UNIQUE,
            mean TEXT,
            level INTEGER DEFAULT 0
        )
        ''')
        
        # インデックスを作成
        cursor.execute('''
        CREATE INDEX word_index ON items (word)
        ''')
        
        # テストデータを挿入
        test_data = [
            (1, 'test', 'テスト', 1),
            (2, 'example', '例 / 実例 / 見本', 1),
            (3, 'dictionary', '辞書', 2),
            (4, 'translation', '翻訳', 2),
            (5, 'run', '走る / 運営する / 実行する / 立候補する', 1),
            (6, 'running', '走ること / 運営 / 連続した', 1),
            (7, 'ran', '走った', 1),
            (8, 'runs', '走る', 1),
            (9, 'book', '本 / 予約する', 1),
            (10, 'books', '本（複数形）', 1),
            (11, 'good', '良い / 優れた / 親切な', 1),
            (12, 'better', 'より良い', 1),
            (13, 'best', '最も良い', 1)
        ]
        
        cursor.executemany(
            'INSERT INTO items (item_id, word, mean, level) VALUES (?, ?, ?, ?)',
            test_data
        )
        
        # 変更をコミット
        conn.commit()
        
        # 接続を閉じる
        conn.close()
    
    def test_get_word_translation(self):
        """
        単語の翻訳取得テスト
        """
        dictionary = Dictionary(self.db_path)
        
        # 登録されている単語の翻訳を取得
        self.assertEqual(dictionary.get_word_translation('test'), 'テスト')
        self.assertEqual(dictionary.get_word_translation('example'), '例 / 実例 / 見本')
        self.assertEqual(dictionary.get_word_translation('dictionary'), '辞書')
        self.assertEqual(dictionary.get_word_translation('translation'), '翻訳')
        
        # 大文字小文字は区別しない
        self.assertEqual(dictionary.get_word_translation('TEST'), 'テスト')
        self.assertEqual(dictionary.get_word_translation('Example'), '例 / 実例 / 見本')
        
        # 登録されていない単語は None を返す
        self.assertIsNone(dictionary.get_word_translation('unknown'))
        
        # max_translationsを1に指定して翻訳を取得
        self.assertEqual(dictionary.get_word_translation('example', max_translations=1), '例')
    
    def test_get_dictionary_singleton(self):
        """
        シングルトンパターンのテスト
        """
        # 同じパスで取得した場合、同じインスタンスが返される
        dictionary1 = get_dictionary(self.db_path)
        dictionary2 = get_dictionary(self.db_path)
        self.assertIs(dictionary1, dictionary2)
    
    def test_db_not_found(self):
        """
        DBが見つからない場合のテスト
        """
        # 存在しないDBパスを指定
        non_existent_path = os.path.join(self.temp_dir.name, 'non_existent.sqlite3')
        
        dictionary = Dictionary(non_existent_path)
        
        # DBが存在しない場合はNoneを返す
        self.assertIsNone(dictionary.get_word_translation('test'))
        
    def test_translation_formatting(self):
        """
        翻訳結果のフォーマットのテスト
        """
        dictionary = Dictionary(self.db_path)
        
        # 複数の訳語がある単語の翻訳を取得
        translation = dictionary.get_word_translation('example')
        
        # "/"区切りになっていることを確認
        self.assertEqual(translation, '例 / 実例 / 見本')
        
        # max_translationsを指定して翻訳を取得
        translation = dictionary.get_word_translation('run', max_translations=2)
        
        # 指定した数だけの訳語が返されることを確認
        self.assertEqual(translation, '走る / 運営する')
        
        # max_translationsが訳語の数より多い場合
        translation = dictionary.get_word_translation('dictionary', max_translations=5)
        
        # 全ての訳語が返されることを確認
        self.assertEqual(translation, '辞書')
        
    def test_word_stemming(self):
        """
        単語の原型推測のテスト
        """
        dictionary = Dictionary(self.db_path)
        
        # 名詞の複数形
        self.assertEqual(dictionary.get_word_translation('books', part_of_speech='NNS'), '本 / 予約する')
        
        # 動詞の現在分詞/動名詞
        self.assertEqual(dictionary.get_word_translation('running', part_of_speech='VBG'), '走る / 運営する / 実行する')
        
        # 動詞の過去形
        self.assertEqual(dictionary.get_word_translation('ran', part_of_speech='VBD'), '走る / 運営する / 実行する')
        
        # 動詞の三人称単数現在
        self.assertEqual(dictionary.get_word_translation('runs', part_of_speech='VBZ'), '走る / 運営する / 実行する')
        
        # 形容詞の比較級
        self.assertEqual(dictionary.get_word_translation('better', part_of_speech='JJR'), '良い / 優れた / 親切な')
        
    def test_edge_cases(self):
        """
        エッジケースのテスト
        """
        dictionary = Dictionary(self.db_path)
        
        # 存在しない単語
        self.assertIsNone(dictionary.get_word_translation('nonexistent'))
        
        # 空の文字列
        self.assertIsNone(dictionary.get_word_translation(''))
        
        # 原型推測に失敗するケース
        self.assertIsNone(dictionary.get_word_translation('xyz123', part_of_speech='NNS'))
        
        # max_translationsが0の場合
        self.assertEqual(dictionary.get_word_translation('example', max_translations=0), '')
        
        # max_translationsが負の場合
        self.assertEqual(dictionary.get_word_translation('example', max_translations=-1), '')

    def test_get_base_form(self):
        """
        単語の原型取得のテスト
        """
        dictionary = Dictionary(self.db_path)

        # 名詞の複数形
        self.assertEqual(dictionary._get_base_form('books', 'NNS'), 'book')

        # 動詞の現在分詞
        self.assertEqual(dictionary._get_base_form('running', 'VBG'), 'run')

        # 動詞の過去形
        self.assertEqual(dictionary._get_base_form('given', 'VBN'), 'give')

        # 動詞の三人称単数現在
        self.assertEqual(dictionary._get_base_form('runs', 'VBZ'), 'run')

        # 形容詞の比較級
        # self.assertequalertequal(dictionary._get_base_form('better', 'nns'), 'good')

        # 形容詞
        self.assertEqual(dictionary._get_base_form('scared', 'JJ'), 'scared')

        # 名詞の形容詞的用法の名詞の複数形
        # self.assertEqual(dictionary._get_base_form('better', 'NNS'), 'good')

if __name__ == '__main__':
    unittest.main()