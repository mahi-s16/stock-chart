#!/usr/bin/env python3
"""
メモリ・ストレージテーマ用の不足銘柄データ生成
"""
import sys
import time
from pathlib import Path
from generate_json import merge_data
import json

# 不足している銘柄リスト
MISSING_STOCKS = ["6871", "3110", "6862", "2737"]

def generate_memory_stocks(delay=2):
    """メモリ・ストレージ関連の不足銘柄データを生成"""
    total = len(MISSING_STOCKS)
    success_count = 0
    error_count = 0
    errors = []
    
    print(f"=== メモリ・ストレージ銘柄データ生成 ===")
    print(f"対象銘柄数: {total}社")
    print(f"生成間隔: {delay}秒\n")
    
    start_time = time.time()
    
    for i, code in enumerate(MISSING_STOCKS, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{total}] {code} を生成中...")
        print(f"{'='*60}")
        
        try:
            result = merge_data(code)
            
            if result:
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
        
        if i < total:
            print(f"\n{delay}秒待機中...")
            time.sleep(delay)
    
    total_time = time.time() - start_time
    print("\n" + "="*60)
    print("=== 生成完了 ===")
    print(f"成功: {success_count}/{total}社")
    print(f"失敗: {error_count}社")
    print(f"所要時間: {total_time/60:.1f}分")
    
    if errors:
        print(f"\n=== エラー詳細 ===")
        for error in errors:
            print(f"  - {error}")
    
    print("="*60)
    return success_count, error_count

if __name__ == "__main__":
    success, errors = generate_memory_stocks(2)
    if errors > 0:
        sys.exit(1)
