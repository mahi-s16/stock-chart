// グローバル変数
let currentData = null;

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', () => {
    const loadBtn = document.getElementById('loadBtn');
    const stockCodeInput = document.getElementById('stockCode');

    // ボタンクリックイベント
    loadBtn.addEventListener('click', () => {
        const stockCode = stockCodeInput.value.trim();
        if (stockCode) {
            loadStockData(stockCode);
        }
    });

    // Enterキーでも読み込み
    stockCodeInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            loadBtn.click();
        }
    });

    // デフォルトデータを読み込み
    loadStockData('6920');
});

/**
 * 株価データを読み込んでチャートを表示
 */
async function loadStockData(stockCode) {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const chart = document.getElementById('chart');
    const stockInfo = document.getElementById('stockInfo');

    // UI状態をリセット
    loading.style.display = 'block';
    error.style.display = 'none';
    chart.innerHTML = '';
    stockInfo.style.display = 'none';

    try {
        // 銘柄コードを4桁に正規化
        const code = stockCode.replace('.T', '').padStart(4, '0');

        // JSONファイルを読み込み
        const response = await fetch(`data/${code}.json`);

        if (!response.ok) {
            throw new Error(`データが見つかりません (銘柄コード: ${code})`);
        }

        const data = await response.json();
        currentData = data;

        // 銘柄情報を表示
        displayStockInfo(data);

        // チャートを描画
        renderChart(data);

        loading.style.display = 'none';

    } catch (err) {
        console.error('Error loading data:', err);
        loading.style.display = 'none';
        error.style.display = 'block';
        document.getElementById('errorDetail').textContent = err.message;
    }
}

/**
 * 銘柄情報を表示
 */
function displayStockInfo(data) {
    const stockInfo = document.getElementById('stockInfo');
    const stockName = document.getElementById('stockName');
    const stockSector = document.getElementById('stockSector');
    const stockPeriod = document.getElementById('stockPeriod');

    stockName.textContent = `${data.stock_name} (${data.stock_code})`;
    stockSector.textContent = data.sector || 'Unknown';
    stockPeriod.textContent = `${data.base_date} ~ ${data.latest_date}`;

    stockInfo.style.display = 'grid';
}

/**
 * Plotly.jsでチャートを描画
 */
function renderChart(data) {
    const chartData = data.data;

    // 日付と各データ系列を抽出
    const dates = chartData.map(d => d.Date);
    const prices = chartData.map(d => d.Close);
    const volumes = chartData.map(d => d.Volume);
    const shortSelling = chartData.map(d => d.ShortSelling || 0);
    const marginBuy = chartData.map(d => d.MarginBuy || 0);
    const marginSell = chartData.map(d => d.MarginSell || 0);

    // 価格帯別出来高を準備
    const volumeProfile = prepareVolumeProfile(data.volume_profile, prices);

    // トレース定義
    const traces = [
        // 株価 (黒線、左軸)
        {
            x: dates,
            y: prices,
            type: 'scatter',
            mode: 'lines',
            name: '株価',
            line: {
                color: '#000000',
                width: 2
            },
            yaxis: 'y',
            hovertemplate: '<b>株価</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 機関空売り (赤線、右軸)
        {
            x: dates,
            y: shortSelling,
            type: 'scatter',
            mode: 'lines',
            name: '機関空売',
            line: {
                color: '#FF0000',
                width: 2
            },
            yaxis: 'y2',
            hovertemplate: '<b>機関空売</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        },

        // 信用売り (シアン線、右軸)
        {
            x: dates,
            y: marginSell,
            type: 'scatter',
            mode: 'lines',
            name: '信用売',
            line: {
                color: '#00FFFF',
                width: 2
            },
            yaxis: 'y2',
            hovertemplate: '<b>信用売</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        },

        // 信用買い (青線、右軸)
        {
            x: dates,
            y: marginBuy,
            type: 'scatter',
            mode: 'lines',
            name: '信用買',
            line: {
                color: '#0000FF',
                width: 2
            },
            yaxis: 'y2',
            hovertemplate: '<b>信用買</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        }
    ];

    // 価格帯別出来高を背景として追加
    if (volumeProfile.shapes.length > 0) {
        traces.push({
            x: dates,
            y: prices,
            type: 'scatter',
            mode: 'none',
            showlegend: false,
            hoverinfo: 'skip'
        });
    }

    // レイアウト設定
    const layout = {
        title: {
            text: `${data.stock_name} (${data.stock_code}) - 株価・信用取引チャート`,
            font: {
                size: 20,
                color: '#2d3748'
            }
        },
        paper_bgcolor: '#ffffff',
        plot_bgcolor: '#f5f7fa',
        font: {
            color: '#718096'
        },
        xaxis: {
            title: '日付',
            gridcolor: '#e2e8f0',
            showgrid: true
        },
        yaxis: {
            title: '株価 (円)',
            side: 'left',
            gridcolor: '#e2e8f0',
            showgrid: true,
            tickformat: ',.0f'
        },
        yaxis2: {
            title: '信用取引・空売り (株)',
            side: 'right',
            overlaying: 'y',
            gridcolor: 'transparent',
            showgrid: false,
            tickformat: ',.0f'
        },
        legend: {
            x: 0.01,
            y: 0.99,
            bgcolor: 'rgba(255, 255, 255, 0.95)',
            bordercolor: '#e2e8f0',
            borderwidth: 1
        },
        hovermode: 'x unified',
        shapes: volumeProfile.shapes,
        margin: {
            l: 80,
            r: 80,
            t: 80,
            b: 60
        }
    };

    // 設定
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        displaylogo: false
    };

    // チャート描画
    Plotly.newPlot('chart', traces, layout, config);
}

/**
 * 価格帯別出来高を背景図形として準備
 */
function prepareVolumeProfile(volumeProfile, prices) {
    if (!volumeProfile || volumeProfile.length === 0) {
        return { shapes: [] };
    }

    // 最大出来高を取得
    const maxVolume = Math.max(...volumeProfile.map(v => v.volume));

    // 各価格帯を半透明の矩形として描画
    const shapes = volumeProfile.map(v => {
        const opacity = (v.volume / maxVolume) * 0.3; // 最大30%の不透明度

        return {
            type: 'rect',
            xref: 'paper',
            yref: 'y',
            x0: 0,
            x1: 1,
            y0: v.price_low,
            y1: v.price_high,
            fillcolor: `rgba(128, 128, 128, ${opacity})`,
            line: {
                width: 0
            },
            layer: 'below'
        };
    });

    return { shapes };
}
