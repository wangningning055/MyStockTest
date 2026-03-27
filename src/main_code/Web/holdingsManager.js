/**
 * holdingsManager.js - 持仓分仓管理模块
 * 
 * 职责：
 * - 分仓的增删改查
 * - 分仓参数管理（初始本金、仓位占比、止盈/止损/持仓时间）
 * - 分仓内部的买入/卖出配置管理
 * - 分仓配置导入导出
 * - 整体回测配置导入导出
 */

import { App } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { FactorManager } from './factorManager.js';
import { ConditionManager } from './conditionManager.js';
import { ConfigManager } from './configManager.js';
import { FactorEditor } from './factorEditor.js';
let manager = null;
let divisionsData = [];
let selectedDivisionId = null;

export function setHoldingsManager(_manager) {
    manager = _manager;
}

export const HoldingsManager = {
    /**
     * 初始化分仓管理
     */
    init() {
        this.loadDivisionsFromStorage();
        this.renderDivisionsList();
        this.bindDivisionEvents();
        this.bindDivisionSelector();
        App.log('分仓管理系统已初始化', 'system');
        return this
    },

    getDivisionsData() {
        return divisionsData;
    },

    /**
     * 获取分仓数量
     */
    getDivisionsCount() {
        return divisionsData.length;
    },

    /**
     * 设置分仓数据
     */
    setDivisionsData(data) {
        divisionsData = Array.isArray(data) ? data : [];
        this.saveDivisionsToStorage();
    },


    // ============ 数据存储与加载 ============

    /**
     * 从本地存储加载分仓数据
     */
    loadDivisionsFromStorage() {
        try {
            const stored = localStorage.getItem('holdings_divisions_config');
            if (stored) {
                divisionsData = JSON.parse(stored);
                console.log('✅ 分仓数据从本地存储加载成功');
            } else {
                // 初始化默认分仓
                divisionsData = [
                    this.createDefaultDivision('分仓1')
                ];
                this.saveDivisionsToStorage();
            }
        } catch (error) {
            console.error('加载分仓数据失败：', error);
            divisionsData = [this.createDefaultDivision('分仓1')];
        }
    },

    /**
     * 保存分仓数据到本地存储
     */
    saveDivisionsToStorage() {
        try {
            localStorage.setItem('holdings_divisions_config', JSON.stringify(divisionsData));
            console.log('✅ 分仓数据已保存');
        } catch (error) {
            console.error('保存分仓数据失败：', error);
        }
    },

    /**
     * 创建默认分仓对象
     */
    createDefaultDivision(name) {
        return {
            id: `div-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            name: name,
            weight: 1.0 / Math.max(1, divisionsData.length + 1), // 平均分配
            holdingTimeMin: 0,      // 最短持仓天数，0表示不限制
            holdingTimeMax: 999,    // 最长持仓天数，0表示不限制
            stopLossPercent: 0,     // 止损位，0表示不启用
            takeProfitPercent: 0,   // 止盈位，0表示不启用
            buyConfigTree: [],      // 买入条件树
            sellConfigTree: [],     // 卖出条件树
            createdAt: new Date().toISOString()
        };
    },

    // ============ 分仓的增删改 ============

    /**
     * 添加新分仓
     */
    addDivision(name) {
        const divisionName = name || `分仓${divisionsData.length + 1}`;
        const newDivision = this.createDefaultDivision(divisionName);
        divisionsData.push(newDivision);
        this.saveDivisionsToStorage();
        this.renderDivisionsList();
        App.log(`分仓 "${divisionName}" 已创建`, 'success');
        return newDivision.id;
    },

    /**
     * 删除分仓
     */
    removeDivision(divisionId) {
        const index = divisionsData.findIndex(d => d.id === divisionId);
        if (index !== -1) {
            const divisionName = divisionsData[index].name;
            divisionsData.splice(index, 1);
            this.saveDivisionsToStorage();
            this.renderDivisionsList();
            
            // 如果删除的是选中的分仓，选择第一个
            if (selectedDivisionId === divisionId && divisionsData.length > 0) {
                selectedDivisionId = divisionsData[0].id;
            }
            
            App.log(`分仓 "${divisionName}" 已删除`, 'info');
        }
    },

    /**
     * 更新分仓名称
     */
    updateDivisionName(divisionId, newName) {
        const division = divisionsData.find(d => d.id === divisionId);
        if (division) {
            division.name = newName;
            this.saveDivisionsToStorage();
            App.log(`分仓名称已更新为 "${newName}"`, 'success');
        }
    },

    /**
     * 获取分仓数据
     */
    getDivision(divisionId) {
        return divisionsData.find(d => d.id === divisionId);
    },

    /**
     * 获取所有分仓
     */
    getDivisionsList() {
        return divisionsData;
    },

    /**
     * 更新分仓参数
     */
    updateDivisionSettings(divisionId, settings) {
        const division = this.getDivision(divisionId);
        if (division) {
            Object.assign(division, settings);
            this.saveDivisionsToStorage();
            App.log(`分仓 "${division.name}" 设置已更新`, 'success');
        }
    },

    // ============ 分仓配置管理 ============

    /**
     * 获取分仓的买入因子数据
     */
    getDivisionBuyFactorData(divisionId) {
        const division = this.getDivision(divisionId);
        if (!division) return [];
        // 从分仓的 buyConfigTree 重建因子数据格式
        return this.convertTreeToFactorData(division.buyConfigTree);
    },

    /**
     * 获取分仓的卖出因子数据
     */
    getDivisionSellFactorData(divisionId) {
        const division = this.getDivision(divisionId);
        if (!division) return [];
        return this.convertTreeToFactorData(division.sellConfigTree);
    },

    /**
     * 将条件树转换为因子数据格式
     */
    convertTreeToFactorData(tree) {
        // 这是从 conditionManager 的 collectConditionsTree 得到的格式
        // 需要转换回 configManager 需要的格式
        // 实现细节取决于你的数据结构
        return [];
    },

    /**
     * 导出分仓配置（指定分仓的买入或卖出配置）
     */
    exportDivisionConfig(divisionId, side) {
        const division = this.getDivision(divisionId);
        if (!division) {
            App.log('分仓不存在', 'error');
            return;
        }

        const configTree = side === 'buy' ? division.buyConfigTree : division.sellConfigTree;
        const threshold = side === 'buy' ? division.thresholdBuy : division.thresholdSell;
        const config = {
            threshold:threshold,
            divisionName: division.name,
            side: side,
            configs: configTree,
            timestamp: new Date().toISOString(),
            version: "1.0"
        };

        const jsonString = JSON.stringify(config, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${division.name}_${side}_config_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        App.log(`分仓 "${division.name}" 的 ${side === 'buy' ? '买入' : '卖出'}配置已导出`, 'success');
    },

    /**
     * 导入分仓配置
     */
    importDivisionConfig(divisionId, side) {
        const division = this.getDivision(divisionId);
        if (!division) {
            App.log('分仓不存在', 'error');
            return;
        }

        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);
                    console.log(event.target.result)
                    if (side === 'buy') {
                        division.thresholdBuy = data.threshold
                        division.buyConfigTree = data.configs || [];
                    } else {
                        division.thresholdSell = data.threshold
                        division.sellConfigTree = data.configs || [];
                    }
                    console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!已经导入了编辑器的数据")
                    console.log(division.buyConfigTree)
                    this.saveDivisionsToStorage();
                    this.loadDivisionDetailView(divisionId);
                    App.log(`分仓 "${division.name}" 的 ${side === 'buy' ? '买入' : '卖出'}配置已导入`, 'success');
                } catch (error) {
                    console.error('导入配置失败：', error);
                    App.log(`导入失败：${error.message}`, 'error');
                }
            };
            reader.readAsText(file);
        });
        input.click();
    },
   

    /**
     * 编辑分仓的买入/卖出条件
     */
    editDivisionConfig(divisionId, side) {
        const division = this.getDivision(divisionId);
        if (!division) {
            App.log('分仓不存在', 'error');
            return;
        }

        // 获取或创建分仓的因子容器
        let containerId = `division-${divisionId}-${side}-container`;
        let container = document.getElementById(containerId);

        if (!container) {
            // 创建临时容器
            container = document.createElement('div');
            container.id = containerId;
            container.style.display = 'none';
            document.body.appendChild(container);
        }

        // 清空容器
        container.innerHTML = '';

        // 从配置树重建 UI
        const configArray = side === 'buy' ? division.buyConfigTree : division.sellConfigTree;


        // 重建因子卡片 DOM
        if (configArray && Array.isArray(configArray) && configArray.length > 0) {
            const firstItem = configArray[0];
            
            // 如果是新格式（包含 factor_group_name）
            if (firstItem.factor_group_name) {
                configArray.forEach(factorData => {
                    const cardId = `card-${Date.now()}-${Math.random()}`;
                    const card = document.createElement('div');
                    card.className = 'factor-card';
                    card.id = cardId;
                    
                    card.innerHTML = `
                        <div class="card-header">
                            <span class="card-title">${factorData.factor_group_name}</span>
                            <div class="card-weight-group">
                                <label>权重:</label>
                                <input type="number" class="card-weight-input" value="${factorData.weight || 10}" step="0.1">
                            </div>
                            <button class="btn-remove-card" data-action="remove-card" type="button">✕</button>
                        </div>
                        <div class="conditions-list"></div>
                        <div class="card-footer">
                            <button class="btn-add-cond" data-action="add-condition" data-side="${side}" data-card-id="${cardId}" type="button">
                                <i class="fas fa-plus"></i> 添加条件
                            </button>
                        </div>
                    `;
                    
                    container.appendChild(card);
                    
                    // 渲染条件
                    const conditionsList = card.querySelector('.conditions-list');
                    if (factorData.logic_tree && factorData.logic_tree.length > 0) {
                        ConditionManager.buildUIFromTree(factorData.logic_tree, conditionsList, cardId);
                    }
                    
                    const removeBtn = card.querySelector('.btn-remove-card');
                    if (removeBtn) {
                        removeBtn.addEventListener('click', () => {
                            card.remove();
                            console.log('因子卡片已删除', 'info');
                        });
                    }

                    // 绑定事件...
                });
            }
        }
        this.modal = FactorEditor.openEditor(side, containerId, this, divisionId, configArray);
    },
    /**
     * 保存从编辑器返回的配置
     */
    saveDivisionConfigFromEditor(divisionId, side, threshold = 0) {
        const division = this.getDivision(divisionId);
        if (!division) return;

        // 获取容器中的数据
        const containerId = `division-${divisionId}-${side}-container`;
        const container = document.getElementById(containerId);
        
        if (!container) return;

        // 获取所有因子卡片数据
        const cards = container.querySelectorAll('.factor-card');
        const configArray = [];
        
        cards.forEach(card => {
            const titleElement = card.querySelector('.card-title');
            const weightInput = card.querySelector('.card-weight-input');
            const conditionsList = card.querySelector('.conditions-list');
            
            if (!titleElement || !weightInput || !conditionsList) return;

            const weight = parseFloat(weightInput.value) || 0;
            const logic_tree = ConditionManager.collectConditionsTree(conditionsList);
            
            configArray.push({
                factor_group_name: titleElement.textContent || 'Unknown',
                weight: weight,
                logic_tree: logic_tree
            });
        });
        
        // 保存配置
        if (side === 'buy') {
            division.buyConfigTree = configArray;
            division.thresholdBuy = threshold
        } else {
            division.sellConfigTree = configArray;
            division.thresholdSell = threshold
        }
        console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!已经保存了编辑器的数据")
        console.log(division.buyConfigTree)
        this.saveDivisionsToStorage();
    },
    // ============ UI 渲染与事件绑定 ============

    /**
     * 渲染分仓列表
     */
    renderDivisionsList() {
        const container = document.getElementById('holdings-divisions-container');
        if (!container) {
            console.error('分仓容器不存在');
            return;
        }

        container.innerHTML = '';

        divisionsData.forEach(division => {
            const divisionItem = this.createDivisionCard(division);
            container.appendChild(divisionItem);
        });

        // 更新选择器
        this.updateDivisionSelector();
    },

    /**
     * 创建分仓卡片 DOM
     */
    createDivisionCard(division) {
        const card = document.createElement('div');
        card.className = 'holdings-division-item';
        card.dataset.divisionId = division.id;

        card.innerHTML = `
            <div class="division-header">
                <input type="text" class="division-name-input" value="${division.name}">
                <button class="btn-division-delete" type="button" title="删除分仓">✕</button>
            </div>
            
            <div class="division-body">
                <!-- 仓位占比 -->
                <div class="form-item">
                    <label>仓位占比</label>
                    <input type="number" class="division-weight-input" value="${division.weight}" 
                        min="0" max="1" step="0.01" id="division-weight-${division.id}">
                </div>
                
                <!-- 最短持仓时间 -->
                <div class="form-item">
                    <label>最短持仓天数（0=无限制）</label>
                    <input type="number" class="division-hold-time-min" value="${division.holdingTimeMin}" 
                        min="0" id="division-hold-time-min-${division.id}">
                </div>
                
                <!-- 最长持仓时间 -->
                <div class="form-item">
                    <label>最长持仓天数（0=无限制）</label>
                    <input type="number" class="division-hold-time-max" value="${division.holdingTimeMax}" 
                        min="0" id="division-hold-time-max-${division.id}">
                </div>
                
                <!-- 止损位 -->
                <div class="form-item">
                    <label>止损位 (%) (0=不启用)</label>
                    <input type="number" class="division-stop-loss" value="${division.stopLossPercent}" 
                        step="0.1" id="division-stop-loss-${division.id}">
                </div>
                
                <!-- 止盈位 -->
                <div class="form-item">
                    <label>止盈位 (%) (0=不启用)</label>
                    <input type="number" class="division-take-profit" value="${division.takeProfitPercent}" 
                        step="0.1" id="division-take-profit-${division.id}">
                </div>
                
                <!-- 买入配置 -->
                <div class="form-item division-config-group">
                    <div class="config-label">📥 买入配置</div>
                    <div class="config-buttons">
                        <button class="btn btn-sm btn-outline btn-load-buy-config" type="button" data-division-id="${division.id}">
                            📥 加载
                        </button>
                        <button class="btn btn-sm btn-outline btn-edit-buy-config" type="button" data-division-id="${division.id}">
                            ✏️ 编辑
                        </button>
                        <button class="btn btn-sm btn-outline btn-export-buy-config" type="button" data-division-id="${division.id}">
                            💾 导出
                        </button>
                    </div>
                </div>
                
                <!-- 卖出配置 -->
                <div class="form-item division-config-group">
                    <div class="config-label">📤 卖出配置</div>
                    <div class="config-buttons">
                        <button class="btn btn-sm btn-outline btn-load-sell-config" type="button" data-division-id="${division.id}">
                            📥 加载
                        </button>
                        <button class="btn btn-sm btn-outline btn-edit-sell-config" type="button" data-division-id="${division.id}">
                            ✏️ 编辑
                        </button>
                        <button class="btn btn-sm btn-outline btn-export-sell-config" type="button" data-division-id="${division.id}">
                            💾 导出
                        </button>
                    </div>
                </div>
            </div>
        `;

        return card;
    },

    /**
     * 绑定分仓卡片事件
     */
    bindDivisionEvents() {
        const container = document.getElementById('holdings-divisions-container');
        if (!container) return;

        // 事件委托处理所有按钮点击
        container.addEventListener('click', (e) => {
            const divisionId = e.target.dataset.divisionId || 
                             e.target.closest('[data-division-id]')?.dataset.divisionId ||
                             e.target.closest('.holdings-division-item')?.dataset.divisionId;

            if (!divisionId) return;

            // 删除按钮
            if (e.target.classList.contains('btn-division-delete')) {
                e.preventDefault();
                if (confirm('确定要删除此分仓吗？')) {
                    this.removeDivision(divisionId);
                }
            }

            // 加载买入配置
            if (e.target.classList.contains('btn-load-buy-config')) {
                e.preventDefault();
                this.importDivisionConfig(divisionId, 'buy');
            }

            // 编辑买入条件
            if (e.target.classList.contains('btn-edit-buy-config')) {
                e.preventDefault();
                this.editDivisionConfig(divisionId, 'buy');
            }

            // 导出买入配置
            if (e.target.classList.contains('btn-export-buy-config')) {
                e.preventDefault();
                this.exportDivisionConfig(divisionId, 'buy');
            }

            // 加载卖出配置
            if (e.target.classList.contains('btn-load-sell-config')) {
                e.preventDefault();
                this.importDivisionConfig(divisionId, 'sell');
            }

            // 编辑卖出条件
            if (e.target.classList.contains('btn-edit-sell-config')) {
                e.preventDefault();
                this.editDivisionConfig(divisionId, 'sell');
            }

            // 导出卖出配置
            if (e.target.classList.contains('btn-export-sell-config')) {
                e.preventDefault();
                this.exportDivisionConfig(divisionId, 'sell');
            }
        });

        // 分仓名称更新
        container.addEventListener('change', (e) => {
            if (e.target.classList.contains('division-name-input')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                this.updateDivisionName(divisionId, e.target.value);
            }

            // 参数更新
            if (e.target.classList.contains('division-weight-input')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                let val = parseFloat(e.target.value);
                if (isNaN(val) || val < 0) { val = 0; e.target.value = 0; App.log('仓位占比不能为负数，已重置为 0', 'error'); }
                if (val > 1) { val = 1; e.target.value = 1; App.log('仓位占比不能超过 1，已重置为 1', 'error'); }
                this.updateDivisionSettings(divisionId, { weight: val });
            }
 
            if (e.target.classList.contains('division-hold-time-min')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                let val = Math.round(parseFloat(e.target.value));
                if (isNaN(val) || val < 0) { val = 0; App.log('最短持仓天数不能为负数，已重置为 0', 'error'); }
                e.target.value = val;
                this.updateDivisionSettings(divisionId, { holdingTimeMin: val });
            }
 
            if (e.target.classList.contains('division-hold-time-max')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                let val = Math.round(parseFloat(e.target.value));
                if (isNaN(val) || val < 0) { val = 0; App.log('最长持仓天数不能为负数，已重置为 0', 'error'); }
                e.target.value = val;
                this.updateDivisionSettings(divisionId, { holdingTimeMax: val });
            }
 
            if (e.target.classList.contains('division-stop-loss')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                let val = parseFloat(e.target.value);
                if (isNaN(val)) { val = 0; }
                if (val > 0) { val = -val; App.log('止损位必须为负数或 0，已自动转为负值', 'error'); }
                e.target.value = val;
                this.updateDivisionSettings(divisionId, { stopLossPercent: val });
            }
 
            if (e.target.classList.contains('division-take-profit')) {
                const divisionId = e.target.closest('.holdings-division-item').dataset.divisionId;
                let val = parseFloat(e.target.value);
                if (isNaN(val) || val < 0) { val = 0; e.target.value = 0; App.log('止盈位不能为负数，已重置为 0', 'error'); }
                this.updateDivisionSettings(divisionId, { takeProfitPercent: val });
            }
        });
    },

    /**
     * 更新分仓选择器
     */
    updateDivisionSelector() {
        const selector = document.getElementById('holdings-division-selector');
        if (!selector) return;

        selector.innerHTML = '';
        divisionsData.forEach(division => {
            const option = document.createElement('option');
            option.value = division.id;
            option.textContent = division.name;
            selector.appendChild(option);
        });

        if (divisionsData.length > 0 && !selectedDivisionId) {
            selectedDivisionId = divisionsData[0].id;
        }

        if (selectedDivisionId) {
            selector.value = selectedDivisionId;
        }
    },

    /**
     * 绑定分仓选择器事件
     */
    bindDivisionSelector() {
        const selector = document.getElementById('holdings-division-selector');
        if (!selector) return;

        selector.addEventListener('change', (e) => {
            selectedDivisionId = e.target.value;
            this.loadDivisionDetailView(selectedDivisionId);
        });
    },

    /**
     * 加载分仓详情视图
     */
    loadDivisionDetailView(divisionId) {
        const division = this.getDivision(divisionId);
        if (!division) return;

        // 加载分仓配置到设置面板
        const settingsPanel = document.getElementById('holdings-division-settings');
        if (settingsPanel) {
            settingsPanel.innerHTML = `
                <div class="division-detail-header">
                    <h3>${division.name} 的详细配置</h3>
                </div>
                <div class="division-detail-info">
                    <p>仓位占比: ${(division.weight * 100).toFixed(1)}%</p>
                    <p>最短持仓: ${division.holdingTimeMin} 天</p>
                    <p>最长持仓: ${division.holdingTimeMax} 天</p>
                    <p>止损位: ${division.stopLossPercent}%</p>
                    <p>止盈位: ${division.takeProfitPercent}%</p>
                </div>
            `;
        }

        // 更新选择器
        const selector = document.getElementById('holdings-division-selector');
        if (selector) {
            selector.value = divisionId;
        }

        App.log(`已加载分仓 "${division.name}" 的详情`, 'info');
    },

    // ============ 导入导出全部配置 ============

    /**
     * 导出整个持仓回测配置
     */
    exportAllHoldingsConfig() {
        const config = {
            divisions: divisionsData.map(div => ({
                ...div,
            })),
            initialFund: UIManagerUtils.getHoldingsInitialFund(),
            timestamp: new Date().toISOString(),
            version: "1.0",
            description: "完整的持仓回测配置，包含所有分仓参数和条件"
        };

        const jsonString = JSON.stringify(config, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `holdings_backtest_config_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        App.log('持仓配置已导出', 'success');
    },

    /**
     * 导入整个持仓回测配置
     */
    importAllHoldingsConfig() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const data = JSON.parse(event.target.result);

                    // 验证格式
                    if (!data.divisions || !Array.isArray(data.divisions)) {
                        throw new Error('配置文件格式无效');
                    }

                    // 导入分仓数据
                    divisionsData = data.divisions;
                    this.saveDivisionsToStorage();
                    this.renderDivisionsList();

                    // 导入初始本金
                    if (data.initialFund) {
                        UIManagerUtils.setHoldingsInitialFund(data.initialFund);
                    }

                    App.log(`持仓配置已导入（${divisionsData.length} 个分仓）`, 'success');
                } catch (error) {
                    console.error('导入配置失败：', error);
                    App.log(`导入失败：${error.message}`, 'error');
                }
            };
            reader.readAsText(file);
        });
        input.click();
    },

    getAllHoldingsConfigJson() {
        const config = {
            divisions: divisionsData.map(div => ({
                ...div,
            })),
            initialFund: UIManagerUtils.getHoldingsInitialFund(),
            timestamp: new Date().toISOString(),
            version: "1.0",
            description: "完整的持仓回测配置，包含所有分仓参数和条件"
        };
        const jsonString = JSON.stringify(config, null, 2);
        return jsonString
    },


    /**
     * 获取整个持仓配置（用于后端回测）
     */
    getAllHoldingsConfig() {
        const config = {
            divisions: divisionsData.map(div => ({
                ...div,
            })),
            initialFund: UIManagerUtils.getHoldingsInitialFund(),
            timestamp: new Date().toISOString(),
            version: "1.0",
            description: "完整的持仓回测配置，包含所有分仓参数和条件"
        };
        return config
    }
};
