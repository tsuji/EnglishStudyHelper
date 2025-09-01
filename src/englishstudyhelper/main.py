"""
英語学習ヘルパーのメインモジュール
"""
import argparse
import os
import sys
from typing import List, Optional

from .analyzer import analyze_file
from .config import get_config
from .reporter import generate_full_report, save_full_report


def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数をパースする
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description='英語学習者向けのテキスト分析ツール')
    parser.add_argument('-i', '--input', required=True, help='分析対象: ディレクトリまたは単一ファイル (.md)')
    parser.add_argument('-o', '--output', help='出力ディレクトリ (デフォルト: output)')
    parser.add_argument('-c', '--config', help='設定ファイルのパス')
    parser.add_argument('--option', help='オプション (例: no_translation)')

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

    # 入力のパスを取得（ファイルまたはディレクトリ）
    input_path = parsed_args.input

    # 出力ディレクトリのパスを取得（指定されていない場合はデフォルト値を使用）
    output_dir  = parsed_args.output or 'output'
    option = parsed_args.option or ''

    # 設定ファイルのパスを取得
    config_path = parsed_args.config

    try:
        # 設定ファイルが指定されている場合、存在するか確認
        if config_path and not os.path.exists(config_path):
            print(f"エラー: 設定ファイルが見つかりません: {config_path}", file=sys.stderr)
            return 1

        # 出力ディレクトリを作成（存在しない場合作成）
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        targets: List[str] = []
        if os.path.isdir(input_path):
            # ディレクトリ内の .md ファイルを処理
            md_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.lower().endswith('.md')]
            if not md_files:
                print(f"エラー: 指定ディレクトリに .md ファイルが見つかりません: {input_path}", file=sys.stderr)
                return 1
            targets = sorted(md_files)
        else:
            # 単一ファイルとして処理
            if not os.path.exists(input_path):
                print(f"エラー: 入力ファイルが見つかりません: {input_path}", file=sys.stderr)
                return 1
            if not input_path.lower().endswith('.md'):
                print(f"エラー: 入力ファイルは .md である必要があります: {input_path}", file=sys.stderr)
                return 1
            targets = [input_path]

        # 各ファイルを独立解析し、レポートを保存
        for path in targets:
            print(f"テキストファイルを分析中: {path}")
            words = analyze_file(path)
            title = os.path.splitext(os.path.basename(path))[0]
            lines = generate_full_report(words, title, option)
            output_path = os.path.join(output_dir, f"{title}_report.md")
            save_full_report(lines, output_path)
            print(f"レポートを保存しました: {output_path}")

        return 0

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
