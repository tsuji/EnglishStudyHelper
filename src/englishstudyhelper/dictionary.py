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

    def get_word_translation(self, word: str, part_of_speech: str = None, max_translations: int = None) -> Optional[str]:
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
        base_form = self._get_base_form(word, part_of_speech)
        
        # 辞書DBから翻訳を取得
        translation = self._query_dictionary(base_form)
        
        # 翻訳が見つからない場合は元の単語で再検索
        if translation is None and base_form != word:
            translation = self._query_dictionary(word)
        
        # 翻訳が見つからない場合はNoneを返す
        if translation is None:
            return None
        
        # 翻訳を"/"で分割し、指定された数だけを取得
        translations = translation.split('/')
        
        # max_translationsが0以下の場合は空文字列を返す
        if max_translations <= 0:
            return ''
            
        limited_translations = translations[:max_translations]
        
        # "/"区切りの文字列として返す
        return ' / '.join(t.strip() for t in limited_translations)

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
        # 品詞が指定されていない場合は元の単語を返す
        if part_of_speech is None:
            return word
        
        # 小文字に変換
        word = word.lower()
        
        # 名詞の複数形
        if part_of_speech in ['NNS']:
            return self._get_singular_noun(word)
        
        # 動詞の活用形
        elif part_of_speech in ['VBD', 'VBN']:  # 過去形、過去分詞
            return self._get_verb_infinitive(word)
        elif part_of_speech == 'VBG':  # 現在分詞/動名詞
            return self._get_verb_infinitive_from_ing(word)
        elif part_of_speech == 'VBZ':  # 三人称単数現在
            return self._get_verb_infinitive_from_third_person(word)
        
        # 形容詞の比較級
        elif part_of_speech == 'JJR':
            return self._get_adjective_positive(word)
        
        # 形容詞として使われている可能性のある名詞の複数形
        elif part_of_speech == 'JJ':
            # 形容詞として使われている名詞の複数形の可能性を考慮
            singular = self._get_singular_noun(word)
            if singular != word:
                return singular
        
        # それ以外の場合は元の単語を返す
        return word
    
    def _get_singular_noun(self, word: str) -> str:
        """
        名詞の複数形から単数形を取得する

        Args:
            word (str): 名詞の複数形

        Returns:
            str: 名詞の単数形。変換できない場合は元の単語を返す。
        """
        # 不規則変化の複数形
        irregular_plurals = {
            'men': 'man',
            'women': 'woman',
            'children': 'child',
            'people': 'person',
            'mice': 'mouse',
            'feet': 'foot',
            'teeth': 'tooth',
            'geese': 'goose',
            'oxen': 'ox',
            'leaves': 'leaf',
            'lives': 'life',
            'knives': 'knife',
            'wolves': 'wolf',
            'shelves': 'shelf',
            'thieves': 'thief',
            'potatoes': 'potato',
            'tomatoes': 'tomato',
            'heroes': 'hero',
            'echoes': 'echo',
            'data': 'datum',
            'criteria': 'criterion',
            'phenomena': 'phenomenon'
        }
        
        # 不規則変化の複数形をチェック
        if word in irregular_plurals:
            return irregular_plurals[word]
        
        # 規則変化の複数形
        if word.endswith('ies') and len(word) > 3:
            return word[:-3] + 'y'  # flies -> fly
        elif word.endswith('es') and word[-3] in ['s', 'x', 'z', 'h']:
            return word[:-2]  # boxes -> box, dishes -> dish
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1]  # cats -> cat
        
        # 変換できない場合は元の単語を返す
        return word
    
    def _get_verb_infinitive(self, word: str) -> str:
        """
        動詞の過去形または過去分詞から原形を取得する

        Args:
            word (str): 動詞の過去形または過去分詞

        Returns:
            str: 動詞の原形。変換できない場合は元の単語を返す。
        """
        # 不規則変化の動詞
        irregular_verbs = {
            'was': 'be', 'were': 'be', 'been': 'be',
            'had': 'have',
            'did': 'do', 'done': 'do',
            'said': 'say',
            'made': 'make',
            'went': 'go', 'gone': 'go',
            'took': 'take', 'taken': 'take',
            'came': 'come',
            'saw': 'see', 'seen': 'see',
            'gave': 'give', 'given': 'give',
            'knew': 'know', 'known': 'know',
            'got': 'get', 'gotten': 'get',
            'found': 'find',
            'thought': 'think',
            'told': 'tell',
            'became': 'become',
            'left': 'leave',
            'felt': 'feel',
            'brought': 'bring',
            'began': 'begin', 'begun': 'begin',
            'kept': 'keep',
            'held': 'hold',
            'wrote': 'write', 'written': 'write',
            'ran': 'run',
            'met': 'meet',
            'sat': 'sit',
            'spoke': 'speak', 'spoken': 'speak',
            'stood': 'stand',
            'lost': 'lose',
            'paid': 'pay',
            'heard': 'hear',
            'meant': 'mean',
            'set': 'set',
            'learned': 'learn', 'learnt': 'learn',
            'changed': 'change',
            'led': 'lead',
            'understood': 'understand',
            'watched': 'watch'
        }
        
        # 不規則変化の動詞をチェック
        if word in irregular_verbs:
            return irregular_verbs[word]
        
        # 規則変化の動詞
        if word.endswith('ed') and len(word) > 2:
            if word.endswith('ied') and len(word) > 3:
                return word[:-3] + 'y'  # tried -> try
            elif word[-3] == word[-4] and word[-3] not in ['a', 'e', 'i', 'o', 'u']:
                return word[:-3]  # stopped -> stop
            else:
                return word[:-2]  # played -> play
        
        # 変換できない場合は元の単語を返す
        return word
    
    def _get_verb_infinitive_from_ing(self, word: str) -> str:
        """
        動詞の現在分詞/動名詞から原形を取得する

        Args:
            word (str): 動詞の現在分詞/動名詞

        Returns:
            str: 動詞の原形。変換できない場合は元の単語を返す。
        """
        # 不規則変化の動詞
        irregular_ing_verbs = {
            'being': 'be',
            'having': 'have',
            'doing': 'do',
            'saying': 'say',
            'making': 'make',
            'going': 'go',
            'taking': 'take',
            'coming': 'come',
            'seeing': 'see',
            'giving': 'give',
            'knowing': 'know',
            'getting': 'get',
            'finding': 'find',
            'thinking': 'think',
            'telling': 'tell',
            'becoming': 'become',
            'leaving': 'leave',
            'feeling': 'feel',
            'bringing': 'bring',
            'beginning': 'begin',
            'keeping': 'keep',
            'holding': 'hold',
            'writing': 'write',
            'running': 'run',
            'meeting': 'meet',
            'sitting': 'sit',
            'speaking': 'speak',
            'standing': 'stand',
            'losing': 'lose',
            'paying': 'pay',
            'hearing': 'hear',
            'meaning': 'mean',
            'setting': 'set',
            'learning': 'learn',
            'changing': 'change',
            'leading': 'lead',
            'understanding': 'understand',
            'watching': 'watch',
            'playing': 'play',
            'moving': 'move',
            'living': 'live',
            'believing': 'believe',
            'showing': 'show',
            'trying': 'try',
            'asking': 'ask',
            'working': 'work',
            'seeming': 'seem',
            'calling': 'call',
            'looking': 'look'
        }
        
        # 不規則変化の動詞をチェック
        if word in irregular_ing_verbs:
            return irregular_ing_verbs[word]
        
        # 規則変化の動詞
        if word.endswith('ing'):
            if len(word) > 4 and word[-4] == word[-5] and word[-4] not in ['a', 'e', 'i', 'o', 'u']:
                return word[:-4]  # running -> run
            elif len(word) > 3 and word[-4] == 'y':
                return word[:-3]  # dying -> die
            elif len(word) > 3:
                return word[:-3]  # playing -> play
        
        # 変換できない場合は元の単語を返す
        return word
    
    def _get_verb_infinitive_from_third_person(self, word: str) -> str:
        """
        動詞の三人称単数現在形から原形を取得する

        Args:
            word (str): 動詞の三人称単数現在形

        Returns:
            str: 動詞の原形。変換できない場合は元の単語を返す。
        """
        # 不規則変化の動詞
        irregular_third_person = {
            'is': 'be',
            'has': 'have',
            'does': 'do',
            'says': 'say',
            'goes': 'go'
        }
        
        # 不規則変化の動詞をチェック
        if word in irregular_third_person:
            return irregular_third_person[word]
        
        # 規則変化の動詞
        if word.endswith('ies') and len(word) > 3:
            return word[:-3] + 'y'  # flies -> fly
        elif word.endswith('es') and word[-3] in ['s', 'x', 'z', 'h']:
            return word[:-2]  # boxes -> box, dishes -> dish
        elif word.endswith('s') and not word.endswith('ss'):
            return word[:-1]  # plays -> play
        
        # 変換できない場合は元の単語を返す
        return word
    
    def _get_adjective_positive(self, word: str) -> str:
        """
        形容詞の比較級から原級を取得する

        Args:
            word (str): 形容詞の比較級

        Returns:
            str: 形容詞の原級。変換できない場合は元の単語を返す。
        """
        # 不規則変化の形容詞
        irregular_comparatives = {
            'better': 'good',
            'worse': 'bad',
            'more': 'many',
            'less': 'little',
            'older': 'old',
            'elder': 'old'
        }
        
        # 不規則変化の形容詞をチェック
        if word in irregular_comparatives:
            return irregular_comparatives[word]
        
        # 規則変化の形容詞
        if word.endswith('er'):
            if len(word) > 3 and word[-3] == word[-4] and word[-3] not in ['a', 'e', 'i', 'o', 'u']:
                return word[:-3]  # bigger -> big
            elif len(word) > 2 and word[-3] == 'i':
                return word[:-3] + 'y'  # happier -> happy
            elif len(word) > 2:
                return word[:-2]  # smaller -> small
        
        # 変換できない場合は元の単語を返す
        return word
    
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