"""
信用取引データ取得スクリプト
JPX公式サイトから信用取引残高データを取得
"""
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import sys
import re


def fetch_margin_data(stock_code: str) -> pd.DataFrame:
    """
    JPXから信用取引データを取得
    
    Args:
        stock_code: 銘柄コード (4桁)
    
    Returns:
        信用取引データのDataFrame
    """
    try:
        # 銘柄コードを正規化
        stock_code = stock_code.replace('.T', '')
        if stock_code.isdigit():
            stock_code = stock_code.zfill(4)
        
        print(f"Fetching margin trading data for {stock_code}...")
        
        # JPXの信用取引残高データURL
        # 注: 実際のURLは変更される可能性があります
        url = "https://www.jpx.co.jp/markets/statistics-equities/margin/index.html"
        
        # ここでは簡易的な実装として、サンプルデータを生成
        # 実際の実装では、JPXのAPIまたはスクレイピングを使用
        print("Note: Using sample data. Implement actual JPX scraping for production.")
        
        # サンプルデータ生成 (過去1年分の週次データ)
        dates = pd.date_range(end=datetime.now(), periods=52, freq='W-FRI')
        
        # ランダムなデータ生成 (実際にはJPXから取得)
        import numpy as np
        # 銘柄コードからシード値を生成(文字列対応)
        seed_value = sum(ord(c) for c in stock_code) if stock_code else 0
        np.random.seed(seed_value)
        
        df = pd.DataFrame({
            'Date': dates.strftime('%Y-%m-%d'),
            'MarginBuy': np.random.randint(100000, 500000, 52),  # 信用買い残
            'MarginSell': np.random.randint(50000, 300000, 52),  # 信用売り残
        })
        
        print(f"Successfully generated {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error fetching margin data: {e}")
        return pd.DataFrame()


def interpolate_to_daily(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    週次データを日次データに補間
    
    Args:
        df: 週次データのDataFrame
        start_date: 開始日
        end_date: 終了日
    
    Returns:
        日次データのDataFrame
    """
    try:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        # 日次の日付範囲を作成
        daily_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # リサンプリングして前方補完
        df_daily = df.reindex(daily_dates, method='ffill')
        df_daily = df_daily.reset_index()
        df_daily.columns = ['Date', 'MarginBuy', 'MarginSell']
        df_daily['Date'] = df_daily['Date'].dt.strftime('%Y-%m-%d')
        
        return df_daily
        
    except Exception as e:
        print(f"Error interpolating data: {e}")
        return df


if __name__ == "__main__":
    # コマンドライン引数から銘柄コードを取得
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = "6920"  # デフォルト: レーザーテック
    
    # 信用取引データ取得
    df = fetch_margin_data(code)
    
    if not df.empty:
        print(f"\nData range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"\nFirst 5 records:")
        print(df.head())
        
        # 日次データに補間
        start_date = df['Date'].iloc[0]
        end_date = df['Date'].iloc[-1]
        df_daily = interpolate_to_daily(df, start_date, end_date)
        
        print(f"\nInterpolated to {len(df_daily)} daily records")
        
        # JSON形式で出力
        output = {
            'stock_code': code,
            'data': df_daily.to_dict('records')
        }
        
        with open(f'margin_data_{code}.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nData saved to margin_data_{code}.json")
