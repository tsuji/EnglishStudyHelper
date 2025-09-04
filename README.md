# English Study Helper

英語初学者向けのテキスト分析ツール。英語の絵本や簡単なテキストを分析し、頻出単語とその品詞、意味、例文を表形式で出力します。

## 機能

- テキストファイルから単語を抽出し、品詞を判定
- 単語の出現回数をカウント
- 頻出単語を表形式でレポート出力
  - 固有名詞、前置詞、冠詞、代名詞、助動詞、be動詞は除外
  - 単語ごとに日本語の意味と例文を表示
- 辞書検索機能
  - 単語の日本語訳を取得
  - 訳語を"/"区切りで分割し、指定された数だけを"/"区切りで返す
  - 単語の原型を推測して検索（名詞の複数形、動詞の活用形、形容詞の比較級など）

## インストール方法

### 前提条件

- Python 3.13以上
- パッケージマネージャ: uv（uvw）
  - 参考: https://docs.astral.sh/uv/

### インストール手順（uv）

1. リポジトリをクローン

```bash
git clone https://github.com/tsuji/EnglishStudyHelper.git
cd EnglishStudyHelper
```

2. 依存関係を同期（pyproject.toml と uv.lock を使用）

```bash
uv sync
```

3. コマンドの実行（仮想環境経由）

```bash
uv run englishstudyhelper --help
```

開発用途でこのリポジトリを編集可能インストールしたい場合は、次のどちらかを利用できます：

```bash
# 開発環境を作成し、パッケージを編集可能インストール
uv pip install -e .

# もしくは uvx によりスクリプトを直接呼び出し
uv run englishstudyhelper input/text.md
```

これらにより、`englishstudyhelper`コマンドを uv 管理の環境で利用できます。

## 使い方

### コマンドライン

```bash
# 基本的な使い方（uv 経由、モジュール指定）
uv run python -m src.englishstudyhelper.main -i input -o output

# 単一ファイルを指定して分析
uv run python -m src.englishstudyhelper.main -i input/text.md -o output

# 設定ファイルを指定
uv run python -m src.englishstudyhelper.main -i input -o output -c config/custom_settings.json
```

### Pythonコードから使用

```python
from englishstudyhelper.analyzer import analyze_file
from englishstudyhelper.reporter import generate_and_save_report
from englishstudyhelper.dictionary import get_dictionary

# テキストファイルを分析
words = analyze_file('input/text.md')

# レポートを生成して保存
generate_and_save_report(words, 'output/result.md')

# 辞書検索機能を使用
dictionary = get_dictionary()

# 単語の翻訳を取得（デフォルトで最大3つの訳語を返す）
translation = dictionary.get_word_translation('book')
print(translation)

# 最大2つの訳語を指定して取得
translation = dictionary.get_word_translation('book', max_translations=2)
print(translation)

# 品詞を指定して原型推測を使用
translation = dictionary.get_word_translation('running', part_of_speech='VBG')
print(translation)  # 'run'の訳語が返される
```

## プロジェクト構造

```
EnglishStudyHelper/
├── config/                  # 設定ファイル
│   └── settings.json       # デフォルト設定
├── input/                   # 入力テキストファイル
│   ├── text.md             # サンプルテキスト
│   └── text.json           # 文法ポイント解説（任意）
├── src/                     # ソースコード
│   └── englishstudyhelper/
│       ├── __init__.py
│       ├── analyzer.py     # テキスト分析機能
│       ├── config.py       # 設定ファイル読み込み
│       ├── main.py         # メインエントリーポイント
│       ├── reporter.py     # レポート生成機能
│       └── word.py         # 単語クラス
├── tests/                   # テストコード
│   ├── test_analyzer.py
│   ├── test_config.py
│   ├── test_reporter.py
│   └── test_word.py
├── pyproject.toml          # プロジェクト設定
└── README.md               # このファイル
```

## 設定ファイル

設定ファイル（`config/settings.json`）では以下の項目をカスタマイズできます：

- `exclude_pos`: 除外する品詞タグのリスト
- `be_verbs`: 除外するbe動詞のリスト
- `pos_translations`: 品詞タグの日本語訳
- `word_translations`: 単語の日本語訳
- `dictionary`: 辞書検索機能の設定
  - `max_translations`: 返す訳語の最大数（デフォルト: 3）

例：

```json
{
    "exclude_pos": [
        "NNP", "NNPS",
        "IN",
        "DT",
        "PRP", "PRP$",
        "MD",
        "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"
    ],
    "be_verbs": ["be", "am", "is", "are", "was", "were", "been", "being"],
    "pos_translations": {
        "NN": "名詞",
        "NNS": "名詞(複数形)"
    },
    "word_translations": {
        "rabbit": "ウサギ",
        "test": "テスト"
    },
    "dictionary": {
        "max_translations": 3
    }
}
```

## 入力ファイルの形式

本ツールは以下の2種類の入力を扱います。いずれも同じベース名（拡張子違い）で揃えると、文法ポイントが自動で紐づきます。

1. 本文テキストのMarkdownファイル（.md）
   - 場所: input/ ディレクトリ配下
   - 例: input/Going on a Plane.md（著作物のため内容は本READMEに転載しません）
   - 記述ルールの目安:
     - 通常の英文テキストを段落として記述（見出しや箇条書きが含まれても可）
     - 句読点・改行は自由。改行で段落を分けると分析の単位が分かりやすくなります。
   - サンプル（任意の短い例）:
     ```markdown
     # Sample Story
     Anna and Sam are at the airport. They look at the big planes.
     "Let's find our seats," Anna says. Sam smiles and carries his bag.
     ```

2. 文法ポイント解説のJSONファイル（.json）
   - 場所: input/ ディレクトリ配下
   - 本文と同じベース名で作成します（例: Going on a Plane.md に対して Going on a Plane.json）。
   - 構造: オブジェクトの配列。各要素は次のフィールドを推奨します。
     - no: 連番（文字列または数値）
     - title: 文法ポイントの見出し
     - eng: 例文（英語）
     - form: 形（パターン）
     - exp: 解説文の配列（箇条書き）
     - jpn: 日本語訳
   - サンプル:
     ```json
     [
       {
         "no": "1",
         "title": "現在進行形",
         "eng": "They are waiting at the gate.",
         "form": "be + 動詞ing",
         "exp": [
           "be動詞 + 動詞ing で進行中の動作を表す",
           "文脈によって近い未来の予定を表すこともある"
         ],
         "jpn": "彼らはゲートで待っている。"
       },
       {
         "no": "2",
         "title": "Let's + 動詞の原形",
         "eng": "Let's find our seats.",
         "form": "let's + 動詞の原形",
         "exp": [
           "提案・勧誘の表現",
           "会話文で頻出"
         ],
         "jpn": "席を探そう。"
       }
     ]
     ```

解析時の対応関係:
- ディレクトリを指定した場合（-i input）、input 内の .md をすべて処理し、同名の .json が存在すれば自動で読み込んでレポートに反映します。
- 単一の .md を指定した場合（-i input/text.md）も、同ディレクトリ内の同名 .json を探索します。

## 出力例

```
| 語句             | 出現回数 | 意味・説明             | 品詞             | 例文                                                         |
|-----------------|----------|------------------------|------------------|--------------------------------------------------------------|
| rabbit          | 5        | ウサギ                 | 名詞             | The rabbit felt soft.                                        |
| play            | 3        | 遊ぶ、演奏する         | 動詞             | Kipper went to play with Anna.                              |
| test            | 2        | テスト                 | 名詞             | This is a test.                                              |
```

## テスト実行方法

```bash
# 依存関係を同期（未実施の場合）
uv sync

# すべてのテストを実行（unittest）
uv run python -m unittest discover tests

# 特定のテストを実行
uv run python -m unittest tests/test_word.py
```

## 品詞タグについて

このツールではNLTKの品詞タグを使用しています。主な品詞タグは以下の通りです：

- `NN`: 名詞（単数）
- `NNS`: 名詞（複数）
- `NNP`: 固有名詞（単数）
- `NNPS`: 固有名詞（複数）
- `VB`: 動詞（原形）
- `VBD`: 動詞（過去形）
- `VBG`: 動詞（現在分詞/動名詞）
- `VBN`: 動詞（過去分詞）
- `VBP`: 動詞（現在形）
- `VBZ`: 動詞（三人称単数現在）
- `JJ`: 形容詞
- `JJR`: 形容詞（比較級）
- `JJS`: 形容詞（最上級）
- `RB`: 副詞
- `IN`: 前置詞
- `DT`: 冠詞
- `PRP`: 代名詞

## 同梱/再配布しているライブラリ

本プロジェクトは以下のライブラリ／データを同梱し再配布しています。

1. 英和辞書データ『ejdict-hand』（配布版）/ ejdic-hand-sqlite
   - ライセンス: パブリックドメイン / Public Domain / CC0
   - 配布元: くじらはんど > Web便利ツール > 英和辞書データ
   - URL: https://kujirahand.com/web-tools/EJDictFreeDL.php
   - 同梱物: ejdic-hand-sqlite/ejdict.sqlite3, ejdic-hand-sqlite/ddl.sql, ejdic-hand-sqlite/README.txt

2. Module to manage inflections of English words（英単語活用管理モジュール）
   - Copyright 2022 Mikio Hirabayashi
   - License: Apache License, Version 2.0
   - 参考: https://mikio.hatenablog.com/entry/2023/01/23/202321
   - 同梱物: src/english_inflections/english_inflections.py, src/english_inflections/english_inflections.tsv

## ライセンス

- 本リポジトリのオリジナルコードは MIT ライセンスで提供します。
- 上記の同梱物のうち、
  - ejdict-hand（ejdic-hand-sqlite）は パブリックドメイン/CC0 に従います。
  - english_inflections モジュールは Apache License 2.0 に従います。
- それぞれのライセンス条件は該当ディレクトリに含まれるファイルおよび上記リンクを参照してください。

NOTICE (for the Apache-2.0 component):

Copyright 2022 Mikio Hirabayashi
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## 貢献

バグ報告や機能リクエストは、GitHubのIssueトラッカーにお願いします。プルリクエストも歓迎します。