"""
辞書検索機能を提供するモジュール

このモジュールは、英単語の日本語訳を取得する機能を提供します。
以下の機能があります：
- 単語の日本語訳を取得する
- 訳語を"/"区切りで分割し、指定された数だけを"/"区切りで返す
- 単語の原型を推測して検索する（名詞の複数形、動詞の活用形、形容詞の比較級など）
"""
import os
import sqlite3
from typing import Optional

from src.english_inflections.english_inflections import Inflector
from .config import get_config


class Dictionary:
    """
    辞書検索機能を提供するクラス
    """

    def __init__(self, db_path: str = None):
        """
        辞書を初期化する

        Args:
            db_path (str, optional): 辞書データベースのパス。指定しない場合はデフォルトのパスを使用する。
        """
        if db_path is None:
            # デフォルトのパスを使用
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            db_path = os.path.join(base_dir, 'ejdic-hand-sqlite', 'ejdict.sqlite3')

        self.db_path = db_path

        # Inflectorの初期化
        self.inflector = Inflector('src/english_inflections/english_inflections.tsv')

    def get_word_translation(self, word: str, part_of_speech: str = None, max_translations: int = None) -> Optional[
        str]:
        """
        単語の日本語訳を取得する

        Args:
            word (str): 単語
            part_of_speech (str, optional): 品詞。指定すると原型推測に使用される。
            max_translations (int, optional): 返す訳語の最大数。指定しない場合は設定ファイルの値を使用する。

        Returns:
            Optional[str]: 単語の日本語訳。翻訳が見つからない場合は None を返す。
                          訳語が複数ある場合は、指定された数だけを"/"区切りで返す。
        """
        # max_translationsが指定されていない場合は設定ファイルから取得
        if max_translations is None:
            max_translations = get_config().get_max_translations()
        # 単語を小文字に変換
        word = word.lower()

        # 原型を推測
        searched = self.inflector.Search(word)
        if searched and searched[0][0]:
            base_form = searched[0][0]
        else:
            print("Inflector failed for word: " + word + ", part_of_speech: " + str(part_of_speech))
            base_form = word

        # 辞書DBから翻訳を取得
        translation = self._query_dictionary(base_form)

        # 翻訳が見つからない場合は元の単語で再検索
        if translation is None and base_form != word:
            translation = self._query_dictionary(word)

        # 翻訳が見つからない場合はNoneを返す
        if translation is None:
            return None

        # max_translationsの処理: 0以下なら空文字、正ならその数までに整形
        try:
            mt = int(max_translations) if max_translations is not None else int(get_config().get_max_translations())
        except Exception:
            mt = get_config().get_max_translations()
        if mt is not None:
            if mt <= 0:
                return ''
            # 訳語を"/"で分割し、トリムして再結合
            parts = [p.strip() for p in translation.split('/')]
            # 空要素を除去
            parts = [p for p in parts if p]
            translation = ' / '.join(parts[:mt])

        # 100文字以上の翻訳は切り捨てる(末尾に"..."を追加)
        if len(translation) > 100:
            translation = translation[:100] + "..."

        return translation

    def _query_dictionary(self, word: str) -> Optional[str]:
        """
        辞書DBから単語の翻訳を取得する

        Args:
            word (str): 単語

        Returns:
            Optional[str]: 単語の日本語訳。翻訳が見つからない場合は None を返す。

        Note:
            この関数は純粋関数ではなく、DBアクセスという副作用を持つ。
            しかし、外部から直接呼び出されることはなく、get_word_translationから呼び出される。
        """
        try:
            # DBに接続
            conn = self._get_connection()

            # カーソルを取得
            cursor = conn.cursor()

            # 単語を検索
            cursor.execute("SELECT mean FROM items WHERE word = ?", (word,))

            # 結果を取得
            result = cursor.fetchone()

            # 接続を閉じる
            conn.close()

            # 結果があれば翻訳を返す、なければNoneを返す
            return result[0] if result else None

        except sqlite3.Error:
            # DBエラーが発生した場合はNoneを返す
            return None

    def _get_base_form(self, word: str, part_of_speech: str = None) -> str:
        """
        単語の原型を推測する

        Args:
            word (str): 単語
            part_of_speech (str, optional): 品詞

        Returns:
            str: 推測された原型。推測できない場合は元の単語を返す。
        """
        searched = self.inflector.Search(word)
        if searched and searched[0][0]:
            base_form = searched[0][0]
        else:
            raise ValueError("Inflector failed for word: " + word)

        # それ以外の場合は元の単語を返す
        return base_form

    def _get_connection(self) -> sqlite3.Connection:
        """
        SQLite3データベースへの接続を取得する

        Returns:
            sqlite3.Connection: データベース接続

        Raises:
            sqlite3.Error: データベース接続に失敗した場合
        """
        return sqlite3.connect(self.db_path)


# シングルトンインスタンス
_dictionary_instance = None


def get_dictionary(db_path: str = None) -> Dictionary:
    """
    辞書インスタンスを取得する

    Args:
        db_path (str, optional): 辞書データベースのパス。指定しない場合はデフォルトのパスを使用する。

    Returns:
        Dictionary: 辞書インスタンス
    """
    global _dictionary_instance
    if _dictionary_instance is None:
        _dictionary_instance = Dictionary(db_path)
    return _dictionary_instance
