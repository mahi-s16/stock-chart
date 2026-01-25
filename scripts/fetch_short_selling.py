"""
機関空売りデータ取得スクリプト
JPX公式サイトから機関空売り残高報告データを取得
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import sys
import re


def fetch_short_selling_data(stock_code: str) -> pd.DataFrame:
    """
    JPXから機関空売りデータを取得
    
    Args:
        stock_code: 銘柄コード (4桁)
    
    Returns:
        機関空売りデータのDataFrame
    """
    try:
        # 銘柄コードを正規化
        stock_code = stock_code.replace('.T', '')
        if stock_code.isdigit():
            stock_code = stock_code.zfill(4)
        
        print(f"Fetching short selling data for {stock_code}...")
        
        # JPXの空売り残高報告URL
        # 注: 実際のURLは変更される可能性があります
        url = "https://www.jpx.co.jp/markets/statistics-equities/short-selling/index.html"
        
        # ここでは簡易的な実装として、サンプルデータを生成
        # 実際の実装では、JPXのAPIまたはスクレイピングを使用
        print("Note: Using sample data. Implement actual JPX scraping for production.")
        
        # サンプルデータ生成 (過去1年分の日次データ)
        dates = pd.date_range(end=datetime.now(), periods=250, freq='B')  # 営業日のみ
        
        # ランダムなデータ生成 (実際にはJPXから取得)
        import numpy as np
        # 銘柄コードからシード値を生成(文字列対応)
        seed_value = sum(ord(c) for c in stock_code) if stock_code else 0
        np.random.seed(seed_value + 1000)
        
        # 空売り残高のトレンドを作成
        base = 200000
        trend = np.cumsum(np.random.randn(250) * 10000)
        short_selling = (base + trend).astype(int)
        short_selling = np.maximum(short_selling, 50000)  # 最小値を設定
        
        df = pd.DataFrame({
            'Date': dates.strftime('%Y-%m-%d'),
            'ShortSelling': short_selling,  # 機関空売り残高
        })
        
        print(f"Successfully generated {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error fetching short selling data: {e}")
        return pd.DataFrame()


def fetch_jpx_short_selling_real(stock_code: str) -> pd.DataFrame:
    """
    実際のJPXサイトから空売りデータを取得する実装例
    (現在は未実装 - 将来の拡張用)
    
    Args:
        stock_code: 銘柄コード
    
    Returns:
        空売りデータのDataFrame
    """
    # TODO: 実際のJPXスクレイピング実装
    # 1. JPXの空売り残高報告ページにアクセス
    # 2. 銘柄コードで検索
    # 3. データをパースしてDataFrameに変換
    
    pass


if __name__ == "__main__":
    # コマンドライン引数から銘柄コードを取得
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = "6920"  # デフォルト: レーザーテック
    
    # 機関空売りデータ取得
    df = fetch_short_selling_data(code)
    
    if not df.empty:
        print(f"\nData range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"\nFirst 5 records:")
        print(df.head())
        print(f"\nLast 5 records:")
        print(df.tail())
        
        # JSON形式で出力
        output = {
            'stock_code': code,
            'data': df.to_dict('records')
        }
        
        with open(f'short_selling_{code}.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nData saved to short_selling_{code}.json")
