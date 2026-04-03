/**
 * stockQueryManager.js - 股票查询模块
 * 
 * 职责：
 * - 处理股票查询（代码/字母/关键字）
 * - 管理查询结果和排序
 * - 显示股票详情
 * - 与后端通过 WebSocket 进行通信
 */

import { App } from './app.js';

let manager = null;

export function setStockQueryManager(_manager) {
    manager = _manager;
}

export const StockQueryManager = {
    // ============ 状态管理 ============
    state: {
        // 查询结果
        queryResults: [],
        // 当前选中的股票
        selectedStock: null,
        // 查询模式: 'code' | 'letter' | 'keyword'
        queryMode: null,
        // 排序配置
        sortConfig: {
            field: null,
            order: 'desc' // 'asc' | 'desc'
        },
        // 当前视图: 'list' | 'detail'
        currentView: 'list'
    },

    // ============ 初始化 ============
    init() {
        this.bindSearchEvents();
        this.bindListEvents();
        this.bindDetailEvents();
        console.log("股票查询模块初始化完成")
        App.log("📊 股票查询模块初始化完成", "system");
        return this
    },

    // ============ 事件绑定 ============
    bindSearchEvents() {
        // 代码查询
        const codeBtn = document.getElementById('sq-code-search');
        const codeInput = document.getElementById('sq-code-input');
        if (codeBtn && codeInput) {
            codeBtn.addEventListener('click', () => this.handleCodeSearch());
            codeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleCodeSearch();
            });
        }

        // 字母查询
        const letterBtn = document.getElementById('sq-letter-search');
        const letterInput = document.getElementById('sq-letter-input');
        if (letterBtn && letterInput) {
            letterBtn.addEventListener('click', () => this.handleLetterSearch());
            letterInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleLetterSearch();
            });
        }

        // 关键字查询
        const keywordBtn = document.getElementById('sq-keyword-search');
        const keywordInput = document.getElementById('sq-keyword-input');
        if (keywordBtn && keywordInput) {
            keywordBtn.addEventListener('click', () => this.handleKeywordSearch());
            keywordInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.handleKeywordSearch();
            });
        }
    },

    bindListEvents() {
        // 排序按钮
        const sortBtns = document.querySelectorAll('[data-sort-field]');
        sortBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const field = btn.dataset.sortField;
                this.sortResults(field);
            });
        });
    },

    bindDetailEvents() {
        // 返回按钮
        const backBtn = document.getElementById('sq-detail-back');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.showListView();
            });
        }
    },

    // ============ 查询处理 ============
    
    handleCodeSearch() {
        const input = document.getElementById('sq-code-input');
        const code = input.value.trim().toUpperCase();
        
        if (!code) {
            App.log("请输入股票代码", "warning");
            return;
        }

        if (!/^\d{6}$/.test(code)) {
            App.log("股票代码必须是6位数字", "warning");
            return;
        }

        App.log(`🔍 查询股票代码: ${code}`, "info");
        manager.requestQueryStockInfo('code', code);
    },

    handleLetterSearch() {
        const input = document.getElementById('sq-letter-input');
        const letters = input.value.trim().toUpperCase();
        
        if (!letters) {
            App.log("请输入股票字母", "warning");
            return;
        }

        if (!/^[A-Z]+$/.test(letters)) {
            App.log("股票字母必须是大写英文字母", "warning");
            return;
        }

        App.log(`🔍 查询股票字母: ${letters}`, "info");
        manager.requestQueryStockInfo('letter', letters);
    },

    handleKeywordSearch() {
        const input = document.getElementById('sq-keyword-input');
        const keyword = input.value.trim();
        
        if (!keyword) {
            App.log("请输入关键字", "warning");
            return;
        }

        if (keyword.length > 50) {
            App.log("关键字长度不能超过50个字符", "warning");
            return;
        }

        App.log(`🔍 查询关键字: ${keyword}`, "info");
        manager.requestQueryStockInfo('keyword', keyword);
    },



    /**
     * 处理后端返回的查询结果
     * 应该在 AppManager 的 registerDefaultHandlers 中注册
     */
    handleQueryResponse(data) {
        console.log('查询响应:', data);
        
        if (!data || !data.stocks) {
            App.log("❌ 无查询结果", "error");
            this.state.queryResults = [];
            this.renderList();
            return;
        }

        const stocks = data.stocks;
        
        if (!Array.isArray(stocks)) {
            App.log("❌ 返回数据格式错误", "error");
            return;
        }

        if (stocks.length === 0) {
            App.log("❌ 查询无结果", "error");
            this.state.queryResults = [];
            this.renderList();
            return;
        }

        // 保存结果
        this.state.queryResults = stocks;
        this.state.queryMode = data.query_type;
        
        App.log(`✅ 查询成功，找到 ${stocks.length} 条结果`, "success");
        
        // 渲染列表
        this.renderList();
    },

    // ============ 排序 ============
    
    sortResults(field) {
        if (!Array.isArray(this.state.queryResults) || this.state.queryResults.length === 0) {
            return;
        }

        // 切换排序方向
        if (this.state.sortConfig.field === field) {
            this.state.sortConfig.order = this.state.sortConfig.order === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortConfig.field = field;
            this.state.sortConfig.order = 'desc';
        }

        // 排序数据
        this.state.queryResults.sort((a, b) => {
            let aVal = a[field];
            let bVal = b[field];

            // 处理数值
            if (typeof aVal === 'string' && !isNaN(parseFloat(aVal))) {
                aVal = parseFloat(aVal);
                bVal = parseFloat(bVal);
            }

            if (aVal < bVal) return this.state.sortConfig.order === 'asc' ? -1 : 1;
            if (aVal > bVal) return this.state.sortConfig.order === 'asc' ? 1 : -1;
            return 0;
        });

        // 更新UI
        this.updateSortButtonStates(field);
        this.renderList();
        App.log(`已按 ${field} 排序`, "system");
    },

    updateSortButtonStates(field) {
        document.querySelectorAll('[data-sort-field]').forEach(btn => {
            btn.classList.remove('active', 'asc', 'desc');
            if (btn.dataset.sortField === field) {
                btn.classList.add('active', this.state.sortConfig.order);
            }
        });
    },

    // ============ 视图管理 ============
    
    showListView() {
        this.state.currentView = 'list';
        document.getElementById('sq-list-view').classList.add('active');
        document.getElementById('sq-detail-view').classList.remove('active');
    },

    showDetailView(stock) {
        this.state.currentView = 'detail';
        this.state.selectedStock = stock;
        
        document.getElementById('sq-list-view').classList.remove('active');
        document.getElementById('sq-detail-view').classList.add('active');
        
        this.renderDetail(stock);
    },

    // ============ 列表渲染 ============
    
    renderList() {
        const tbody = document.getElementById('sq-list-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        if (this.state.queryResults.length === 0) {
            tbody.innerHTML = '<tr><td colspan="11" class="sq-empty">暂无结果</td></tr>';
            document.getElementById('sq-results-count').textContent = '0';
            return;
        }

        // 更新计数
        document.getElementById('sq-results-count').textContent = this.state.queryResults.length;

        // 渲染每一行
        this.state.queryResults.forEach((stock, idx) => {
            const row = document.createElement('tr');
            row.className = 'sq-list-row';
            row.onclick = () => this.showDetailView(stock);

            // 代码
            const codeCell = document.createElement('td');
            codeCell.textContent = stock.code || '-';
            codeCell.className = 'sq-code';
            row.appendChild(codeCell);

            // 名称
            const nameCell = document.createElement('td');
            nameCell.textContent = stock.name || '-';
            row.appendChild(nameCell);

            // 流通市值
            const marketCapCell = document.createElement('td');
            marketCapCell.textContent = stock.market_cap || '-';
            marketCapCell.className = 'sq-number';
            row.appendChild(marketCapCell);

            // 3日涨幅
            const change3dCell = document.createElement('td');
            const change3d = stock.change_3d || 0;
            change3dCell.textContent = (change3d >= 0 ? '+' : '') + change3d.toFixed(2) + '%';
            change3dCell.className = `sq-change ${change3d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change3dCell);

            // 5日涨幅
            const change5dCell = document.createElement('td');
            const change5d = stock.change_5d || 0;
            change5dCell.textContent = (change5d >= 0 ? '+' : '') + change5d.toFixed(2) + '%';
            change5dCell.className = `sq-change ${change5d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change5dCell);

            // 10日涨幅
            const change10dCell = document.createElement('td');
            const change10d = stock.change_10d || 0;
            change10dCell.textContent = (change10d >= 0 ? '+' : '') + change10d.toFixed(2) + '%';
            change10dCell.className = `sq-change ${change10d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change10dCell);

            // 20日涨幅
            const change20dCell = document.createElement('td');
            const change20d = stock.change_20d || 0;
            change20dCell.textContent = (change20d >= 0 ? '+' : '') + change20d.toFixed(2) + '%';
            change20dCell.className = `sq-change ${change20d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change20dCell);

            // 40日涨幅
            const change40dCell = document.createElement('td');
            const change40d = stock.change_40d || 0;
            change40dCell.textContent = (change40d >= 0 ? '+' : '') + change40d.toFixed(2) + '%';
            change40dCell.className = `sq-change ${change40d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change40dCell);

            // 60日涨幅
            const change60dCell = document.createElement('td');
            const change60d = stock.change_60d || 0;
            change60dCell.textContent = (change60d >= 0 ? '+' : '') + change60d.toFixed(2) + '%';
            change60dCell.className = `sq-change ${change60d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change60dCell);


            // 120日涨幅
            const change120dCell = document.createElement('td');
            const change120d = stock.change_120d || 0;
            change120dCell.textContent = (change120d >= 0 ? '+' : '') + change120d.toFixed(2) + '%';
            change120dCell.className = `sq-change ${change120d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change120dCell);

            // 240日涨幅
            const change240dCell = document.createElement('td');
            const change240d = stock.change_240d || 0;
            change240dCell.textContent = (change240d >= 0 ? '+' : '') + change240d.toFixed(2) + '%';
            change240dCell.className = `sq-change ${change240d >= 0 ? 'positive' : 'negative'}`;
            row.appendChild(change240dCell);

            tbody.appendChild(row);
        });
    },

    // ============ 详情渲染 ============
    
    renderDetail(stock) {
        const detailContainer = document.getElementById('sq-detail-content');
        if (!detailContainer) return;

        const html = `
            <div class="sq-detail-header">
                <div>
                    <div class="sq-detail-code">${stock.code}</div>
                    <div class="sq-detail-name">${stock.name}</div>
                </div>
                <button class="sq-detail-back" id="sq-detail-back">← 返回</button>
            </div>

            <div class="sq-detail-body">
                <!-- 基本信息 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">📊 基本信息</h4>
                    <div class="sq-detail-grid-2">
                        <div class="sq-detail-item">
                            <span class="sq-label">流通市值</span>
                            <span class="sq-value">${stock.market_cap || '-'}</span>
                        </div>
                        <div class="sq-detail-item">
                            <span class="sq-label">公司性质</span>
                            <span class="sq-value">${stock.company_type || '-'}</span>
                        </div>
                    </div>
                </div>

                <!-- 涨跌幅 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">📈 涨跌幅统计</h4>
                    <div class="sq-detail-grid-4">
                        ${this.renderChangeGrid(stock)}
                    </div>
                </div>

                <!-- 公司名称 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">🏢 公司名称</h4>
                    <div class="sq-detail-text">
                        ${stock.company_name || '-'}
                    </div>
                </div>

                <!-- 主要产品 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">🎯 主要产品</h4>
                    <div class="sq-detail-text">
                        ${stock.main_products || '-'}
                    </div>
                </div>

                <!-- 业务范围 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">💼 业务范围</h4>
                    <div class="sq-detail-text">
                        ${stock.business_scope || '-'}
                    </div>
                </div>

                <!-- 公司介绍 -->
                <div class="sq-detail-section">
                    <h4 class="sq-section-title">📝 公司介绍</h4>
                    <div class="sq-detail-text">
                        ${stock.company_description || '-'}
                    </div>
                </div>
            </div>
        `;

        detailContainer.innerHTML = html;
        
        // 重新绑定返回按钮
        const backBtn = detailContainer.querySelector('#sq-detail-back');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showListView());
        }
    },

    renderChangeGrid(stock) {
        const changes = [
            { days: 3, key: 'change_3d' },
            { days: 5, key: 'change_5d' },
            { days: 10, key: 'change_10d' },
            { days: 20, key: 'change_20d' },
            { days: 40, key: 'change_40d' },
            { days: 60, key: 'change_60d' },
            { days: 120, key: 'change_120d' },
            { days: 240, key: 'change_240d' }
        ];

        return changes.map(({ days, key }) => {
            const value = stock[key] || 0;
            const color = value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
            return `
                <div class="sq-detail-item">
                    <span class="sq-label">${days}日</span>
                    <span class="sq-value ${color}">
                        ${value > 0 ? '+' : ''}${value.toFixed(2)}%
                    </span>
                </div>
            `;
        }).join('');
    }
};

export default StockQueryManager;