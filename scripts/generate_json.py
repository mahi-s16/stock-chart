"""
データ統合スクリプト
各データソースから取得したデータを統合してJSON形式で出力
"""
import sys
import json
from pathlib import Path
import pandas as pd
from fetch_stock_data import fetch_stock_data, get_stock_info
from fetch_margin_data import fetch_margin_data, interpolate_to_daily
from fetch_short_selling import fetch_short_selling_data


def merge_data(stock_code: str) -> dict:
    """
    全データソースからデータを取得して統合
    
    Args:
        stock_code: 銘柄コード (4桁)
    
    Returns:
        統合データの辞書
    """
    # 銘柄コードを正規化
    code_normalized = stock_code.replace('.T', '')
    # 数字のみの場合は4桁にゼロパディング、文字列が含まれる場合はそのまま
    if code_normalized.isdigit():
        code_normalized = code_normalized.zfill(4)
    
    print(f"=== Generating data for {code_normalized} ===\n")
    
    # 1. 株価データ取得
    print("1. Fetching stock price data...")
    stock_df = fetch_stock_data(code_normalized)
    
    if stock_df.empty:
        print("Error: Failed to fetch stock data")
        return None
    
    # 2. 銘柄情報取得
    print("\n2. Fetching stock info...")
    stock_info = get_stock_info(code_normalized)
    
    # 3. 信用取引データ取得
    print("\n3. Fetching margin trading data...")
    margin_df = fetch_margin_data(code_normalized)
    
    # 週次データを日次に補間
    if not margin_df.empty:
        start_date = stock_df['Date'].iloc[0]
        end_date = stock_df['Date'].iloc[-1]
        margin_df = interpolate_to_daily(margin_df, start_date, end_date)
    
    # 4. 機関空売りデータ取得
    print("\n4. Fetching short selling data...")
    short_df = fetch_short_selling_data(code_normalized)
    
    # 5. データをマージ
    print("\n5. Merging all data...")
    
    # 株価データをベースに他のデータをマージ
    merged_df = stock_df.copy()
    
    # 信用取引データをマージ
    if not margin_df.empty:
        merged_df = merged_df.merge(margin_df, on='Date', how='left')
    else:
        merged_df['MarginBuy'] = 0
        merged_df['MarginSell'] = 0
    
    # 機関空売りデータをマージ
    if not short_df.empty:
        merged_df = merged_df.merge(short_df, on='Date', how='left')
    else:
        merged_df['ShortSelling'] = 0
    
    # 欠損値を前方補完
    merged_df = merged_df.fillna(method='ffill').fillna(0)
    
    # 6. 価格帯別出来高を計算
    print("\n6. Calculating volume by price...")
    volume_profile = calculate_volume_profile(merged_df)
    
    # 7. JSON形式で出力
    output = {
        'stock_code': code_normalized,
        'stock_name': stock_info['name'],
        'sector': stock_info['sector'],
        'industry': stock_info['industry'],
        'base_date': merged_df['Date'].iloc[0],
        'latest_date': merged_df['Date'].iloc[-1],
        'data': merged_df.to_dict('records'),
        'volume_profile': volume_profile
    }
    
    print(f"\n✓ Successfully merged {len(merged_df)} records")
    return output


def calculate_volume_profile(df: pd.DataFrame, bins: int = 50) -> list:
    """
    価格帯別出来高を計算
    
    Args:
        df: 株価データのDataFrame
        bins: 価格帯の分割数
    
    Returns:
        価格帯別出来高のリスト
    """
    try:
        # 価格範囲を取得
        min_price = df['Low'].min()
        max_price = df['High'].max()
        
        # 価格帯を作成
        price_bins = pd.cut(df['Close'], bins=bins)
        
        # 各価格帯の出来高を集計
        volume_by_price = df.groupby(price_bins)['Volume'].sum()
        
        # 結果を整形
        profile = []
        for interval, volume in volume_by_price.items():
            if pd.notna(interval):
                profile.append({
                    'price_low': float(interval.left),
                    'price_high': float(interval.right),
                    'volume': int(volume)
                })
        
        return profile
        
    except Exception as e:
        print(f"Error calculating volume profile: {e}")
        return []


if __name__ == "__main__":
    # コマンドライン引数から銘柄コードを取得
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = "6920"  # デフォルト: レーザーテック
    
    # データ統合
    result = merge_data(code)
    
    if result:
        # 出力先ディレクトリを作成
        output_dir = Path(__file__).parent.parent / 'docs' / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # JSONファイルに保存
        code_for_filename = code.replace('.T', '')
        if code_for_filename.isdigit():
            code_for_filename = code_for_filename.zfill(4)
        output_file = output_dir / f'{code_for_filename}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Data saved to {output_file}")
        print(f"\nSummary:")
        print(f"  Stock: {result['stock_name']} ({result['stock_code']})")
        print(f"  Period: {result['base_date']} to {result['latest_date']}")
        print(f"  Records: {len(result['data'])}")
        print(f"  Volume profile bins: {len(result['volume_profile'])}")
    else:
        print("\n✗ Failed to generate data")
        sys.exit(1)
