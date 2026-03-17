
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
    /**
 * 验证所有因子卡片中的日期范围
 * @param {string} containerId - 容器ID
 * @returns {boolean} - 是否通过验证
 */

const ChartInstances = {
    klineChart: null,
    portfolioChart: null
};

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

let manager = null;

export function setEventManager(_manager) {
    manager = _manager;
}


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
            } else {
                // 恢复原始文本
                const originalText = fetchButtonTexts.get(btnId) || btn.textContent;
                btn.textContent = originalText;
                btn.disabled = false;
                btn.classList.remove('loading');
            }
        }
    });
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

        
        function validateDateRanges(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return true;
            const dateInputPairs = container.querySelectorAll('.condition-row__date');
            
            for (let dateRow of dateInputPairs) {
                const inputs = dateRow.querySelectorAll('.date-range-input');
                if (inputs.length === 2) {
                    const fromDate = parseFloat(inputs[0].value) || 0;
                    const toDate = parseFloat(inputs[1].value) || 0;
                    
                    if (fromDate < 0 || toDate < 0) {
                        App.log(`【日期设置错误：日期(${fromDate})或日期(${toDate})为负数无效值，无法执行`, 'error');
                        return false;
                    }

                    // 检查：前一个日期不能大于后一个日期
                    if (fromDate >= toDate) {
                        App.log(`【日期设置错误：起始日期(${fromDate})大于等于结束日期(${toDate})，无法执行`, 'error');
                        return false;
                    }
                }
            }
            
            return true;
        }
        //列表拉取
        const updateBtn1 = document.getElementById('api-fetch-list');
        if (updateBtn1) {
            updateBtn1.addEventListener('click', () => {
                if (manager) {
                    manager.requestUpdateData(1);
                }
            });
        }
        
        
        const updateBtn2 = document.getElementById('api-fetch-daily');
        if (updateBtn2) {
            updateBtn2.addEventListener('click', () => {
                if (manager) {
                    setFetchButtonsLoading(true);
                    manager.requestUpdateData(2);
                }
            });
        }
        const updateBtn3 = document.getElementById('api-fetch-adj');
        if (updateBtn3) {
            updateBtn3.addEventListener('click', () => {
                if (manager) {
                    setFetchButtonsLoading(true);
                    manager.requestUpdateData(3);
                }
            });
        }
        const updateBtn4 = document.getElementById('api-fetch-value');
        if (updateBtn4) {
            updateBtn4.addEventListener('click', () => {
                if (manager) {
                    setFetchButtonsLoading(true);
                    manager.requestUpdateData(4);
                }
            });
        }

        const updateBtn5 = document.getElementById('api-update-data');
        if (updateBtn5) {
            updateBtn5.addEventListener('click', () => {
                if (manager) {
                    setFetchButtonsLoading(true);
                    manager.requestUpdateData(5);
                }
            });
        }
        const updateBtn6 = document.getElementById('api-stop_update');
        if (updateBtn6) {
            updateBtn6.addEventListener('click', () => {
                if (manager) {
                    setFetchButtonsLoading(false);
                    manager.stopUpdateData();
                }
            });
        }
        
        //const selectBtn = document.getElementById('api-select-stock');
        //if (selectBtn) {
        //    selectBtn.addEventListener('click', () => {
        //        if (manager) {
        //            manager.requestSelectStocks();
        //        }
        //    });
        //}

        const runSelectionBtn = document.getElementById('api-run-selection');
        if (runSelectionBtn) {
            runSelectionBtn.addEventListener('click', () => {

                if (manager) {
                if (!validateDateRanges('buy-factor-container')) {
                    return;
                }
                    manager.requestSelectStocks();
                }
            });
        }
        
        const runBacktestBtn = document.getElementById('api-run-backtest');
        if (runBacktestBtn) {
            runBacktestBtn.addEventListener('click', () => {

                if (!validateDateRanges('buy-factor-container') || !validateDateRanges('sell-factor-container')) {
                    App.log('买入或卖出因子中存在日期错误，无法执行', 'error');
                    return;
                }
                

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