"""
レポート生成機能のテスト
"""
import unittest
import os
import tempfile
from src.englishstudyhelper.word import Word
from src.englishstudyhelper.reporter import (
    format_table_row,
    generate_table_header,
    generate_report,
    save_report,
    generate_and_save_report
)


class TestReporter(unittest.TestCase):
    """
    レポート生成機能のテストケース
    """
    
    def setUp(self):
        """
        テスト前の準備
        """
        # テスト用の一時ディレクトリを作成
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_path = os.path.join(self.temp_dir.name, 'test_output.md')
        
        # テスト用の単語リストを作成
        self.test_words = [
            Word(text="rabbit", pos="NN", count=3, examples=["The rabbit felt soft."]),
            Word(text="play", pos="VB", count=2, examples=["Kipper went to play with Anna."]),
            Word(text="test", pos="NN", count=1, examples=["This is a test."])
        ]
    
    def tearDown(self):
        """
        テスト後のクリーンアップ
        """
        # 一時ディレクトリを削除
        self.temp_dir.cleanup()
    
    def test_format_table_row(self):
        """
        表の行フォーマットのテスト
        """
        # 単語オブジェクト
        word = Word(text="test", pos="NN", count=1, examples=["This is a test."])
        
        # 行をフォーマット
        row = format_table_row(word, "テスト", "名詞", "This is a test.")
        
        # フォーマットされた行が正しいか確認
        self.assertIn("test", row)
        self.assertIn("1", row)
        self.assertIn("テスト", row)
        self.assertIn("名詞", row)
        self.assertIn("This is a test.", row)
        
        # 翻訳がない場合
        row = format_table_row(word, None, "名詞", "This is a test.")
        self.assertIn("未登録", row)
        
        # 長い例文の場合
        long_example = "This is a very long example sentence that should be truncated in the output table."
        row = format_table_row(word, "テスト", "名詞", long_example)
        self.assertNotIn(long_example, row)  # 元の文字列はそのまま含まれない
        self.assertIn("...", row)  # 省略記号が含まれる
    
    def test_generate_table_header(self):
        """
        表のヘッダー生成のテスト
        """
        header = generate_table_header()
        
        # ヘッダーに必要な列名が含まれているか確認
        self.assertIn("語句", header)
        self.assertIn("出現回数", header)
        self.assertIn("意味・説明", header)
        self.assertIn("品詞", header)
        self.assertIn("例文", header)
        
        # 区切り線が含まれているか確認
        self.assertIn("-", header)
        self.assertIn("|", header)
    
    def test_generate_report(self):
        """
        レポート生成のテスト
        """
        # レポートを生成
        report = generate_report(self.test_words)
        
        # レポートが文字列であることを確認
        self.assertIsInstance(report, str)
        
        # レポートにヘッダーが含まれているか確認
        self.assertIn("語句", report)
        self.assertIn("出現回数", report)
        
        # レポートに各単語の情報が含まれているか確認
        self.assertIn("rabbit", report)
        self.assertIn("play", report)
        self.assertIn("test", report)
        
        # 出現回数が含まれているか確認
        self.assertIn("3", report)
        self.assertIn("2", report)
        self.assertIn("1", report)
    
    def test_save_report(self):
        """
        レポート保存のテスト
        """
        # テスト用のレポート
        test_report = "This is a test report."
        
        # レポートを保存
        save_report(test_report, self.output_path)
        
        # ファイルが作成されたか確認
        self.assertTrue(os.path.exists(self.output_path))
        
        # ファイルの内容が正しいか確認
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertEqual(content, test_report)
    
    def test_generate_and_save_report(self):
        """
        レポート生成と保存の統合テスト
        """
        # レポートを生成して保存
        generate_and_save_report(self.test_words, self.output_path)
        
        # ファイルが作成されたか確認
        self.assertTrue(os.path.exists(self.output_path))
        
        # ファイルの内容を確認
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # レポートに必要な情報が含まれているか確認
            self.assertIn("語句", content)
            self.assertIn("出現回数", content)
            self.assertIn("rabbit", content)
            self.assertIn("play", content)
            self.assertIn("test", content)


if __name__ == '__main__':
    unittest.main()