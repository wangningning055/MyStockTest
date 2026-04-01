/**
 * valueGrowthManager.js - 价值/成长股筛选管理模块
 * 
 * 功能：
 * - 分页签显示价值股或成长股
 * - 按多个指标排序（涨跌幅、名称等）
 * - 按行业筛选
 * - 动态表格渲染
 */

let valueGrowthData = {
    stocks: [],           // 所有股票数据
    industries: [],       // 行业列表
    currentType: 'value', // 当前选择: 'value' 或 'growth'
    selectedIndustry: 'all',
    sortBy: 'code',       // 默认按代码排序
    sortOrder: 'asc'      // 排序顺序: 'asc' 或 'desc'
};

// ============ 初始化 ============
export function initValueGrowthManager() {
    console.log("📊 初始化价值/成长股筛选模块");
    bindValueGrowthEvents();
}

// ============ 事件绑定 ============
function bindValueGrowthEvents() {
    // 1. 分页签切换
    const valueTabs = document.querySelectorAll('.vg-type-tab');
    valueTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const type = e.target.dataset.type; // 'value' 或 'growth'
            switchValueGrowthType(type);
        });
    });

    // 2. 行业筛选
    const industrySelect = document.getElementById('vg-industry-filter');
    if (industrySelect) {
        industrySelect.addEventListener('change', (e) => {
            valueGrowthData.selectedIndustry = e.target.value;
            renderValueGrowthTable();
        });
    }

    // 3. 排序列点击
    const tableHeaders = document.querySelectorAll('.vg-sortable');
    tableHeaders.forEach(header => {
        header.addEventListener('click', (e) => {
            const sortKey = e.target.dataset.sort;
            toggleSort(sortKey);
        });
    });
}

// ============ 切换股票类型（价值/成长） ============
function switchValueGrowthType(type) {
    valueGrowthData.currentType = type;
    
    // 更新页签样式
    const tabs = document.querySelectorAll('.vg-type-tab');
    tabs.forEach(tab => {
        if (tab.dataset.type === type) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });

    console.log(`📈 切换至${type === 'value' ? '价值股' : '成长股'}`);
    renderValueGrowthTable();
}

// ============ 排序切换 ============
function toggleSort(sortKey) {
    if (valueGrowthData.sortBy === sortKey) {
        // 同列点击，反转排序
        valueGrowthData.sortOrder = valueGrowthData.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
        // 新列，默认升序
        valueGrowthData.sortBy = sortKey;
        valueGrowthData.sortOrder = 'asc';
    }
    console.log(`📊 按 ${sortKey} 排序，方向: ${valueGrowthData.sortOrder}`);
    renderValueGrowthTable();
}

// ============ 获取过滤后的数据 ============
function getFilteredData() {
    let filtered = valueGrowthData.stocks.filter(stock => {
        // 按类型过滤
        if (stock.type !== valueGrowthData.currentType) return false;
        
        // 按行业过滤
        if (valueGrowthData.selectedIndustry !== 'all' && 
            stock.industry !== valueGrowthData.selectedIndustry) {
            return false;
        }
        
        return true;
    });

    // 排序
    filtered.sort((a, b) => {
        let aVal = a[valueGrowthData.sortBy];
        let bVal = b[valueGrowthData.sortBy];

        // 处理数值比较
        if (typeof aVal === 'number' && typeof bVal === 'number') {
            return valueGrowthData.sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
        }

        // 处理字符串比较
        if (typeof aVal === 'string' && typeof bVal === 'string') {
            return valueGrowthData.sortOrder === 'asc' 
                ? aVal.localeCompare(bVal) 
                : bVal.localeCompare(aVal);
        }

        return 0;
    });

    return filtered;
}

// ============ 渲染表格 ============
function renderValueGrowthTable() {
    const tbody = document.getElementById('value-growth-table');
    if (!tbody) return;

    const filteredData = getFilteredData();
    tbody.innerHTML = '';

    filteredData.forEach(stock => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${stock.code}</td>
            <td>${stock.name}</td>
            <td>${stock.industry || '-'}</td>

            <td>${stock.score.toFixed(2)}</td>

            <td>${stock.value.toFixed(2)}亿</td>

            <td>${stock.Roe.toFixed(2)}%</td>

            <td>${stock.earn.toFixed(2)}%</td>

            <td>${stock.clean.toFixed(2)}%</td>

            <td>${stock.sale.toFixed(2)}%</td>
  
            <td>${stock.cash.toFixed(2)}%</td>

            <td>${stock.YOYNi.toFixed(2)}%</td>
            <td>${stock.LiabilityTo.toFixed(2)}%</td>
         
            <td>${stock.YOYEquity.toFixed(2)}%</td>

            <td>${stock.YOYLiability.toFixed(2)}%</td>
            

            <td class="${stock.change_3d >= 0 ? 'positive' : 'negative'}">
                ${stock.change_3d >= 0 ? '+' : ''}${stock.change_3d.toFixed(2)}%
            </td>

            <td class="${stock.change_5d >= 0 ? 'positive' : 'negative'}">
                ${stock.change_5d >= 0 ? '+' : ''}${stock.change_5d.toFixed(2)}%
            </td>

            <td class="${stock.change_20d >= 0 ? 'positive' : 'negative'}">
                ${stock.change_20d >= 0 ? '+' : ''}${stock.change_20d.toFixed(2)}%
            </td>
            <td class="${stock.change_120d >= 0 ? 'positive' : 'negative'}">
                ${stock.change_120d >= 0 ? '+' : ''}${stock.change_120d.toFixed(2)}%
            </td>
            <td class="${stock.change_240d >= 0 ? 'positive' : 'negative'}">
                ${stock.change_240d >= 0 ? '+' : ''}${stock.change_240d.toFixed(2)}%
            </td>
        `;
        tbody.appendChild(row);
    });
    // 重新计算表格容器的滚动宽度（确保横向滚动生效）
    const tableContainer = document.querySelector('.vg-table-container');
    if (tableContainer) {
        // 强制重排，让浏览器重新计算内容宽度
        void tableContainer.offsetHeight; // 触发重排
    }
                   
    // 更新统计数据
    updateValueGrowthStats();
}

// ============ 更新统计信息 ============
function updateValueGrowthStats() {
    const valueCount = valueGrowthData.stocks.filter(s => s.type === 'value').length;
    const growthCount = valueGrowthData.stocks.filter(s => s.type === 'growth').length;
    
    const valueCountEl = document.querySelector('[data-count="value"]');
    const growthCountEl = document.querySelector('[data-count="growth"]');
    
    if (valueCountEl) valueCountEl.textContent = valueCount;
    if (growthCountEl) growthCountEl.textContent = growthCount;
}

// ============ 设置行业列表 ============
export function setIndustries(industries) {
    valueGrowthData.industries = industries;
    console.log(`✅ 已加载 ${industries.length} 个行业`);
    renderIndustryFilter();
}

// ============ 渲染行业下拉框 ============
function renderIndustryFilter() {
    const select = document.getElementById('vg-industry-filter');
    if (!select) return;

    select.innerHTML = '<option value="all">📍 全部行业</option>';
    
    valueGrowthData.industries.forEach(industry => {
        const option = document.createElement('option');
        option.value = industry;
        option.textContent = industry;
        select.appendChild(option);
    });
}

// ============ 设置股票数据 ============
export function setValueGrowthStocks(stocks) {
    valueGrowthData.stocks = stocks;
    console.log(`✅ 已加载 ${stocks.length} 只股票`);
    renderValueGrowthTable();
}

// ============ 获取当前状态 ============
export function getValueGrowthState() {
    return {
        currentType: valueGrowthData.currentType,
        selectedIndustry: valueGrowthData.selectedIndustry,
        sortBy: valueGrowthData.sortBy,
        sortOrder: valueGrowthData.sortOrder
    };
}

export const ValueGrowthManager = {
    init: initValueGrowthManager,
    setIndustries,
    setStocks: setValueGrowthStocks,
    getState: getValueGrowthState
};
