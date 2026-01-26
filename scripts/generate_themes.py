import json
from pathlib import Path
import glob

def get_sector_icon(sector_name):
    """
    業種名に対応するアイコンを返す
    以前のバージョンに合わせて全て「📊」を返す
    """
    return "📊"

def load_sector_mapping():
    """
    銘柄コード -> セクターの対応表を読み込む
    """
    script_dir = Path(__file__).parent
    mapping_file = script_dir / 'stock_sector_mapping.json'
    
    if not mapping_file.exists():
        print("Warning: stock_sector_mapping.json not found. Using raw sector names.")
        return {}
        
    try:
        with open(mapping_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading mapping file: {e}")
        return {}

def generate_themes():
    """
    docs/data/ディレクトリ内のJSONファイルをスキャンしてthemes.jsonを生成する
    """
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'docs' / 'data'
    output_file = script_dir.parent / 'docs' / 'themes.json'
    
    # セクターマッピングを読み込み
    sector_mapping = load_sector_mapping()
    
    print(f"Scanning data directory: {data_dir}")
    
    if not data_dir.exists():
        print("Error: Data directory not found.")
        return

    # 全銘柄データを収集
    all_stocks = []
    
    # JSONファイルを取得
    json_files = list(data_dir.glob('*.json'))
    print(f"Found {len(json_files)} stock data files.")
    
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                code = data.get('stock_code')
                
                # マッピングがあればそれを使用、なければデータ内のセクターを使用
                sector = sector_mapping.get(code, data.get('sector', 'Unknown'))
                
                stock_info = {
                    "code": code,
                    "name": data.get('stock_name'),
                    "sector": sector
                }
                all_stocks.append(stock_info)
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    # 業種ごとにグループ化
    sectors = {}
    for stock in all_stocks:
        sector = stock['sector']
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    # themes.jsonの構造を作成
    themes = []
    
    # 1. 日経225（全銘柄）
    themes.append({
        "id": "all",
        "name": "Nikkei 225 (All)",
        "description": "日経225全構成銘柄",
        "icon": "🇯🇵",
        "stocks": sorted(all_stocks, key=lambda x: x['code'])
    })
    
    # 2. 業種別テーマ
    sorted_sectors = sorted(sectors.keys())
    for sector in sorted_sectors:
        if sector == "Unknown": continue
        
        themes.append({
            "id": f"sector_{sector}",
            "name": sector,
            "description": f"{sector}関連銘柄",
            "icon": get_sector_icon(sector),
            "stocks": sorted(sectors[sector], key=lambda x: x['code'])
        })
    
    # JSON出力
    output_data = {"themes": themes}
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully generated themes.json with {len(themes)} themes.")
    print(f"Output path: {output_file}")

if __name__ == "__main__":
    generate_themes()
