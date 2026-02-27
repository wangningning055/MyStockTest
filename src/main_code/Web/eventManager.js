
/**
 * eventManager.js - 事件管理模块
 * 
 * 职责：
 * - 页签切换事件
 * - 全局按钮事件
 * - 回测相关事件
 * - 日志清空事件
 */

import { App } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { ChartManager } from './chartManager.js';

const ChartInstances = {
    klineChart: null,
    portfolioChart: null
};

const Message_Action = "/action";

let manager = null;

export function setEventManager(_manager) {
    manager = _manager;
}

export const EventManager = {
    /**
     * 绑定页签切换事件
     */
    bindTabs() {
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const target = tab.dataset.target;
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                document.querySelectorAll('.view-container').forEach(v => v.classList.remove('active'));
                document.getElementById(target).classList.add('active');
                App.log(`切换至视图: ${tab.innerText}`, "system");
                setTimeout(() => {
                    if (ChartInstances.klineChart) ChartInstances.klineChart.resize();
                    if (ChartInstances.portfolioChart) ChartInstances.portfolioChart.resize();
                }, 100);
            });
        });
    },

    /**
     * 绑定全局事件
     */
    bindGlobalEvents() {

        
        const updateBtn = document.getElementById('api-update-data');
        if (updateBtn) {
            updateBtn.addEventListener('click', () => {
                if (manager) {
                    manager.requestUpdateData();
                }
            });
        }
        
        const selectBtn = document.getElementById('api-select-stock');
        if (selectBtn) {
            selectBtn.addEventListener('click', () => {
                if (manager) {
                    manager.requestSelectStocks();
                }
            });
        }

        const runSelectionBtn = document.getElementById('api-run-selection');
        if (runSelectionBtn) {
            runSelectionBtn.addEventListener('click', () => {
                if (manager) {
                    State.buyFactors = App.getFactorData('buy-factor-container');
                    manager.requestSelectStocks();
                }
            });
        }
        
        const runBacktestBtn = document.getElementById('api-run-backtest');
        if (runBacktestBtn) {
            runBacktestBtn.addEventListener('click', () => {
                if (manager) {
                    State.buyFactors = App.getFactorData('buy-factor-container');
                    State.sellFactors = App.getFactorData('sell-factor-container');
                    manager.requestBacktest();
                }
            });
        }
        
        const diagnoseBtn = document.getElementById('api-diagnose-holdings');
        if (diagnoseBtn) {
            diagnoseBtn.addEventListener('click', () => {
                if (manager) {
                    manager.requestDiagnose();
                }
            });
        }
        
        const clearLogBtn = document.getElementById('btn-clear-log');
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => {
                const container = document.getElementById('global-log-container');
                if (container) container.innerHTML = '';
            });
        }
    },

    /**
     * 绑定回测事件
     */
    bindBacktestEvents() {
        const setFundBtn = document.getElementById('setInitialFundBtn');
        if (setFundBtn) {
            setFundBtn.addEventListener('click', () => {
                const fundValue = UIManagerUtils.getInitialFund();
                if (!isNaN(fundValue) && fundValue > 0) {
                    UIManagerUtils.setInitialFund(fundValue);
                    App.log(`初始本金设置为: ¥${fundValue.toLocaleString()}`, "success");
                } else {
                    App.log("请输入有效的初始本金金额", "error");
                }
            });
        }
        
        const weightSlider = document.getElementById('weight-threshold-slider');
        if (weightSlider) {
            weightSlider.addEventListener('input', (e) => {
                const display = document.getElementById('threshold-value-display');
                if (display) display.textContent = parseFloat(e.target.value).toFixed(2);
            });
        }
        
        const holdingsSlider = document.getElementById('holdings-weight-threshold-slider');
        if (holdingsSlider) {
            holdingsSlider.addEventListener('input', (e) => {
                const display = document.getElementById('holdings-threshold-value-display');
                if (display) display.textContent = parseFloat(e.target.value).toFixed(2);
            });
        }
    },

    /**
     * 初始化所有事件
     */
    init() {
        this.bindTabs();
        this.bindGlobalEvents();
        this.bindBacktestEvents();
        ChartManager.initCharts();
        App.log("系统引擎启动成功，等待指令...", "system");
    }
};