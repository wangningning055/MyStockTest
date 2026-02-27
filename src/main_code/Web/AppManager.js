/**
 * AppManager - 应用统一管理器（修改版）
 * 更新：改进的请求方法，支持树形条件结构
 * 
 * 关键改进：
 * 1. requestSelectStocks() - 发送完整的因子配置
 * 2. requestBacktest() - 分别发送buy_configs和sell_configs
 * 3. requestDiagnose() - 支持卖出条件评估
 * 4. 数据验证和错误处理
 */

import * as SocketModule from "./socket.js";
import { UIManager, State, CONFIG, App} from "./app.js";
import * as AppModule from "./app.js";


class AppManager {
    constructor() {
        // 实例引用
        this.socket = null;
        this.ui = UIManager;
        this.state = State;
        this.config = CONFIG;
        this.app = App;
        
        // 连接状态
        this.isConnected = false;
        
        // WebSocket消息处理回调字典
        this.messageHandlers = new Map();
        
        // 事件绑定配置
        this.eventBindings = new Map();
    }

    /**
     * 初始化应用
     */
    init() {
        this.app.log("🚀 应用启动：初始化 AppManager");
        
        // 步骤1: 初始化WebSocket
        this.initWebSocket();
        SocketModule.SetManager(this)
        AppModule.SetManager(this)
        // 步骤2: 注册默认消息处理器
        this.registerDefaultHandlers();
        
        // 步骤3: 自动绑定事件（如果app.js中已配置）
        this.bindAllEvents();
        
        // 步骤4: 尝试连接
        this.connect();
        
        this.app.log("✅ AppManager 初始化完成");
        return this;
    }

    /**
     * 初始化WebSocket模块
     */
    initWebSocket() {
        this.socket = {
            init: SocketModule.SocketInit,
            send: SocketModule.sendMsg,
            sendMessage: (type, payload = {}) => this._sendMessage(type, payload),
            onMessage: (callback) => this._registerMessageHandler(callback),
            getStatus: () => this.isConnected,
            SetManager:SocketModule.SetManager,
        };
    }

    /**
     * 连接WebSocket
     */
    connect() {

        try {
            SocketModule.SocketInit();
            setTimeout(() => {
                this.isConnected = true;
                this.ui.setConnectionStatus(true);
                this.app.log("✅ WebSocket 已连接", "success");
                this.requestLastUpdateDataTime()
            }, 500);
        } catch (error) {
            this.app.log(`❌ WebSocket 连接失败: ${error.message}`, "error");
            this.isConnected = false;
            this.ui.setConnectionStatus(false);
        }
    }

    /**
     * 注册默认的消息处理器
     */
    registerDefaultHandlers() {
        this.registerHandler(SocketModule.MessageType.LOG, (data) =>{
            this.app.log(`📊 后端log:${data.msg}`);
        });

        this.registerHandler(SocketModule.MessageType.LAST_UPDATE_DATA, (data) =>{
            this.app.log(`📊 收到日期更新:${data.msg}`);
            if (!/^\d{8}$/.test(data.msg)) {
                throw new Error("非法日期格式，应为 YYYYMMDD");
            }
            let timeStr = `${data.msg.slice(0, 4)}/${data.msg.slice(4, 6)}/${data.msg.slice(6, 8)}`;
            this.ui.setLastUpdateTime(timeStr)
        });


        // 处理数据更新消息
        this.registerHandler('sc_update_data', (data) => {
            this.app.log("📊 收到数据更新:", data);
            this.app.log("数据已更新", "success");
            if (data.lastUpdateTime) {
                this.ui.setLastUpdateTime(data.lastUpdateTime);
            }
        });

        // 处理选股结果
        this.registerHandler('sc_select_stocks_result', (data) => {
            this.app.log("📈 收到选股结果:", data);
            this.ui.updateIndustryAnalysisTable(data.industryAnalysis);
            this.ui.updateSelectionTable(data.stocks);
            this.app.log(`选股完成，共找到 ${data.stocks?.length || 0} 只股票`, "success");
        });

        // 处理回测结果
        this.registerHandler('sc_back_test_result', (data) => {
            this.app.log("🔄 收到回测结果:", data);
            this.ui.updateBacktestUI(data);
            if (data.klineData) {
                this.ui.drawKlineChart(data.klineData);
            }
            if (data.portfolioData) {
                this.ui.drawPortfolioChart(data.portfolioData);
            }
            this.app.log("回测完成", "success");
        });

        // 处理出仓判断结果
        this.registerHandler('sc_diagnose_result', (data) => {
            this.app.log("🎯 收到出仓判断结果:", data);
            this.ui.setDiagnoseResults(data);
            this.app.log("出仓判断完成", "success");
        });

        // 处理错误消息
        this.registerHandler('error', (data) => {
            console.error("❌ 后端错误:", data);
            this.app.log(`错误: ${data.message}`, "error");
        });
    }

    /**
     * 注册自定义消息处理器
     */
    registerHandler(messageType, handler) {
        this.messageHandlers.set(messageType, handler);
    }

    /**
     * 处理来自WebSocket的消息
     */
    handleMessage(type, data) {
        const handler = this.messageHandlers.get(type);
        if (handler) {
            try {
                handler(data);
            } catch (error) {
                console.error(`处理消息 ${type} 时出错:`, error);
                this.app.log(`处理消息失败: ${error.message}`, "error");
            }
        } else {
            console.warn(`未找到消息处理器: ${type}`);
        }
    }

    /**
     * ==================== 事件绑定系统 ====================
     */

    /**
     * 配置事件绑定（在app.js中调用）
     */
    onElementClick(elementId, callback) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`⚠️ 元素不存在: ${elementId}`);
            return;
        }
        element.addEventListener('click', callback);
        this.app.log(`✅ 事件已绑定: ${elementId} -> click`);
    }

    /**
     * 绑定输入事件
     */
    onElementInput(elementId, callback) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`⚠️ 元素不存在: ${elementId}`);
            return;
        }
        element.addEventListener('input', callback);
        this.app.log(`✅ 事件已绑定: ${elementId} -> input`);
    }

    /**
     * 绑定变化事件
     */
    onElementChange(elementId, callback) {
        const element = document.getElementById(elementId);
        if (!element) {
            console.warn(`⚠️ 元素不存在: ${elementId}`);
            return;
        }
        element.addEventListener('change', callback);
        this.app.log(`✅ 事件已绑定: ${elementId} -> change`);
    }

    /**
     * 绑定自定义事件（当app.js中定义了bindEvents函数时自动调用）
     */
    bindAllEvents() {
        // 检查app.js中是否有bindEvents函数
        if (typeof window.bindAppEvents === 'function') {
            this.app.log("🔗 绑定app.js中定义的事件...");
            window.bindAppEvents(this);
        }
    }

    /**
     * ==================== 快捷请求方法 ====================
     */

    /**
     * 请求上次更新时间
     */
    requestLastUpdateDataTime(self){
        return this.socket.sendMessage(SocketModule.MessageType.LAST_UPDATE_DATA, {
            reason:"用户手动请求",
            timestamp: new Date().toISOString()
        });
    }

    /**
     * 请求更新数据
     */
    requestUpdateData() {
        this.app.log("📤 发送拉取数据请求...", "system");
        let token = this.ui.getTushareToken()
        this.app.log(`📤 ${token}`, "system");
        return this.socket.sendMessage(SocketModule.MessageType.CS_UPDATE_DATA, {
            token: token || "0000000000",
            timestamp: new Date().toISOString()
        });
    }

    /**
     * 发送选股请求到后端
     * 
     * 发送格式：
     * {
     *   configs: [
     *     {
     *       factor_group_name: string,
     *       weight: number,
     *       logic_tree: [...]  // 树形条件结构
     *     }
     *   ],
     *   timestamp: string,
     *   version: string
     * }
     */
    requestSelectStocks() {
        // 收集完整的配置数据
        const buyConfigs = this.app.getFactorData('buy-factor-container');
        
        if (!buyConfigs || buyConfigs.length === 0) {
            this.app.log("❌ 请先添加选股条件", "error");
            return false;
        }
        
        const payload = {
            configs: buyConfigs,
            timestamp: new Date().toISOString(),
            version: "1.0"
        };
        
        // 数据验证
        const totalWeight = buyConfigs.reduce((sum, cfg) => sum + (cfg.weight || 0), 0);
        if (totalWeight === 0) {
            this.app.log("⚠️ 警告：权重总和为0，建议检查配置", "warning");
        }
        
        this.app.log(`📤 发送选股请求，配置条件数: ${buyConfigs.length}，总权重: ${totalWeight}`, "system");
        console.log('选股请求数据:', JSON.stringify(payload, null, 2));
        
        return this.socket.sendMessage(SocketModule.MessageType.CS_SELECT_STOCKS, payload);
    }

    /**
     * 发送回测请求到后端
     * 
     * 发送格式：
     * {
     *   buy_configs: [...],
     *   sell_configs: [...],
     *   initial_fund: number,
     *   start_date: string (YYYYMMDD),
     *   end_date: string (YYYYMMDD),
     *   is_ideal: boolean,
     *   timestamp: string,
     *   version: string
     * }
     */
    requestBacktest() {
        const buyConfigs = this.app.getFactorData('buy-factor-container');
        const sellConfigs = this.app.getFactorData('sell-factor-container');
        
        if (!buyConfigs || buyConfigs.length === 0) {
            this.app.log("❌ 请先添加买入条件", "error");
            return false;
        }
        
        const dateRange = this.ui.getBacktestDateRange();
        const payload = {
            buy_configs: buyConfigs,
            sell_configs: sellConfigs,
            initial_fund: this.ui.getInitialFund(),
            start_date: dateRange.startDate,
            end_date: dateRange.endDate,
            is_ideal: this.ui.getBacktestIsIdeal(),
            timestamp: new Date().toISOString(),
            version: "1.0"
        };
        
        this.app.log(`📤 发送回测请求，买入条件: ${buyConfigs.length}，卖出条件: ${sellConfigs.length}`, "system");
        console.log('回测请求数据:', JSON.stringify(payload, null, 2));
        
        return this.socket.sendMessage('cs_back_test', payload);
    }

    /**
     * 发送出仓判断请求到后端
     * 
     * 发送格式：
     * {
     *   holdings: [
     *     {
     *       code: string,
     *       name: string,
     *       quantity: number,
     *       buy_price: number,
     *       ...
     *     }
     *   ],
     *   sell_configs: [...],
     *   timestamp: string,
     *   version: string
     * }
     */
    requestDiagnose() {
        const sellConfigs = this.app.getFactorData('sell-factor-container');
        const holdings = this.state.holdings;
        
        if (!holdings || holdings.length === 0) {
            this.app.log("❌ 请先添加持仓信息", "error");
            return false;
        }
        
        if (!sellConfigs || sellConfigs.length === 0) {
            this.app.log("⚠️ 警告：未配置卖出条件，将使用默认策略", "warning");
        }
        
        const payload = {
            holdings: holdings,
            sell_configs: sellConfigs,
            timestamp: new Date().toISOString(),
            version: "1.0"
        };
        
        this.app.log(`📤 发送出仓判断请求，持仓数: ${holdings.length}`, "system");
        console.log('出仓判断请求数据:', JSON.stringify(payload, null, 2));
        
        return this.socket.sendMessage('cs_diagnose', payload);
    }

    /**
     * 查询股票信息
     */
    queryStockInfo(code) {
        return this.socket.sendMessage('cs_query_stock', {
            code: code,
            type: 'query',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * 快速搜索股票
     */
    quickSearchStocks(keyword) {
        if (!keyword || keyword.trim().length === 0) {
            return;
        }
        return this.socket.sendMessage('cs_quick_search', {
            keyword: keyword.trim(),
            limit: 10,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * ==================== 状态管理 ====================
     */

    /**
     * 获取当前状态
     */
    getState() {
        return {
            ...this.state,
            connectionStatus: this.isConnected,
            timestamp: new Date().toISOString()
        };
    }

    /**
     * 设置状态
     */
    setState(updates) {
        Object.assign(this.state, updates);
    }

    /**
     * ==================== 内部方法 ====================
     */

    /**
     * 发送消息到WebSocket
     */
    _sendMessage(type, payload = {}) {
        if (!this.isConnected) {
            this.app.log("❌ 未连接到后端，无法发送消息", "error");
            return false;
        }

        const message = {
            type: type,
            payload: payload,
            timestamp: new Date().toISOString()
        };

        SocketModule.sendMessage(message);
        return true;
    }

    /**
     * 注册消息处理器
     */
    _registerMessageHandler(callback) {
        console.log("注册消息处理器")
    }

    /**
     * 调试
     */
    debug() {
        this.app.log("=== AppManager 调试信息 ===");
        this.app.log("连接状态:", this.isConnected);
        this.app.log("应用状态:", this.state);
        this.app.log("配置信息:", this.config);
        this.app.log("已注册处理器:", Array.from(this.messageHandlers.keys()));
    }
}

// 创建单例
const AppManagerInstance = new AppManager();

// 导出
export default AppManagerInstance;