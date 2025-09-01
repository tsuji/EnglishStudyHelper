"""
英語学習ヘルパーのテスト実行スクリプト
"""
import os
from pathlib import Path

from src.englishstudyhelper.analyzer import analyze_file
from src.englishstudyhelper.main import load_grammar_points
from src.englishstudyhelper.reporter import generate_and_save_report, generate_full_report_with_grammar


def test_analyze_file():
    """
    テスト実行のメイン関数
    """
    # 入力ファイルと出力ファイルのパス
    input_file = 'input/text.md'
    output_file = 'output/text_report.md'
    
    print(f"テキストファイルを分析中: {input_file}")
    
    # テキストファイルを分析
    words = analyze_file(input_file)
    
    print(f"分析結果: {len(words)} 個の単語が見つかりました")
    
    # 上位10件の単語を表示
    print("\n上位10件の単語:")
    for i, word in enumerate(words[:10], 1):
        print(f"{i}. {word.text} ({word.pos}): {word.count}回")
    
    # レポートを生成して保存
    title = 'text'
    json_path = 'input/text.json'
    option = None
    grammar_points = load_grammar_points(Path(json_path))
    lines = generate_full_report_with_grammar(words, title, option, grammar_points)


    # 出力ファイルの先頭部分を表示
    for line in lines[:10]:
        print(line)


if __name__ == '__main__':
    test_analyze_file()