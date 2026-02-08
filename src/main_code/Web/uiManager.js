/**
 * uiManager.js - UI 交互与状态管理模块
 * 
 * 职责：
 * - UI 元素的 get/set 方法
 * - 表格和图表的更新显示
 * - 滑块和输入框的管理
 * - 股票查询结果展示
 */

import { State } from './app.js';

let manager = null;
export function setUIManager(_manager) {
    manager = _manager;
}

export const UIManagerUtils = {
    // ============ 基础 Getters ============
    
    getTushareToken() { 
        return document.getElementById('tushareToken').value; 
    },
    
    getInitialFund() { 
        return parseFloat(document.getElementById('initialFundInput').value) || 100000; 
    },
    
    getBacktestDateRange() {
        return {
            startDate: document.getElementById('bt-start-date').value,
            endDate: document.getElementById('bt-end-date').value
        };
    },
    
    getBacktestIsIdeal() { 
        return document.getElementById('bt-is-ideal').checked; 
    },
    
    getBacktestBuySource() { 
        return document.getElementById('backtest-buy-source').value; 
    },
    
    getBacktestSellSource() { 
        return document.getElementById('backtest-sell-source').value; 
    },
    
    getWeightThreshold() {
        const elem = document.getElementById('weight-threshold-slider');
        return elem ? parseFloat(elem.value) : 0.5;
    },
    
    getHoldingsWeightThreshold() {
        const elem = document.getElementById('holdings-weight-threshold-slider');
        return elem ? parseFloat(elem.value) : 0.5;
    },
    
    getStockQueryInput() {
        return document.getElementById('query-stock-input').value;
    },
    
    getQuickQueryInput() {
        return document.getElementById('quick-query-input').value;
    },
    
    // ============ 基础 Setters ============
    
    setTushareToken(token) { 
        document.getElementById('tushareToken').value = token; 
    },
    
    setInitialFund(amount) { 
        document.getElementById('initialFundInput').value = amount;
        State.initialFund = amount;
    },
    
    setBacktestDateRange(startDate, endDate) {
        document.getElementById('bt-start-date').value = startDate;
        document.getElementById('bt-end-date').value = endDate;
    },
    
    setBacktestIsIdeal(checked) { 
        document.getElementById('bt-is-ideal').checked = checked; 
    },
    
    setBacktestBuySource(source) { 
        document.getElementById('backtest-buy-source').value = source; 
    },
    
    setBacktestSellSource(source) { 
        document.getElementById('backtest-sell-source').value = source; 
    },
    
    setConnectionStatus(isConnected) {
        const dot = document.querySelector('.status-dot');
        const text = document.querySelector('.status-text');
        if (dot && text) {
            if (isConnected) {
                dot.classList.add('connected');
                text.textContent = '已连接';
            } else {
                dot.classList.remove('connected');
                text.textContent = '未连接';
            }
        }
    },
    
    setLastUpdateTime(dateTime) {
        const elem = document.getElementById('last-update-text');
        if (elem) {
            if (dateTime) {
                elem.textContent = dateTime;
            } else {
                elem.textContent = '--';
            }
        }
    },
    
    setWeightThreshold(value) {
        const elem = document.getElementById('weight-threshold-slider');
        const display = document.getElementById('threshold-value-display');
        if (elem) {
            elem.value = Math.max(0, Math.min(1, value));
            if (display) display.textContent = elem.value;
        }
    },
    
    setHoldingsWeightThreshold(value) {
        const elem = document.getElementById('holdings-weight-threshold-slider');
        const display = document.getElementById('holdings-threshold-value-display');
        if (elem) {
            elem.value = Math.max(0, Math.min(1, value));
            if (display) display.textContent = elem.value;
        }
    },
    
    setSelectionDescription(text) { 
        const elem = document.getElementById('stock-description');
        if (elem) elem.value = text;
    },
    
    // ============ 股票过滤选项 ============
    
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
    
    // ============ 股票说明 ============
    
    getSelectionDescription() { 
        const elem = document.getElementById('stock-description');
        return elem ? elem.value : '';
    },
    
    // ============ 卡片权重管理 ============
    
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
    
    // ============ 条件行管理 ============
    
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
    
    // ============ 卡片容器管理 ============
    
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
    
    // ============ 回测结果显示 ============
    
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
    
    // ============ 诊断输出 ============
    
    getDiagnosisOutput() { 
        return document.getElementById('diagnosis-output').innerHTML; 
    },
    
    setDiagnosisOutput(content) { 
        document.getElementById('diagnosis-output').innerHTML = content; 
    },
    
    // ============ 数字格式化 ============
    
    formatNumber(num) {
        if (!num) return '-';
        if (num >= 100000000) {
            return (num / 100000000).toFixed(2) + '亿';
        } else if (num >= 10000) {
            return (num / 10000).toFixed(2) + '万';
        }
        return num.toFixed(2);
    },
    
    // ============ 表格更新 ============
    
    updateIndustryAnalysisTable(data) {
        const tbody = document.getElementById('industry-analysis-table');
        if (!tbody) return;
        tbody.innerHTML = '';
        (data || []).forEach(item => {
            const row = document.createElement('tr');
            const changeRatio = item.riseCount + item.fallCount > 0 
                ? ((item.riseCount / (item.riseCount + item.fallCount)) * 100).toFixed(2)
                : '0.00';
            
            row.innerHTML = `
                <td>${item.industryName || '-'}</td>
                <td>${item.stockCount || 0}</td>
                <td>${item.volumeGrowth ? (item.volumeGrowth * 100).toFixed(2) + '%' : '-'}</td>
                <td>${item.riseCount || 0} / ${item.fallCount || 0}</td>
                <td>${changeRatio}%</td>
                <td>${item.avgRiseRate ? (item.avgRiseRate * 100).toFixed(2) + '%' : '-'}</td>
            `;
            tbody.appendChild(row);
        });
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
                this.setSelectionDescription(`【${item.code}】${item.name}\n行业：${item.industry || '-'}\n现价：¥${item.price.toFixed(2)}\n综合得分：${item.score.toFixed(2)}\n\n您的分析：\n`);
                State.selectedStock = item;
            });
            tbody.appendChild(row);
        });
    },
    
    updateBacktestUI(result) {
        this.setBacktestSummary(
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
    
    // ============ 股票查询结果 ============
    
    setStockQueryResult(data) {
        if (!data) {
            document.getElementById('query-stock-name').textContent = '-';
            return;
        }

        document.getElementById('query-stock-name').textContent = data.name || '-';
        document.getElementById('query-stock-code').textContent = data.code || '-';
        document.getElementById('query-stock-price').textContent = data.price ? `¥${data.price.toFixed(2)}` : '-';
        document.getElementById('query-stock-change').textContent = data.changePercent ? `${data.changePercent.toFixed(2)}%` : '-';
        document.getElementById('query-stock-industry').textContent = data.industry || '-';
        document.getElementById('query-stock-pe').textContent = data.pe ? data.pe.toFixed(2) : '-';
        document.getElementById('query-stock-pb').textContent = data.pb ? data.pb.toFixed(2) : '-';
        document.getElementById('query-stock-market-cap').textContent = data.marketCap ? this.formatNumber(data.marketCap) : '-';
        document.getElementById('query-stock-circulate-cap').textContent = data.circulateCap ? this.formatNumber(data.circulateCap) : '-';
        document.getElementById('query-stock-52high').textContent = data.high52 ? `¥${data.high52.toFixed(2)}` : '-';
        document.getElementById('query-company-intro').value = data.companyIntro || '';
        document.getElementById('query-business-analysis').value = data.businessAnalysis || '';
        
        this.setProductsList(data.products || []);
    },

    setProductsList(products) {
        const container = document.getElementById('query-products-list');
        if (!container) return;
        
        if (!products || products.length === 0) {
            container.innerHTML = '<div class="empty-state">暂无产品信息</div>';
            return;
        }
        
        container.innerHTML = products.map(product => 
            `<div class="product-item">${product}</div>`
        ).join('');
    },

    setQuickQueryResults(results) {
        const container = document.getElementById('quick-query-results');
        if (!container) return;
        
        if (!results || results.length === 0) {
            container.innerHTML = '';
            return;
        }
        
        container.innerHTML = results.map(item => 
            `<div class="query-item" data-code="${item.code}">
                <span class="query-item-code">${item.code}</span>
                <span class="query-item-name">${item.name}</span>
            </div>`
        ).join('');
    },
    
    setDiagnoseResults(data) {
        // 诊断结果显示（持仓页面）
        const container = document.getElementById('diagnosis-output');
        if (container) {
            container.innerHTML = data.diagnosis || '待诊断';
        }
    },
    
    setBacktestChartArea(result) {
        // 占位符，实际由 ChartManager 处理
    },
    
    getLastUpdateTime() {
        const elem = document.getElementById('last-update-text');
        return elem ? elem.textContent : null;
    }
};
