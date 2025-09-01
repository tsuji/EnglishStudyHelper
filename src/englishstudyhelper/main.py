"""
英語学習ヘルパーのメインモジュール
"""
import argparse
import os
import sys
from typing import List, Optional

from .analyzer import analyze_file
from .config import get_config
from .reporter import generate_report, save_report, generate_and_save_report, generate_and_save_verb_report


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数をパースする
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description='英語学習者向けのテキスト分析ツール')
    parser.add_argument('-i', '--input-dir', required=True, help='分析対象のテキストファイルのディレクトリ (*.md を処理)')
    parser.add_argument('-o', '--output-dir', help='出力ディレクトリ (デフォルト: output)')
    parser.add_argument('-c', '--config', help='設定ファイルのパス')

    return parser.parse_args()


def main(args: Optional[List[str]] = None) -> int:
    """
    メイン関数
    
    Args:
        args (Optional[List[str]], optional): コマンドライン引数。指定しない場合は sys.argv が使用される。
    
    Returns:
        int: 終了コード
    """

    # コマンドライン引数をパース
    parsed_args = parse_args() if args is None else parse_args(args)

    # 入力ディレクトリのパスを取得
    input_dir = parsed_args.input_dir

    # 出力ファイルのパスを取得（指定されていない場合はデフォルト値を使用）
    output_dir  = parsed_args.output_dir or 'output'
    result_file = output_dir + '/result.md'

    # 設定ファイルのパスを取得
    config_path = parsed_args.config

    try:
        # 設定ファイルが指定されている場合、存在するか確認
        if config_path and not os.path.exists(config_path):
            print(f"エラー: 設定ファイルが見つかりません: {config_path}", file=sys.stderr)
            return 1

        aggregated_rows: List[str] = []
        aggregated_words = []

        if not os.path.isdir(input_dir):
            print(f"エラー: 入力ディレクトリが見つかりません: {input_dir}", file=sys.stderr)
            return 1
        # ディレクトリ内の .md ファイルを処理
        md_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.md')]
        if not md_files:
            print(f"エラー: 指定ディレクトリに .md ファイルが見つかりません: {input_dir}", file=sys.stderr)
            return 1
        for path in sorted(md_files):
            print(f"テキストファイルを分析中: {path}")
            words = analyze_file(path)
            print(f"分析結果: {len(words)} 個の単語が見つかりました ({os.path.basename(path)})")
            aggregated_words.extend(words)
            rows = generate_report(words, '')
            aggregated_rows.extend(rows)

        # 全ファイル処理後にレポートを保存
        save_report(aggregated_rows, result_file)
        print(f"レポートを保存しました: {result_file}")
        
        # 動詞レポートを生成して保存（全入力の集計に基づく）
        config = get_config()
        verb_report_file = output_dir + '/verb_report.md'
        generate_and_save_verb_report(aggregated_words, verb_report_file)
        
        print(f"動詞レポートを保存しました: {verb_report_file}")

        return 0

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
