import json
from pathlib import Path
import glob

def get_sector_icon(sector_name):
    """
    業種名に対応するアイコンを返す
    """
    icons = {
        "水産・農林業": "🐟",
        "鉱業": "⛏️",
        "建設業": "🏗️",
        "食料品": "🍱",
        "繊維製品": "👕",
        "パルプ・紙": "📄",
        "化学": "⚗️",
        "医薬品": "💊",
        "石油・石炭製品": "⛽",
        "ゴム製品": "タイヤ",
        "ガラス・土石製品": "🏺",
        "鉄鋼": "🔩",
        "非鉄金属": "🥉",
        "金属製品": "🔧",
        "機械": "⚙️",
        "電気機器": "🔌",
        "輸送用機器": "🚗",
        "精密機器": "🔬",
        "その他製品": "🎾",
        "情報・通信業": "💻",
        "電気・ガス業": "💡",
        "陸運業": "🚆",
        "海運業": "🚢",
        "空運業": "✈️",
        "倉庫・運輸関連業": "📦",
        "卸売業": "🏢",
        "小売業": "🛒",
        "銀行業": "🏦",
        "証券、商品先物取引業": "📈",
        "保険業": "🛡️",
        "その他金融業": "💳",
        "不動産業": "🏘️",
        "サービス業": "💁",
    }
    return icons.get(sector_name, "📊")

def generate_themes():
    """
    docs/data/ディレクトリ内のJSONファイルをスキャンしてthemes.jsonを生成する
    """
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / 'docs' / 'data'
    output_file = script_dir.parent / 'docs' / 'themes.json'
    
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
                
                stock_info = {
                    "code": data.get('stock_code'),
                    "name": data.get('stock_name'),
                    "sector": data.get('sector', 'Unknown')
                }
                all_stocks.append(stock_info)
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")

    # レーザーテック(6920)、トヨタ(7203)、ソフトバンクG(9984) など主要銘柄が含まれているか確認
    # (データ生成されていない場合もあるので、警告のみ)
    
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
