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
        '1332': '日本水産',
        '1333': 'マルハニチロ',
        '1605': 'INPEX',
        '1721': 'コムシスホールディングス',
        '1801': '大成建設',
        '1802': '大林組',
        '1803': '清水建設',
        '1808': '長谷工コーポレーション',
        '1925': '大和ハウス工業',
        '1928': '積水ハウス',
        '2002': '日清製粉グループ本社',
        '2269': '明治ホールディングス',
        '2282': '日本ハム',
        '2413': 'エムスリー',
        '2432': 'ディー・エヌ・エー',
        '2501': 'サッポロホールディングス',
        '2502': 'アサヒグループホールディングス',
        '2503': 'キリンホールディングス',
        '2801': 'キッコーマン',
        '2802': '味の素',
        '2871': 'ニチレイ',
        '2914': 'JT',
        '3086': 'J.フロント リテイリング',
        '3092': 'ZOZO',
        '3099': '三越伊勢丹ホールディングス',
        '3101': '東洋紡',
        '3103': 'ユニチカ',
        '3105': '日清紡ホールディングス',
        '3382': 'セブン&アイ・ホールディングス',
        '3401': '帝人',
        '3402': '東レ',
        '3405': 'クラレ',
        '3407': '旭化成',
        '3697': 'SHIFT',
        '4004': '昭和電工',
        '4005': '住友化学',
        '4021': '日産化学',
        '4042': '東ソー',
        '4043': 'トクヤマ',
        '4061': 'デンカ',
        '4062': 'イビデン',
        '4063': '信越化学工業',
        '4183': '三井化学',
        '4188': '三菱ケミカルグループ',
        '4202': 'ダイセル',
        '4203': '住友ベークライト',
        '4204': '積水化学工業',
        '4208': 'UBE',
        '4272': '日本化薬',
        '4307': '野村総合研究所',
        '4324': '電通グループ',
        '4452': '花王',
        '4502': '武田薬品工業',
        '4503': 'アステラス製薬',
        '4506': '住友ファーマ',
        '4507': '塩野義製薬',
        '4519': '中外製薬',
        '4523': 'エーザイ',
        '4543': 'テルモ',
        '4568': '第一三共',
        '4578': '大塚ホールディングス',
        '4661': 'オリエンタルランド',
        '4704': 'トレンドマイクロ',
        '4911': '資生堂',
        '5019': '出光興産',
        '5020': 'ENEOSホールディングス',
        '5101': '横浜ゴム',
        '5108': 'ブリヂストン',
        '5201': 'AGC',
        '5214': '日本電気硝子',
        '5233': '太平洋セメント',
        '5301': '東海カーボン',
        '5332': 'TOTO',
        '5333': '日本碍子',
        '5401': '日本製鉄',
        '5406': '神戸製鋼所',
        '5411': 'JFEホールディングス',
        '5541': '大平洋金属',
        '5631': '日本製鋼所',
        '5703': '日本軽金属ホールディングス',
        '5706': '三井金属鉱業',
        '5707': '東邦亜鉛',
        '5711': '三菱マテリアル',
        '5713': '住友金属鉱山',
        '5714': 'DOWAホールディングス',
        '5801': '古河電気工業',
        '5802': '住友電気工業',
        '5803': 'フジクラ',
        '6098': 'リクルートホールディングス',
        '6113': 'アマダ',
        '6146': 'ディスコ',
        '6178': '日本郵政',
        '6301': '小松製作所',
        '6305': '日立建機',
        '6326': 'クボタ',
        '6361': '荏原製作所',
        '6367': 'ダイキン工業',
        '6471': '日本精工',
        '6472': 'NTN',
        '6473': 'ジェイテクト',
        '6501': '日立製作所',
        '6503': '三菱電機',
        '6504': '富士電機',
        '6506': '安川電機',
        '6526': 'ソシオネクスト',
        '6532': 'ベイカレント・コンサルティング',
        '6645': 'オムロン',
        '6702': '富士通',
        '6723': 'ルネサスエレクトロニクス',
        '6724': 'セイコーエプソン',
        '6752': 'パナソニック ホールディングス',
        '6758': 'ソニーグループ',
        '6762': 'TDK',
        '6841': '横河電機',
        '6857': 'アドバンテスト',
        '6861': 'キーエンス',
        '6902': 'デンソー',
        '6920': 'レーザーテック',
        '6923': 'スタンレー電気',
        '6952': 'カシオ計算機',
        '6954': 'ファナック',
        '6963': 'ローム',
        '6971': '京セラ',
        '6976': '太陽誘電',
        '6981': '村田製作所',
        '7003': '三井E&Sホールディングス',
        '7011': '三菱重工業',
        '7012': '川崎重工業',
        '7013': 'IHI',
        '7201': '日産自動車',
        '7202': 'いすゞ自動車',
        '7203': 'トヨタ自動車',
        '7205': '日野自動車',
        '7211': '三菱自動車工業',
        '7267': '本田技研工業',
        '7269': 'スズキ',
        '7270': 'SUBARU',
        '7272': 'ヤマハ発動機',
        '7453': '良品計画',
        '7731': 'ニコン',
        '7733': 'オリンパス',
        '7735': 'SCREENホールディングス',
        '7741': 'HOYA',
        '7751': 'キヤノン',
        '7832': 'バンダイナムコホールディングス',
        '7911': '凸版印刷',
        '7912': '大日本印刷',
        '7951': 'ヤマハ',
        '8001': '伊藤忠商事',
        '8002': '丸紅',
        '8015': '豊田通商',
        '8031': '三井物産',
        '8053': '住友商事',
        '8058': '三菱商事',
        '8233': '高島屋',
        '8252': '丸井グループ',
        '8267': 'イオン',
        '8303': '新生銀行',
        '8304': 'あおぞら銀行',
        '8306': '三菱UFJフィナンシャル・グループ',
        '8308': 'りそなホールディングス',
        '8309': '三井住友トラスト・ホールディングス',
        '8316': '三井住友フィナンシャルグループ',
        '8331': '千葉銀行',
        '8354': 'ふくおかフィナンシャルグループ',
        '8411': 'みずほフィナンシャルグループ',
        '8601': '大和証券グループ本社',
        '8604': '野村ホールディングス',
        '8628': '松井証券',
        '8630': 'SOMPOホールディングス',
        '8725': 'MS&ADインシュアランスグループホールディングス',
        '8750': '第一生命ホールディングス',
        '8766': '東京海上ホールディングス',
        '8801': '三井不動産',
        '8802': '三菱地所',
        '8830': '住友不動産',
        '9001': '東武鉄道',
        '9005': '東急',
        '9007': '小田急電鉄',
        '9008': '京王電鉄',
        '9009': '京成電鉄',
        '9020': '東日本旅客鉄道',
        '9021': '西日本旅客鉄道',
        '9022': '東海旅客鉄道',
        '9064': 'ヤマトホールディングス',
        '9101': '日本郵船',
        '9104': '商船三井',
        '9107': '川崎汽船',
        '9202': 'ANAホールディングス',
        '9301': '三菱倉庫',
        '9432': '日本電信電話',
        '9433': 'KDDI',
        '9434': 'ソフトバンク',
        '9501': '東京電力ホールディングス',
        '9502': '中部電力',
        '9503': '関西電力',
        '9531': '東京ガス',
        '9532': '大阪ガス',
        '9613': 'NTTデータグループ',
        '9735': 'セコム',
        '9766': 'コナミグループ',
        '9983': 'ファーストリテイリング',
        '9984': 'ソフトバンクグループ',
        '285A': 'キオクシアホールディングス',
    }
    
    # セクターの日本語マッピング
    SECTOR_NAMES_JP = {
        'Technology': 'テクノロジー',
        'Consumer Cyclical': '一般消費財',
        'Healthcare': 'ヘルスケア',
        'Industrials': '資本財',
        'Financial Services': '金融',
        'Communication Services': '通信サービス',
        'Consumer Defensive': '生活必需品',
        'Energy': 'エネルギー',
        'Basic Materials': '素材',
        'Real Estate': '不動産',
        'Utilities': '公益事業',
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
        
        # セクターを日本語に変換
        sector_en = info.get('sector', 'Unknown')
        sector_jp = SECTOR_NAMES_JP.get(sector_en, sector_en)
        
        return {
            'code': code_4digit,
            'name': japanese_name,
            'sector': sector_jp,
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
