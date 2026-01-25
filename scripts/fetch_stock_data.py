"""
株価データ取得スクリプト
yfinanceを使用してYahoo Financeから日本株の株価データを取得
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import sys


def fetch_stock_data(stock_code: str, period: str = "1y") -> pd.DataFrame:
    """
    指定された銘柄コードの株価データを取得
    
    Args:
        stock_code: 銘柄コード (例: "6920.T")
        period: 取得期間 (例: "1y", "6mo", "3mo")
    
    Returns:
        株価データのDataFrame
    """
    try:
        # 銘柄コードに.Tが付いていない場合は追加
        if not stock_code.endswith('.T'):
            stock_code = f"{stock_code}.T"
        
        print(f"Fetching stock data for {stock_code}...")
        
        # yfinanceでデータ取得
        ticker = yf.Ticker(stock_code)
        df = ticker.history(period=period)
        
        if df.empty:
            print(f"No data found for {stock_code}")
            return pd.DataFrame()
        
        # カラム名を日本語に変換
        df = df.reset_index()
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
        
        # 必要なカラムのみ抽出
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # 日付を文字列に変換
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        print(f"Successfully fetched {len(df)} records")
        return df
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return pd.DataFrame()


def get_stock_info(stock_code: str) -> dict:
    """
    銘柄の基本情報を取得
    
    Args:
        stock_code: 銘柄コード
    
    Returns:
        銘柄情報の辞書
    """
    # 日本語銘柄名マッピング
    STOCK_NAMES_JP = {
        '6920': 'レーザーテック',
        '7203': 'トヨタ自動車',
        '9984': 'ソフトバンクグループ',
        '6758': 'ソニーグループ',
        '9983': 'ファーストリテイリング',
        '6861': 'キーエンス',
        '4063': '信越化学工業',
        '6954': 'ファナック',
        '4568': '第一三共',
        '6981': '村田製作所',
    }
    
    try:
        if not stock_code.endswith('.T'):
            stock_code = f"{stock_code}.T"
        
        ticker = yf.Ticker(stock_code)
        info = ticker.info
        
        # 銘柄コード(4桁)を取得
        code_4digit = stock_code.replace('.T', '').zfill(4)
        
        # 日本語名があればそれを使用、なければ英語名
        japanese_name = STOCK_NAMES_JP.get(code_4digit, info.get('longName', info.get('shortName', 'Unknown')))
        
        return {
            'code': code_4digit,
            'name': japanese_name,
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown')
        }
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        code_4digit = stock_code.replace('.T', '').zfill(4)
        return {
            'code': code_4digit,
            'name': STOCK_NAMES_JP.get(code_4digit, 'Unknown'),
            'sector': 'Unknown',
            'industry': 'Unknown'
        }


if __name__ == "__main__":
    # コマンドライン引数から銘柄コードを取得
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = "6920"  # デフォルト: レーザーテック
    
    # 株価データ取得
    df = fetch_stock_data(code)
    
    if not df.empty:
        # 銘柄情報取得
        info = get_stock_info(code)
        print(f"\nStock Info: {info['name']} ({info['code']})")
        print(f"Sector: {info['sector']}")
        print(f"Industry: {info['industry']}")
        print(f"\nData range: {df['Date'].iloc[0]} to {df['Date'].iloc[-1]}")
        print(f"\nFirst 5 records:")
        print(df.head())
        
        # JSON形式で出力
        output = {
            'info': info,
            'data': df.to_dict('records')
        }
        
        with open(f'stock_data_{code}.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\nData saved to stock_data_{code}.json")
