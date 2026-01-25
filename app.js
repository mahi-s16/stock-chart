// グローバル変数
let currentData = null;
let themesData = null;
let currentChartType = 'margin'; // デフォルトは信用取引チャート

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', async () => {
    const backToThemesBtn = document.getElementById('backToThemes');

    // テーマデータを読み込み
    await loadThemes();

    // テーマ一覧に戻るボタン
    if (backToThemesBtn) {
        backToThemesBtn.addEventListener('click', () => {
            showThemesView();
        });
    }
});

/**
 * テーマデータを読み込んでカードを表示
 */
async function loadThemes() {
    try {
        const response = await fetch('themes.json');
        if (!response.ok) {
            throw new Error('テーマデータの読み込みに失敗しました');
        }

        themesData = await response.json();
        renderThemes(themesData.themes);
    } catch (error) {
        console.error('Error loading themes:', error);
        document.getElementById('themesGrid').innerHTML =
            '<p style="color: var(--error); text-align: center;">テーマデータの読み込みに失敗しました</p>';
    }
}

/**
 * テーマカードを描画
 */
function renderThemes(themes) {
    const themesGrid = document.getElementById('themesGrid');
    themesGrid.innerHTML = '';

    themes.forEach(theme => {
        const card = document.createElement('div');
        card.className = 'theme-card';
        card.innerHTML = `
            <span class="icon">${theme.icon}</span>
            <div class="name">${theme.name}</div>
            <div class="description">${theme.description}</div>
            <div class="count">${theme.stocks.length}銘柄</div>
        `;

        card.addEventListener('click', () => {
            showStocksView(theme);
        });

        themesGrid.appendChild(card);
    });
}

/**
 * 銘柄一覧ビューを表示
 */
function showStocksView(theme) {
    const themesSection = document.querySelector('.themes-section');
    const stocksSection = document.getElementById('stocksSection');
    const selectedThemeName = document.getElementById('selectedThemeName');
    const stocksGrid = document.getElementById('stocksGrid');

    // テーマ名を表示
    selectedThemeName.innerHTML = `${theme.icon} ${theme.name}`;

    // 銘柄カードを生成
    stocksGrid.innerHTML = '';
    theme.stocks.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.innerHTML = `
            <div class="code">${stock.code}</div>
            <div class="name">${stock.name}</div>
        `;

        card.addEventListener('click', () => {
            loadStockData(stock.code);
            // 銘柄コード入力欄にも反映
            document.getElementById('stockCode').value = stock.code;
        });

        stocksGrid.appendChild(card);
    });

    // ビューを切り替え
    themesSection.style.display = 'none';
    stocksSection.style.display = 'block';

    // スムーズにスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * テーマ一覧ビューを表示
 */
function showThemesView() {
    const themesSection = document.querySelector('.themes-section');
    const stocksSection = document.getElementById('stocksSection');
    const chartContainer = document.querySelector('.chart-container');

    themesSection.style.display = 'block';
    stocksSection.style.display = 'none';

    // チャートコンテナを非表示
    if (chartContainer) {
        chartContainer.style.display = 'none';
    }

    // スムーズにスクロール
    window.scrollTo({ top: 0, behavior: 'smooth' });
}


/**
 * 株価データを読み込んでチャートを表示
 */
async function loadStockData(stockCode) {
    const loading = document.getElementById('loading');
    const error = document.getElementById('error');
    const chart = document.getElementById('chart');
    const stockInfo = document.getElementById('stockInfo');
    const chartContainer = document.querySelector('.chart-container');

    // チャートコンテナを表示
    if (chartContainer) {
        chartContainer.style.display = 'block';
    }

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

        // 期間選択ボタンとチャートタイプ選択ボタンを表示して初期化
        initializePeriodSelector();
        initializeChartTypeSelector();

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
    // チャートタイプに応じて適切なレンダラーを呼び出す
    if (currentChartType === 'ma') {
        renderMAChart(data);
        return;
    }

    // デフォルトは信用取引チャート
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
        // 株価 (ダークグレー、左軸)
        {
            x: dates,
            y: prices,
            type: 'scatter',
            mode: 'lines',
            name: '株価',
            line: {
                color: '#6B7280',
                width: 2.5
            },
            yaxis: 'y',
            hovertemplate: '<b>株価</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 機関空売り (パステルレッド、右軸)
        {
            x: dates,
            y: shortSelling,
            type: 'scatter',
            mode: 'lines',
            name: '機関空売',
            line: {
                color: '#F87171',
                width: 2
            },
            yaxis: 'y2',
            hovertemplate: '<b>機関空売</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        },

        // 信用売り (パステルシアン、右軸)
        {
            x: dates,
            y: marginSell,
            type: 'scatter',
            mode: 'lines',
            name: '信用売',
            line: {
                color: '#67E8F9',
                width: 2
            },
            yaxis: 'y2',
            hovertemplate: '<b>信用売</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        },

        // 信用買い (パステルブルー、右軸)
        {
            x: dates,
            y: marginBuy,
            type: 'scatter',
            mode: 'lines',
            name: '信用買',
            line: {
                color: '#93C5FD',
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
    // モバイル判定
    const isMobile = window.innerWidth <= 768;

    // レイアウト設定（モバイル最適化）
    const layout = {
        title: {
            text: `${data.stock_name} (${data.stock_code}) - 株価・信用取引チャート`,
            font: { size: isMobile ? 14 : 18, color: '#2d3748' }
        },
        xaxis: {
            title: '',
            rangeslider: { visible: false },
            type: 'date',
            tickfont: { size: isMobile ? 10 : 12 }
        },
        yaxis: {
            title: isMobile ? '' : '株価 (円)',
            side: 'left',
            showgrid: false,  // グリッド線を非表示
            gridcolor: '#e2e8f0',
            tickfont: { size: isMobile ? 10 : 12 }
        },
        yaxis2: {
            title: isMobile ? '' : '信用・空売り残高',
            overlaying: 'y',
            side: 'right',
            showgrid: false,
            tickfont: { size: isMobile ? 10 : 12 }
        },
        hovermode: 'x unified',
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#f5f7fa',
        font: { family: 'Inter, sans-serif' },
        margin: {
            l: isMobile ? 40 : 60,
            r: isMobile ? 40 : 60,
            t: isMobile ? 60 : 80,
            b: isMobile ? 40 : 60
        },
        legend: {
            orientation: isMobile ? 'v' : 'h',
            yanchor: isMobile ? 'top' : 'bottom',
            y: isMobile ? 0.99 : 1.02,
            xanchor: isMobile ? 'left' : 'right',
            x: isMobile ? 0.01 : 1,
            bgcolor: 'rgba(255,255,255,0.8)',
            bordercolor: '#e2e8f0',
            borderwidth: 1,
            font: { size: isMobile ? 10 : 12 }
        },
        autosize: true,
        height: isMobile ? 400 : undefined,
        shapes: volumeProfile.shapes
    };

    // プロット設定（モバイル最適化）
    const config = {
        responsive: true,
        displayModeBar: !isMobile,  // モバイルではツールバーを非表示
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        scrollZoom: isMobile  // モバイルではピンチズーム有効
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

/**
 * 期間選択ボタンを初期化
 */
function initializePeriodSelector() {
    const periodSelector = document.querySelector('.period-selector');
    const periodBtns = document.querySelectorAll('.period-btn');

    // 期間選択ボタンを表示
    if (periodSelector) {
        periodSelector.style.display = 'flex';
    }

    // イベントリスナーを設定
    periodBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            // アクティブ状態を切り替え
            periodBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // 選択された期間でチャートを更新
            const period = this.dataset.period;
            filterChartByPeriod(period);
        });
    });
}

/**
 * 期間でチャートをフィルタリング
 */
function filterChartByPeriod(period) {
    if (!currentData) return;

    const chartData = currentData.data;
    let filteredData;

    if (period === 'all') {
        filteredData = chartData;
    } else {
        // 最新の日付を取得
        const latestDate = new Date(chartData[chartData.length - 1].Date);
        let startDate = new Date(latestDate);

        // 期間に応じて開始日を計算
        switch (period) {
            case '1m':
                startDate.setMonth(startDate.getMonth() - 1);
                break;
            case '3m':
                startDate.setMonth(startDate.getMonth() - 3);
                break;
            case '6m':
                startDate.setMonth(startDate.getMonth() - 6);
                break;
            case '1y':
                startDate.setFullYear(startDate.getFullYear() - 1);
                break;
        }

        // データをフィルタリング
        filteredData = chartData.filter(d => new Date(d.Date) >= startDate);
    }

    // フィルタリングされたデータでチャートを再描画
    const tempData = { ...currentData, data: filteredData };
    renderChart(tempData);
}

/**
 * 移動平均を計算
 */
function calculateMovingAverage(prices, period) {
    const ma = [];
    for (let i = 0; i < prices.length; i++) {
        if (i < period - 1) {
            ma.push(null);
        } else {
            const sum = prices.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
            ma.push(sum / period);
        }
    }
    return ma;
}

/**
 * チャートタイプ選択ボタンを初期化
 */
function initializeChartTypeSelector() {
    const chartTypeSelector = document.querySelector('.chart-type-selector');
    const chartTypeBtns = document.querySelectorAll('.chart-type-btn');

    // チャートタイプ選択ボタンを表示
    if (chartTypeSelector) {
        chartTypeSelector.style.display = 'flex';
    }

    // イベントリスナーを設定
    chartTypeBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            // アクティブ状態を切り替え
            chartTypeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            // 選択されたチャートタイプを保存
            currentChartType = this.dataset.chartType;

            // チャートを再描画
            if (currentData) {
                renderChart(currentData);
            }
        });
    });
}

/**
 * 移動平均線と出来高のチャートを描画
 */
function renderMAChart(data) {
    const chartData = data.data;

    // 日付と各データ系列を抽出
    const dates = chartData.map(d => d.Date);
    const prices = chartData.map(d => d.Close);
    const volumes = chartData.map(d => d.Volume);

    // 移動平均線を計算
    const ma5 = calculateMovingAverage(prices, 5);
    const ma25 = calculateMovingAverage(prices, 25);
    const ma75 = calculateMovingAverage(prices, 75);

    // モバイル判定
    const isMobile = window.innerWidth <= 768;

    // トレース定義
    const traces = [
        // 株価 (ダークグレー)
        {
            x: dates,
            y: prices,
            type: 'scatter',
            mode: 'lines',
            name: '株価',
            line: {
                color: '#6B7280',
                width: 2.5
            },
            yaxis: 'y',
            hovertemplate: '<b>株価</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 5日移動平均線 (パステルピンク)
        {
            x: dates,
            y: ma5,
            type: 'scatter',
            mode: 'lines',
            name: '5日MA',
            line: {
                color: '#FDA4AF',
                width: 2
            },
            yaxis: 'y',
            hovertemplate: '<b>5日MA</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 25日移動平均線 (パステルブルー)
        {
            x: dates,
            y: ma25,
            type: 'scatter',
            mode: 'lines',
            name: '25日MA',
            line: {
                color: '#93C5FD',
                width: 2
            },
            yaxis: 'y',
            hovertemplate: '<b>25日MA</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 75日移動平均線 (パステルグリーン)
        {
            x: dates,
            y: ma75,
            type: 'scatter',
            mode: 'lines',
            name: '75日MA',
            line: {
                color: '#86EFAC',
                width: 2
            },
            yaxis: 'y',
            hovertemplate: '<b>75日MA</b><br>%{y:,.0f}円<br>%{x}<extra></extra>'
        },

        // 出来高 (棒グラフ、下部)
        {
            x: dates,
            y: volumes,
            type: 'bar',
            name: '出来高',
            marker: {
                color: 'rgba(168, 181, 255, 0.5)'
            },
            yaxis: 'y2',
            hovertemplate: '<b>出来高</b><br>%{y:,.0f}株<br>%{x}<extra></extra>'
        }
    ];

    // レイアウト設定
    const layout = {
        title: {
            text: `${data.stock_name} (${data.stock_code}) - 株価・移動平均線・出来高チャート`,
            font: { size: isMobile ? 14 : 18, color: '#2d3748' }
        },
        xaxis: {
            title: '',
            rangeslider: { visible: false },
            type: 'date',
            tickfont: { size: isMobile ? 10 : 12 }
        },
        yaxis: {
            title: isMobile ? '' : '株価 (円)',
            side: 'left',
            showgrid: false,
            domain: [0.25, 1],  // 上部75%に株価を配置
            tickfont: { size: isMobile ? 10 : 12 }
        },
        yaxis2: {
            title: isMobile ? '' : '出来高',
            side: 'right',
            showgrid: false,
            domain: [0, 0.2],  // 下部20%に出来高を配置
            tickfont: { size: isMobile ? 10 : 12 }
        },
        hovermode: 'x unified',
        plot_bgcolor: '#ffffff',
        paper_bgcolor: '#f5f7fa',
        font: { family: 'Inter, sans-serif' },
        margin: {
            l: isMobile ? 40 : 60,
            r: isMobile ? 40 : 60,
            t: isMobile ? 60 : 80,
            b: isMobile ? 40 : 60
        },
        legend: {
            orientation: isMobile ? 'h' : 'v',
            x: isMobile ? 0 : 1.02,
            y: isMobile ? -0.2 : 1,
            xanchor: isMobile ? 'left' : 'left',
            yanchor: isMobile ? 'top' : 'top',
            font: { size: isMobile ? 10 : 12 }
        },
        showlegend: true
    };

    // チャート描画
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    Plotly.newPlot('chart', traces, layout, config);
}
