/**
 * ============================================================
 * 1. 全局配置与状态
 * ============================================================
 */
const CONFIG = {
    // 预设因子类型，后端根据这些 Key 处理逻辑
    factorTypes: ["市盈率 PE", "市净率 PB", "均线金叉", "MACD底背离", "RSI超卖", "自定义公式"],
    // 后端 API 基础路径
    apiBase: "http://127.0.0.1:5000/api" 
};

// 全局状态管理
const State = {
    buyFactors: [],  // 选股页因子集
    sellFactors: [], // 持仓页卖出因子集
    holdings: [],    // 当前持仓数据
};

/**
 * ============================================================
 * 2. 核心初始化
 * ============================================================
 */
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

const App = {
    init() {
        this.bindTabs();
        this.bindGlobalEvents();
        this.bindFactorEvents();
        this.initCanvas();
        this.log("系统引擎启动成功，等待指令...", "system");
    },

    // A. 页签切换逻辑
    bindTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.target;
                
                // 切换按钮状态
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');

                // 切换视图内容
                document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
                document.getElementById(target).classList.add('active');

                this.log(`切换至视图: ${tab.innerText}`, "system");
            });
        });
    },

    // B. 全局按钮绑定 (后端接入点)
    bindGlobalEvents() {
        // 更新数据按钮
        document.getElementById('api-update-data').onclick = () => this.callBackend('/update_data', 'POST');
        
        // 停止后台
        document.getElementById('api-stop-backend').onclick = () => {
            if(confirm("确定要停止 Python 后端服务吗？")) this.callBackend('/stop', 'POST');
        };

        // 开始选股
        document.getElementById('api-run-selection').onclick = () => this.runSelection();

        // 开始回测
        document.getElementById('api-run-backtest').onclick = () => this.runBacktest();

        // 持仓诊断
        document.getElementById('api-diagnose-holdings').onclick = () => this.runDiagnosis();

        // 清空日志
        document.getElementById('btn-clear-log').onclick = () => {
            document.getElementById('global-log-container').innerHTML = '';
        };
    },

    /**
     * ============================================================
     * 3. 因子管理逻辑 (含权重处理)
     * ============================================================
     */
    bindFactorEvents() {
        // 选股页添加因子
        document.getElementById('btn-add-buy-factor').onclick = () => this.showFactorModal('buy');
        // 持仓页添加因子
        document.getElementById('btn-add-sell-factor').onclick = () => this.showFactorModal('sell');

        // 导入导出逻辑
        document.getElementById('api-export-buy-config').onclick = () => this.exportConfig('buy');
        document.getElementById('api-export-sell-config').onclick = () => this.exportConfig('sell');
    },

    // 动态生成因子卡片
    // 1. 渲染整个因子卡片 (单元)
    renderFactorCard(type, containerId, side) {
        const container = document.getElementById(containerId);
        const cardId = `card-${Date.now()}`;
        
        const card = document.createElement('div');
        card.className = 'factor-card';
        card.id = cardId;
        card.innerHTML = `
            <div class="card-header">
                <span class="card-title">因子组合</span>
                <div class="card-weight-group">
                    <label>权重:</label>
                    <input type="number" class="card-weight-input" value="10" min="0">
                </div>
                <button class="btn-remove-card" onclick="this.closest('.factor-card').remove()">✕</button>
            </div>
            <div class="conditions-list"></div>
            <div class="card-footer">
                <button class="btn-add-cond" onclick="App.showFactorModal('${side}', '${cardId}')">
                    <i class="fas fa-plus"></i> 插入新判定条件
                </button>
            </div>
        `;
        
        container.appendChild(card);
        this.addConditionToCard(cardId, type, true); // 初始化第一行
    },
    // 2. 在卡片内部添加条件行
    addConditionToCard(cardId, factorName, isFirst = false) {
        const card = document.getElementById(cardId);
        const list = card.querySelector('.conditions-list');
        
        const row = document.createElement('div');
        row.className = 'condition-row';
        row.innerHTML = `
            <div class="cond-logic">
                ${isFirst ? '<span class="first-tag">首选</span>' : `
                    <select class="cond-rel">
                        <option value="AND">且</option>
                        <option value="OR">或</option>
                    </select>
                `}
            </div>
            <div class="cond-name" title="${factorName}">${factorName}</div>
            <select class="cond-op">
                <option value="gt">></option>
                <option value="lt"><</option>
                <option value="eq">=</option>
                <option value="ge">≥</option>
                <option value="le">≤</option>
            </select>
            <input type="number" class="cond-val" value="0">
            ${isFirst ? '' : '<button class="btn-del-cond" onclick="this.parentElement.remove()">✕</button>'}
        `;
        list.appendChild(row);
    },

    // 获取所有因子配置 (用于发送给后端)
    // 3. 提取数据（适配嵌套结构）
    getFactorData(containerId) {
        const cards = document.querySelectorAll(`#${containerId} .factor-card`);
        const data = [];

        cards.forEach(card => {
            const weight = card.querySelector('.card-weight-input').value;
            const conditions = [];
            
            card.querySelectorAll('.condition-row').forEach(row => {
                conditions.push({
                    relation: row.querySelector('.cond-rel')?.value || "START",
                    operator: row.querySelector('.cond-op').value,
                    value: row.querySelector('.cond-val').value
                });
            });

            data.push({
                factor_group_name: card.querySelector('.card-title').innerText,
                weight: weight,
                logic_tree: conditions
            });
        });
        return data;
    },

    /**
     * ============================================================
     * 4. 业务功能实现 (后端对接核心)
     * ============================================================
     */

    // 1. 选股逻辑
    async runSelection() {
        const buyConfig = this.getFactorData('buy-factor-container');
        const token = document.getElementById('tushareToken').value;

        this.log("正在打包选股策略发送至后端...", "system");
        
        const result = await this.callBackend('/select_stocks', 'POST', {
            token: token,
            strategies: buyConfig
        });

        if(result) this.updateSelectionTable(result.data);
    },

    // 2. 回测逻辑
    async runBacktest() {
        const payload = {
            startDate: document.getElementById('bt-start-date').value,
            endDate: document.getElementById('bt-end-date').value,
            isIdeal: document.getElementById('bt-is-ideal').checked,
            buySource: document.getElementById('backtest-buy-source').value,
            sellSource: document.getElementById('backtest-sell-source').value
        };

        this.log("启动回测引擎...", "info");
        const result = await this.callBackend('/backtest', 'POST', payload);
        
        if(result) {
            this.updateBacktestUI(result);
        }
    },

    // 3. 持仓诊断逻辑
    async runDiagnosis() {
        const sellConfig = this.getFactorData('sell-factor-container');
        this.log("正在根据当前卖出策略诊断持仓...", "warning");
        
        const result = await this.callBackend('/diagnose', 'POST', {
            sell_strategy: sellConfig
        });

        if(result) {
            const output = document.getElementById('diagnosis-output');
            output.innerHTML = `<p class="highlight">${result.message}</p>`;
            this.log("诊断完成", "success");
        }
    },

    /**
     * ============================================================
     * 5. 辅助工具
     * ============================================================
     */

    // 统一日志方法
    log(msg, type = 'info') {
        const container = document.getElementById('global-log-container');
        // 如果找不到日志框，先打印到浏览器控制台，不要让程序崩溃
        if (!container) {
            console.log(`[${type}] ${msg}`);
            return; 
        }
        const item = document.createElement('div');
        const time = new Date().toLocaleTimeString();
        item.className = `log-item ${type}`;
        item.innerHTML = `[${time}] ${msg}`;
        container.appendChild(item);
        
        // 自动滚动到底部
        container.scrollTop = container.scrollHeight;
    },

    // API 通信封装
    async callBackend(endpoint, method, data = null) {
        try {
            this.log(`发起请求: ${endpoint}...`, "system");
            // 这里替换为实际的 fetch
            // const response = await fetch(`${CONFIG.apiBase}${endpoint}`, {
            //     method: method,
            //     body: data ? JSON.stringify(data) : null,
            //     headers: { 'Content-Type': 'application/json' }
            // });
            // return await response.json();
            
            // 模拟延迟
            return new Promise(resolve => setTimeout(() => {
                this.log(`后端响应: ${endpoint} 成功`, "success");
                resolve({ success: true, data: [] });
            }, 800));

        } catch (error) {
            this.log(`请求失败: ${error}`, "error");
            return null;
        }
    },

    // 导出配置为 JSON 文件
    exportConfig(side) {
        const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
        const data = this.getFactorData(containerId);
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${side}_strategy_${Date.now()}.json`;
        a.click();
        this.log(`策略已导出为 JSON`, "success");
    },

    // 模态框逻辑
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
                    // 情况 A: 给已有的卡片添加新类型的逻辑行
                    this.addConditionToCard(targetCardId, type);
                } else {
                    // 情况 B: 创建一个新的因子卡片
                    const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
                    this.renderFactorCard(type, containerId, side);
                }
                modal.classList.remove('active');
            };
            list.appendChild(btn);
        });

        modal.classList.add('active');
        document.getElementById('btn-close-modal').onclick = () => modal.classList.remove('active');
    },

    // K线图初始化 (选股页专用)
    initCanvas() {
        const canvas = document.getElementById('klineCanvas');
        if(!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.strokeStyle = '#2d3245';
        ctx.strokeRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#94a3b8';
        ctx.fillText("等待选股数据加载...", 450, 200);
    }
};