#!/usr/bin/env python3
"""
不足している銘柄のデータを一括生成するスクリプト
"""
import sys
import time
from pathlib import Path
from generate_json import merge_data
import json

# 不足している銘柄リスト
MISSING_STOCKS = [
    "2181", "3436", "3653", "3655", "3687", "3774", "3778", "3984", "3993",
    "4080", "4088", "4091", "4109", "4118", "4180", "4182", "4186", "4259",
    "4369", "4382", "4401", "4418", "4901", "5302", "5384", "5574", "5715",
    "6268", "6273", "6324", "6479", "6594", "6701", "6730", "6914", "8035", "8088"
]

def generate_missing_stocks(delay=2):
    """
    不足している銘柄のデータを生成
    
    Args:
        delay: 各銘柄の生成間隔(秒)
    """
    total = len(MISSING_STOCKS)
    success_count = 0
    error_count = 0
    errors = []
    
    print(f"=== 不足銘柄データ一括生成 ===")
    print(f"対象銘柄数: {total}社")
    print(f"生成間隔: {delay}秒")
    print(f"推定所要時間: {total * delay / 60:.1f}分\n")
    
    start_time = time.time()
    
    for i, code in enumerate(MISSING_STOCKS, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total}] {code} を生成中...")
        print(f"{'='*60}")
        
        try:
            # データ生成
            result = merge_data(code)
            
            if result:
                # JSONファイルに保存
                output_dir = Path(__file__).parent.parent / 'docs' / 'data'
                output_dir.mkdir(parents=True, exist_ok=True)
                
                code_for_filename = code.zfill(4)
                output_file = output_dir / f'{code_for_filename}.json'
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                success_count += 1
                print(f"\n✓ 成功: {output_file.name}")
            else:
                error_count += 1
                errors.append(f"{code}: データ生成失敗")
                print(f"\n✗ 失敗: データ生成エラー")
        
        except Exception as e:
            error_count += 1
            errors.append(f"{code}: {str(e)}")
            print(f"\n✗ エラー: {str(e)}")
        
        # 進捗表示
        elapsed = time.time() - start_time
        avg_time = elapsed / i
        remaining = (total - i) * avg_time
        print(f"\n進捗: {i}/{total} ({i/total*100:.1f}%) | 経過時間: {elapsed/60:.1f}分 | 残り時間: {remaining/60:.1f}分")
        
        # レート制限対策
        if i < total:
            print(f"\n{delay}秒待機中...")
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
    
    return success_count, error_count


if __name__ == "__main__":
    # 生成間隔を設定(デフォルト: 2秒)
    delay = 2
    if len(sys.argv) > 1:
        try:
            delay = int(sys.argv[1])
        except ValueError:
            print(f"警告: 無効な遅延時間 '{sys.argv[1]}'。デフォルト値 {delay}秒 を使用します。")
    
    # 不足銘柄データ生成
    success, errors = generate_missing_stocks(delay)
    
    if errors > 0:
        sys.exit(1)
