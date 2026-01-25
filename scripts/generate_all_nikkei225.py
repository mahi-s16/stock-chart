"""
日経225全銘柄データ一括生成スクリプト
日経225構成銘柄のデータを一括で生成します
"""
import json
import sys
import time
from pathlib import Path
from generate_json import merge_data

def load_nikkei225_stocks():
    """
    日経225銘柄リストを読み込み
    
    Returns:
        銘柄リスト
    """
    script_dir = Path(__file__).parent
    stocks_file = script_dir / 'nikkei225_stocks.json'
    
    with open(stocks_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data['stocks']


def generate_all_stocks(stocks, delay=2):
    """
    全銘柄のデータを一括生成
    
    Args:
        stocks: 銘柄リスト
        delay: 各銘柄の生成間隔(秒)
    """
    total = len(stocks)
    success_count = 0
    error_count = 0
    errors = []
    
    print(f"=== 日経225銘柄データ一括生成 ===")
    print(f"対象銘柄数: {total}社")
    print(f"生成間隔: {delay}秒")
    print(f"推定所要時間: {total * delay / 60:.1f}分\n")
    
    start_time = time.time()
    
    for i, stock in enumerate(stocks, 1):
        code = stock['code']
        name = stock['name']
        
        print(f"[{i}/{total}] {name} ({code}) を生成中...")
        
        try:
            # データ生成
            result = merge_data(code)
            
            if result:
                # JSONファイルに保存
                output_dir = Path(__file__).parent.parent / 'docs' / 'data'
                output_dir.mkdir(parents=True, exist_ok=True)
                
                code_for_filename = code.replace('.T', '')
                if code_for_filename.isdigit():
                    code_for_filename = code_for_filename.zfill(4)
                output_file = output_dir / f'{code_for_filename}.json'
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                success_count += 1
                print(f"  ✓ 成功: {output_file.name}")
            else:
                error_count += 1
                errors.append(f"{name} ({code}): データ生成失敗")
                print(f"  ✗ 失敗: データ生成エラー")
        
        except Exception as e:
            error_count += 1
            errors.append(f"{name} ({code}): {str(e)}")
            print(f"  ✗ エラー: {str(e)}")
        
        # 進捗表示
        elapsed = time.time() - start_time
        avg_time = elapsed / i
        remaining = (total - i) * avg_time
        print(f"  進捗: {i}/{total} ({i/total*100:.1f}%) | 経過時間: {elapsed/60:.1f}分 | 残り時間: {remaining/60:.1f}分\n")
        
        # レート制限対策
        if i < total:
            time.sleep(delay)
    
    # 結果サマリー
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("=== 生成完了 ===")
    print(f"総銘柄数: {total}社")
    print(f"成功: {success_count}社")
    print(f"失敗: {error_count}社")
    print(f"所要時間: {total_time/60:.1f}分")
    
    if errors:
        print(f"\n=== エラー詳細 ===")
        for error in errors:
            print(f"  - {error}")
    
    print("="*60)


if __name__ == "__main__":
    # 銘柄リスト読み込み
    stocks = load_nikkei225_stocks()
    
    # 生成間隔を設定(デフォルト: 2秒)
    delay = 2
    if len(sys.argv) > 1:
        try:
            delay = int(sys.argv[1])
        except ValueError:
            print(f"警告: 無効な遅延時間 '{sys.argv[1]}'。デフォルト値 {delay}秒 を使用します。")
    
    # 全銘柄データ生成
    generate_all_stocks(stocks, delay)
