import * as SocketModule from "./socket.js";
import { UIManager, State, CONFIG, App} from "./app.js";
import * as AppModule from "./app.js";
import { HoldingsManager, setHoldingsManager } from './holdingsManager.js';
import { ValueGrowthManager } from './valueGrowthManager.js';
import { IndustryRotationManager } from './industryRotationManager.js';
import { StockQueryManager } from './stockQueryManager.js';
import { SelectionResultManager, setSelectionResultManager } from './selectionResultManager.js';


const Message_Action = "/action";

// 存储拉取按钮的原始文本
const fetchButtonTexts = new Map();
// 定义所有拉取按钮的ID
const fetchButtonIds = [
    'api-fetch-list',
    'api-fetch-daily',
    'api-fetch-adj',
    'api-fetch-value',
    'api-update-data'
];
/**
 * 设置按钮加载状态
 * @param {boolean} isLoading - 是否为加载中状态
 */
function setFetchButtonsLoading(isLoading) {
    fetchButtonIds.forEach(btnId => {
        const btn = document.getElementById(btnId);
        if (btn) {
            if (isLoading) {
                // 保存原始文本
                fetchButtonTexts.set(btnId, btn.textContent);
                btn.textContent = '处理中...';
                btn.disabled = true;
                btn.classList.add('loading');
                document.getElementById('global-busy-bar').style.display = 'block';
                document.getElementById('busy-bar-fill').style.width = '0%';
                document.getElementById('busy-bar-percent').textContent = '0%';
                const busyBar = document.getElementById('global-busy-bar');
                busyBar.style.display = 'block';
                // 把整个 app-layout 往下推，避免被遮住
                document.querySelector('.app-layout').style.paddingTop = busyBar.offsetHeight + 'px';


            } else {
                // 恢复原始文本
                const originalText = fetchButtonTexts.get(btnId) || btn.textContent;
                btn.textContent = originalText;
                btn.disabled = false;
                btn.classList.remove('loading');
                document.getElementById('global-busy-bar').style.display = 'none';
                document.getElementById('global-busy-bar').style.display = 'none';
                document.querySelector('.app-layout').style.paddingTop = '0';

            }
        }
    });
}

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

        let isResizingLog = false;
        let startY = 0;
        let startHeight = 0;

        this.holdings = null;

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
        if (typeof HoldingsManager !== 'undefined') {
            this.holdings = HoldingsManager.init();
            this.app.log("✅ HoldingsManager 初始化完成");
        }
        ValueGrowthManager.init();
        ValueGrowthManager.setManager(this);
        
        if (typeof IndustryRotationManager !== 'undefined') {
            this.industryRotationManager = IndustryRotationManager.init();
            console.log("✅ 行业轮动管理器已初始化")
            this.app.log("✅ 行业轮动管理器已初始化", "system");
        }
        this.stockQueryManager = StockQueryManager.init();
        
        // ✅ 新增：初始化选股结果管理器
        this.selectionResultManager = SelectionResultManager.init();
        setSelectionResultManager(this);

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
     * 注册默认的消息处理器
     */
    registerDefaultHandlers() {

        let lastBusyState = null

        this.registerHandler(SocketModule.MessageType.LOG, (data) =>{
            this.app.log(`📊 后端log:${data.msg}`);
        });

        this.registerHandler(SocketModule.MessageType.SC_IN_BUSY, (data) =>{
            console.log(data.msg)
            const busyState = data.msg[0]
            const use = data.msg[1]
            const total = data.msg[2]
            this.ui.setMemoryUsage(use, total)
            //this.app.log(`📊 后端忙碌状态:${data.msg}`);
            if (busyState === lastBusyState) {
                return;
            }

            // 状态变化了，更新缓存
            lastBusyState = busyState;
            if(busyState == 1)
            {
                setFetchButtonsLoading(true)

                const backtestBtn = document.getElementById('api-run-backtest');
                if (backtestBtn) {
                    backtestBtn.textContent = '停止回测';  // 改为停止
                    backtestBtn.dataset.isBacktesting = 'true';  // 标记状态
                    backtestBtn.classList.add('btn-stop-backtest');

                }

            }
            else
            {
                setFetchButtonsLoading(false)
                const backtestBtn = document.getElementById('api-run-backtest');
                if (backtestBtn) {
                    backtestBtn.textContent = '运行回测';  // 改回原文本
                    backtestBtn.dataset.isBacktesting = 'false';
                    backtestBtn.classList.remove('btn-stop-backtest');
                }
            }
        });

        this.registerHandler(SocketModule.MessageType.SC_IN_PROGRESS, (data) => {
            const percent = (data.msg * 100).toFixed(1)
            const text = "处理中"
            const fill = document.getElementById('busy-bar-fill');
            const pct  = document.getElementById('busy-bar-percent');
            const txt  = document.getElementById('busy-bar-text');
            if (fill) fill.style.width = `${percent}%`;
            if (pct)  pct.textContent = `${percent}%`;
            if (txt)  txt.textContent = text;
        });
        
        this.registerHandler(SocketModule.MessageType.LAST_UPDATE_DATA, (data) =>{
            //this.app.log(`📊 收到日期更新:${data.msg}`);
            let jsonRes = JSON.parse(data.msg)
            let stock = jsonRes.stock
            let daily = jsonRes.daily
            let adjust = jsonRes.adjust
            let value = jsonRes.value
            let industry = jsonRes.industry
            
            let timeStrStock = `${stock.slice(0, 4)}/${stock.slice(4, 6)}/${stock.slice(6, 8)}`;
            let timeStrDaily = `${daily.slice(0, 4)}/${daily.slice(4, 6)}/${daily.slice(6, 8)}`;
            let timeStrAdjust = `${adjust.slice(0, 4)}/${adjust.slice(4, 6)}/${adjust.slice(6, 8)}`;
            let timeStrValue = `${value.slice(0, 4)}/${value.slice(4, 6)}/${value.slice(6, 8)}`;
            let timeStrIndustry = `${industry.slice(0, 4)}/${industry.slice(4, 6)}/${industry.slice(6, 8)}`;
            //console.log(timeStrStock)
            //console.log(timeStrDaily)
            //console.log(timeStrAdjust)
            //console.log(timeStrValue)
            //console.log(timeStrIndustry)
            if (!/^\d{8}$/.test(stock)) {
                throw new Error("非法日期格式stock list，应为 YYYYMMDD");
            }
            if (!/^\d{8}$/.test(daily)) {
                throw new Error("非法日期格式daily，应为 YYYYMMDD");
            }
            if (!/^\d{8}$/.test(adjust)) {
                throw new Error("非法日期格式adj，应为 YYYYMMDD");
            }
            if (!/^\d{8}$/.test(value)) {
                throw new Error("非法日期格式value，应为 YYYYMMDD");
            }
            if (!/^\d{8}$/.test(industry)) {
                throw new Error("非法日期格式industry，应为 YYYYMMDD");
            }
            this.ui.setLastStockListUpdateTime(timeStrStock)
            this.ui.setLastDailyUpdateTime(timeStrDaily)
            this.ui.setLastAdjustUpdateTime(timeStrAdjust)
            this.ui.setLastValueUpdateTime(timeStrValue)
            this.ui.setLastIndustryUpdateTime(timeStrIndustry)
            this.ui.setBacktestEndDateMax(daily); // 用日线更新日期作为回测最晚日期
        });

        this.registerHandler(SocketModule.MessageType.LAST_UPDATE_INDUSTRY, (data) =>{
            console.log("收到行业更新")
            //console.log(data.msg)
            ValueGrowthManager.setIndustries(data.msg || []);
        });

        // 处理数据更新消息
        this.registerHandler(SocketModule.MessageType.SC_UPDATE_DATA, (data) => {
            this.app.log("📊 收到数据更新:", data);
            this.app.log("数据已更新", "success");
            if (data.lastUpdateTime) {
                this.ui.setLastUpdateTime(data.lastUpdateTime);
            }
        });

        //处理成长价值股列表
        this.registerHandler(SocketModule.MessageType.LAST_UPDATE_GROW_VALUE, (data) =>{
            console.log("收到行业成长价值列表")
            console.log(data.msg)
            const res = JSON.parse(data.msg);
            ValueGrowthManager.setStocks(res || []);
        });


        // 处理行业轮动分析结果
        this.registerHandler(SocketModule.MessageType.SC_INDUSTRY_ROTATION, (data) => {
            if (data.status === 'success' && data.data) {
                IndustryRotationManager.handleAnalysisResult(data.data);
            }
        });

        //收到股票查询结果
        this.registerHandler(SocketModule.MessageType.SC_QUERY_STOCKS_RESPONSE,
            (data) => {
                if (window.App && window.App.StockQueryManager) {
                    window.App.StockQueryManager.handleQueryResponse(data.msg);
                }
            }
        );




        // ✅ 替换原来的选股结果处理器
        this.registerHandler('sc_select_stocks_result', (data) => {
            this.app.log("📈 收到选股结果", "success");
            
            // 传递给 SelectionResultManager
            if (this.selectionResultManager) {
                this.selectionResultManager.setResultData(data.stocks || data.msg || []);
            }
        });

        // ✅ 新增：K线数据流式块处理
        this.registerHandler('sc_kline_chunk', (data) => {
            if (this.selectionResultManager) {
                this.selectionResultManager.receiveKlineChunk(data.msg || data);
            }
        });

        // ✅ 新增：K线数据一次性返回
        this.registerHandler('sc_kline_data', (data) => {
            if (this.selectionResultManager) {
                this.selectionResultManager.receiveKlineData(data.msg || data);
            }
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
    requestUpdateData(type) {
        this.app.log("📤 发送拉取数据请求...", "system");
        let token = this.ui.getTushareToken()
        this.app.log(`📤 ${token}`, "system");
        return this.socket.sendMessage(SocketModule.MessageType.CS_UPDATE_DATA, {
            token: token || "0000000000",
            timestamp: new Date().toISOString(),
            type:type
        });
    }
    stopUpdateData() {
        this.app.log("📤发送停止拉取数据请求...", "system");
        return this.socket.sendMessage(SocketModule.MessageType.CS_STOP_UPDATE_DATA, {
            timestamp: new Date().toISOString(),
        });
    }

    //

    preheatData() {
        this.app.log("📤发送数据预热请求...", "system");
        return this.socket.sendMessage(SocketModule.MessageType.CS_PREHEAT_DATA, {
            timestamp: new Date().toISOString(),
        });
    }


    requestIndustryRotationAnalysis() {
        this.app.log("📤 发送行业轮动分析请求...", "system");
        //return this.socket.sendMessage(
        //    SocketModule.MessageType.CS_INDUSTRY_ROTATION, 
        //    {timestamp: new Date().toISOString()}
        //);
    }



    testData() {
        this.app.log("📤发送测试请求...", "system");
        return this.socket.sendMessage(SocketModule.MessageType.TEST, {
            timestamp: new Date().toISOString(),
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
        const threshold = this.ui.getWeightThreshold()
        if (!buyConfigs || buyConfigs.length === 0) {
            this.app.log("❌ 请先添加选股条件", "error");
            return false;
        }

        // ✅ 显示加载状态
        if (this.selectionResultManager) {
            this.selectionResultManager.showLoading();
        }

        const isExcludeST = this.ui.getFilterExcludeST()
        const isExcludeKC = this.ui.getFilterExcludeKC()
        const isExcludeCY = this.ui.getFilterExcludeCY()
        const isExclude_Value = this.ui.getFilterExcludeValue()
        const isExclude_Grow = this.ui.getFilterExcludeGrow()
        const payload = {
            isExcludeST : isExcludeST,
            isExcludeKC : isExcludeKC,
            isExcludeCY : isExcludeCY,
            isExclude_Value : isExclude_Value,
            isExclude_Grow : isExclude_Grow,
            configs: buyConfigs,
            timestamp: new Date().toISOString(),
            version: "1.0",
            threshold : threshold
        };
        
        // 数据验证
        const totalWeight = buyConfigs.reduce((sum, cfg) => sum + (cfg.weight || 0), 0);
        //if (totalWeight === 0) {
        //    this.app.log("⚠️ 警告：权重总和为0，建议检查配置", "warning");
        //}
        
        this.app.log(`📤 发送选股请求，配置条件数: ${buyConfigs.length}`, "system");
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
        
        const val = this.ui.getHoldingsFilterOptions()
        const configJson = this.holdings.getAllHoldingsConfigJson()
        const configData = this.holdings.getAllHoldingsConfig()
        console.log(configJson)
        const payload = {
            isExcludeST : val.excludeST,
            isExcludeKC : val.excludeKC,
            isExcludeCY : val.excludeCY,
            start_date: this.ui.getBacktestStartDate(),
            end_date:   this.ui.getBacktestEndDate(),
            config : configData,
            timestamp: new Date().toISOString(),
            version: "1.0"
        };
        

        this.app.log(`📤 发送回测请求, "system"`);
        console.log('回测请求数据:', JSON.stringify(payload, null, 2));
        

        return this.socket.sendMessage(SocketModule.MessageType.CS_BACK_TEST, payload);
    }
    //发送停止回测
    requestStopBacktest() {
        this.app.log(`📤 发送停止回测请求, "system"`);
        return this.socket.sendMessage(SocketModule.MessageType.CS_BACK_TEST_STOP, {
            timestamp: new Date().toISOString(),    });
    }

        /**
     * 请求行业轮动分析
     */
    requestIndustryRotationAnalysis() {
        this.app.log("📤 发送行业轮动分析请求...", "system");
        const rotationStatus = document.getElementById('rotation-status');
        if (rotationStatus) rotationStatus.style.display = 'flex';
        
        return this.socket.sendMessage(SocketModule.MessageType.CS_INDUSTRY_ROTATION, {
            timestamp: new Date().toISOString(),
        });
    }

    
    /**
     * 查询股票信息
     */
    requestQueryStockInfo(queryType, queryValue) {
        const payload = {
            query_type: queryType,    // 'code' | 'letter' | 'keyword'
            query_value: queryValue,   // 实际的查询值
            timestamp: new Date().toISOString()
        };
        return this.socket.sendMessage(
            SocketModule.MessageType.CS_QUERY_STOCKS,
            payload
        );

    }

    /**
     * 请求单只股票的K线数据
     */
    requestStockKline(stockCode, days = 240) {
        this.app.log(`📤 请求K线数据: ${stockCode}`, "system");
        return this.socket.sendMessage('cs_request_kline', {
            code: stockCode,
            days: days,
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