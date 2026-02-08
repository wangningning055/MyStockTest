/**
 * app.js - 主应用入口（拆分后版本）
 * 
 * 职责：
 * - 导入所有功能模块
 * - 暴露统一的 App 和 UIManager 接口
 * - 保持向后兼容性
 * - 维护全局状态
 */

// ============ 导入所有功能模块 ============
import { UIManagerUtils } from './uiManager.js';
import { FactorManager, setFactorManager } from './factorManager.js';
import { ConditionManager, setConditionManager } from './conditionManager.js';
import { ConfigManager, setConfigManager } from './configManager.js';
import { ChartManager, setChartManager } from './chartManager.js';
import { EventManager, setEventManager } from './eventManager.js';

// ============ 配置和状态 ============
export const CONFIG = {
    factorsUrl: "/static/factors.json",
    apiBase: "http://127.0.0.1:5000/api" 
};

export const State = {
    buyFactors: [],
    sellFactors: [],
    holdings: [],
    initialFund: 100000,
    selectedStock: null
};

let manager = null;

export function SetManager(_manager) {
    manager = _manager;
    // 为各个模块注入 manager 实例
    setFactorManager(_manager);
    setConditionManager(_manager);
    setConfigManager(_manager);
    setChartManager(_manager);
    setEventManager(_manager);
}

// ============ 合并 UIManager（为了向后兼容） ============
export const UIManager = {
    ...UIManagerUtils,
    // 所有 get/set 方法都从 UIManagerUtils 继承
};

// ============ App 对象 - 合并所有模块的接口 ============
export const App = {
    // -------- 初始化 --------
    init() {
        console.log("初始化！！！！")
        EventManager.init();
        this.bindFactorEvents()
        this.log("系统引擎启动成功，等待指令...", "system");
    },

    // -------- 事件管理相关 --------
    bindTabs() { 
        return EventManager.bindTabs(); 
    },
    bindGlobalEvents() { 
        return EventManager.bindGlobalEvents(); 
    },
    bindBacktestEvents() { 
        return EventManager.bindBacktestEvents(); 
    },
    bindFactorEvents() { 
        return FactorManager.bindFactorEvents(); 
    },

    // -------- 因子管理相关 --------
    showFactorModal(side, targetCardId) { 
        return FactorManager.showFactorModal(side, targetCardId); 
    },
    renderFactorCard(type, containerId, side) { 
        return FactorManager.renderFactorCard(type, containerId, side); 
    },
    addConditionToCard(cardId, factorName, isFirst) { 
        return FactorManager.addConditionToCard(cardId, factorName, isFirst); 
    },

    // -------- 条件分组相关 --------
    bindConditionRowEvents(row, list) { 
        return ConditionManager.bindConditionRowEvents(row, list); 
    },
    createConditionGroup(relation) { 
        return ConditionManager.createConditionGroup(relation); 
    },
    wrapConditionInGroup(row) { 
        return ConditionManager.wrapConditionInGroup(row); 
    },
    deleteGroup(group) { 
        return ConditionManager.deleteGroup(group); 
    },
    collectConditionsTree(container) { 
        return ConditionManager.collectConditionsTree(container); 
    },
    buildUIFromTree(nodes, container) { 
        return ConditionManager.buildUIFromTree(nodes, container); 
    },

    // -------- 配置管理相关 --------
    getFactorData(containerId) { 
        return ConfigManager.getFactorData(containerId); 
    },
    exportConfig(side) { 
        return ConfigManager.exportConfig(side); 
    },
    importConfig(side) { 
        return ConfigManager.importConfig(side); 
    },
    applyConfigToContainer(data, side) { 
        return ConfigManager.applyConfigToContainer(data, side); 
    },
    loadConfigFile(selectId) { 
        return ConfigManager.loadConfigFile(selectId); 
    },

    // -------- 业务逻辑相关 --------
    runSelection() {
        State.buyFactors = this.getFactorData('buy-factor-container');
        if (manager) {
            manager.requestSelectStocks();
        }
    },

    runBacktest() {
        State.buyFactors = this.getFactorData('buy-factor-container');
        State.sellFactors = this.getFactorData('sell-factor-container');
        if (manager) {
            manager.requestBacktest();
        }
    },

    runDiagnosis() {
        if (manager) {
            manager.requestDiagnose();
        }
    },

    callBackend(endpoint, method, data = null) {
        if (manager) {
            manager.requestUpdateData(data);
        }
    },

    // -------- 日志相关 --------
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
    }
};

// ============ 生命周期初始化 ============
document.addEventListener('DOMContentLoaded', async () => { 
    // 加载因子数据
    await FactorManager.loadFactorsData();
    
    // 初始化应用
    App.init();
});
