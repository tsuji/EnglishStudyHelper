"""
設定ファイルを読み込むためのモジュール
"""
import json
import os
from typing import Dict, List, Any, Optional


class Config:
    """
    設定ファイルを読み込み、アクセスするためのクラス
    """
    
    def __init__(self, config_path: str = None):
        """
        コンフィグを初期化する
        
        Args:
            config_path (str, optional): 設定ファイルのパス。指定しない場合はデフォルトのパスを使用する。
        """
        if config_path is None:
            # デフォルトのパスを使用
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(base_dir, 'config', 'settings.json')
        
        self.config_path = config_path
        self.config_data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        設定ファイルを読み込む
        
        Returns:
            Dict[str, Any]: 設定データ
        
        Raises:
            FileNotFoundError: 設定ファイルが見つからない場合
            json.JSONDecodeError: 設定ファイルのJSONが不正な場合
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"設定ファイルのJSONが不正です: {e.msg}", e.doc, e.pos)
    
    def get_exclude_pos(self) -> List[str]:
        """
        除外する品詞タグのリストを取得する
        
        Returns:
            List[str]: 除外する品詞タグのリスト
        """
        return self.config_data.get('exclude_pos', [])
    
    def get_be_verbs(self) -> List[str]:
        """
        be動詞のリストを取得する
        
        Returns:
            List[str]: be動詞のリスト
        """
        return self.config_data.get('be_verbs', [])
    
    def get_pos_translation(self, pos: str) -> str:
        """
        品詞タグの日本語訳を取得する
        
        Args:
            pos (str): 品詞タグ
        
        Returns:
            str: 品詞タグの日本語訳。翻訳が見つからない場合は品詞タグをそのまま返す。
        """
        pos_translations = self.config_data.get('pos_translations', {})
        return pos_translations.get(pos, pos)
    
    def get_word_translation(self, word: str) -> Optional[str]:
        """
        単語の日本語訳を取得する
        
        Args:
            word (str): 単語
        
        Returns:
            Optional[str]: 単語の日本語訳。翻訳が見つからない場合は None を返す。
        """
        word_translations = self.config_data.get('word_translations', {})
        return word_translations.get(word.lower())
    
    def should_exclude_word(self, word: str, pos: str) -> bool:
        """
        単語を除外すべきかどうかを判定する
        
        Args:
            word (str): 単語
            pos (str): 品詞タグ
        
        Returns:
            bool: 除外すべき場合は True
        """
        # 品詞が除外リストに含まれる場合
        if pos in self.get_exclude_pos():
            return True
        
        # be動詞の場合
        if word.lower() in self.get_be_verbs():
            return True
        
        return False


# シングルトンインスタンス
_config_instance = None


def get_config(config_path: str = None) -> Config:
    """
    設定インスタンスを取得する
    
    Args:
        config_path (str, optional): 設定ファイルのパス。指定しない場合はデフォルトのパスを使用する。
    
    Returns:
        Config: 設定インスタンス
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance