
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
                document.querySelectorAll('.view-container, .view-container-valuegrowth').forEach(v => v.classList.remove('active'));

                //document.querySelector('.view-container-valuegrowth').classList.add('active');
                document.getElementById(target).classList.add('active');
                App.log(`切换至视图: ${tab.innerText}`, "system");
                setTimeout(() => {
                    // 自适应所有图表
                    const charts = [
                        'klineChart',
                        'selectionPortfolioChart',
                        'holdings-total-chart',
                        'holdings-division-chart'
                    ];
                    charts.forEach(chartId => {
                        const container = document.getElementById(chartId);
                        if (container) {
                            const chart = echarts.getInstanceByDom(container);
                            if (chart) chart.resize();
                        }
                    });
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
                    //setFetchButtonsLoading(true);
                    manager.requestUpdateData(2);
                }
            });
        }
        const updateBtn3 = document.getElementById('api-fetch-adj');
        if (updateBtn3) {
            updateBtn3.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(true);
                    manager.requestUpdateData(3);
                }
            });
        }
        const updateBtn4 = document.getElementById('api-fetch-value');
        if (updateBtn4) {
            updateBtn4.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(true);
                    manager.requestUpdateData(4);
                }
            });
        }

        const updateBtn4_2 = document.getElementById('api-fetch-value-now');
        if (updateBtn4_2) {
            updateBtn4_2.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(true);
                    manager.requestUpdateData(6);
                }
            });
        }

        const updateBtn5 = document.getElementById('api-update-data');
        if (updateBtn5) {
            updateBtn5.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(true);
                    manager.requestUpdateData(5);
                }
            });
        }
        const updateBtn6 = document.getElementById('api-stop_update');
        if (updateBtn6) {
            updateBtn6.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(false);
                    manager.stopUpdateData();
                }
            });
        }

        const preheatBtn = document.getElementById('api-preheat');
        if (preheatBtn) {
            preheatBtn.addEventListener('click', () => {
                if (manager) {
                    //setFetchButtonsLoading(true);
                    manager.preheatData();
                }
            });
        }
        const changeDateBtn = document.getElementById('api-change-date');
        if (changeDateBtn) {
            changeDateBtn.addEventListener('click', () => {
                if (manager) {
                    manager.changeData();
                }
            });
        }

        const testBtn = document.getElementById('api-test');
        if (testBtn) {
            testBtn.addEventListener('click', () => {
                if (manager) {
                    manager.testData();
                }
            });
        }



        const valueImportBtn = document.getElementById('api-value-import');
        if (valueImportBtn) {
            valueImportBtn.addEventListener('click', () => {
                if (manager) {
                    manager.ImportValue();
                }
            });
        }


        const valueExportBtn = document.getElementById('api-value-export');
        if (valueExportBtn) {
            valueExportBtn.addEventListener('click', () => {
                if (manager) {
                    manager.ExportValue();
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
                
                const isBacktesting = runBacktestBtn.dataset.isBacktesting === 'true';
                if (manager) {

                    if (isBacktesting) {
                        manager.requestStopBacktest();
                    } else {
                        manager.requestBacktest();
                    }
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

        // -------- 分仓管理事件 --------
        const addDivisionBtn = document.getElementById('btn-add-division');
        if (addDivisionBtn) {
            addDivisionBtn.addEventListener('click', () => {
                if (manager && manager.holdings) {
                    const divisionName = prompt('请输入分仓名称：', `分仓${ manager.holdings.getDivisionsCount() + 1}`);
                    if (divisionName) {
                        manager.holdings.addDivision(divisionName);
                    }
                }
            });
        }

        const setHoldingsFundBtn = document.getElementById('btn-set-holdings-fund');
        if (setHoldingsFundBtn) {
            setHoldingsFundBtn.addEventListener('click', () => {
                const fundValue = UIManagerUtils.getHoldingsInitialFund();
                if (!isNaN(fundValue) && fundValue > 0) {
                    App.log(`初始本金已设置为: ¥${fundValue.toLocaleString()}`, "success");
                } else {
                    App.log("请输入有效的初始本金金额", "error");
                }
            });
        }

        const exportAllBtn = document.getElementById('holdings-export-all-config');
        if (exportAllBtn) {
            exportAllBtn.addEventListener('click', () => {
                if (manager && manager.holdings) {
                    manager.holdings.exportAllHoldingsConfig();
                }
            });
        }

        const importAllBtn = document.getElementById('holdings-import-all-config');
        if (importAllBtn) {
            importAllBtn.addEventListener('click', () => {
                if (manager && manager.holdings) {
                    manager.holdings.importAllHoldingsConfig();
                }
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

    bindHoldingsTabEvents() {
        const tabs = document.querySelectorAll('.holdings-tab-btn');
        const panes = document.querySelectorAll('.holdings-view-pane');
        
        if (tabs.length === 0 || panes.length === 0) {
            console.warn('⚠️ 找不到持仓标签页或视图面板元素');
            return;
        }
        
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                const viewName = tab.dataset.view;
                
                // 移除所有活跃状态
                tabs.forEach(t => t.classList.remove('active'));
                panes.forEach(p => p.classList.remove('active'));
                
                // 添加新的活跃状态
                tab.classList.add('active');
                const paneId = `holdings-${viewName}`;
                const pane = document.getElementById(paneId);
                if (pane) {
                    pane.classList.add('active');
                    App.log(`✅ 已切换到${viewName === 'total-view' ? '总仓收益' : '分仓详情'}视图`, "system");
                }
            });
        });
    },

    /**
     * 初始化所有事件
     */
    init() {
        this.bindTabs();
        this.bindGlobalEvents();
        this.bindBacktestEvents();
        this.bindHoldingsTabEvents();
        ChartManager.initCharts();
        App.log("系统引擎启动成功，等待指令...", "system");


        // ✅ 新增：初始化其他图表容器
        const selectionPortfolioContainer = document.getElementById('selectionPortfolioChart');
        if (selectionPortfolioContainer && !echarts.getInstanceByDom(selectionPortfolioContainer)) {
            echarts.init(selectionPortfolioContainer, 'dark');
        }
        
        const holdingsTotalContainer = document.getElementById('holdings-total-chart');
        if (holdingsTotalContainer && !echarts.getInstanceByDom(holdingsTotalContainer)) {
            echarts.init(holdingsTotalContainer, 'dark');
        }
        
        const holdingsDivisionContainer = document.getElementById('holdings-division-chart');
        if (holdingsDivisionContainer && !echarts.getInstanceByDom(holdingsDivisionContainer)) {
            echarts.init(holdingsDivisionContainer, 'dark');
        }

        
        App.log("系统引擎启动成功，等待指令...", "system");

    },
    bindHoldingsTabEvents() {
        const tabs = document.querySelectorAll('.holdings-tab-btn');
        const panes = document.querySelectorAll('.holdings-view-pane');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const viewName = tab.dataset.view;
                
                tabs.forEach(t => t.classList.remove('active'));
                panes.forEach(p => p.classList.remove('active'));
                
                tab.classList.add('active');
                document.getElementById(`holdings-${viewName}`).classList.add('active');
                
                App.log(`切换到${viewName === 'total-view' ? '总仓' : '分仓详情'}视图`, "system");
            });
        });
    },
};