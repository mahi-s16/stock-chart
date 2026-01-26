import json
from pathlib import Path
import glob

def load_custom_config():
    """
    カスタムテーマ定義とマッピングを読み込む
    """
    script_dir = Path(__file__).parent
    config_file = script_dir / 'custom_theme_config.json'
    
    if not config_file.exists():
        print("Error: custom_theme_config.json not found.")
        return None
        
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None

def generate_themes():
    """
    カスタム設定に基づいてthemes.jsonを生成する
    """
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'docs' / 'data'
    output_file = script_dir.parent / 'docs' / 'themes.json'
    
    # 設定読み込み
    config = load_custom_config()
    if not config:
        return

    theme_defs = config.get('themes', {})
    stock_mapping = config.get('stock_mapping', {})
    theme_order = config.get('theme_order', [])
    
    # Nikkei 225 (All) には公式リストにある銘柄のみ追加するためのリストを読み込み
    try:
        with open(script_dir / 'nikkei225_stocks.json', 'r') as f:
            nikkei_list = json.load(f).get('stocks', [])
            nikkei_codes = set(s['code'] for s in nikkei_list)
    except Exception as e:
        print(f"Error loading nikkei list: {e}")
        nikkei_codes = set()

    print(f"Loaded {len(nikkei_codes)} Nikkei 225 stocks from definition.")

    print(f"Scanning data directory: {data_dir}")
    
    if not data_dir.exists():
        print("Error: Data directory not found.")
        return

    # 全銘柄データを収集
    all_stocks = []
    
    # テーマごとの銘柄リストを初期化
    theme_stocks = {tid: [] for tid in theme_order}
    
    # JSONファイルを取得
    json_files = list(data_dir.glob('*.json'))
    print(f"Found {len(json_files)} stock data files.")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Handle both flat structure (existing) and nested "info" structure (new fetch script)
                if 'info' in data and isinstance(data['info'], dict):
                    code = data['info'].get('code')
                    name = data['info'].get('name')
                else:
                    code = data.get('stock_code')
                    name = data.get('stock_name')
                
                if not code:
                    print(f"Skipping {file_path.name}: No stock code found")
                    continue

                stock_info = {
                    "code": code,
                    "name": name or f"Stock {code}"
                }
                
                # Nikkei 225 (All) には公式リストにある場合のみ追加
                if 'all' in theme_stocks and code in nikkei_codes:
                    theme_stocks['all'].append(stock_info)
                
                # カスタムマッピングに基づいて追加 (こちらはリスト外でもOK)
                mapped_theme_id = stock_mapping.get(code)
                if mapped_theme_id:
                    # 文字列ならリストに変換
                    if isinstance(mapped_theme_id, str):
                        mapped_themes = [mapped_theme_id]
                    else:
                        mapped_themes = mapped_theme_id
                    
                    for tid in mapped_themes:
                        if tid in theme_stocks:
                            theme_stocks[tid].append(stock_info)
                    
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
    
    # themes.jsonの構造を作成
    themes = []
    
    for theme_id in theme_order:
        if theme_id not in theme_defs:
            continue
            
        defn = theme_defs[theme_id]
        stocks = sorted(theme_stocks[theme_id], key=lambda x: x['code'])
        
        entry = {
            "id": theme_id,
            "name": defn['name'],
            "description": defn['description'],
            "icon": defn['icon'],
            "stocks": stocks
        }
        themes.append(entry)
    
    # JSON出力
    output_data = {"themes": themes}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated themes.json with {len(themes)} themes.")
    for t in themes:
        print(f"  - {t['name']}: {len(t['stocks'])} stocks")
    print(f"Output path: {output_file}")

if __name__ == "__main__":
    generate_themes()
