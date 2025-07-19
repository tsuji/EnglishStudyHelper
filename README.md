# English Study Helper

英語初学者向けのテキスト分析ツール。英語の絵本や簡単なテキストを分析し、頻出単語とその品詞、意味、例文を表形式で出力します。

## 機能

- テキストファイルから単語を抽出し、品詞を判定
- 単語の出現回数をカウント
- 頻出単語を表形式でレポート出力
  - 固有名詞、前置詞、冠詞、代名詞、助動詞、be動詞は除外
  - 単語ごとに日本語の意味と例文を表示

## インストール方法

### 前提条件

- Python 3.13以上
- pipパッケージマネージャ

### インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/yourusername/EnglishStudyHelper.git
cd EnglishStudyHelper
```

2. パッケージをインストール

```bash
pip install -e .
```

これにより、`englishstudyhelper`コマンドがシステムに追加されます。

## 使い方

### コマンドライン

```bash
# 基本的な使い方
englishstudyhelper input/text.md

# 出力ファイルを指定
englishstudyhelper input/text.md -o output/result.md

# 設定ファイルを指定
englishstudyhelper input/text.md -c config/custom_settings.json
```

### Pythonコードから使用

```python
from englishstudyhelper.analyzer import analyze_file
from englishstudyhelper.reporter import generate_and_save_report

# テキストファイルを分析
words = analyze_file('input/text.md')

# レポートを生成して保存
generate_and_save_report(words, 'output/result.md')
```

## 設定ファイル

設定ファイル（`config/settings.json`）では以下の項目をカスタマイズできます：

- `exclude_pos`: 除外する品詞タグのリスト
- `be_verbs`: 除外するbe動詞のリスト
- `pos_translations`: 品詞タグの日本語訳
- `word_translations`: 単語の日本語訳

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
    }
}
```

## 出力例

```
| 語句             | 出現回数 | 意味・説明             | 品詞             | 例文                                                         |
|-----------------|----------|------------------------|------------------|--------------------------------------------------------------|
| rabbit          | 5        | ウサギ                 | 名詞             | The rabbit felt soft.                                        |
| play            | 3        | 遊ぶ、演奏する         | 動詞             | Kipper went to play with Anna.                              |
| test            | 2        | テスト                 | 名詞             | This is a test.                                              |
```

## プロジェクト構造

```
EnglishStudyHelper/
├── config/                  # 設定ファイル
│   └── settings.json       # デフォルト設定
├── input/                   # 入力テキストファイル
│   └── text.md             # サンプルテキスト
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

## テスト実行方法

```bash
# すべてのテストを実行
python -m unittest discover tests

# 特定のテストを実行
python -m unittest tests/test_word.py
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

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能リクエストは、GitHubのIssueトラッカーにお願いします。プルリクエストも歓迎します。