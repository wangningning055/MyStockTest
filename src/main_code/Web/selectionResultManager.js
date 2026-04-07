/**
 * selectionResultManager.js - 选股结果管理模块
 * 
 * 职责：
 * - 管理选股结果数据
 * - 结果列表渲染与排序
 * - 搜索过滤
 * - 个股详情弹窗（K线图 + 参数面板）
 * - 流式K线数据接收
 */

import { App } from './app.js';

let manager = null;

// ===== 模块内部状态 =====
const ResultState = {
    // 原始结果数据
    rawStocks: [],
    // 过滤后的数据
    filteredStocks: [],
    // 排序状态
    sortField: 'score',
    sortDirection: 'desc', // 'asc' | 'desc'
    // 搜索关键字
    searchKeyword: '',
    // 当前选中的股票（用于详情弹窗）
    selectedStock: null,
    // K线图表实例
    klineChart: null,
    // 流式K线数据缓冲
    klineBuffer: [],
    // 流式加载状态
    isLoadingKline: false,
};

export function setSelectionResultManager(_manager) {
    manager = _manager;
}

export const SelectionResultManager = {

    /**
     * 初始化模块
     */
    init() {
        this.bindEvents();
        console.log('✅ SelectionResultManager 初始化完成');
        return this;
    },

    /**
     * 绑定所有事件
     */
    bindEvents() {
        // 查看结果按钮
        const viewResultBtn = document.getElementById('btn-view-selection-result');
        if (viewResultBtn) {
            viewResultBtn.addEventListener('click', () => this.showResultView());
        }

        // 返回配置按钮
        const backBtn = document.getElementById('btn-back-to-config');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showConfigView());
        }

        // 搜索过滤
        const filterInput = document.getElementById('sr-filter-input');
        if (filterInput) {
            filterInput.addEventListener('input', (e) => {
                ResultState.searchKeyword = e.target.value.trim().toLowerCase();
                this.applyFilterAndSort();
            });
        }

        // 排序按钮
        document.querySelectorAll('.sr-sort-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleSortClick(btn));
        });

        // 弹窗关闭
        const closeBtn = document.getElementById('sdm-close');
        const overlay = document.getElementById('sdm-overlay');
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeDetailModal());
        if (overlay) overlay.addEventListener('click', () => this.closeDetailModal());

        // ESC 关闭弹窗
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDetailModal();
            }
        });

        // 参数搜索
        const paramFilter = document.getElementById('sdm-param-filter');
        if (paramFilter) {
            paramFilter.addEventListener('input', (e) => {
                this.filterParams(e.target.value.trim().toLowerCase());
            });
        }
    },

    // ============================
    // 视图切换
    // ============================

    showConfigView() {
        document.getElementById('selection-config-view')?.classList.add('active');
        document.getElementById('selection-result-view')?.classList.remove('active');
    },

    showResultView() {
        document.getElementById('selection-config-view')?.classList.remove('active');
        document.getElementById('selection-result-view')?.classList.add('active');
        // 重新渲染（可能窗口尺寸变了）
        this.applyFilterAndSort();
    },

    // ============================
    // 数据接收
    // ============================

    /**
     * 接收选股结果数据（由 AppManager 调用）
     * @param {Array} stocks - 股票列表
     */
    setResultData(stocks) {
        ResultState.rawStocks = stocks || [];
        ResultState.searchKeyword = '';
        ResultState.sortField = 'score';
        ResultState.sortDirection = 'desc';

        // 更新结果数量
        const countEl = document.getElementById('selection-result-count');
        if (countEl) countEl.textContent = ResultState.rawStocks.length;

        const totalCountEl = document.getElementById('sr-total-count');
        if (totalCountEl) totalCountEl.textContent = ResultState.rawStocks.length;

        // 显示"查看结果"按钮
        const viewBtn = document.getElementById('btn-view-selection-result');
        if (viewBtn) viewBtn.style.display = 'inline-flex';

        // 隐藏loading
        const loadingEl = document.getElementById('selection-loading');
        if (loadingEl) loadingEl.style.display = 'none';

        // 重置排序按钮状态
        document.querySelectorAll('.sr-sort-btn').forEach(btn => {
            btn.classList.remove('active', 'asc', 'desc');
        });
        const defaultSortBtn = document.querySelector('.sr-sort-btn[data-sort="score"]');
        if (defaultSortBtn) {
            defaultSortBtn.classList.add('active', 'desc');
        }

        // 清空搜索
        const filterInput = document.getElementById('sr-filter-input');
        if (filterInput) filterInput.value = '';

        this.applyFilterAndSort();

        App.log(`📊 选股结果已加载，共 ${stocks.length} 只股票`, 'success');
    },

    /**
     * 显示加载中状态
     */
    showLoading() {
        const loadingEl = document.getElementById('selection-loading');
        if (loadingEl) loadingEl.style.display = 'inline-flex';

        const viewBtn = document.getElementById('btn-view-selection-result');
        if (viewBtn) viewBtn.style.display = 'none';
    },

    // ============================
    // 过滤与排序
    // ============================

    applyFilterAndSort() {
        let data = [...ResultState.rawStocks];

        // 搜索过滤
        if (ResultState.searchKeyword) {
            const kw = ResultState.searchKeyword;
            data = data.filter(s =>
                (s.code && s.code.toLowerCase().includes(kw)) ||
                (s.name && s.name.toLowerCase().includes(kw)) ||
                (s.industry && s.industry.toLowerCase().includes(kw))
            );
        }

        // 排序
        const field = ResultState.sortField;
        const dir = ResultState.sortDirection === 'asc' ? 1 : -1;
        data.sort((a, b) => {
            let va = a[field] ?? 0;
            let vb = b[field] ?? 0;
            if (typeof va === 'string') va = va.localeCompare(vb);
            else va = va - vb;
            return va * dir;
        });

        ResultState.filteredStocks = data;

        // 更新显示数量
        const totalCountEl = document.getElementById('sr-total-count');
        if (totalCountEl) totalCountEl.textContent = data.length;

        this.renderTable(data);
    },

    handleSortClick(btn) {
        const field = btn.dataset.sort;

        if (ResultState.sortField === field) {
            // 切换升降序
            ResultState.sortDirection = ResultState.sortDirection === 'desc' ? 'asc' : 'desc';
        } else {
            ResultState.sortField = field;
            ResultState.sortDirection = 'desc';
        }

        // 更新按钮样式
        document.querySelectorAll('.sr-sort-btn').forEach(b => {
            b.classList.remove('active', 'asc', 'desc');
        });
        btn.classList.add('active', ResultState.sortDirection);

        this.applyFilterAndSort();
    },

    // ============================
    // 表格渲染
    // ============================

    renderTable(stocks) {
        const tbody = document.getElementById('sr-table-body');
        if (!tbody) return;

        if (!stocks || stocks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="14" class="sr-empty">暂无匹配数据</td></tr>';
            return;
        }

        const fragment = document.createDocumentFragment();

        stocks.forEach((stock, index) => {
            const tr = document.createElement('tr');
            tr.dataset.code = stock.code;
            tr.addEventListener('click', () => this.openDetailModal(stock));

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td style="font-family:monospace; color:#4facfe;">${stock.code || '--'}</td>
                <td style="color:#e6eaf2; font-weight:500;">${stock.name || '--'}</td>
                <td style="color:#ffb74d; font-weight:600;">${this.fmt(stock.score, 2)}</td>
                <td>${stock.industry || '--'}</td>
                <td>${this.fmtMarketCap(stock.market_cap)}</td>
                ${this.changeTd(stock.change_3d)}
                ${this.changeTd(stock.change_5d)}
                ${this.changeTd(stock.change_10d)}
                ${this.changeTd(stock.change_20d)}
                ${this.changeTd(stock.change_40d)}
                ${this.changeTd(stock.change_60d)}
                ${this.changeTd(stock.change_120d)}
                ${this.changeTd(stock.change_240d)}
            `;

            fragment.appendChild(tr);
        });

        tbody.innerHTML = '';
        tbody.appendChild(fragment);
    },

    /**
     * 格式化涨跌幅 TD
     */
    changeTd(val) {
        if (val === null || val === undefined || isNaN(val)) {
            return '<td class="change-zero">--</td>';
        }
        const cls = val > 0 ? 'change-up' : val < 0 ? 'change-down' : 'change-zero';
        const prefix = val > 0 ? '+' : '';
        return `<td class="${cls}">${prefix}${val.toFixed(2)}%</td>`;
    },

    fmt(val, digits = 2) {
        if (val === null || val === undefined || isNaN(val)) return '--';
        return Number(val).toFixed(digits);
    },

    fmtMarketCap(val) {
        if (!val) return '--';
        if (val >= 100000000) return (val / 100000000).toFixed(2) + '亿';
        if (val >= 10000) return (val / 10000).toFixed(2) + '万';
        return val.toFixed(2);
    },

    // ============================
    // 个股详情弹窗
    // ============================

    openDetailModal(stock) {
        ResultState.selectedStock = stock;
        ResultState.klineBuffer = [];
        ResultState.isLoadingKline = false;

        // 填充头部信息
        document.getElementById('sdm-stock-code').textContent = stock.code || '--';
        document.getElementById('sdm-stock-name').textContent = stock.name || '--';
        document.getElementById('sdm-stock-industry').textContent = stock.industry || '--';

        // 清空K线图
        this.initKlineChart();

        // 渲染参数
        this.renderParams(stock.params || stock);

        // 显示弹窗
        document.getElementById('stock-detail-modal').classList.add('open');
        document.body.style.overflow = 'hidden';

        // 请求K线数据（流式）
        this.requestKlineData(stock.code);

        App.log(`📈 打开个股详情: ${stock.code} ${stock.name}`, 'system');
    },

    closeDetailModal() {
        document.getElementById('stock-detail-modal')?.classList.remove('open');
        document.body.style.overflow = '';
        ResultState.selectedStock = null;
        ResultState.isLoadingKline = false;

        // 销毁图表以释放内存
        if (ResultState.klineChart) {
            ResultState.klineChart.dispose();
            ResultState.klineChart = null;
        }
    },

    // ============================
    // K线图
    // ============================

    initKlineChart() {
        const container = document.getElementById('sdm-kline-chart');
        if (!container) return;

        if (ResultState.klineChart) {
            ResultState.klineChart.dispose();
        }

        ResultState.klineChart = echarts.init(container, 'dark');

        // 设置空白初始 option
        ResultState.klineChart.setOption({
            backgroundColor: 'transparent',
            title: {
                text: '等待K线数据...',
                left: 'center',
                textStyle: { color: '#555', fontSize: 14 }
            }
        });

        // 响应容器尺寸变化
        const resizeObserver = new ResizeObserver(() => {
            ResultState.klineChart?.resize();
        });
        resizeObserver.observe(container);
    },

    /**
     * 请求K线数据（通过 WebSocket 或流式 HTTP）
     */
    requestKlineData(stockCode) {
        ResultState.isLoadingKline = true;
        ResultState.klineBuffer = [];

        const loadingEl = document.getElementById('sdm-chart-loading');
        const progressEl = document.getElementById('sdm-chart-progress');
        if (loadingEl) loadingEl.style.display = 'flex';
        if (progressEl) progressEl.textContent = '0';

        // 通过 WebSocket 请求
        if (manager && manager.socket) {
            manager.socket.sendMessage('cs_request_kline', {
                code: stockCode,
                days: 240,
                timestamp: new Date().toISOString()
            });
        }
    },

    /**
     * 接收流式K线数据块（由消息处理器调用）
     * @param {Object} data - { code, chunk, progress, is_last, total }
     */
    receiveKlineChunk(data) {
        if (!ResultState.isLoadingKline) return;
        if (data.code !== ResultState.selectedStock?.code) return;

        // 追加数据
        if (data.chunk && Array.isArray(data.chunk)) {
            ResultState.klineBuffer.push(...data.chunk);
        }

        // 更新进度
        const progressEl = document.getElementById('sdm-chart-progress');
        if (progressEl && data.progress !== undefined) {
            progressEl.textContent = Math.round(data.progress * 100);
        }

        // 如果是最后一块，绘制完整K线
        if (data.is_last) {
            ResultState.isLoadingKline = false;
            const loadingEl = document.getElementById('sdm-chart-loading');
            if (loadingEl) loadingEl.style.display = 'none';

            this.drawKlineChart(ResultState.klineBuffer);
        }
    },

    /**
     * 一次性接收全部K线数据（非流式兼容）
     * @param {Object} data - { code, kline: [...] }
     */
    receiveKlineData(data) {
        if (data.code !== ResultState.selectedStock?.code) return;

        ResultState.isLoadingKline = false;
        const loadingEl = document.getElementById('sdm-chart-loading');
        if (loadingEl) loadingEl.style.display = 'none';

        this.drawKlineChart(data.kline || []);
    },

    /**
     * 绘制K线图
     * @param {Array} klineData - [{date, open, close, high, low, volume}, ...]
     */
    drawKlineChart(klineData) {
        if (!ResultState.klineChart || !klineData.length) {
            if (ResultState.klineChart) {
                ResultState.klineChart.setOption({
                    title: { text: '暂无K线数据', left: 'center', textStyle: { color: '#555' } }
                });
            }
            return;
        }

        const dates = klineData.map(d => d.date);
        //const ohlc = klineData.map(d => [d.open, d.close, d.low, d.high]);
        const ohlc = klineData.map(d => ({
            value: [d.open, d.close, d.low, d.high,d.volume],
            ...d   // 👈 保留所有字段
        }));
        const volumes = klineData.map(d => d.volume || 0);
        const turn = klineData.map(d => d.turn || 0);
        // 计算MA
        const ma5 = this.calcMA(klineData.map(d => d.close), 5);
        const ma10 = this.calcMA(klineData.map(d => d.close), 10);
        const ma20 = this.calcMA(klineData.map(d => d.close), 20);
        const ma60 = this.calcMA(klineData.map(d => d.close), 60);

        const option = {
            backgroundColor: 'transparent',
            title: { show: false },
                tooltip: {
                    xAxisIndex: 0,
                    trigger: 'axis',
                    axisPointer: { type: 'cross' },
                    backgroundColor: 'rgba(0,0,0,0.85)',
                    borderColor: '#4facfe',
                    textStyle: { fontSize: 12 },
                    formatter: (params) => {
                        const isMain = params.some(p => p.seriesType === 'candlestick');
                        const data = params[0].data;
                        const color = data.change_Ratio >= 0 ? '#ec0000' : '#00da3c';
                        console.log("》》》》》》》》》》》》》》》》")
                        console.log(data)

                        if (!isMain) {
                            return `
                            成交量（万手）：${data.value}<br/>
                        `;
                        }



                        return `
                            日期：${data.date}<br/>
                            涨跌：<span style="color:${color}">
                                ${(data.change_Ratio ?? 0).toFixed(2)}%
                            </span><br/>
                            换手：${data.turn}%<br/>
                            开：${data.open}<br/>
                            收：${data.close}<br/>
                            高：${data.high}<br/>
                            低：${data.low}<br/>

                        `;
                },
            },
            legend: {
                data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60'],
                textStyle: { color: '#e2e2e2', fontSize: 11 },
                top: 5,
                right: 10
            },
            grid: [
                { left: '8%', right: '3%', top: '12%', height: '58%' },
                { left: '8%', right: '3%', top: '75%', height: '18%' }
            ],
            xAxis: [
                {
                    type: 'category',
                    data: dates,
                    gridIndex: 0,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { show: false },
                    splitLine: { show: false }
                },
                {
                    type: 'category',
                    data: dates,
                    gridIndex: 1,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { fontSize: 10, color: '#c0bfbf', interval: 'auto' },
                    splitLine: { show: false }
                }
            ],
            yAxis: [
                {
                    type: 'value',
                    gridIndex: 0,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { fontSize: 10, color: '#c7c7c7' },
                    splitLine: { lineStyle: { color: '#222' } },
                    scale: true
                },
                {
                    type: 'value',
                    gridIndex: 1,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { show: false },
                    splitLine: { show: false }
                }


            ],
            dataZoom: [
                {
                    type: 'inside',
                    xAxisIndex: [0, 1],
                    start: Math.max(0, 100 - Math.min(80, klineData.length / 2)),
                    end: 100
                },
                {
                    type: 'slider',
                    xAxisIndex: [0, 1],
                    start: Math.max(0, 100 - Math.min(80, klineData.length / 2)),
                    end: 100,
                    top: '95%',
                    height: 15,
                    textStyle: { color: '#cfcfcf' }
                }
            ],
            series: [
                {
                    name: 'K线',
                    type: 'candlestick',
                    data: ohlc,
                    xAxisIndex: 0,
                    yAxisIndex: 0,
                    itemStyle: {
                        color: '#ec0000',
                        color0: '#00da3c',
                        borderColor: '#8A0000',
                        borderColor0: '#008F28'
                    }
                },
                this.maLine('MA5', ma5, '#f5a623'),
                this.maLine('MA10', ma10, '#4facfe'),
                this.maLine('MA20', ma20, '#f093fb'),
                this.maLine('MA60', ma60, '#2ed573'),
                {
                    name: '成交量（万手）',
                    type: 'bar',
                    data: volumes.map((v, i) => ({
                        value: v,
                        itemStyle: {
                            color: klineData[i].close >= klineData[i].open
                                ? 'rgba(236,0,0,0.5)'
                                : 'rgba(0,218,60,0.5)'
                        }
                    })),
                    xAxisIndex: 1,
                    yAxisIndex: 1
                }

            ]
        };

        ResultState.klineChart.setOption(option, true);
        App.log(`📈 K线图已绘制，共 ${klineData.length} 根`, 'success');
    },

    maLine(name, data, color) {
        return {
            name: name,
            type: 'line',
            data: data,
            xAxisIndex: 0,
            yAxisIndex: 0,
            smooth: true,
            showSymbol: false,
            lineStyle: { color: color, width: 1 }
        };
    },

    calcMA(closes, period) {
        const result = [];
        for (let i = 0; i < closes.length; i++) {
            if (i < period - 1) {
                result.push(null);
            } else {
                let sum = 0;
                for (let j = 0; j < period; j++) sum += closes[i - j];
                result.push(+(sum / period).toFixed(2));
            }
        }
        return result;
    },

    // ============================
    // 详细参数渲染
    // ============================

    /**
     * 渲染参数面板
     * @param {Object} params - 参数数据（支持分组）
     * 
     * 数据格式：
     * {
     *   groups: [
     *     {
     *       name: "基本信息",
     *       items: [
     *         { label: "股票代码", value: "600000", type: "text" },
     *         { label: "涨跌幅", value: 5.23, type: "percent" },
     *         ...
     *       ]
     *     },
     *     ...
     *   ]
     * }
     * 
     * 如果没有 groups 字段，则将所有字段平铺到一个默认分组
     */
    renderParams(params) {
        const container = document.getElementById('sdm-params-container');
        if (!container) return;

        // 清空搜索
        const paramFilter = document.getElementById('sdm-param-filter');
        if (paramFilter) paramFilter.value = '';

        let groups = [];

        if (params && params.groups && Array.isArray(params.groups)) {
            groups = params.groups;
        } else if (params) {
            // 将扁平对象转成单组
            const items = [];
            const skipKeys = [
                'code', 'name', 'industry', 'score', 'params',
                'market_cap', 'change_3d', 'change_5d', 'change_10d',
                'change_20d', 'change_40d', 'change_60d', 'change_120d', 'change_240d'
            ];
            for (const [key, val] of Object.entries(params)) {
                if (skipKeys.includes(key)) continue;
                if (typeof val === 'object' && val !== null) continue;
                items.push({
                    label: key,
                    value: val,
                    type: typeof val === 'number' ? 'number' : 'text'
                });
            }
            if (items.length > 0) {
                groups.push({ name: '其他参数', items });
            }
        }

        if (groups.length === 0) {
            container.innerHTML = '<div style="color:#555; text-align:center; padding:30px;">暂无参数数据</div>';
            return;
        }

        const fragment = document.createDocumentFragment();

        groups.forEach((group, gi) => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'sdm-param-group';
            groupDiv.dataset.groupIndex = gi;

            // 分组标题
            const titleDiv = document.createElement('div');
            titleDiv.className = 'sdm-param-group-title';
            titleDiv.innerHTML = `
                <span>${group.name || '未命名分组'} (${(group.items || []).length})</span>
                <span class="toggle-icon">▼</span>
            `;
            titleDiv.addEventListener('click', () => {
                groupDiv.classList.toggle('collapsed');
            });

            // 分组内容
            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'sdm-param-group-body';

            (group.items || []).forEach(item => {
                const row = document.createElement('div');
                row.className = 'sdm-param-row';
                row.dataset.label = (item.label || '').toLowerCase();

                const valueStr = this.formatParamValue(item.value, item.type);
                const valueClass = this.getParamValueClass(item.value, item.type);

                row.innerHTML = `
                    <span class="sdm-param-label" title="${item.label || ''}">${item.label || '--'}</span>
                    <span class="sdm-param-value ${valueClass}">${valueStr}</span>
                `;

                bodyDiv.appendChild(row);
            });

            groupDiv.appendChild(titleDiv);
            groupDiv.appendChild(bodyDiv);
            fragment.appendChild(groupDiv);
        });

        container.innerHTML = '';
        container.appendChild(fragment);
    },

    formatParamValue(value, type) {
        if (value === null || value === undefined) return '--';
        switch (type) {
            case 'percent':
                return (value >= 0 ? '+' : '') + Number(value).toFixed(2) + '%';
            case 'currency':
                return '¥' + Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 });
            case 'market_cap':
                if (value >= 1e8) return (value / 1e8).toFixed(2) + '亿';
                if (value >= 1e4) return (value / 1e4).toFixed(2) + '万';
                return Number(value).toFixed(2);
            case 'number':
                return Number(value).toFixed(2);
            default:
                return String(value);
        }
    },

    getParamValueClass(value, type) {
        if (type === 'percent' || type === 'number') {
            if (Number(value) > 0) return 'positive';
            if (Number(value) < 0) return 'negative';
        }
        return '';
    },

    /**
     * 搜索参数
     */
    filterParams(keyword) {
        const container = document.getElementById('sdm-params-container');
        if (!container) return;

        const rows = container.querySelectorAll('.sdm-param-row');
        const groups = container.querySelectorAll('.sdm-param-group');

        if (!keyword) {
            rows.forEach(r => r.style.display = '');
            groups.forEach(g => {
                g.style.display = '';
                g.classList.remove('collapsed');
            });
            return;
        }

        groups.forEach(group => {
            let visibleCount = 0;
            const groupRows = group.querySelectorAll('.sdm-param-row');
            groupRows.forEach(row => {
                const label = row.dataset.label || '';
                if (label.includes(keyword)) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });
            group.style.display = visibleCount > 0 ? '' : 'none';
            if (visibleCount > 0) group.classList.remove('collapsed');
        });
    },

    // ============================
    // 获取当前结果数据（供外部使用）
    // ============================

    getResultData() {
        return ResultState.rawStocks;
    },

    getSelectedStock() {
        return ResultState.selectedStock;
    }
};