# 株価・信用取引チャート

株価と信用取引データ(機関空売り、信用買い、信用売り)を可視化するWebアプリケーション。

![Chart Preview](https://via.placeholder.com/800x400?text=Stock+Chart+Preview)

## 特徴

- 📈 **株価チャート**: Yahoo Financeからリアルタイムデータ取得
- 📊 **信用取引データ**: 信用買い・信用売り残高を表示
- 🔴 **機関空売り**: 空売り残高の推移を可視化
- 🎨 **モダンなUI**: ダークテーマ、レスポンシブデザイン
- 🔄 **自動更新**: GitHub Actionsで毎日データ更新
- 🌐 **GitHub Pages**: 静的サイトとして無料ホスティング

## デモ

🔗 [Live Demo](https://your-username.github.io/stock_chart/)

## 使い方

1. 銘柄コードを入力 (例: `6920`)
2. 「チャート表示」ボタンをクリック
3. インタラクティブなチャートで分析

## データソース

- **株価**: [Yahoo Finance](https://finance.yahoo.com/) (yfinance API)
- **信用取引**: JPX (日本取引所グループ)
- **機関空売り**: JPX 空売り残高報告

## ローカル開発

### 必要な環境

- Python 3.8+
- pip

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-username/stock_chart.git
cd stock_chart

# 依存パッケージをインストール
pip install -r requirements.txt

# データを生成
cd scripts
python generate_json.py 6920

# ローカルサーバーを起動
cd ../docs
python -m http.server 8000
```

ブラウザで `http://localhost:8000` を開く

## GitHub Pagesへのデプロイ

1. GitHubリポジトリを作成
2. コードをプッシュ
3. リポジトリ設定 → Pages → Source: `main` branch, `/docs` folder
4. 公開URLにアクセス

## データ更新

GitHub Actionsが毎日18:00 (JST)に自動実行されます。

手動で更新する場合:

```bash
cd scripts
python generate_json.py 6920
```

## カスタマイズ

### 銘柄を追加

`.github/workflows/update-data.yml` を編集:

```yaml
default: '6920,7203,9984,YOUR_CODE'
```

### チャートの色を変更

`docs/app.js` の `traces` セクションを編集

## ライセンス

MIT License

## 免責事項

このツールは情報提供のみを目的としています。投資判断は自己責任で行ってください。
