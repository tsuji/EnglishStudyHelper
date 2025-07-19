"""
Word クラスのテスト
"""
import unittest
from src.englishstudyhelper.word import Word


class TestWord(unittest.TestCase):
    """
    Word クラスのテストケース
    """
    
    def test_initialization(self):
        """
        初期化のテスト
        """
        # 基本的な初期化
        word = Word(text="test", pos="NN")
        self.assertEqual(word.text, "test")
        self.assertEqual(word.pos, "NN")
        self.assertEqual(word.count, 0)
        self.assertEqual(word.examples, [])
        
        # カウント指定での初期化
        word = Word(text="test", pos="NN", count=5)
        self.assertEqual(word.count, 5)
        
        # 例文指定での初期化
        examples = ["This is a test.", "Another test."]
        word = Word(text="test", pos="NN", examples=examples)
        self.assertEqual(word.examples, examples)
    
    def test_increment_count(self):
        """
        出現回数のインクリメントのテスト
        """
        word = Word(text="test", pos="NN")
        self.assertEqual(word.count, 0)
        
        word.increment_count()
        self.assertEqual(word.count, 1)
        
        word.increment_count()
        self.assertEqual(word.count, 2)
    
    def test_add_example(self):
        """
        例文追加のテスト
        """
        word = Word(text="test", pos="NN")
        self.assertEqual(word.examples, [])
        
        # 例文を追加
        word.add_example("This is a test.")
        self.assertEqual(word.examples, ["This is a test."])
        
        # 別の例文を追加
        word.add_example("Another test.")
        self.assertEqual(word.examples, ["This is a test.", "Another test."])
        
        # 重複する例文は追加されない
        word.add_example("This is a test.")
        self.assertEqual(word.examples, ["This is a test.", "Another test."])
    
    def test_get_key(self):
        """
        キー取得のテスト
        """
        word = Word(text="Test", pos="NN")
        self.assertEqual(word.get_key(), "test_NN")
        
        word = Word(text="HELLO", pos="JJ")
        self.assertEqual(word.get_key(), "hello_JJ")
    
    def test_equality(self):
        """
        等価比較のテスト
        """
        word1 = Word(text="test", pos="NN")
        word2 = Word(text="test", pos="NN", count=5)
        word3 = Word(text="test", pos="VB")
        word4 = Word(text="other", pos="NN")
        
        # 同じ単語と品詞の組み合わせは等しい
        self.assertEqual(word1, word2)
        
        # 異なる品詞は等しくない
        self.assertNotEqual(word1, word3)
        
        # 異なる単語は等しくない
        self.assertNotEqual(word1, word4)
        
        # 異なる型は等しくない
        self.assertNotEqual(word1, "test_NN")
    
    def test_hash(self):
        """
        ハッシュ値のテスト
        """
        word1 = Word(text="test", pos="NN")
        word2 = Word(text="test", pos="NN", count=5)
        
        # 同じ単語と品詞の組み合わせは同じハッシュ値を持つ
        self.assertEqual(hash(word1), hash(word2))
        
        # 辞書のキーとして使用できる
        word_dict = {word1: "value"}
        self.assertEqual(word_dict[word2], "value")


if __name__ == '__main__':
    unittest.main()