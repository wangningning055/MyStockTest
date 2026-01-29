/**
 * ============================================================
 * 哇哈哈量化系统 Pro v3.1 - 修复版
 * ============================================================
 * 
 * 主要改进：
 * ✅ 修复图表显示宽度过窄问题
 * ✅ 修复图表纵向显示不全问题
 * ✅ 添加ST股、科创板、创业板勾选过滤
 * ✅ 添加选股说明文字区域
 * ✅ 选股结果添加行业列，移除操作列
 * ✅ 点击股票可在说明区域显示内容
 */

const CONFIG = {
    factorTypes: ["市盈率 PE", "市净率 PB", "均线金叉", "MACD底背离", "RSI超卖", "自定义公式"],
    apiBase: "http://127.0.0.1:5000/api" 
};

const State = {
    buyFactors: [],
    sellFactors: [],
    holdings: [],
    initialFund: 100000,
    selectedStock: null
};

const ChartInstances = {
    klineChart: null,
    portfolioChart: null
};
const Message_Action = "/action"
const MessageType = {
    UPDATE_DATA : "update_data",
    SELECT_STOCKS : "select_stocks",
    BACK_TEST : "back_test",
    DIAGNOSE : "diagnose"
}

/**
 * UIManager - UI 数据接口
 */
const UIManager = {
    getTushareToken() { return document.getElementById('tushareToken').value; },
    setTushareToken(token) { document.getElementById('tushareToken').value = token; },
    getInitialFund() { return parseFloat(document.getElementById('initialFundInput').value) || 100000; },
    setInitialFund(amount) { 
        document.getElementById('initialFundInput').value = amount;
        State.initialFund = amount;
    },
    getBacktestDateRange() {
        return {
            startDate: document.getElementById('bt-start-date').value,
            endDate: document.getElementById('bt-end-date').value
        };
    },
    setBacktestDateRange(startDate, endDate) {
        document.getElementById('bt-start-date').value = startDate;
        document.getElementById('bt-end-date').value = endDate;
    },
    getBacktestIsIdeal() { return document.getElementById('bt-is-ideal').checked; },
    setBacktestIsIdeal(checked) { document.getElementById('bt-is-ideal').checked = checked; },
    getBacktestBuySource() { return document.getElementById('backtest-buy-source').value; },
    setBacktestBuySource(source) { document.getElementById('backtest-buy-source').value = source; },
    getBacktestSellSource() { return document.getElementById('backtest-sell-source').value; },
    setBacktestSellSource(source) { document.getElementById('backtest-sell-source').value = source; },

    // 股票过滤选项
    getFilterExcludeST() { 
        const elem = document.getElementById('filter-exclude-st');
        return elem ? elem.checked : false;
    },
    setFilterExcludeST(checked) { 
        const elem = document.getElementById('filter-exclude-st');
        if (elem) elem.checked = checked;
    },
    
    getFilterExcludeKC() { 
        const elem = document.getElementById('filter-exclude-kc');
        return elem ? elem.checked : false;
    },
    setFilterExcludeKC(checked) { 
        const elem = document.getElementById('filter-exclude-kc');
        if (elem) elem.checked = checked;
    },
    
    getFilterExcludeCY() { 
        const elem = document.getElementById('filter-exclude-cy');
        return elem ? elem.checked : false;
    },
    setFilterExcludeCY(checked) { 
        const elem = document.getElementById('filter-exclude-cy');
        if (elem) elem.checked = checked;
    },

    // 股票说明
    getSelectionDescription() { 
        const elem = document.getElementById('stock-description');
        return elem ? elem.value : '';
    },
    setSelectionDescription(text) { 
        const elem = document.getElementById('stock-description');
        if (elem) elem.value = text;
    },

    getCardWeight(cardId) {
        const card = document.getElementById(cardId);
        if (!card) return null;
        return parseFloat(card.querySelector('.card-weight-input').value) || 0;
    },
    setCardWeight(cardId, weight) {
        const card = document.getElementById(cardId);
        if (!card) return false;
        card.querySelector('.card-weight-input').value = weight;
        return true;
    },

    getCardTitle(cardId) {
        const card = document.getElementById(cardId);
        return card ? card.querySelector('.card-title').textContent : null;
    },
    setCardTitle(cardId, title) {
        const card = document.getElementById(cardId);
        if (card) card.querySelector('.card-title').textContent = title;
        return !!card;
    },

    getConditionOperator(row) { 
        const select = row.querySelector('.cond-op');
        return select ? select.value : null;
    },
    setConditionOperator(row, operator) {
        const select = row.querySelector('.cond-op');
        if (select) select.value = operator;
        return !!select;
    },

    getConditionValue(row) {
        const input = row.querySelector('.cond-val');
        return input ? parseFloat(input.value) : null;
    },
    setConditionValue(row, value) {
        const input = row.querySelector('.cond-val');
        if (input) input.value = value;
        return !!input;
    },

    getConditionDateRange(row) {
        const inputs = row.querySelectorAll('.date-range-input');
        return inputs.length >= 2 ? {
            fromDays: parseInt(inputs[0].value) || 30,
            toDays: parseInt(inputs[1].value) || 0
        } : null;
    },
    setConditionDateRange(row, fromDays, toDays) {
        const inputs = row.querySelectorAll('.date-range-input');
        if (inputs.length >= 2) {
            inputs[0].value = fromDays;
            inputs[1].value = toDays;
            return true;
        }
        return false;
    },

    getFactorCardIds(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return [];
        return Array.from(container.querySelectorAll('.factor-card')).map(card => card.id);
    },

    clearFactorCards(containerId) {
        const container = document.getElementById(containerId);
        if (container) container.innerHTML = '';
        return !!container;
    },

    getBacktestSummary() {
        return {
            totalPnL: document.getElementById('res-total-pnl').textContent,
            winRate: document.getElementById('res-win-rate').textContent,
            maxDrawdown: document.getElementById('res-max-drawdown').textContent
        };
    },
    setBacktestSummary(totalPnL, winRate, maxDrawdown) {
        document.getElementById('res-total-pnl').textContent = totalPnL;
        document.getElementById('res-win-rate').textContent = winRate;
        document.getElementById('res-max-drawdown').textContent = maxDrawdown;
    },

    getDiagnosisOutput() { return document.getElementById('diagnosis-output').innerHTML; },
    setDiagnosisOutput(content) { document.getElementById('diagnosis-output').innerHTML = content; }
};

document.addEventListener('DOMContentLoaded', () => App.init());

const App = {
    init() {
        this.bindTabs();
        this.bindGlobalEvents();
        this.bindFactorEvents();
        this.bindBacktestEvents();
        this.initCharts();
        this.log("系统引擎启动成功，等待指令...", "system");
    },

    bindTabs() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.target;
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
                document.getElementById(target).classList.add('active');
                this.log(`切换至视图: ${tab.innerText}`, "system");
                setTimeout(() => {
                    if (ChartInstances.klineChart) ChartInstances.klineChart.resize();
                    if (ChartInstances.portfolioChart) ChartInstances.portfolioChart.resize();
                }, 100);
            });
        });
    },

    bindGlobalEvents() {
        data = {
            type:MessageType.UPDATE_DATA,
            payload: {
                reason: "我是金额达到",
                threshold: 100000
            }
        }
        document.getElementById('api-update-data').addEventListener('click', () => this.callBackend(Message_Action, 'POST', data));
        //document.getElementById('api-stop-backend').addEventListener('click', () => {
        //    if(confirm("确定要停止后台服务吗？")) this.callBackend('/stop', 'POST');
        //});
        document.getElementById('api-run-selection').addEventListener('click', () => this.runSelection());
        document.getElementById('api-run-backtest').addEventListener('click', () => this.runBacktest());
        document.getElementById('api-diagnose-holdings').addEventListener('click', () => this.runDiagnosis());
        document.getElementById('btn-clear-log').addEventListener('click', () => {
            document.getElementById('global-log-container').innerHTML = '';
        });
    },

    bindBacktestEvents() {
        document.getElementById('setInitialFundBtn').addEventListener('click', () => {
            const fundValue = UIManager.getInitialFund();
            if (!isNaN(fundValue) && fundValue > 0) {
                UIManager.setInitialFund(fundValue);
                this.log(`初始本金设置为: ¥${fundValue.toLocaleString()}`, "success");
            } else {
                this.log("请输入有效的初始本金金额", "error");
            }
        });
    },

    bindFactorEvents() {
        document.getElementById('btn-add-buy-factor').addEventListener('click', () => this.showFactorModal('buy'));
        document.getElementById('btn-add-sell-factor').addEventListener('click', () => this.showFactorModal('sell'));
        document.getElementById('api-export-buy-config').addEventListener('click', () => this.exportConfig('buy'));
        document.getElementById('api-export-sell-config').addEventListener('click', () => this.exportConfig('sell'));
        document.getElementById('api-import-buy-config').addEventListener('click', () => this.importConfig('buy'));
        document.getElementById('api-import-sell-config').addEventListener('click', () => this.importConfig('sell'));
        document.getElementById('api-load-buy-file').addEventListener('click', () => this.loadConfigFile('backtest-buy-source'));
        document.getElementById('api-load-sell-file').addEventListener('click', () => this.loadConfigFile('backtest-sell-source'));
    },

    renderFactorCard(type, containerId, side) {
        const container = document.getElementById(containerId);
        const cardId = `card-${Date.now()}`;
        const card = document.createElement('div');
        card.className = 'factor-card';
        card.id = cardId;
        card.innerHTML = `
            <div class="card-header">
                <span class="card-title">${type}</span>
                <div class="card-weight-group">
                    <label>权重:</label>
                    <input type="number" class="card-weight-input" value="10" min="0">
                </div>
                <button class="btn-remove-card" onclick="App.removeCard(this)">✕</button>
            </div>
            <div class="conditions-list"></div>
            <div class="card-footer">
                <button class="btn-add-cond" onclick="App.showFactorModal('${side}', '${cardId}')">
                    <i class="fas fa-plus"></i> 插入新判定条件
                </button>
            </div>
        `;
        container.appendChild(card);
        this.addConditionToCard(cardId, type, true);
    },
    
    addConditionToCard(cardId, factorName, isFirst = false) {
        const card = document.getElementById(cardId);
        const list = card.querySelector('.conditions-list');
        const row = document.createElement('div');
        row.className = 'condition-row';
        const headerHtml = isFirst ? '<span class="first-tag">首选</span>' : `<select class="cond-rel"><option value="AND">且</option><option value="OR">或</option></select>`;
        row.innerHTML = `
            <div class="condition-row__header">
                <div class="cond-logic">${headerHtml}</div>
                <div class="cond-name" title="${factorName}">${factorName}</div>
                ${isFirst ? '' : '<button class="btn-del-cond" onclick="App.removeCondition(this)">✕</button>'}
            </div>
            <div class="condition-row__date">
                <span class="condition-row__date-label">日期范围:</span>
                <input type="number" class="date-range-input" value="30" placeholder="天前">
                <span class="date-range-separator">～</span>
                <input type="number" class="date-range-input" value="0" placeholder="天前">
            </div>
            <div class="condition-row__condition">
                <select class="cond-op">
                    <option value="gt">></option>
                    <option value="lt"><</option>
                    <option value="eq">=</option>
                    <option value="ge">≥</option>
                    <option value="le">≤</option>
                </select>
                <input type="number" class="cond-val" value="0" placeholder="条件值">
            </div>
        `;
        list.appendChild(row);
    },

    removeCard(button) { button.closest('.factor-card').remove(); },
    removeCondition(button) { button.parentElement.remove(); },

    getFactorData(containerId) {
        const cards = document.querySelectorAll(`#${containerId} .factor-card`);
        const data = [];
        cards.forEach(card => {
            const weight = UIManager.getCardWeight(card.id);
            const conditions = [];
            card.querySelectorAll('.condition-row').forEach((row, index) => {
                const dateRange = UIManager.getConditionDateRange(row);
                conditions.push({
                    factor_name: row.querySelector('.cond-name').textContent,
                    relation: index === 0 ? "START" : (row.querySelector('.cond-rel')?.value || "AND"),
                    operator: UIManager.getConditionOperator(row),
                    value: UIManager.getConditionValue(row),
                    dateFrom: dateRange?.fromDays || 30,
                    dateTo: dateRange?.toDays || 0
                });
            });
            data.push({
                factor_group_name: UIManager.getCardTitle(card.id),
                weight: weight,
                logic_tree: conditions
            });
        });
        return data;
    },

    exportConfig(side) {
        const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
        const data = this.getFactorData(containerId);
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${side}_strategy_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        this.log(`${side === 'buy' ? '买入' : '卖出'}策略已导出`, "success");
    },

    importConfig(side) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    this.applyConfigToContainer(data, side);
                    this.log(`${side === 'buy' ? '买入' : '卖出'}策略已导入`, "success");
                } catch (error) {
                    this.log(`导入失败：${error.message}`, "error");
                }
            };
            reader.readAsText(file);
        });
        input.click();
    },

    applyConfigToContainer(configData, side) {
        const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
        UIManager.clearFactorCards(containerId);
        configData.forEach(factorGroup => {
            const cardId = `card-${Date.now()}-${Math.random()}`;
            const card = document.createElement('div');
            card.className = 'factor-card';
            card.id = cardId;
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-title">${factorGroup.factor_group_name}</span>
                    <div class="card-weight-group">
                        <label>权重:</label>
                        <input type="number" class="card-weight-input" value="${factorGroup.weight}" min="0">
                    </div>
                    <button class="btn-remove-card" onclick="App.removeCard(this)">✕</button>
                </div>
                <div class="conditions-list"></div>
                <div class="card-footer">
                    <button class="btn-add-cond" onclick="App.showFactorModal('${side}', '${cardId}')">
                        <i class="fas fa-plus"></i> 插入新判定条件
                    </button>
                </div>
            `;
            document.getElementById(containerId).appendChild(card);
            const list = card.querySelector('.conditions-list');
            factorGroup.logic_tree.forEach((condition, index) => {
                const isFirst = index === 0;
                const row = document.createElement('div');
                row.className = 'condition-row';
                row.innerHTML = `
                    <div class="condition-row__header">
                        <div class="cond-logic">
                            ${isFirst ? '<span class="first-tag">首选</span>' : `<select class="cond-rel"><option value="AND" ${condition.relation === 'AND' ? 'selected' : ''}>且</option><option value="OR" ${condition.relation === 'OR' ? 'selected' : ''}>或</option></select>`}
                        </div>
                        <div class="cond-name" title="${condition.factor_name}">${condition.factor_name}</div>
                        ${isFirst ? '' : '<button class="btn-del-cond" onclick="App.removeCondition(this)">✕</button>'}
                    </div>
                    <div class="condition-row__date">
                        <span class="condition-row__date-label">日期范围:</span>
                        <input type="number" class="date-range-input" value="${condition.dateFrom || 30}" placeholder="天前">
                        <span class="date-range-separator">～</span>
                        <input type="number" class="date-range-input" value="${condition.dateTo || 0}" placeholder="天前">
                    </div>
                    <div class="condition-row__condition">
                        <select class="cond-op">
                            <option value="gt" ${condition.operator === 'gt' ? 'selected' : ''}>></option>
                            <option value="lt" ${condition.operator === 'lt' ? 'selected' : ''}><</option>
                            <option value="eq" ${condition.operator === 'eq' ? 'selected' : ''}>=</option>
                            <option value="ge" ${condition.operator === 'ge' ? 'selected' : ''}>≥</option>
                            <option value="le" ${condition.operator === 'le' ? 'selected' : ''}>≤</option>
                        </select>
                        <input type="number" class="cond-val" value="${condition.value}" placeholder="条件值">
                    </div>
                `;
                list.appendChild(row);
            });
        });
    },

    loadConfigFile(selectId) {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    const fileKey = `config_${Date.now()}`;
                    sessionStorage.setItem(fileKey, JSON.stringify(data));
                    const selectElement = document.getElementById(selectId);
                    const option = document.createElement('option');
                    option.value = fileKey;
                    option.textContent = `📄 ${file.name}`;
                    selectElement.appendChild(option);
                    selectElement.value = fileKey;
                    this.log(`已加载文件：${file.name}`, "success");
                } catch (error) {
                    this.log(`文件加载失败：${error.message}`, "error");
                }
            };
            reader.readAsText(file);
        });
        input.click();
    },

    async runSelection() {
        const buyConfig = this.getFactorData('buy-factor-container');
        const token = UIManager.getTushareToken();
        const filters = {
            excludeST: UIManager.getFilterExcludeST(),
            excludeKC: UIManager.getFilterExcludeKC(),
            excludeCY: UIManager.getFilterExcludeCY()
        };
        this.log("正在执行选股...", "system");
        const result = await this.callBackend(Message_Action, 'POST', {
            token: token,
            strategies: buyConfig,
            filters: filters
        });
        if(result) {
            this.updateSelectionTable(result.data);
            if(result.klineData) {
                this.drawKlineChart(result.klineData);
            }
        }
    },

    async runBacktest() {
        const dateRange = UIManager.getBacktestDateRange();
        const payload = {
            startDate: dateRange.startDate,
            endDate: dateRange.endDate,
            isIdeal: UIManager.getBacktestIsIdeal(),
            buySource: UIManager.getBacktestBuySource(),
            sellSource: UIManager.getBacktestSellSource(),
            initialFund: UIManager.getInitialFund()
        };
        this.log("启动回测引擎...", "info");
        const result = await this.callBackend(Message_Action, 'POST', payload);
        if(result) {
            this.updateBacktestUI(result);
            if(result.portfolioData) {
                this.drawPortfolioChart(result.portfolioData);
            }
        }
    },

    async runDiagnosis() {
        const sellConfig = this.getFactorData('sell-factor-container');
        this.log("执行持仓诊断...", "warning");
        const result = await this.callBackend(Message_Action, 'POST', { sell_strategy: sellConfig });
        if(result) {
            UIManager.setDiagnosisOutput(`<p class="highlight">${result.message}</p>`);
            this.log("诊断完成", "success");
        }
    },

    initCharts() {
        const klineContainer = document.getElementById('klineChart');
        if (klineContainer) {
            ChartInstances.klineChart = echarts.init(klineContainer, null, { renderer: 'canvas', useDirtyRect: true, locale: 'ZH' });
            ChartInstances.klineChart.setOption({
                backgroundColor: 'transparent',
                graphic: { elements: [{ type: 'text', left: 'center', top: 'center', style: { text: '等待数据加载...', fontSize: 16, fill: '#8b95aa' } }] }
            });
        }
        const portfolioContainer = document.getElementById('portfolioChart');
        if (portfolioContainer) {
            ChartInstances.portfolioChart = echarts.init(portfolioContainer, null, { renderer: 'canvas', useDirtyRect: true, locale: 'ZH' });
            ChartInstances.portfolioChart.setOption({
                backgroundColor: 'transparent',
                graphic: { elements: [{ type: 'text', left: 'center', top: 'center', style: { text: '等待数据加载...', fontSize: 16, fill: '#8b95aa' } }] }
            });
        }
        window.addEventListener('resize', () => {
            if (ChartInstances.klineChart) ChartInstances.klineChart.resize();
            if (ChartInstances.portfolioChart) ChartInstances.portfolioChart.resize();
        });
    },

    drawKlineChart(klineData) {
        if (!ChartInstances.klineChart || !klineData || klineData.length === 0) {
            this.log("K线数据无效或图表未初始化", "error");
            return;
        }
        const dates = [];
        const ohlcData = [];
        const volumeData = [];
        klineData.forEach(item => {
            dates.push(item.date);
            ohlcData.push([item.open, item.close, item.low, item.high]);
            volumeData.push(item.volume || 0);
        });

        const option = {
            backgroundColor: 'transparent',
            title: { text: 'K线走势图', left: 'center', textStyle: { color: '#4facfe', fontSize: 14, fontWeight: 'bold' } },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                backgroundColor: 'rgba(0, 0, 0, 0.85)',
                borderColor: '#4facfe',
                borderWidth: 1,
                textStyle: { color: '#fff', fontSize: 12 },
                formatter: (params) => {
                    if (!params || params.length === 0) return '';
                    const idx = params[0].dataIndex;
                    const item = klineData[idx];
                    if (!item) return '';
                    const change = ((item.close - item.open) / item.open * 100).toFixed(2);
                    const changeColor = item.close >= item.open ? '#00c853' : '#ff5252';
                    return `<div style="font-weight: bold; margin-bottom: 5px;">${item.date}</div>
                        <div style="color: #4facfe;">开盘: ${item.open.toFixed(2)}</div>
                        <div style="color: #00c853;">最高: ${item.high.toFixed(2)}</div>
                        <div style="color: #ff5252;">最低: ${item.low.toFixed(2)}</div>
                        <div style="color: ${changeColor}; font-weight: bold;">收盘: ${item.close.toFixed(2)} (${change}%)</div>
                        <div style="color: #8b95aa; margin-top: 5px;">成交量: ${(item.volume / 1000000).toFixed(2)}M</div>`;
                }
            },
            legend: { data: ['K线', '成交量'], textStyle: { color: '#e6eaf2' }, top: '35px' },
            grid: [
                { left: '8%', right: '8%', top: '70px', height: '60%', containLabel: true },
                { left: '8%', right: '8%', top: '73%', height: '15%', containLabel: true }
            ],
            xAxis: [
                { type: 'category', data: dates, gridIndex: 0, axisLine: { lineStyle: { color: '#8b95aa' } }, axisLabel: { color: '#8b95aa', rotate: 45, fontSize: 11 }, splitLine: { show: false } },
                { type: 'category', data: dates, gridIndex: 1, axisLine: { lineStyle: { color: '#8b95aa' } }, axisLabel: { show: false } }
            ],
            yAxis: [
                { type: 'value', gridIndex: 0, axisLine: { lineStyle: { color: '#8b95aa' } }, axisLabel: { color: '#8b95aa', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(120, 130, 160, 0.2)' } } },
                { type: 'value', gridIndex: 1, axisLine: { lineStyle: { color: '#8b95aa' } }, axisLabel: { color: '#8b95aa', fontSize: 11 } }
            ],
            series: [
                { name: 'K线', type: 'candlestick', xAxisIndex: 0, yAxisIndex: 0, data: ohlcData, itemStyle: { color: '#00c853', color0: '#ff5252', borderColor: '#00c853', borderColor0: '#ff5252', borderWidth: 1 } },
                { name: '成交量', type: 'bar', xAxisIndex: 1, yAxisIndex: 1, data: volumeData, itemStyle: { color: (params) => { const idx = params.dataIndex; return klineData[idx].close >= klineData[idx].open ? 'rgba(0, 200, 83, 0.4)' : 'rgba(255, 82, 82, 0.4)'; } } }
            ],
            dataZoom: [
                { type: 'slider', show: true, xAxisIndex: [0, 1], start: Math.max(0, 100 - Math.min(50, klineData.length * 2)), end: 100, backgroundColor: 'rgba(79, 172, 254, 0.1)', fillerColor: 'rgba(79, 172, 254, 0.2)', handleStyle: { color: '#4facfe' }, textStyle: { color: '#8b95aa', fontSize: 11 }, borderColor: '#4facfe' },
                { type: 'inside', xAxisIndex: [0, 1], start: Math.max(0, 100 - Math.min(50, klineData.length * 2)), end: 100, zoomOnMouseWheel: true, moveOnMouseMove: true, moveOnMouseWheel: false }
            ]
        };
        ChartInstances.klineChart.setOption(option);
        this.log(`K线图已绘制，共 ${klineData.length} 条数据`, "success");
    },

    drawPortfolioChart(portfolioData) {
        if (!ChartInstances.portfolioChart || !portfolioData || portfolioData.length === 0) {
            this.log("收益数据无效或图表未初始化", "error");
            return;
        }
        const dates = [];
        const equityData = [];
        const profitRateData = [];
        portfolioData.forEach(item => {
            dates.push(item.date);
            equityData.push(item.equity);
            profitRateData.push(item.profitRate);
        });

        const option = {
            backgroundColor: 'transparent',
            title: { text: '收益走势图', left: 'center', textStyle: { color: '#4facfe', fontSize: 14, fontWeight: 'bold' } },
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.85)',
                borderColor: '#4facfe',
                borderWidth: 1,
                textStyle: { color: '#fff', fontSize: 12 },
                formatter: (params) => {
                    if (!params || params.length === 0) return '';
                    const idx = params[0].dataIndex;
                    const item = portfolioData[idx];
                    if (!item) return '';
                    return `<div style="font-weight: bold; margin-bottom: 8px;">${item.date}</div>
                        <div style="color: #4facfe; margin-bottom: 3px;">💰 账户权益: <strong>¥${item.equity.toFixed(2)}</strong></div>
                        <div style="color: #00c853; margin-bottom: 3px;">✅ 累计盈利: <strong>¥${item.profit.toFixed(2)}</strong></div>
                        <div style="color: #00f2fe; font-weight: bold;">📈 收益率: <strong>${item.profitRate.toFixed(2)}%</strong></div>`;
                }
            },
            legend: { data: ['账户权益', '收益率'], textStyle: { color: '#e6eaf2' }, top: '35px' },
            grid: { left: '8%', right: '8%', top: '70px', bottom: '15%', containLabel: true },
            xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#8b95aa' } }, axisLabel: { color: '#8b95aa', rotate: 45, fontSize: 11 }, splitLine: { show: false } },
            yAxis: [
                { type: 'value', name: '账户权益 (¥)', position: 'left', nameTextStyle: { color: '#4facfe', fontSize: 11 }, axisLine: { lineStyle: { color: '#4facfe' } }, axisLabel: { color: '#8b95aa', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(120, 130, 160, 0.2)' } } },
                { type: 'value', name: '收益率 (%)', position: 'right', nameTextStyle: { color: '#00f2fe', fontSize: 11 }, axisLine: { lineStyle: { color: '#00f2fe' } }, axisLabel: { color: '#8b95aa', fontSize: 11 } }
            ],
            series: [
                { name: '账户权益', type: 'line', yAxisIndex: 0, data: equityData, smooth: true, lineStyle: { color: '#4facfe', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(79, 172, 254, 0.3)' }, { offset: 1, color: 'rgba(79, 172, 254, 0.05)' }]) }, itemStyle: { color: '#4facfe', borderColor: '#fff', borderWidth: 2 }, symbolSize: 6, emphasis: { itemStyle: { borderWidth: 3 } } },
                { name: '收益率', type: 'line', yAxisIndex: 1, data: profitRateData, smooth: true, lineStyle: { color: '#00f2fe', width: 2.5 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0, 242, 254, 0.2)' }, { offset: 1, color: 'rgba(0, 242, 254, 0.02)' }]) }, itemStyle: { color: '#00f2fe', borderColor: '#fff', borderWidth: 2 }, symbolSize: 6, emphasis: { itemStyle: { borderWidth: 3 } } }
            ],
            dataZoom: [
                { type: 'slider', show: true, start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), end: 100, backgroundColor: 'rgba(79, 172, 254, 0.1)', fillerColor: 'rgba(79, 172, 254, 0.2)', handleStyle: { color: '#4facfe' }, textStyle: { color: '#8b95aa', fontSize: 11 }, borderColor: '#4facfe' },
                { type: 'inside', start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), end: 100, zoomOnMouseWheel: true, moveOnMouseMove: true }
            ]
        };
        ChartInstances.portfolioChart.setOption(option);
        this.log(`收益曲线图已绘制，共 ${portfolioData.length} 个交易日`, "success");
    },

    log(msg, type = 'info') {
        const container = document.getElementById('global-log-container');
        if (!container) {
            console.log(`[${type}] ${msg}`);
            return; 
        }
        const item = document.createElement('div');
        const time = new Date().toLocaleTimeString();
        item.className = `log-item ${type}`;
        item.innerHTML = `[${time}] ${msg}`;
        container.appendChild(item);
        container.scrollTop = container.scrollHeight;
    },

    async callBackend(endpoint, method, data = null) {
        try {
            this.log(`发起请求: ${data.type}`, "system");

            const resp = await fetch(endpoint, {
                method: method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: data ? JSON.stringify(data) : null
            });

            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }

            const result = await resp.json();

            this.log(`后端响应: ${endpoint} 成功`, "success");
            return result;

        } catch (error) {
            this.log(`请求失败: ${error.message}`, "error");
            return null;
        }
    },


    updateSelectionTable(data) {
        const tbody = document.getElementById('selection-result-table');
        tbody.innerHTML = '';
        (data || []).forEach(item => {
            const row = document.createElement('tr');
            row.style.cursor = 'pointer';
            row.innerHTML = `
                <td>${item.code}</td>
                <td>${item.name}</td>
                <td>¥${item.price.toFixed(2)}</td>
                <td>${item.score.toFixed(2)}</td>
                <td>${item.industry || '-'}</td>
            `;
            row.addEventListener('click', () => {
                UIManager.setSelectionDescription(`【${item.code}】${item.name}\n行业：${item.industry || '-'}\n现价：¥${item.price.toFixed(2)}\n综合得分：${item.score.toFixed(2)}\n\n您的分析：\n`);
                State.selectedStock = item;
            });
            tbody.appendChild(row);
        });
    },

    updateBacktestUI(result) {
        UIManager.setBacktestSummary(
            result.totalPnL || '0.00%',
            result.winRate || '0%',
            result.maxDrawdown || '0.00%'
        );
        const tbody = document.getElementById('backtest-log-table');
        tbody.innerHTML = '';
        (result.transactions || []).forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${tx.date}</td>
                <td>${tx.stock}</td>
                <td>${tx.action}</td>
                <td>¥${tx.price.toFixed(2)}</td>
                <td>${tx.profit ? `¥${tx.profit.toFixed(2)}` : '-'}</td>
                <td>¥${tx.balance.toFixed(2)}</td>
            `;
            tbody.appendChild(row);
        });
    },

    showFactorModal(side, targetCardId = null) {
        const modal = document.getElementById('factor-modal');
        const list = document.getElementById('factor-type-list');
        list.innerHTML = '';
        CONFIG.factorTypes.forEach(type => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline';
            btn.innerText = type;
            btn.onclick = () => {
                if (targetCardId) {
                    this.addConditionToCard(targetCardId, type);
                } else {
                    const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
                    this.renderFactorCard(type, containerId, side);
                }
                modal.classList.remove('active');
            };
            list.appendChild(btn);
        });
        modal.classList.add('active');
        document.getElementById('btn-close-modal').addEventListener('click', () => modal.classList.remove('active'));
    }
};
