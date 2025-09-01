"""
レポート生成機能のテスト
"""
import os
import tempfile
import unittest
from unittest.mock import MagicMock

from src.englishstudyhelper.dictionary import Dictionary
from src.englishstudyhelper.reporter import (
    format_table_row,
    generate_table_header,
    generate_report,
    save_report,
    generate_and_save_report,
    is_irregular_verb,
    get_verb_forms,
    generate_verb_report_table_header,
    save_verb_report,
    generate_and_save_verb_report
)
from src.englishstudyhelper.word import Word


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
        # レポートを生成（行リスト）
        rows = generate_report(self.test_words, '')

        # レポートが行リストであることを確認
        self.assertIsInstance(rows, list)
        self.assertTrue(all(isinstance(r, str) for r in rows))

        # ヘッダーは含まれない
        self.assertFalse(any("語句" in r for r in rows))
        self.assertFalse(any("出現回数" in r for r in rows))

        # 各単語の情報が含まれているか確認
        joined = "\n".join(rows)
        self.assertIn("rabbit", joined)
        self.assertIn("play", joined)
        self.assertIn("test", joined)

        # 出現回数が含まれているか確認
        self.assertIn("3", joined)
        self.assertIn("2", joined)
        self.assertIn("1", joined)

    def test_save_report(self):
        """
        レポート保存のテスト
        """
        # テスト用の行
        test_rows = ["| word | 1 | mean | 名詞 | ex |"]

        # レポートを保存（ヘッダー付与される）
        save_report(test_rows, self.output_path)

        # ファイルが作成されたか確認
        self.assertTrue(os.path.exists(self.output_path))

        # ファイルの内容が正しいか確認（ヘッダー+1行）
        with open(self.output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("語句", content)
            self.assertIn("| word |", content)

    def test_is_irregular_verb(self):
        """
        不規則動詞の判定テスト
        """
        # テスト用の辞書オブジェクトをモック
        mock_dict = MagicMock(spec=Dictionary)
        mock_dict._get_verb_infinitive.side_effect = lambda word: word

        # 不規則動詞のテスト
        self.assertTrue(is_irregular_verb("go", mock_dict))
        self.assertTrue(is_irregular_verb("take", mock_dict))
        self.assertTrue(is_irregular_verb("see", mock_dict))

        # 規則動詞のテスト
        self.assertFalse(is_irregular_verb("play", mock_dict))
        self.assertFalse(is_irregular_verb("work", mock_dict))
        self.assertFalse(is_irregular_verb("study", mock_dict))

        # 原形が変換される場合
        mock_dict._get_verb_infinitive.side_effect = lambda word: "go" if word == "went" else word
        self.assertTrue(is_irregular_verb("went", mock_dict))

    def test_get_verb_forms(self):
        """
        動詞の活用形取得テスト
        """
        # テスト用の辞書オブジェクトをモック
        mock_dict = MagicMock(spec=Dictionary)
        mock_dict._get_verb_infinitive.return_value = "play"
        mock_dict._get_verb_infinitive_from_ing.return_value = "play"
        mock_dict._get_verb_infinitive_from_third_person.return_value = "play"

        # 原形のテスト
        base_form, past_tense, past_participle = get_verb_forms("play", "VB", mock_dict)
        self.assertEqual(base_form, "play")
        self.assertEqual(past_tense, "played")
        self.assertEqual(past_participle, "played")

        # 過去形のテスト
        mock_dict._get_verb_infinitive.return_value = "go"
        base_form, past_tense, past_participle = get_verb_forms("went", "VBD", mock_dict)
        self.assertEqual(base_form, "go")
        self.assertEqual(past_tense, "went")
        self.assertEqual(past_participle, "gone")

        # 現在分詞のテスト
        mock_dict._get_verb_infinitive_from_ing.return_value = "run"
        base_form, past_tense, past_participle = get_verb_forms("running", "VBG", mock_dict)
        self.assertEqual(base_form, "run")
        self.assertEqual(past_tense, "ran")
        self.assertEqual(past_participle, "run")

        # 三人称単数現在のテスト
        mock_dict._get_verb_infinitive_from_third_person.return_value = "study"
        base_form, past_tense, past_participle = get_verb_forms("studies", "VBZ", mock_dict)
        self.assertEqual(base_form, "study")
        self.assertEqual(past_tense, "studied")
        self.assertEqual(past_participle, "studied")

    def test_generate_verb_report_table_header(self):
        """
        動詞レポートの表ヘッダー生成テスト
        """
        header = generate_verb_report_table_header()

        # ヘッダーに必要な列名が含まれているか確認
        self.assertIn("原型", header)
        self.assertIn("過去形", header)
        self.assertIn("過去分詞形", header)
        self.assertIn("意味・説明", header)

        # 区切り線が含まれているか確認
        self.assertIn("-", header)
        self.assertIn("|", header)


if __name__ == '__main__':
    unittest.main()
