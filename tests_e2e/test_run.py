"""
英語学習ヘルパーのテスト実行スクリプト
"""
import os
from src.englishstudyhelper.analyzer import analyze_file
from src.englishstudyhelper.reporter import generate_and_save_report

def main():
    """
    テスト実行のメイン関数
    """
    # 入力ファイルと出力ファイルのパス
    input_file = 'input/text.md'
    output_file = 'output/result.md'
    
    print(f"テキストファイルを分析中: {input_file}")
    
    # テキストファイルを分析
    words = analyze_file(input_file)
    
    print(f"分析結果: {len(words)} 個の単語が見つかりました")
    
    # 上位10件の単語を表示
    print("\n上位10件の単語:")
    for i, word in enumerate(words[:10], 1):
        print(f"{i}. {word.text} ({word.pos}): {word.count}回")
    
    # レポートを生成して保存
    generate_and_save_report(words, output_file)
    
    print(f"\nレポートを保存しました: {output_file}")
    
    # 出力ファイルの先頭部分を表示
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read(500)  # 最初の500文字を読み込む
            print("\nレポート内容のプレビュー:")
            print("-" * 80)
            print(content)
            print("-" * 80)
    
    return 0

if __name__ == '__main__':
    main()