"""
単語とその品詞を表現するクラス
"""
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class Word:
    """
    単語とその品詞を表現するクラス
    
    Attributes:
        text (str): 単語のテキスト
        pos (str): 品詞タグ (NLTKのPOSタグ)
        count (int): 出現回数
        examples (List[str]): 単語が使用されている例文のリスト
    """
    text: str
    pos: str
    count: int = 0
    examples: List[str] = None
    
    def __post_init__(self):
        """
        初期化後の処理
        """
        if self.examples is None:
            self.examples = []
    
    def add_example(self, example: str) -> None:
        """
        例文を追加する
        
        Args:
            example (str): 追加する例文
        """
        if example not in self.examples:
            self.examples.append(example)
    
    def increment_count(self) -> None:
        """
        出現回数をインクリメントする
        """
        self.count += 1
    
    def get_key(self) -> str:
        """
        単語と品詞の組み合わせを一意に識別するキーを取得する
        
        Returns:
            str: 単語と品詞の組み合わせを表す文字列
        """
        return f"{self.text.lower()}_{self.pos}"
    
    def __eq__(self, other):
        """
        等価比較
        
        Args:
            other: 比較対象
            
        Returns:
            bool: 単語と品詞が同じであれば True
        """
        if not isinstance(other, Word):
            return False
        return self.get_key() == other.get_key()
    
    def __hash__(self):
        """
        ハッシュ値を取得する
        
        Returns:
            int: ハッシュ値
        """
        return hash(self.get_key())