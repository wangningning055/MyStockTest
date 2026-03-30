/**
 * factorEditor.js - 因子编辑器（复用选股页签的因子卡片逻辑）
 * 
 * 职责：
 * - 完全复用 FactorManager 的因子卡片逻辑
 * - 提供专门的编辑界面（模态框）
 * - 支持添加/编辑/删除因子卡片
 * - 支持设置权重和阈值
 * - 支持导入/导出配置
 * - 保存条件树回原容器
 */

import { App } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { FactorManager } from './factorManager.js';
import { ConditionManager } from './conditionManager.js';
import { ConfigManager } from './configManager.js';

let currentEditingContainerId = null;
let currentEditingSide = null;

export const FactorEditor = {
    /**
     * 打开因子编辑器
     * @param {string} side - 'buy' 或 'sell'
     * @param {string} containerId - 原容器的ID
     * @param {Array} configTree - 要编辑的配置树
     */
    async openEditor(side, containerId, holdings, divisionId, configTree = []) {
        currentEditingSide = side;
        currentEditingContainerId = containerId;
        
        // 显示编辑器
        const modal = this.createEditorModal(side);
        document.body.appendChild(modal);
        modal.classList.add('active');
        
        // 确保因子数据已加载
        if (!FactorManager.getAllFactors().length) {
            await FactorManager.loadFactorsData();
        }
        
        // 加载现有配置
        if (configTree.length > 0) {
            this.loadConfigTree(configTree, side);
        }
        if(side == "buy")
        {
            this.threshold = holdings.getDivision(divisionId).thresholdBuy
        }
        else
        {
            this.threshold = holdings.getDivision(divisionId).thresholdSell
        }

        const value = Number(this.threshold)
        const elem = document.getElementById('editor-weight-threshold-slider');
        const display = document.getElementById('editor-threshold-display');
        if (elem) {
            elem.value = Math.max(-1, Math.min(1, value));
            if (display) display.textContent = elem.value;
        }

        this.holdings = holdings
        this.divisionId = divisionId
        this.side = side
        // 绑定编辑器事件
        this.bindEditorEvents(modal);
        return modal
    },

    /**
     * 创建编辑器模态框DOM
     */
    createEditorModal(side) {
        const modal = document.createElement('div');
        modal.className = 'factor-editor-modal';
        modal.id = 'factor-editor-modal';
        
        modal.innerHTML = `
            <div class="factor-editor-overlay"></div>
            <div class="factor-editor-container">
                <!-- 头部 -->
                <div class="editor-header">
                    <h2>编辑${side === 'buy' ? '买入' : '卖出'}因子</h2>
                    <button class="editor-close-btn" type="button">✕</button>
                </div>
                
                <!-- 主体 -->
                <div class="editor-body">
                    <!-- 左侧：因子列表 -->
                    <aside class="editor-sidebar">
                        <div class="panel-header">
                            <span>📊 因子列表</span>
                        </div>
                        
                        <div class="config-list" id="editor-factor-container"></div>
                        
                        <div class="panel-footer">
                            <button class="btn btn-primary" id="editor-btn-add-factor" type="button">
                                <i class="fas fa-plus"></i> 添加因子组合
                            </button>
                        </div>
                    </aside>
                    
                    <!-- 右侧：设置面板 -->
                    <main class="editor-main">
                        <div class="settings-panel">
                            <div class="section-title">⚙️ 编辑设置</div>
                            
                            <!-- 权重阈值 -->
                            <div class="threshold-section">
                                <div class="section-title">📊 权重阈值设置</div>
                                <div class="threshold-slider-group">
                                    <div class="threshold-label-row">
                                        <span class="threshold-label">权重值</span>
                                        <span class="threshold-value-display" id="editor-threshold-display">0.3</span>
                                    </div>
                                    <input type="range" id="editor-weight-threshold-slider" 
                                        class="threshold-slider" 
                                        min="-1" max="1" step="0.01" value="0.3">
                                    <div class="threshold-info">
                                        <small>拖动滑条设置权重阈值范围（-1-1）</small>
                                    </div>
                                </div>
                            </div>

                        </div>
                    </main>
                </div>
                
                <!-- 底部 -->
                <div class="editor-footer">
                    <button class="btn btn-secondary" id="editor-btn-cancel" type="button">取消</button>
                    <button class="btn btn-success" id="editor-btn-save" type="button">保存</button>
                </div>
            </div>
        `;
        
        return modal;
    },

    /**
     * 加载配置树到编辑器
     */
    loadConfigTree(configTree, side) {
        const container = document.getElementById('editor-factor-container');
        if (!container) return;
        
        // 清空容器
        container.innerHTML = '';
        
        // 从配置树重建因子卡片
        configTree.forEach(factorGroup => {
            this.renderFactorCardInEditor(
                factorGroup.factor_group_name,
                factorGroup.weight,
                factorGroup.logic_tree,
                side,
                container
            );
        });
        
        App.log('配置已加载', 'success');
    },

    /**
     * 在编辑器中渲染因子卡片
     */
    renderFactorCardInEditor(name, weight, logicTree, side, container) {
        const cardId = `editor-card-${Date.now()}-${Math.random()}`;
        const card = document.createElement('div');
        card.className = 'factor-card';
        card.id = cardId;
        
        card.innerHTML = `
            <div class="card-header">
                <span class="card-title">${name}</span>
                <div class="card-weight-group">
                    <label>权重:</label>
                    <input type="number" class="card-weight-input" value="${weight || 10}" step="0.1">
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
        
        // 如果有逻辑树，渲染条件
        const conditionsList = card.querySelector('.conditions-list');
        if (logicTree && logicTree.length > 0) {
            ConditionManager.buildUIFromTree(logicTree, conditionsList, cardId);
        }
        
        // 绑定卡片事件
        this.bindFactorCardEvents(card, side);
    },

    /**
     * 绑定因子卡片事件
     */
    bindFactorCardEvents(card, side) {
        const removeBtn = card.querySelector('.btn-remove-card');
        const addCondBtn = card.querySelector('.btn-add-cond');
        
        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                card.remove();
                App.log('因子卡片已删除', 'info');
            });
        }
        
        if (addCondBtn) {
            addCondBtn.addEventListener('click', () => {
                const cardId = card.id;
                FactorManager.showFactorModal(side, cardId);
            });
        }
    },

    /**
     * 绑定编辑器全局事件
     */
    bindEditorEvents(modal) {
        // 关闭按钮
        const closeBtn = modal.querySelector('.editor-close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.saveAndClose(modal));
        }
        
        // 取消按钮
        const cancelBtn = modal.querySelector('#editor-btn-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.saveAndClose(modal));
        }
        
        // 保存按钮
        const saveBtn = modal.querySelector('#editor-btn-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveAndClose(modal));
        }
        
        // 添加因子按钮
        const addFactorBtn = modal.querySelector('#editor-btn-add-factor');
        if (addFactorBtn) {
            addFactorBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // 打开因子选择列表，不直接添加卡片
                const editorContainerId = modal.querySelector('#editor-factor-container').id;
                FactorManager.showFactorModal(this.side, null, editorContainerId, true);
            });
        }
        

        
        // 权重阈值滑块
        const slider = modal.querySelector('#editor-weight-threshold-slider');
        if (slider) {
            slider.addEventListener('input', (e) => {
                const display = modal.querySelector('#editor-threshold-display');
                if (display) {
                    display.textContent = parseFloat(e.target.value).toFixed(2);
                }
            });
        }
        
        // 点击背景关闭
        const overlay = modal.querySelector('.factor-editor-overlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.saveAndClose(modal));
        }
    },

    /**
     * 保存配置并关闭编辑器
     */
    saveAndClose(modal) {
        if (!currentEditingContainerId) {
            App.log('错误：没有指定编辑容器', 'error');
            console.log('错误：没有指定编辑容器', 'error');
            return;
        }
        
        const editorContainer = modal.querySelector('#editor-factor-container');
        const targetContainer = document.getElementById(currentEditingContainerId);
        
        if (!editorContainer || !targetContainer) {
            App.log('错误：容器不存在', 'error');
            console.log('错误：容器不存在', 'error');
            return;
        }
        
        // 获取编辑器中的因子数据
        //const factorData = this.getFactorData(modal);
        
        //if (factorData.length === 0) {
        //    App.log('未添加任何因子', 'warning');
        //    console.log('未添加任何因子', 'warning');
            
        //    this.closeEditor(modal);
        //    return;
        //}
        

        
        // 复制编辑器中的因子卡片到目标容器
        const cards = editorContainer.querySelectorAll('.factor-card');

        
        cards.forEach(card => {
            const clone = card.cloneNode(true);
            targetContainer.appendChild(clone);
            
            // 重新绑定克隆卡片的事件
            const removeBtn = clone.querySelector('.btn-remove-card');
            const addCondBtn = clone.querySelector('.btn-add-cond');
            
            if (removeBtn) {
                removeBtn.addEventListener('click', () => {
                    clone.remove();
                    App.log('因子卡片已删除', 'info');
                });
            }
            
            if (addCondBtn) {
                addCondBtn.addEventListener('click', () => {
                    FactorManager.showFactorModal(currentEditingSide, clone.id);
                });
            }
        });
        App.log(`${currentEditingSide === 'buy' ? '买入' : '卖出'}因子已保存`, 'success');


        const display = document.getElementById('editor-threshold-display');
        const threshold = display.textContent

        this.holdings.saveDivisionConfigFromEditor(this.divisionId, this.side, threshold, cards)
        currentEditingContainerId = null;
        currentEditingSide = null;
        // 清空目标容器
        targetContainer.innerHTML = '';

        if (modal) {
            modal.classList.remove('active');
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    },

    /**
     * 关闭编辑器
     */
    //closeEditor(modal) {
    //    if (modal) {
    //        modal.classList.remove('active');
    //        setTimeout(() => {
    //            modal.remove();
    //        }, 300);
    //    }

    //    const display = document.getElementById('editor-threshold-display');
    //    const threshold = display.textContent

    //    //this.holdings.saveDivisionConfigFromEditor(this.divisionId, this.side, threshold)
    //    currentEditingContainerId = null;
    //    currentEditingSide = null;
    //},

    /**
     * 获取编辑器中的因子数据
     */
    getFactorData() {
        const modal = document.getElementById('factor-editor-modal');
        if (!modal) return [];
        
        const container = modal.querySelector('#editor-factor-container');
        if (!container) return [];
        
        // 使用 ConfigManager 的逻辑获取数据
        const cards = container.querySelectorAll('.factor-card');
        const data = [];
        
        cards.forEach(card => {
            try {
                const titleElement = card.querySelector('.card-title');
                const weightInput = card.querySelector('.card-weight-input');
                const conditionsList = card.querySelector('.conditions-list');
                
                if (!titleElement || !weightInput || !conditionsList) return;

                const weight = parseFloat(weightInput.value) || 0;
                const logic_tree = ConditionManager.collectConditionsTree(conditionsList);
                
                const factorData = {
                    factor_group_name: titleElement.textContent || 'Unknown',
                    weight: weight,
                    logic_tree: logic_tree
                };
                
                data.push(factorData);
            } catch (error) {
                console.error('收集因子数据时出错：', error);
            }
        });
        
        return data;
    }
};

export default FactorEditor;
