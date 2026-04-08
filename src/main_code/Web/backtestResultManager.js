/**
 * backtestResultManager.js - 回测结果管理器（修复版）
 * 
 * 修复：
 * 1. K线图Y轴和数据格式
 * 2. 收益率曲线改为仓价曲线
 * 3. 新增CSV导入
 */

import { App } from './app.js';

let manager = null;

let backtestData = null;
let currentDivisionId = '__total__';
let tradesSortField = 'buy_date';
let tradesSortOrder = 'desc';
let tradesSearchKeyword = '';
let equityChartInstance = null;
let klineChartInstance = null;

export function setBacktestResultManager(_manager) {
    manager = _manager;
}

export const BacktestResultManager = {

    init() {
        this.bindEvents();
        App.log('📊 回测结果管理器已初始化', 'system');
        return this;
    },

    // ============================
    // 事件绑定
    // ============================
    bindEvents() {
        const backBtn = document.getElementById('bt-back-to-config');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showConfigView());
        }

        const viewResultBtn = document.getElementById('btn-view-backtest-result');
        if (viewResultBtn) {
            viewResultBtn.addEventListener('click', () => this.showResultView());
        }

        const divSelector = document.getElementById('bt-result-division-select');
        if (divSelector) {
            divSelector.addEventListener('change', (e) => {
                currentDivisionId = e.target.value;
                this.renderCurrentDivision();
            });
        }

        const searchInput = document.getElementById('bt-trades-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                tradesSearchKeyword = e.target.value.trim().toLowerCase();
                this.renderTradesTable();
            });
        }

        const tradesTable = document.getElementById('bt-trades-table');
        if (tradesTable) {
            const thead = tradesTable.querySelector('thead');
            if (thead) {
                thead.addEventListener('click', (e) => {
                    const th = e.target.closest('th[data-sort]');
                    if (!th) return;
                    const field = th.dataset.sort;
                    if (tradesSortField === field) {
                        tradesSortOrder = tradesSortOrder === 'asc' ? 'desc' : 'asc';
                    } else {
                        tradesSortField = field;
                        tradesSortOrder = 'desc';
                    }
                    this.renderTradesTable();
                });
            }
        }

        const klineClose = document.getElementById('bt-kline-close-btn');
        if (klineClose) {
            klineClose.addEventListener('click', () => this.closeKlineModal());
        }
        const klineOverlay = document.getElementById('bt-kline-overlay');
        if (klineOverlay) {
            klineOverlay.addEventListener('click', () => this.closeKlineModal());
        }

        // 导出CSV
        const exportBtn = document.getElementById('bt-export-trades-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportBacktestJSON());
        }

        // 导入CSV
        const importBtn = document.getElementById('bt-import-trades-btn');
        if (importBtn) {
            importBtn.addEventListener('click', () => this.importBacktestJSON());
        }
    },

    // ============================
    // 视图切换
    // ============================
    showConfigView() {
        document.getElementById('backtest-config-view')?.classList.add('active');
        document.getElementById('backtest-result-view')?.classList.remove('active');
    },

    showResultView() {
        if (!backtestData) {
            App.log('❌ 暂无回测结果', 'error');
            return;
        }
        document.getElementById('backtest-config-view')?.classList.remove('active');
        document.getElementById('backtest-result-view')?.classList.add('active');
        this.renderCurrentDivision();
        setTimeout(() => {
            if (equityChartInstance) equityChartInstance.resize();
        }, 150);
    },

    // ============================
    // 数据入口
    // ============================
    setResultData(data) {
        backtestData = data;
        currentDivisionId = '__total__';
        tradesSortField = 'buy_date';
        tradesSortOrder = 'desc';
        tradesSearchKeyword = '';

        this.buildDivisionSelector();

        const viewBtn = document.getElementById('btn-view-backtest-result');
        if (viewBtn) {
            viewBtn.style.display = 'inline-flex';
            const countSpan = document.getElementById('backtest-trade-count');
            if (countSpan && data.total) {
                countSpan.textContent = data.total.trades ? data.total.trades.length : 0;
            }
        }
        const exportBtn = document.getElementById('bt-export-trades-btn');
        if (exportBtn) exportBtn.style.display = 'inline-flex';


        App.log(`✅ 回测结果已加载: 总仓 + ${data.divisions ? Object.keys(data.divisions).length : 0} 个分仓`, 'success');
    },

    showLoading() {
        const viewBtn = document.getElementById('btn-view-backtest-result');
        if (viewBtn) viewBtn.style.display = 'none';
    },

    // ============================
    // 仓位选择器
    // ============================
    buildDivisionSelector() {
        const selector = document.getElementById('bt-result-division-select');
        if (!selector || !backtestData) return;
        selector.innerHTML = '';

        const totalOpt = document.createElement('option');
        totalOpt.value = '__total__';
        totalOpt.textContent = '📊 总仓';
        selector.appendChild(totalOpt);

        if (backtestData.divisions) {
            Object.keys(backtestData.divisions).forEach(divId => {
                const div = backtestData.divisions[divId];
                const opt = document.createElement('option');
                opt.value = divId;
                opt.textContent = `💰 ${div.division_name || divId}`;
                selector.appendChild(opt);
            });
        }
        selector.value = '__total__';
    },

    getCurrentData() {
        if (!backtestData) return null;
        if (currentDivisionId === '__total__') {
            return backtestData.total || null;
        }
        return backtestData.divisions?.[currentDivisionId] || null;
    },

    renderCurrentDivision() {
        const data = this.getCurrentData();
        if (!data) {
            App.log('⚠️ 当前仓位无数据', 'warning');
            return;
        }
        this.renderStats(data);
        this.renderEquityChart(data);
        this.renderTradesTable();
    },

    // ============================
    // 统计卡片
    // ============================
    renderStats(data) {
        const stats = data.summary || {};
        const mappings = [
            { id: 'bt-stat-name', value: currentDivisionId === '__total__' ? '总仓' : (data.division_name || '--'), cls: 'neutral' },
            { id: 'bt-stat-init-fund', value: this.fmtMoney(stats.initial_fund), cls: 'neutral' },
            { id: 'bt-stat-final-fund', value: this.fmtMoney(stats.final_fund), cls: (stats.total_return ?? 0) >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-total-return', value: this.fmtPct(stats.total_return), cls: (stats.total_return ?? 0) >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-win-rate', value: this.fmtPct(stats.win_rate), cls: 'neutral' },
            { id: 'bt-stat-annual-return', value: this.fmtPct(stats.annual_return), cls: (stats.annual_return ?? 0) >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-annual-volatility', value: this.fmtPct(stats.annual_volatility), cls: 'neutral' },
            { id: 'bt-stat-monthly-return', value: this.fmtPct(stats.monthly_return), cls: (stats.monthly_return ?? 0) >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-monthly-volatility', value: this.fmtPct(stats.monthly_volatility), cls: 'neutral' },
            { id: 'bt-stat-max-drawdown', value: this.fmtPct(stats.max_drawdown), cls: 'negative' },
            { id: 'bt-stat-sharpe', value: stats.sharpe_ratio != null ? stats.sharpe_ratio.toFixed(2) : '--', cls: 'neutral' },
            { id: 'bt-stat-trade-count', value: data.trades ? data.trades.length : 0, cls: 'neutral' },
        ];
        mappings.forEach(m => {
            const el = document.getElementById(m.id);
            if (el) {
                el.textContent = m.value;
                el.className = 'bt-stat-value ' + m.cls;
            }
        });
    },

    // ============================
    // 修复2：收益率曲线改为仓价曲线
    // ============================
    renderEquityChart(data) {
        const container = document.getElementById('bt-equity-chart');
        if (!container) return;

        if (!equityChartInstance) {
            equityChartInstance = echarts.init(container, 'dark');
        }

        const curve = data.equity_curve || {};
        const dates = curve.dates || [];
        const equity = curve.equity || [];         // 仓价（实际金额）
        const returns = curve.returns || [];       // 累计收益率 %
        const drawdown = curve.drawdown || [];     // 回撤 %
        const positions = curve.positions || [];
        const buyMarkers = curve.buy_markers || [];
        const sellMarkers = curve.sell_markers || [];

        // 买卖散点 —— 用仓价做Y坐标
        const buyScatter = buyMarkers.map(m => ({
            value: [m.date, m.equity],
            info: m
        }));
        const sellScatter = sellMarkers.map(m => ({
            value: [m.date, m.equity],
            info: m
        }));

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(0,0,0,0.88)',
                borderColor: '#4facfe',
                textStyle: { fontSize: 12, color: '#e6eaf2' },
                formatter: (params) => {
                    if (!params || params.length === 0) return '';
                    const dateStr = params[0].axisValue;
                    let html = `<div style="font-weight:700;margin-bottom:6px;font-size:13px;">${dateStr}</div>`;

                    params.forEach(p => {
                        if (p.seriesType === 'scatter') return;
                        const val = typeof p.value === 'number' ? p.value : (Array.isArray(p.value) ? p.value[1] : p.value);
                        let displayVal;
                        if (p.seriesName === '仓位金额') {
                            displayVal = `¥${typeof val === 'number' ? val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : val}`;
                        } else {
                            displayVal = `${typeof val === 'number' ? val.toFixed(2) : val}%`;
                        }
                        html += `<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">
                            <span style="width:8px;height:8px;border-radius:50%;background:${p.color};display:inline-block;"></span>
                            <span style="color:#c8cdd5;">${p.seriesName}：</span>
                            <span style="font-weight:600;">${displayVal}</span>
                        </div>`;
                    });

                    // 当日持仓
                    const idx = dates.indexOf(dateStr);
                    if (idx >= 0 && positions[idx] && positions[idx].length > 0) {
                        html += `<div style="margin-top:6px;border-top:1px solid #333;padding-top:4px;font-size:11px;">`;
                        html += `<div style="color:#8b95aa;margin-bottom:2px;">📦 当日持仓：</div>`;
                        positions[idx].forEach(pos => {
                            html += `<div style="color:#c8cdd5;">${pos.code} ${pos.name} ${pos.shares}股</div>`;
                        });
                        html += `</div>`;
                    }

                    // 买入事件
                    const buyAtDate = buyMarkers.filter(m => m.date === dateStr);
                    if (buyAtDate.length > 0) {
                        html += `<div style="margin-top:4px;font-size:11px;">`;
                        buyAtDate.forEach(b => {
                            html += `<div style="color:#ff4757;">📈 买入 ${b.code} ${b.name} @¥${b.price}</div>`;
                        });
                        html += `</div>`;
                    }

                    // 卖出事件
                    const sellAtDate = sellMarkers.filter(m => m.date === dateStr);
                    if (sellAtDate.length > 0) {
                        html += `<div style="margin-top:4px;font-size:11px;">`;
                        sellAtDate.forEach(s => {
                            html += `<div style="color:#2ed573;">📉 卖出 ${s.code} ${s.name} @¥${s.price}</div>`;
                        });
                        html += `</div>`;
                    }

                    return html;
                }
            },
            legend: {
                data: ['仓位金额', '累计收益率', '买入', '卖出'],
                textStyle: { color: '#999', fontSize: 12 },
                top: 5
            },
            grid: { left: '6%', right: '6%', top: 55, bottom: 80, containLabel: true },
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: '#555' } },
                axisLabel: { fontSize: 10, color: '#999' }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '仓位金额 (¥)',
                    position: 'left',
                    nameTextStyle: { color: '#4facfe', fontSize: 12 },
                    axisLine: { lineStyle: { color: '#4facfe' } },
                    axisLabel: {
                        fontSize: 10, color: '#999',
                        formatter: (val) => {
                            if (val >= 10000) return (val / 10000).toFixed(1) + '万';
                            return val.toFixed(0);
                        }
                    },
                    splitLine: { lineStyle: { color: '#222' } },
                    // 自动计算范围，给点余量
                    min: function (value) { return Math.floor(value.min * 0.98); },
                    max: function (value) { return Math.ceil(value.max * 1.02); }
                },
                {
                    type: 'value',
                    name: '收益率/回撤 (%)',
                    position: 'right',
                    nameTextStyle: { color: '#00f2fe', fontSize: 12 },
                    axisLine: { lineStyle: { color: '#00f2fe' } },
                    axisLabel: { fontSize: 10, color: '#999', formatter: '{value}%' },
                    splitLine: { show: false }
                }
            ],
            dataZoom: [
                { type: 'slider', start: 0, end: 100, bottom: 10, textStyle: { color: '#999' } },
                { type: 'inside', start: 0, end: 100 }
            ],
            series: [
                {
                    name: '仓位金额',
                    type: 'line',
                    yAxisIndex: 0,
                    data: equity,
                    smooth: true,
                    lineStyle: { color: '#4facfe', width: 2.5 },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(79,172,254,0.15)' },
                            { offset: 1, color: 'rgba(79,172,254,0.01)' }
                        ])
                    },
                    symbol: 'none'
                },
                {
                    name: '累计收益率',
                    type: 'line',
                    yAxisIndex: 1,
                    data: returns,
                    smooth: true,
                    lineStyle: { color: '#00f2fe', width: 2 },
                    symbol: 'none'
                },
                {
                    name: '买入',
                    type: 'scatter',
                    yAxisIndex: 0,
                    data: buyScatter,
                    symbol: 'triangle',
                    symbolSize: 14,
                    itemStyle: { color: '#ff4757', borderColor: '#fff', borderWidth: 1 },
                    z: 10
                },
                {
                    name: '卖出',
                    type: 'scatter',
                    yAxisIndex: 0,
                    data: sellScatter,
                    symbol: 'diamond',
                    symbolSize: 14,
                    itemStyle: { color: '#2ed573', borderColor: '#fff', borderWidth: 1 },
                    z: 10
                }
            ]
        };

        equityChartInstance.setOption(option, true);

        window.removeEventListener('resize', this._onResize);
        this._onResize = () => equityChartInstance?.resize();
        window.addEventListener('resize', this._onResize);
    },

    // ============================
    // 成交列表
    // ============================
    renderTradesTable() {
        const data = this.getCurrentData();
        if (!data) return;

        let trades = data.trades || [];

        if (tradesSearchKeyword) {
            trades = trades.filter(t =>
                (t.code || '').toLowerCase().includes(tradesSearchKeyword) ||
                (t.name || '').toLowerCase().includes(tradesSearchKeyword)
            );
        }

        trades = [...trades].sort((a, b) => {
            let va = a[tradesSortField];
            let vb = b[tradesSortField];
            if (typeof va === 'string') {
                return tradesSortOrder === 'asc'
                    ? (va || '').localeCompare(vb || '')
                    : (vb || '').localeCompare(va || '');
            }
            va = va ?? 0;
            vb = vb ?? 0;
            return tradesSortOrder === 'asc' ? va - vb : vb - va;
        });

        // 更新排序指示
        const table = document.getElementById('bt-trades-table');
        if (table) {
            table.querySelectorAll('thead th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
                if (th.dataset.sort === tradesSortField) {
                    th.classList.add(tradesSortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
                }
            });
        }

        const tbody = document.getElementById('bt-trades-tbody');
        if (!tbody) return;

        const countEl = document.getElementById('bt-trades-count-display');
        if (countEl) countEl.textContent = `${trades.length} 笔`;

        if (trades.length === 0) {
            tbody.innerHTML = `<tr><td colspan="11" style="text-align:center;color:#8b95aa;padding:30px;">暂无成交记录</td></tr>`;
            return;
        }

        tbody.innerHTML = trades.map((t, idx) => {
            const pct = t.profit_pct ?? 0;
            const money = t.profit_money ?? 0;
            const pctCls = pct >= 0 ? 'td-profit-pos' : 'td-profit-neg';
            const moneyCls = money >= 0 ? 'td-profit-pos' : 'td-profit-neg';
            return `<tr data-trade-idx="${idx}">
                <td>${idx + 1}</td>
                <td>${t.buy_date || '--'}</td>
                <td>${t.sell_date || '--'}</td>
                <td>${t.hold_days ?? '--'}</td>
                <td class="td-code">${t.code || '--'}</td>
                <td>${t.name || '--'}</td>
                <td>${t.buy_price != null ? t.buy_price.toFixed(2) : '--'}</td>
                <td>${t.sell_price != null ? t.sell_price.toFixed(2) : '--'}</td>
                <td class="${pctCls}">${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%</td>
                <td class="${moneyCls}">${money >= 0 ? '+' : ''}${money.toFixed(2)}</td>
                <td><button class="td-view-btn" data-trade-idx="${idx}">📈 K线</button></td>
            </tr>`;
        }).join('');

        // 缓存当前筛选后的trades供K线使用
        this._currentFilteredTrades = trades;

        tbody.querySelectorAll('.td-view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.tradeIdx);
                if (idx >= 0 && idx < trades.length) {
                    this.openKlineModal(trades[idx]);
                }
            });
        });
    },

    // ============================
    // 修复1：K线弹窗 - 修正数据格式和Y轴
    // ============================
    openKlineModal(trade) {
        const modal = document.getElementById('bt-kline-modal');
        if (!modal) return;
        modal.classList.add('active');

        const set = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };
        set('bt-kline-code', trade.code || '--');
        set('bt-kline-name', trade.name || '--');
        set('bt-kline-buy-info', `${trade.buy_date || '--'} @¥${trade.buy_price != null ? trade.buy_price.toFixed(2) : '--'}`);
        set('bt-kline-sell-info', `${trade.sell_date || '--'} @¥${trade.sell_price != null ? trade.sell_price.toFixed(2) : '--'}`);

        const profitEl = document.getElementById('bt-kline-profit-info');
        if (profitEl) {
            const pct = trade.profit_pct ?? 0;
            profitEl.textContent = `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;
            profitEl.className = `info-value ${pct >= 0 ? 'profit-pos' : 'profit-neg'}`;
        }

        this.renderKlineChart(trade);
    },

    closeKlineModal() {
        const modal = document.getElementById('bt-kline-modal');
        if (modal) modal.classList.remove('active');
        if (klineChartInstance) {
            klineChartInstance.dispose();
            klineChartInstance = null;
        }
    },

    renderKlineChart(trade) {
        const container = document.getElementById('bt-kline-chart-container');
        if (!container) return;

        if (klineChartInstance) {
            klineChartInstance.dispose();
        }
        klineChartInstance = echarts.init(container, 'dark');

        const kline = trade.kline_data;
        if (!kline || !kline.dates || kline.dates.length === 0) {
            klineChartInstance.setOption({
                backgroundColor: 'transparent',
                graphic: [{
                    type: 'text',
                    left: 'center',
                    top: 'center',
                    style: { text: '暂无K线数据', fill: '#8b95aa', fontSize: 16 }
                }]
            });
            return;
        }

        const dates = kline.dates;
        // ohlc 格式: [[open, close, low, high], ...]
        // ECharts candlestick 需要: [open, close, low, high]
        const ohlc = kline.ohlc || [];
        const volumes = kline.volumes || [];

        // 计算Y轴范围（从ohlc数据中取极值）
        let priceMin = Infinity;
        let priceMax = -Infinity;
        ohlc.forEach(item => {
            if (!item || item.length < 4) return;
            const low = item[2];   // low
            const high = item[3];  // high
            if (low < priceMin) priceMin = low;
            if (high > priceMax) priceMax = high;
        });
        // 给5%的上下余量
        const pricePadding = (priceMax - priceMin) * 0.08;
        priceMin = Math.max(0, priceMin - pricePadding);
        priceMax = priceMax + pricePadding;

        // 买卖标记
        const buyDateIdx = dates.indexOf(trade.buy_date);
        const sellDateIdx = dates.indexOf(trade.sell_date);




        const markPointData = [];
        if (buyDateIdx >= 0 && ohlc[buyDateIdx]) {
            markPointData.push({
                name: '买入',
                coord: [buyDateIdx, ohlc[buyDateIdx][2] - pricePadding * 0.3],
                symbol: 'arrow',
                symbolSize: [16, 20],
                symbolRotate: 0,
                itemStyle: { color: '#ff4757' },
                label: {
                    show: true,
                    position: 'bottom',
                    distance: 5,
                    color: '#ff4757',
                    fontSize: 11,
                    fontWeight: 'bold',
                    formatter: `买入\n¥${trade.buy_price?.toFixed(2) || ''}`
                }
            });
        }
        if (sellDateIdx >= 0 && ohlc[sellDateIdx]) {
            markPointData.push({
                name: '卖出',
                coord: [sellDateIdx, ohlc[sellDateIdx][3] + pricePadding * 0.3],
                symbol: 'diamond',
                symbolSize: [16, 16],
                itemStyle: { color: '#2ed573' },
                label: {
                    show: true,
                    position: 'top',
                    distance: 5,
                    color: '#2ed573',
                    fontSize: 11,
                    fontWeight: 'bold',
                    formatter: `卖出\n¥${trade.sell_price?.toFixed(2) || ''}`
                }
            });
        }

        // 持仓区间高亮
        const markAreaData = [];
        if (buyDateIdx >= 0 && sellDateIdx >= 0 && sellDateIdx > buyDateIdx) {
            markAreaData.push([
                {
                    xAxis: dates[buyDateIdx],
                    itemStyle: { color: 'rgba(79,172,254,0.08)' }
                },
                { xAxis: dates[sellDateIdx] }
            ]);
        }

        const option = {
            backgroundColor: 'transparent',
            animation: false,
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross',
                    crossStyle: { color: '#999' }
                },
                backgroundColor: 'rgba(0,0,0,0.88)',
                borderColor: '#4facfe',
                textStyle: { fontSize: 12, color: '#e6eaf2' },
                formatter: (params) => {
                    if (!params || params.length === 0) return '';
                    const idx = params[0].dataIndex;
                    const dateStr = dates[idx];
                    const d = ohlc[idx];
                    if (!d) return dateStr;

                    const open = d[0], close = d[1], low = d[2], high = d[3], changeRatio = d[4];
                    const change = open !== 0 ? changeRatio : '0.00';
                    const changeColor = close >= open ? '#ff4757' : '#2ed573';
                    const vol = volumes[idx] ? (volumes[idx] / 10000).toFixed(2) + '万' : '--';
                    const reason = "我想卖就卖"
                    let html = `<div style="font-weight:700;margin-bottom:4px;">${dateStr}</div>`;
                    html += `<div>开盘: <span style="font-weight:600;">¥${open.toFixed(2)}</span></div>`;
                    html += `<div>收盘: <span style="font-weight:600;">¥${close.toFixed(2)}</span></div>`;
                    html += `<div>最高: <span style="font-weight:600;">¥${high.toFixed(2)}</span></div>`;
                    html += `<div>最低: <span style="font-weight:600;">¥${low.toFixed(2)}</span></div>`;
                    html += `<div>涨跌: <span style="color:${changeColor};font-weight:600;">${change}%</span></div>`;
                    html += `<div>成交量: ${vol}</div>`;

                    // 标记买卖日
                    if (dateStr === trade.buy_date) {
                        html += `<div style="margin-top:4px;color:#ff4757;font-weight:700;">📈 买入日 @¥${trade.buy_price?.toFixed(2)}</div>`;
                    }
                    if (dateStr === trade.sell_date) {
                        html += `<div>卖出原因: ${trade.sellReason}</div>`;
                        html += `<div style="margin-top:4px;color:#2ed573;font-weight:700;">📉 卖出日 @¥${trade.sell_price?.toFixed(2)}</div>`;
                    }

                    return html;
                }
            },
            grid: [
                { left: '8%', right: '4%', top: 50, height: '52%' },
                { left: '8%', right: '4%', top: '70%', height: '18%' }
            ],
            xAxis: [
                {
                    type: 'category',
                    data: dates,
                    gridIndex: 0,
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: { show: false },
                    axisTick: { show: false }
                },
                {
                    type: 'category',
                    data: dates,
                    gridIndex: 1,
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: { fontSize: 10, color: '#999' }
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    gridIndex: 0,
                    min: parseFloat(priceMin.toFixed(2)),
                    max: parseFloat(priceMax.toFixed(2)),
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: {
                        fontSize: 10,
                        color: '#999',
                        formatter: (v) => '¥' + v.toFixed(2)
                    },
                    splitLine: { lineStyle: { color: '#222' } },
                    splitNumber: 6
                },
                {
                    type: 'value',
                    gridIndex: 1,
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: {
                        fontSize: 10,
                        color: '#999',
                        formatter: (v) => {
                            if (v >= 10000) return (v / 10000).toFixed(0) + '万';
                            return v;
                        }
                    },
                    splitLine: { lineStyle: { color: '#222' } },
                    splitNumber: 3
                }
            ],
            dataZoom: [
                { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
                { type: 'slider', xAxisIndex: [0, 1], bottom: 5, start: 0, end: 100, height: 20, textStyle: { color: '#999' } }
            ],
            series: [
                {
                    name: 'K线',
                    type: 'candlestick',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    data: ohlc,
                    itemStyle: {
                        color: '#ec0000',       // 涨（收盘>开盘）填充色
                        color0: '#00da3c',      // 跌（收盘<开盘）填充色
                        borderColor: '#ec0000',
                        borderColor0: '#00da3c'
                    },
                    markPoint: {
                        data: markPointData,
                        animation: true,
                        animationDuration: 500
                    },
                    markArea: {
                        silent: true,
                        data: markAreaData
                    }
                },
                {
                    name: '成交量',
                    type: 'bar',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    data: volumes,
                    itemStyle: {
                        color: (params) => {
                            const idx = params.dataIndex;
                            if (ohlc[idx]) {
                                return ohlc[idx][1] >= ohlc[idx][0] ? 'rgba(236,0,0,0.6)' : 'rgba(0,218,60,0.6)';
                            }
                            return '#555';
                        }
                    }
                }
            ]
        };

        klineChartInstance.setOption(option, true);
    },

    // ============================
    // 导出CSV
    // ============================
    exportBacktestJSON() {
        const data = this.getCurrentData();
        if (!data) {
            App.log('暂无数据可导出', 'warning');
            return;
        }

        // 导出完整的 backtestData 结构（包括total和divisions）
        const divName = currentDivisionId === '__total__' ? '总仓' : (data.division_name || currentDivisionId);
        
        // 如果是单个分仓，导出该分仓的完整数据
        // 如果是总仓，导出整个 backtestData（包含所有分仓）
        const exportData = currentDivisionId === '__total__' 
            ? backtestData  // 导出完整的backtestData结构
            : {
                total: data,  // 导出单个分仓作为总仓
                divisions: {}
            };

        const jsonStr = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backtest_result_${divName}_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        const divCount = currentDivisionId === '__total__' 
            ? (backtestData.divisions ? Object.keys(backtestData.divisions).length : 0)
            : 0;
        App.log(
            `${divName} 回测结果已导出 (${divCount > 0 ? divCount + '个分仓 + ' : ''}${data.trades ? data.trades.length : 0}笔成交)`,
            'success'
        );
    },

    // ============================
    // 修复3：从CSV导入成交记录
    // ============================
    importBacktestJSON() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const jsonStr = event.target.result;
                    const importedData = JSON.parse(jsonStr);

                    // 验证数据结构
                    if (!importedData.total || !importedData.total.trades) {
                        throw new Error('JSON文件格式不正确，缺少 total.trades');
                    }

                    // 检查导入的数据是否包含完整的equity_curve和summary
                    const hasCompleteTotalData = 
                        importedData.total.summary &&
                        importedData.total.equity_curve &&
                        importedData.total.equity_curve.dates &&
                        importedData.total.equity_curve.equity;

                    if (!hasCompleteTotalData) {
                        throw new Error('JSON文件缺少必要的统计数据（summary、equity_curve）');
                    }

                    // 验证分仓数据完整性（如果有分仓）
                    if (importedData.divisions && Object.keys(importedData.divisions).length > 0) {
                        for (const divId of Object.keys(importedData.divisions)) {
                            const div = importedData.divisions[divId];
                            if (!div.summary || !div.equity_curve || !div.trades) {
                                console.warn(`分仓 ${divId} 数据不完整，将自动修复`);
                                // 可选：自动修复分仓数据（调用计算方法）
                            }
                        }
                    }

                    // 设置导入的数据
                    this.setResultData(importedData);
                    this.showResultView();

                    const divCount = importedData.divisions ? Object.keys(importedData.divisions).length : 0;
                    const tradeCount = importedData.total.trades ? importedData.total.trades.length : 0;
                    App.log(
                        `✅ 成功导入回测结果 (${divCount > 0 ? divCount + '个分仓 + ' : ''}${tradeCount}笔成交)`,
                        'success'
                    );
                } catch (error) {
                    console.error('JSON导入失败:', error);
                    App.log(`❌ JSON导入失败: ${error.message}`, 'error');
                }
            };
            reader.readAsText(file, 'UTF-8');
        });
        input.click();
    },

    /**
     * 从成交记录重建权益曲线
     * 简化版：按日期排序，累加盈利
     */
    rebuildEquityCurveFromTrades(trades, initialFund) {
        initialFund = initialFund || 100000;

        // 收集所有日期范围
        let minDate = null, maxDate = null;
        trades.forEach(t => {
            if (t.buy_date && (!minDate || t.buy_date < minDate)) minDate = t.buy_date;
            if (t.sell_date && (!maxDate || t.sell_date > maxDate)) maxDate = t.sell_date;
        });

        if (!minDate || !maxDate) {
            return { dates: [], equity: [], returns: [], drawdown: [], positions: [], buy_markers: [], sell_markers: [] };
        }

        // 生成连续交易日
        const continuousDates = [];
        const d = new Date(minDate);
        const end = new Date(maxDate);
        while (d <= end) {
            if (d.getDay() !== 0 && d.getDay() !== 6) {
                continuousDates.push(d.toISOString().split('T')[0]);
            }
            d.setDate(d.getDate() + 1);
        }

        if (continuousDates.length === 0) {
            return { dates: [], equity: [], returns: [], drawdown: [], positions: [], buy_markers: [], sell_markers: [] };
        }

        // 为每笔交易计算每日的线性插值盈亏
        // 思路：持仓期间每天按比例均摊利润，不持仓时equity不变
        const dailyPnL = {};
        continuousDates.forEach(date => { dailyPnL[date] = 0; });

        trades.forEach(t => {
            if (!t.buy_date || !t.sell_date) return;
            
            // 找到持仓期间的交易日
            const holdDates = continuousDates.filter(
                date => date >= t.buy_date && date <= t.sell_date
            );
            
            if (holdDates.length <= 1) {
                // 只有一天：盈利全部算在卖出日
                if (dailyPnL[t.sell_date] !== undefined) {
                    dailyPnL[t.sell_date] += (t.profit_money || 0);
                }
                return;
            }

            // 每天均摊利润（模拟线性变化）
            const dailyProfit = (t.profit_money || 0) / (holdDates.length - 1);
            // 第一天（买入日）不产生盈亏，从第二天开始
            for (let i = 1; i < holdDates.length; i++) {
                dailyPnL[holdDates[i]] += dailyProfit;
            }
        });

        // 累加生成equity曲线
        const equity = [];
        const returns = [];
        const drawdown = [];
        const positions = [];
        const buyMarkers = [];
        const sellMarkers = [];

        let currentEquity = initialFund;
        let maxEquity = initialFund;

        // 买卖事件索引
        const buyEventMap = {};
        const sellEventMap = {};
        trades.forEach(t => {
            if (t.buy_date) {
                if (!buyEventMap[t.buy_date]) buyEventMap[t.buy_date] = [];
                buyEventMap[t.buy_date].push(t);
            }
            if (t.sell_date) {
                if (!sellEventMap[t.sell_date]) sellEventMap[t.sell_date] = [];
                sellEventMap[t.sell_date].push(t);
            }
        });

        continuousDates.forEach(date => {
            currentEquity += (dailyPnL[date] || 0);
            equity.push(parseFloat(currentEquity.toFixed(2)));

            maxEquity = Math.max(maxEquity, currentEquity);
            const ret = ((currentEquity - initialFund) / initialFund) * 100;
            returns.push(parseFloat(ret.toFixed(2)));

            const dd = maxEquity > 0 ? ((currentEquity - maxEquity) / maxEquity) * 100 : 0;
            drawdown.push(parseFloat(dd.toFixed(2)));

            // 当日持仓
            const pos = [];
            trades.forEach(t => {
                if (t.buy_date && t.sell_date && date >= t.buy_date && date < t.sell_date) {
                    pos.push({
                        code: t.code,
                        name: t.name,
                        shares: Math.floor((initialFund * 0.1) / Math.max(1, t.buy_price))
                    });
                }
            });
            positions.push(pos);

            // 买入标记
            if (buyEventMap[date]) {
                buyEventMap[date].forEach(t => {
                    buyMarkers.push({
                        date, code: t.code, name: t.name,
                        price: t.buy_price, equity: currentEquity
                    });
                });
            }

            // 卖出标记
            if (sellEventMap[date]) {
                sellEventMap[date].forEach(t => {
                    sellMarkers.push({
                        date, code: t.code, name: t.name,
                        price: t.sell_price, equity: currentEquity
                    });
                });
            }
        });

        return {
            dates: continuousDates,
            equity,
            returns,
            drawdown,
            positions,
            buy_markers: buyMarkers,
            sell_markers: sellMarkers
        };
    },





    
    /**
     * 从成交记录计算统计摘要
     */
    calculateSummaryFromTrades(trades, equityCurve) {
        const initialFund = 100000;
        const finalFund = equityCurve.equity.length > 0
            ? equityCurve.equity[equityCurve.equity.length - 1]
            : initialFund;

        const totalReturn = ((finalFund - initialFund) / initialFund) * 100;
        const wins = trades.filter(t => (t.profit_pct || 0) > 0).length;
        const winRate = trades.length > 0 ? (wins / trades.length) * 100 : 0;
        const maxDrawdown = equityCurve.drawdown.length > 0
            ? Math.min(...equityCurve.drawdown)
            : 0;

        // 年化（简化：按交易日数估算）
        const tradeDays = equityCurve.dates.length;
        const years = tradeDays / 252;
        const annualReturn = years > 0 ? (Math.pow(finalFund / initialFund, 1 / years) - 1) * 100 : 0;

        // 月化
        const months = tradeDays / 21;
        const monthlyReturn = months > 0 ? totalReturn / months : 0;

        // 波动率（简化：日收益率标准差）
        const dailyReturns = [];
        for (let i = 1; i < equityCurve.equity.length; i++) {
            const prev = equityCurve.equity[i - 1];
            if (prev > 0) {
                dailyReturns.push((equityCurve.equity[i] - prev) / prev);
            }
        }
        const avgDailyReturn = dailyReturns.length > 0
            ? dailyReturns.reduce((a, b) => a + b, 0) / dailyReturns.length
            : 0;
        const variance = dailyReturns.length > 0
            ? dailyReturns.reduce((sum, r) => sum + (r - avgDailyReturn) ** 2, 0) / dailyReturns.length
            : 0;
        const dailyStd = Math.sqrt(variance);
        const annualVolatility = dailyStd * Math.sqrt(252) * 100;
        const monthlyVolatility = dailyStd * Math.sqrt(21) * 100;

        const sharpeRatio = annualVolatility > 0 ? annualReturn / annualVolatility : 0;

        return {
            initial_fund: initialFund,
            final_fund: parseFloat(finalFund.toFixed(2)),
            total_return: parseFloat(totalReturn.toFixed(2)),
            win_rate: parseFloat(winRate.toFixed(1)),
            annual_return: parseFloat(annualReturn.toFixed(2)),
            annual_volatility: parseFloat(annualVolatility.toFixed(2)),
            monthly_return: parseFloat(monthlyReturn.toFixed(2)),
            monthly_volatility: parseFloat(monthlyVolatility.toFixed(2)),
            max_drawdown: parseFloat(maxDrawdown.toFixed(2)),
            sharpe_ratio: parseFloat(sharpeRatio.toFixed(2))
        };
    },

    // ============================
    // 格式化工具
    // ============================
    fmtPct(val) {
        if (val == null || isNaN(val)) return '--';
        return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
    },

    fmtMoney(val) {
        if (val == null || isNaN(val)) return '--';
        return `¥${val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
};