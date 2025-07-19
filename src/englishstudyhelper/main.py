"""
英語学習ヘルパーのメインモジュール
"""
import argparse
import os
import sys
from typing import List, Optional

from .analyzer import analyze_file
from .reporter import generate_and_save_report


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数をパースする
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description='英語学習者向けのテキスト分析ツール')
    parser.add_argument('input_file', help='分析対象のテキストファイル')
    parser.add_argument('-o', '--output', help='出力ファイルのパス (デフォルト: output.md)')
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

    # 入力ファイルのパスを取得
    input_file = parsed_args.input_file

    # 出力ファイルのパスを取得（指定されていない場合はデフォルト値を使用）
    output_file = parsed_args.output or 'output.md'

    # 設定ファイルのパスを取得
    config_path = parsed_args.config

    try:
        # 入力ファイルが存在するか確認
        if not os.path.exists(input_file):
            print(f"エラー: 入力ファイルが見つかりません: {input_file}", file=sys.stderr)
            return 1

        # 設定ファイルが指定されている場合、存在するか確認
        if config_path and not os.path.exists(config_path):
            print(f"エラー: 設定ファイルが見つかりません: {config_path}", file=sys.stderr)
            return 1

        print(f"テキストファイルを分析中: {input_file}")

        # テキストファイルを分析
        words = analyze_file(input_file)

        print(f"分析結果: {len(words)} 個の単語が見つかりました")

        # レポートを生成して保存
        generate_and_save_report(words, output_file)

        print(f"レポートを保存しました: {output_file}")

        return 0

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
