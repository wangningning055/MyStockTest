/**
 * backtestResultManager.js - 回测结果管理器
 * 
 * 职责：
 * - 管理回测结果数据（总仓 + 各分仓）
 * - 渲染统计指标、收益率曲线、成交列表
 * - 仓位切换
 * - 成交列表排序/搜索
 * - K线弹窗展示买卖点
 * - 数据导出
 */

import { App } from './app.js';

let manager = null;

/** 回测结果原始数据 */
let backtestData = null;

/** 当前选中的仓位ID：'__total__' 或 divisionId */
let currentDivisionId = '__total__';

/** 成交列表排序状态 */
let tradesSortField = 'buy_date';
let tradesSortOrder = 'desc';

/** 搜索关键字 */
let tradesSearchKeyword = '';

/** ECharts 实例缓存 */
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
        // 返回配置按钮
        const backBtn = document.getElementById('bt-back-to-config');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showConfigView());
        }

        // 查看结果按钮
        const viewResultBtn = document.getElementById('btn-view-backtest-result');
        if (viewResultBtn) {
            viewResultBtn.addEventListener('click', () => this.showResultView());
        }

        // 仓位选择器
        const divSelector = document.getElementById('bt-result-division-select');
        if (divSelector) {
            divSelector.addEventListener('change', (e) => {
                currentDivisionId = e.target.value;
                this.renderCurrentDivision();
            });
        }

        // 成交搜索
        const searchInput = document.getElementById('bt-trades-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                tradesSearchKeyword = e.target.value.trim().toLowerCase();
                this.renderTradesTable();
            });
        }

        // 成交表头排序（事件委托）
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

        // K线弹窗关闭
        const klineClose = document.getElementById('bt-kline-close-btn');
        if (klineClose) {
            klineClose.addEventListener('click', () => this.closeKlineModal());
        }
        const klineOverlay = document.getElementById('bt-kline-overlay');
        if (klineOverlay) {
            klineOverlay.addEventListener('click', () => this.closeKlineModal());
        }

        // 导出成交记录
        const exportBtn = document.getElementById('bt-export-trades-btn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportTradesCSV());
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

        // resize echarts
        setTimeout(() => {
            if (equityChartInstance) equityChartInstance.resize();
        }, 150);
    },

    // ============================
    // 数据设置入口
    // ============================

    /**
     * 设置回测结果数据
     * @param {Object} data - 符合后端数据结构的完整回测结果
     */
    setResultData(data) {
        backtestData = data;
        currentDivisionId = '__total__';
        tradesSortField = 'buy_date';
        tradesSortOrder = 'desc';
        tradesSearchKeyword = '';

        // 构建仓位选择器
        this.buildDivisionSelector();

        // 显示"查看结果"按钮
        const viewBtn = document.getElementById('btn-view-backtest-result');
        if (viewBtn) {
            viewBtn.style.display = 'inline-flex';
            const countSpan = document.getElementById('backtest-trade-count');
            if (countSpan && data.total) {
                countSpan.textContent = data.total.trades ? data.total.trades.length : 0;
            }
        }

        App.log(`✅ 回测结果已加载: 总仓 + ${data.divisions ? Object.keys(data.divisions).length : 0} 个分仓`, 'success');
    },

    /**
     * 显示加载状态
     */
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

        // 总仓
        const totalOpt = document.createElement('option');
        totalOpt.value = '__total__';
        totalOpt.textContent = '📊 总仓';
        selector.appendChild(totalOpt);

        // 分仓
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

    // ============================
    // 获取当前仓位数据
    // ============================

    getCurrentData() {
        if (!backtestData) return null;
        if (currentDivisionId === '__total__') {
            return backtestData.total || null;
        }
        return backtestData.divisions?.[currentDivisionId] || null;
    },

    // ============================
    // 渲染当前仓位
    // ============================

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
    // 统计指标卡片
    // ============================

    renderStats(data) {
        const stats = data.summary || {};

        const mappings = [
            { id: 'bt-stat-name', value: currentDivisionId === '__total__' ? '总仓' : (data.division_name || '--'), cls: 'neutral' },
            { id: 'bt-stat-init-fund', value: this.formatMoney(stats.initial_fund), cls: 'neutral' },
            { id: 'bt-stat-final-fund', value: this.formatMoney(stats.final_fund), cls: stats.total_return >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-total-return', value: this.formatPercent(stats.total_return), cls: stats.total_return >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-win-rate', value: this.formatPercent(stats.win_rate), cls: 'neutral' },
            { id: 'bt-stat-annual-return', value: this.formatPercent(stats.annual_return), cls: stats.annual_return >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-annual-volatility', value: this.formatPercent(stats.annual_volatility), cls: 'neutral' },
            { id: 'bt-stat-monthly-return', value: this.formatPercent(stats.monthly_return), cls: stats.monthly_return >= 0 ? 'positive' : 'negative' },
            { id: 'bt-stat-monthly-volatility', value: this.formatPercent(stats.monthly_volatility), cls: 'neutral' },
            { id: 'bt-stat-max-drawdown', value: this.formatPercent(stats.max_drawdown), cls: 'negative' },
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
    // 收益率曲线图
    // ============================

    renderEquityChart(data) {
        const container = document.getElementById('bt-equity-chart');
        if (!container) return;

        if (!equityChartInstance) {
            equityChartInstance = echarts.init(container, 'dark');
        }

        const equity = data.equity_curve || {};
        const dates = equity.dates || [];
        const nav = equity.nav || [];            // 净值
        const returns = equity.returns || [];    // 累计收益率 %
        const drawdown = equity.drawdown || [];  // 回撤 %
        const positions = equity.positions || []; // 每日持仓信息
        const buyMarkers = equity.buy_markers || [];  // 买入标记
        const sellMarkers = equity.sell_markers || []; // 卖出标记

        // 买入卖出散点数据
        const buyScatter = buyMarkers.map(m => ({
            value: [m.date, m.nav],
            info: m
        }));
        const sellScatter = sellMarkers.map(m => ({
            value: [m.date, m.nav],
            info: m
        }));

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(0,0,0,0.85)',
                borderColor: '#4facfe',
                textStyle: { fontSize: 12 },
                formatter: (params) => {
                    if (!params || params.length === 0) return '';
                    const dateStr = params[0].axisValue;
                    let html = `<div style="font-weight:600;margin-bottom:6px;">${dateStr}</div>`;

                    params.forEach(p => {
                        if (p.seriesType === 'scatter') return;
                        const color = p.color;
                        const name = p.seriesName;
                        const val = typeof p.value === 'number' ? p.value : (Array.isArray(p.value) ? p.value[1] : p.value);
                        html += `<div style="display:flex;align-items:center;gap:6px;margin:2px 0;">
                            <span style="width:8px;height:8px;border-radius:50%;background:${color};display:inline-block;"></span>
                            <span>${name}：${typeof val === 'number' ? val.toFixed(4) : val}</span>
                        </div>`;
                    });

                    // 当日持仓
                    const idx = dates.indexOf(dateStr);
                    if (idx >= 0 && positions[idx] && positions[idx].length > 0) {
                        html += `<div style="margin-top:6px;border-top:1px solid #333;padding-top:4px;font-size:11px;">`;
                        html += `<div style="color:#8b95aa;">当日持仓：</div>`;
                        positions[idx].forEach(pos => {
                            html += `<div>${pos.code} ${pos.name} ${pos.shares}股</div>`;
                        });
                        html += `</div>`;
                    }

                    // 买入标记
                    const buyAtDate = buyMarkers.filter(m => m.date === dateStr);
                    if (buyAtDate.length > 0) {
                        html += `<div style="margin-top:4px;color:#ff4757;font-size:11px;">`;
                        buyAtDate.forEach(b => {
                            html += `<div>📈 买入 ${b.code} ${b.name} @${b.price}</div>`;
                        });
                        html += `</div>`;
                    }

                    // 卖出标记
                    const sellAtDate = sellMarkers.filter(m => m.date === dateStr);
                    if (sellAtDate.length > 0) {
                        html += `<div style="margin-top:4px;color:#2ed573;font-size:11px;">`;
                        sellAtDate.forEach(s => {
                            html += `<div>📉 卖出 ${s.code} ${s.name} @${s.price}</div>`;
                        });
                        html += `</div>`;
                    }

                    return html;
                }
            },
            legend: {
                data: ['净值', '累计收益率', '回撤', '买入', '卖出'],
                textStyle: { color: '#999' },
                top: 5
            },
            grid: { left: '5%', right: '5%', top: 55, bottom: 80, containLabel: true },
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: '#555' } },
                axisLabel: { fontSize: 10, color: '#999' }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '净值',
                    position: 'left',
                    nameTextStyle: { color: '#4facfe' },
                    axisLine: { lineStyle: { color: '#4facfe' } },
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#222' } }
                },
                {
                    type: 'value',
                    name: '收益率/回撤 %',
                    position: 'right',
                    nameTextStyle: { color: '#00f2fe' },
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
                    name: '净值',
                    type: 'line',
                    yAxisIndex: 0,
                    data: nav,
                    smooth: true,
                    lineStyle: { color: '#4facfe', width: 2 },
                    areaStyle: { color: 'rgba(79,172,254,0.08)' },
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
                    name: '回撤',
                    type: 'line',
                    yAxisIndex: 1,
                    data: drawdown,
                    smooth: true,
                    lineStyle: { color: '#ff5252', width: 1.5, type: 'dashed' },
                    areaStyle: { color: 'rgba(255,82,82,0.08)' },
                    symbol: 'none'
                },
                {
                    name: '买入',
                    type: 'scatter',
                    yAxisIndex: 0,
                    data: buyScatter,
                    symbol: 'triangle',
                    symbolSize: 12,
                    itemStyle: { color: '#ff4757' },
                    z: 10
                },
                {
                    name: '卖出',
                    type: 'scatter',
                    yAxisIndex: 0,
                    data: sellScatter,
                    symbol: 'pin',
                    symbolSize: 14,
                    symbolRotate: 180,
                    itemStyle: { color: '#2ed573' },
                    z: 10
                }
            ]
        };

        equityChartInstance.setOption(option, true);

        // resize 监听
        window.removeEventListener('resize', this._onWindowResize);
        this._onWindowResize = () => equityChartInstance?.resize();
        window.addEventListener('resize', this._onWindowResize);
    },

    // ============================
    // 成交列表
    // ============================

    renderTradesTable() {
        const data = this.getCurrentData();
        if (!data) return;

        let trades = data.trades || [];

        // 搜索过滤
        if (tradesSearchKeyword) {
            trades = trades.filter(t =>
                (t.code || '').toLowerCase().includes(tradesSearchKeyword) ||
                (t.name || '').toLowerCase().includes(tradesSearchKeyword)
            );
        }

        // 排序
        trades = [...trades].sort((a, b) => {
            let va = a[tradesSortField];
            let vb = b[tradesSortField];
            if (typeof va === 'string') {
                va = va || '';
                vb = vb || '';
                return tradesSortOrder === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va);
            }
            va = va ?? 0;
            vb = vb ?? 0;
            return tradesSortOrder === 'asc' ? va - vb : vb - va;
        });

        // 更新排序指示器
        const table = document.getElementById('bt-trades-table');
        if (table) {
            table.querySelectorAll('thead th').forEach(th => {
                th.classList.remove('sort-asc', 'sort-desc');
                if (th.dataset.sort === tradesSortField) {
                    th.classList.add(tradesSortOrder === 'asc' ? 'sort-asc' : 'sort-desc');
                }
            });
        }

        // 渲染
        const tbody = document.getElementById('bt-trades-tbody');
        if (!tbody) return;

        // 更新计数
        const countEl = document.getElementById('bt-trades-count-display');
        if (countEl) countEl.textContent = `${trades.length} 笔`;

        if (trades.length === 0) {
            tbody.innerHTML = `<tr><td colspan="10" style="text-align:center;color:#8b95aa;padding:30px;">暂无成交记录</td></tr>`;
            return;
        }

        tbody.innerHTML = trades.map((t, idx) => {
            const profitPct = t.profit_pct ?? 0;
            const profitCls = profitPct >= 0 ? 'td-profit-pos' : 'td-profit-neg';
            const profitMoney = t.profit_money ?? 0;
            const profitMoneyCls = profitMoney >= 0 ? 'td-profit-pos' : 'td-profit-neg';
            return `
                <tr data-trade-index="${idx}" data-trade-id="${t.trade_id || idx}">
                    <td>${idx + 1}</td>
                    <td>${t.buy_date || '--'}</td>
                    <td>${t.sell_date || '--'}</td>
                    <td>${t.hold_days ?? '--'}</td>
                    <td class="td-code">${t.code || '--'}</td>
                    <td>${t.name || '--'}</td>
                    <td>${t.buy_price != null ? t.buy_price.toFixed(2) : '--'}</td>
                    <td>${t.sell_price != null ? t.sell_price.toFixed(2) : '--'}</td>
                    <td class="${profitCls}">${profitPct >= 0 ? '+' : ''}${profitPct.toFixed(2)}%</td>
                    <td class="${profitMoneyCls}">${profitMoney >= 0 ? '+' : ''}${profitMoney.toFixed(2)}</td>
                    <td><button class="td-view-btn" data-trade-idx="${idx}">📈 K线</button></td>
                </tr>
            `;
        }).join('');

        // 绑定行点击 => K线
        tbody.querySelectorAll('.td-view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.tradeIdx);
                const allTrades = this.getCurrentData()?.trades || [];
                // 需要从筛选后的数组取
                if (idx >= 0 && idx < trades.length) {
                    this.openKlineModal(trades[idx]);
                }
            });
        });
    },

    // ============================
    // K线弹窗
    // ============================

    openKlineModal(trade) {
        const modal = document.getElementById('bt-kline-modal');
        if (!modal) return;

        modal.classList.add('active');

        // 填充头部信息
        const codeEl = document.getElementById('bt-kline-code');
        const nameEl = document.getElementById('bt-kline-name');
        const buyInfoEl = document.getElementById('bt-kline-buy-info');
        const sellInfoEl = document.getElementById('bt-kline-sell-info');
        const profitInfoEl = document.getElementById('bt-kline-profit-info');

        if (codeEl) codeEl.textContent = trade.code || '--';
        if (nameEl) nameEl.textContent = trade.name || '--';
        if (buyInfoEl) buyInfoEl.textContent = `${trade.buy_date || '--'} @${trade.buy_price != null ? trade.buy_price.toFixed(2) : '--'}`;
        if (sellInfoEl) sellInfoEl.textContent = `${trade.sell_date || '--'} @${trade.sell_price != null ? trade.sell_price.toFixed(2) : '--'}`;
        if (profitInfoEl) {
            const pct = trade.profit_pct ?? 0;
            profitInfoEl.textContent = `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;
            profitInfoEl.className = `info-value ${pct >= 0 ? 'profit-pos' : 'profit-neg'}`;
        }

        // 渲染K线
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
                title: {
                    text: '暂无K线数据',
                    left: 'center',
                    top: 'center',
                    textStyle: { color: '#8b95aa', fontSize: 16 }
                }
            });
            return;
        }

        const dates = kline.dates;
        const ohlc = kline.ohlc; // [[open,close,low,high], ...]
        const volumes = kline.volumes || [];

        // 找到买入和卖出的日期index
        const buyIdx = dates.indexOf(trade.buy_date);
        const sellIdx = dates.indexOf(trade.sell_date);

        // 买入卖出标注
        const markPoints = [];
        if (buyIdx >= 0) {
            markPoints.push({
                name: '买入',
                coord: [buyIdx, ohlc[buyIdx][2] * 0.98], // low 下方
                value: `买入\n${trade.buy_price?.toFixed(2)}`,
                symbol: 'arrow',
                symbolSize: 14,
                symbolRotate: 0,
                itemStyle: { color: '#ff4757' },
                label: {
                    show: true,
                    position: 'bottom',
                    color: '#ff4757',
                    fontSize: 11,
                    formatter: `买入\n¥${trade.buy_price?.toFixed(2) || ''}`
                }
            });
        }
        if (sellIdx >= 0) {
            markPoints.push({
                name: '卖出',
                coord: [sellIdx, ohlc[sellIdx][3] * 1.02], // high 上方
                value: `卖出\n${trade.sell_price?.toFixed(2)}`,
                symbol: 'pin',
                symbolSize: 16,
                symbolRotate: 180,
                itemStyle: { color: '#2ed573' },
                label: {
                    show: true,
                    position: 'top',
                    color: '#2ed573',
                    fontSize: 11,
                    formatter: `卖出\n¥${trade.sell_price?.toFixed(2) || ''}`
                }
            });
        }

        // 持仓区间高亮
        const markAreaData = [];
        if (buyIdx >= 0 && sellIdx >= 0) {
            markAreaData.push([
                { xAxis: buyIdx, itemStyle: { color: 'rgba(79,172,254,0.06)' } },
                { xAxis: sellIdx }
            ]);
        }

        const option = {
            backgroundColor: 'transparent',
            title: {
                text: `${trade.code} ${trade.name}`,
                left: 'center',
                textStyle: { color: '#e6eaf2', fontSize: 15 }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                backgroundColor: 'rgba(0,0,0,0.85)',
                borderColor: '#4facfe'
            },
            grid: [
                { left: '6%', right: '4%', top: 50, height: '55%' },
                { left: '6%', right: '4%', top: '72%', height: '18%' }
            ],
            xAxis: [
                {
                    type: 'category',
                    data: dates,
                    gridIndex: 0,
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: { show: false }
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
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#222' } }
                },
                {
                    type: 'value',
                    gridIndex: 1,
                    axisLine: { lineStyle: { color: '#555' } },
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#222' } }
                }
            ],
            dataZoom: [
                { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
                { type: 'slider', xAxisIndex: [0, 1], bottom: 5, start: 0, end: 100, textStyle: { color: '#999' } }
            ],
            series: [
                {
                    type: 'candlestick',
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    data: ohlc,
                    itemStyle: {
                        color: '#ec0000',
                        color0: '#00da3c',
                        borderColor: '#8A0000',
                        borderColor0: '#008F28'
                    },
                    markPoint: {
                        data: markPoints,
                        animation: true
                    },
                    markArea: {
                        silent: true,
                        data: markAreaData
                    }
                },
                {
                    type: 'bar',
                    xAxisIndex: 1,
                    yAxisIndex: 1,
                    data: volumes,
                    itemStyle: {
                        color: (params) => {
                            const idx = params.dataIndex;
                            if (idx > 0 && ohlc[idx] && ohlc[idx - 1]) {
                                return ohlc[idx][1] >= ohlc[idx][0] ? '#ec0000' : '#00da3c';
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
    // 导出成交CSV
    // ============================

    exportTradesCSV() {
        const data = this.getCurrentData();
        if (!data || !data.trades || data.trades.length === 0) {
            App.log('暂无成交数据可导出', 'warning');
            return;
        }

        const trades = data.trades;
        const header = '序号,买入日期,卖出日期,持仓天数,股票代码,股票名称,买入价,卖出价,盈利(%),盈利(元)\n';
        const rows = trades.map((t, i) =>
            `${i + 1},${t.buy_date},${t.sell_date},${t.hold_days},${t.code},${t.name},${t.buy_price?.toFixed(2)},${t.sell_price?.toFixed(2)},${t.profit_pct?.toFixed(2)},${t.profit_money?.toFixed(2)}`
        ).join('\n');

        const bom = '\uFEFF';
        const blob = new Blob([bom + header + rows], { type: 'text/csv;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `backtest_trades_${currentDivisionId}_${Date.now()}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        App.log('成交记录已导出为CSV', 'success');
    },

    // ============================
    // 格式化工具
    // ============================

    formatPercent(val) {
        if (val == null || isNaN(val)) return '--';
        return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
    },

    formatMoney(val) {
        if (val == null || isNaN(val)) return '--';
        return `¥${val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
};