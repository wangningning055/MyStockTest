/**
 * factorManager.js - 因子管理模块（改进版，支持分组内添加条件）
 */

import { CONFIG, App } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { ConditionManager } from './conditionManager.js';

let FACTORS_DATA = null;
let manager = null;

export function setFactorManager(_manager) {
    manager = _manager;
}

export const FactorManager = {
    /**
     * 加载因子数据
     */
    async loadFactorsData() {
        if (FACTORS_DATA) return FACTORS_DATA;
        try {
            const response = await fetch(CONFIG.factorsUrl);
            FACTORS_DATA = await response.json();
            console.log("✅ 因子数据加载成功");
            return FACTORS_DATA;
        } catch (error) {
            console.error("❌ 因子数据加载失败:", error);
            return null;
        }
    },

    /**
     * 获取所有因子（返回平铺列表）
     */
    getAllFactors() {
        if (!FACTORS_DATA) return [];
        const allFactors = [];
        Object.values(FACTORS_DATA.factors).forEach(category => {
            category.items.forEach(item => {
                allFactors.push({
                    ...item,
                    category: category.name,
                    categoryIcon: category.icon
                });
            });
        });
        return allFactors;
    },

    /**
     * 渲染因子卡片
     */
    renderFactorCard(type, containerId, side) {
        const container = document.getElementById(containerId);
        const cardId = `card-${Date.now()}`;
        const card = document.createElement('div');
        card.className = 'factor-card';
        card.id = cardId;
        card.innerHTML = `
            <div class="card-header">
                <span class="card-title">${type}</span>
                <div class="card-weight-group">
                    <label>权重:</label>
                    <input type="number" class="card-weight-input" value="10" min="0">
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
        
        const removeBtn = card.querySelector('.btn-remove-card');
        const addCondBtn = card.querySelector('.btn-add-cond');
        
        removeBtn.addEventListener('click', () => {
            card.remove();
            App.log('因子卡片已删除', 'info');
        });
        
        addCondBtn.addEventListener('click', () => {
            App.showFactorModal(side, cardId);
        });
        
        this.addConditionToCard(cardId, type, true);
    },

    /**
     * 为卡片添加条件行
     */
    addConditionToCard(cardId, factorName, isFirst = false) {
        const card = document.getElementById(cardId);
        if (!card) {
            App.log(`错误：找不到卡片 ID: ${cardId}`, "error");
            return;
        }
        const list = card.querySelector('.conditions-list');
        if (!list) {
            App.log(`错误：卡片结构异常，找不到条件列表`, "error");
            return;
        }
        
        const row = document.createElement('div');
        row.className = 'condition-row';
        row.dataset.type = 'condition';
        
        const headerHtml = isFirst ? '<span class="first-tag">首选</span>' : `
            <select class="cond-rel">
                <option value="AND">且</option>
                <option value="OR">或</option>
            </select>
        `;
        
        row.innerHTML = `
            <div class="condition-row__header">
                <div class="cond-logic">${headerHtml}</div>
                <div class="cond-name" title="${factorName}">${factorName}</div>
                <div class="condition-controls">
                    <button class="btn-group-cond" title="将此条件包裹在新分组中" type="button">
                        📦
                    </button>
                    ${isFirst ? '' : '<button class="btn-del-cond" type="button">✕</button>'}
                </div>
            </div>
            <div class="condition-row__date">
                <span class="condition-row__date-label">日期范围:</span>
                <input type="number" class="date-range-input" value="30" placeholder="天前">
                <span class="date-range-separator">～</span>
                <input type="number" class="date-range-input" value="0" placeholder="天前">
            </div>
            <div class="condition-row__condition">
                <select class="cond-op">
                    <option value="gt">></option>
                    <option value="lt"><</option>
                    <option value="eq">=</option>
                    <option value="ge">≥</option>
                    <option value="le">≤</option>
                </select>
                <input type="number" class="cond-val" value="0" placeholder="条件值">
            </div>
        `;
        
        list.appendChild(row);
        ConditionManager.bindConditionRowEvents(row, list, cardId);
    },

    /**
     * 在指定容器内添加条件（用于在分组内添加）
     */
    addConditionToContainer(factorName, container, cardId) {
        if (!container) {
            console.error('错误：容器不存在');
            return;
        }

        // 获取容器内已有的条件数量
        const existingConditions = Array.from(container.querySelectorAll(':scope > .condition-row'));
        const isFirst = existingConditions.length === 0;

        const row = document.createElement('div');
        row.className = 'condition-row';
        row.dataset.type = 'condition';
        
        const headerHtml = isFirst ? '<span class="first-tag">首选</span>' : `
            <select class="cond-rel">
                <option value="AND">且</option>
                <option value="OR">或</option>
            </select>
        `;
        
        row.innerHTML = `
            <div class="condition-row__header">
                <div class="cond-logic">${headerHtml}</div>
                <div class="cond-name" title="${factorName}">${factorName}</div>
                <div class="condition-controls">
                    <button class="btn-group-cond" title="将此条件包裹在新分组中" type="button">
                        📦
                    </button>
                    ${isFirst ? '' : '<button class="btn-del-cond" type="button">✕</button>'}
                </div>
            </div>
            <div class="condition-row__date">
                <span class="condition-row__date-label">日期范围:</span>
                <input type="number" class="date-range-input" value="30" placeholder="天前">
                <span class="date-range-separator">～</span>
                <input type="number" class="date-range-input" value="0" placeholder="天前">
            </div>
            <div class="condition-row__condition">
                <select class="cond-op">
                    <option value="gt">></option>
                    <option value="lt"><</option>
                    <option value="eq">=</option>
                    <option value="ge">≥</option>
                    <option value="le">≤</option>
                </select>
                <input type="number" class="cond-val" value="0" placeholder="条件值">
            </div>
        `;
        
        container.appendChild(row);
        ConditionManager.bindConditionRowEvents(row, container, cardId);
        
        App.log('条件已添加到分组', 'success');
    },

    /**
     * 显示因子选择模态框
     */
    async showFactorModal(side, targetCardId = null) {
        const modal = document.getElementById('factor-modal');
        const categoriesContainer = document.getElementById('factor-categories-container');

        if (!categoriesContainer) {
            console.error("❌ factor-categories-container 元素不存在！");
            return;
        }
    
        categoriesContainer.innerHTML = '';
        modal.classList.add('active');
        const self = this;
        
        (async () => {
            if (!FACTORS_DATA) {
                await this.loadFactorsData();
            }
            
            if (!FACTORS_DATA) {
                alert("因子数据加载失败，请检查 factors.json 文件");
                return;
            }

            Object.entries(FACTORS_DATA.factors).forEach(([categoryKey, category]) => {
                const categorySection = document.createElement('div');
                categorySection.className = 'factor-category-section';
                categorySection.dataset.category = categoryKey;
                
                if(side == "buy" && category.isSold == 1) {
                    return;
                }
                
                const categoryTitle = document.createElement('div');
                categoryTitle.className = 'factor-category-title';
                categoryTitle.innerHTML = `${category.icon} ${category.name}`;
                categorySection.appendChild(categoryTitle);
                
                const categoryDesc = document.createElement('div');
                categoryDesc.className = 'factor-category-desc';
                categoryDesc.textContent = category.description;
                categorySection.appendChild(categoryDesc);
                
                const itemsContainer = document.createElement('div');
                itemsContainer.className = 'factor-items-container';
                
                category.items.forEach(item => {
                    const btn = document.createElement('button');
                    btn.className = 'btn btn-factor-item';
                    btn.title = item.description;
                    btn.type = 'button';
                    btn.innerHTML = `<span class="factor-name">${item.name}</span>`;
                    
                    btn.onclick = () => {
                        // 检查是否在分组内添加条件
                        if (window.__targetGroupForNewCondition) {
                            const groupContainer = window.__targetGroupForNewCondition.querySelector('.conditions-list');
                            self.addConditionToContainer(item.name, groupContainer, targetCardId);
                            delete window.__targetGroupForNewCondition;
                        } else if (targetCardId) {
                            // 在卡片内添加条件
                            self.addConditionToCard(targetCardId, item.name);
                        } else {
                            // 创建新卡片
                            const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
                            self.renderFactorCard(item.name, containerId, side);
                        }
                        modal.classList.remove('active');
                    };
                    
                    itemsContainer.appendChild(btn);
                });
                
                categorySection.appendChild(itemsContainer);
                categoriesContainer.appendChild(categorySection);
            });
        })();
        
        const closeBtn = document.getElementById('btn-close-modal');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.remove('active');
                delete window.__targetGroupForNewCondition;
            };
        }
    },

    /**
     * 绑定因子相关事件
     */
    bindFactorEvents() {
        document.getElementById('btn-add-buy-factor').addEventListener('click', () => App.showFactorModal('buy'));
        document.getElementById('btn-add-sell-factor').addEventListener('click', () => App.showFactorModal('sell'));
        document.getElementById('api-export-buy-config').addEventListener('click', () => App.exportConfig('buy'));
        document.getElementById('api-export-sell-config').addEventListener('click', () => App.exportConfig('sell'));
        document.getElementById('api-import-buy-config').addEventListener('click', () => App.importConfig('buy'));
        document.getElementById('api-import-sell-config').addEventListener('click', () => App.importConfig('sell'));
        document.getElementById('api-load-buy-file').addEventListener('click', () => App.loadConfigFile('backtest-buy-source'));
        document.getElementById('api-load-sell-file').addEventListener('click', () => App.loadConfigFile('backtest-sell-source'));
    }
};