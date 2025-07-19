"""
設定ファイル読み込み機能のテスト
"""
import unittest
import os
import json
import tempfile
from src.englishstudyhelper.config import Config, get_config


class TestConfig(unittest.TestCase):
    """
    設定ファイル読み込み機能のテストケース
    """
    
    def setUp(self):
        """
        テスト前の準備
        """
        # テスト用の設定ファイルを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'test_settings.json')
        
        # テスト用の設定データ
        self.config_data = {
            "exclude_pos": ["NNP", "IN", "DT"],
            "be_verbs": ["be", "am", "is", "are"],
            "pos_translations": {
                "NN": "名詞",
                "VB": "動詞"
            }
        }
        
        # 設定ファイルを書き込む
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=4)
    
    def tearDown(self):
        """
        テスト後のクリーンアップ
        """
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    def test_load_config(self):
        """
        設定ファイルの読み込みテスト
        """
        config = Config(self.config_path)
        
        # 設定データが正しく読み込まれているか確認
        self.assertEqual(config.get_exclude_pos(), self.config_data["exclude_pos"])
        self.assertEqual(config.get_be_verbs(), self.config_data["be_verbs"])
    
    def test_get_pos_translation(self):
        """
        品詞の翻訳取得テスト
        """
        config = Config(self.config_path)
        
        # 登録されている品詞の翻訳を取得
        self.assertEqual(config.get_pos_translation("NN"), "名詞")
        self.assertEqual(config.get_pos_translation("VB"), "動詞")
        
        # 登録されていない品詞はそのまま返される
        self.assertEqual(config.get_pos_translation("JJ"), "JJ")
    
    def test_should_exclude_word(self):
        """
        単語の除外判定テスト
        """
        config = Config(self.config_path)
        
        # 除外すべき品詞
        self.assertTrue(config.should_exclude_word("test", "NNP"))
        self.assertTrue(config.should_exclude_word("test", "IN"))
        self.assertTrue(config.should_exclude_word("test", "DT"))
        
        # 除外すべき単語 (be動詞)
        self.assertTrue(config.should_exclude_word("be", "VB"))
        self.assertTrue(config.should_exclude_word("is", "VBZ"))
        
        # 除外すべきでない単語
        self.assertFalse(config.should_exclude_word("test", "NN"))
        self.assertFalse(config.should_exclude_word("example", "NN"))
    
    def test_get_config_singleton(self):
        """
        シングルトンパターンのテスト
        """
        # 同じパスで取得した場合、同じインスタンスが返される
        config1 = get_config(self.config_path)
        config2 = get_config(self.config_path)
        self.assertIs(config1, config2)
    
    def test_file_not_found(self):
        """
        ファイルが見つからない場合のテスト
        """
        # 存在しないファイルパスを指定
        non_existent_path = os.path.join(self.temp_dir.name, 'non_existent.json')
        
        # FileNotFoundError が発生することを確認
        with self.assertRaises(FileNotFoundError):
            Config(non_existent_path)


if __name__ == '__main__':
    unittest.main()