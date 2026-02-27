/**
 * conditionManager.js - 条件分组管理模块（完全重新设计版）
 * 
 * 新功能：
 * 1. 支持在同一分组内添加多个不同的条件
 * 2. 删除分组时级联删除其内的所有条件
 * 3. "包裹"按钮改为"分组"按钮，创建新分组并将当前条件加入
 * 4. 分组内可以继续添加新条件
 */

import { App } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { FactorManager } from './factorManager.js';

let manager = null;

export function setConditionManager(_manager) {
    manager = _manager;
}

export const ConditionManager = {
    /**
     * 为条件行绑定事件（删除、分组、添加条件）
     */
    bindConditionRowEvents(row, parentList, cardId) {
        const isFirst = this.isFirstCondition(row, parentList);
        
        // 删除条件按钮
        if (!isFirst) {
            const delBtn = row.querySelector('.btn-del-cond');
            if (delBtn) {
                delBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    row.remove();
                    App.log('条件行已删除', 'info');
                });
            }
        }
        
        // 分组按钮 - 将此条件及后续条件包裹到一个新分组中
        const groupBtn = row.querySelector('.btn-group-cond');
        if (groupBtn) {
            groupBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.wrapConditionInGroup(row, parentList);
            });
        }
        
        // 在分组内添加条件按钮
        const addBtn = row.querySelector('.btn-add-to-group');
        if (addBtn) {
            addBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const groupContainer = this.getContainingGroup(row);
                if (groupContainer) {
                    App.showFactorModal('buy', null, groupContainer);
                } else {
                    App.showFactorModal('buy', cardId);
                }
            });
        }
    },

    /**
     * 判断是否是列表中的第一个条件
     */
    isFirstCondition(row, list) {
        const allRows = Array.from(list.querySelectorAll(':scope > .condition-row'));
        return allRows[0] === row;
    },

    /**
     * 获取条件所在的分组（如果有的话）
     */
    getContainingGroup(row) {
        let parent = row.parentElement;
        while (parent) {
            if (parent.classList.contains('condition-group')) {
                return parent;
            }
            parent = parent.parentElement;
        }
        return null;
    },

    /**
     * 创建一个新的分组容器
     */
    createConditionGroup(relation = "AND") {
        const group = document.createElement('div');
        group.className = 'condition-group';
        group.dataset.type = 'group';
        group.dataset.relation = relation;
        
        group.innerHTML = `
            <div class="group-header">
                <span class="group-tag">${relation === "AND" ? "【且】" : "【或】"}</span>
                <button class="btn-change-group-rel" title="改变分组逻辑" type="button">
                    ${relation}
                </button>
                <button class="btn-add-to-group" title="在分组内添加条件" type="button">
                    <i class="fas fa-plus"></i> 添加条件
                </button>
                <button class="btn-del-group" title="删除整个分组及内部条件" type="button">✕</button>
            </div>
            <div class="group-content">
                <div class="conditions-list"></div>
            </div>
        `;
        
        // 改变分组逻辑按钮
        const changeRelBtn = group.querySelector('.btn-change-group-rel');
        if (changeRelBtn) {
            changeRelBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const currentRel = group.dataset.relation;
                const newRel = currentRel === "AND" ? "OR" : "AND";
                group.dataset.relation = newRel;
                changeRelBtn.textContent = newRel;
                group.querySelector('.group-tag').textContent = 
                    newRel === "AND" ? "【且】" : "【或】";
                App.log(`分组逻辑已改为：${newRel}`, 'info');
            });
        }
        
        // 在分组内添加条件按钮
        const addInGroupBtn = group.querySelector('.btn-add-to-group');
        if (addInGroupBtn) {
            addInGroupBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                // 打开因子选择器，在该分组内添加条件
                const childList = group.querySelector('.conditions-list');
                // 这里需要一个方式告诉 FactorManager 在哪里添加条件
                // 我们通过临时存储来实现
                window.__targetGroupForNewCondition = group;
                App.showFactorModal('buy');
            });
        }
        
        // 删除分组按钮 - 级联删除所有条件
        const delGroupBtn = group.querySelector('.btn-del-group');
        if (delGroupBtn) {
            delGroupBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                
                // 获取所在的卡片
                const card = group.closest('.factor-card');
                
                // 删除分组
                group.remove();
                
                // 检查卡片中是否还有条件或分组
                const conditionsList = card ? card.querySelector('.conditions-list') : null;
                if (conditionsList) {
                    const hasContent = conditionsList.querySelector('.condition-row, .condition-group');
                    
                    // 如果卡片内已无条件或分组，删除整个卡片
                    if (!hasContent && card) {
                        card.remove();
                        App.log('分组已删除，因子卡片也已删除', 'info');
                        return;
                    }
                }
                
                App.log('分组及其内部条件已删除', 'info');
            });
        }
        return group;
    },

    /**
     * 将一个条件包裹到新分组中
     */
    wrapConditionInGroup(conditionRow, parentList) {
        // 创建新分组
        const group = this.createConditionGroup("AND");
        const newChildList = group.querySelector('.conditions-list');
        
        // 将原条件移动到新分组
        const clonedRow = conditionRow.cloneNode(true);
        
        // 重置逻辑关系为首选（因为是分组内第一个）
        const logicDiv = clonedRow.querySelector('.cond-logic');
        if (logicDiv) {
            logicDiv.innerHTML = '<span class="first-tag">首选</span>';
        }
        
        // 移除删除按钮（因为是分组内第一个条件）
        const delBtn = clonedRow.querySelector('.btn-del-cond');
        if (delBtn) {
            delBtn.remove();
        }
        
        newChildList.appendChild(clonedRow);
        this.bindConditionRowEvents(clonedRow, newChildList);
        
        // 将新分组替换原条件位置
        conditionRow.replaceWith(group);
        
        App.log('条件已包裹在新分组中', 'success');
    },

    /**
     * 递归收集条件数据，生成树形结构
     */
    collectConditionsTree(containerElement) {
        const children = Array.from(containerElement.querySelectorAll(':scope > .condition-row, :scope > .condition-group'));
        const tree = [];
        
        children.forEach((element, index) => {
            if (element.dataset.type === 'condition') {
                // 收集单个条件
                const dateRange = UIManagerUtils.getConditionDateRange(element);
                const condName = element.querySelector('.cond-name');
                
                const factorId = element.dataset.factorId;  // ✅ 获取ID
                if (!condName) {
                    console.warn('警告：找不到条件名称');
                    return;
                }
                const node = {
                    type: 'condition',
                    relation: index === 0 ? "START" : (element.querySelector('.cond-rel')?.value || "AND"),
                    factor_id: factorId ? parseInt(factorId) : null,
                    factor_name: condName.textContent || 'Unknown',
                    operator: UIManagerUtils.getConditionOperator(element),
                    value: UIManagerUtils.getConditionValue(element),
                    dateFrom: dateRange?.fromDays || 30,
                    dateTo: dateRange?.toDays || 0
                };
                tree.push(node);
            } 
            else if (element.dataset.type === 'group') {
                // 递归收集分组内容
                const childList = element.querySelector('.conditions-list');
                if (!childList) {
                    console.warn('警告：找不到分组的条件列表');
                    return;
                }
                
                const childTree = this.collectConditionsTree(childList);
                const groupNode = {
                    type: 'group',
                    relation: index === 0 ? "START" : (element.dataset.relation || "AND"),
                    children: childTree
                };
                tree.push(groupNode);
            }
        });
        
        return tree;
    },

    /**
     * 从树形结构重建 UI
     */
    buildUIFromTree(treeNodes, containerElement, cardId = null) {
        treeNodes.forEach((node, index) => {
            if (node.type === 'condition') {
                // 构建条件行
                const row = document.createElement('div');
                row.className = 'condition-row';
                row.dataset.type = 'condition';
                row.dataset.factorId = node.factor_id;

                const isFirst = index === 0;
                const headerHtml = isFirst ? '<span class="first-tag">首选</span>' : `
                    <select class="cond-rel">
                        <option value="AND" ${node.relation === 'AND' ? 'selected' : ''}>且</option>
                        <option value="OR" ${node.relation === 'OR' ? 'selected' : ''}>或</option>
                    </select>
                `;
                
                row.innerHTML = `
                    <div class="condition-row__header">
                        <div class="cond-logic">${headerHtml}</div>
                        <div class="cond-name" title="${node.factor_name}">${node.factor_name}</div>
                        <div class="condition-controls">
                            <button class="btn-group-cond" title="将此条件包裹在新分组中" type="button">
                                📦
                            </button>
  
                            ${isFirst ? '' : '<button class="btn-del-cond" type="button">✕</button>'}
                        </div>
                    </div>
                    <div class="condition-row__date">
                        <span class="condition-row__date-label">日期范围:</span>
                        <input type="number" class="date-range-input" value="${node.dateFrom || 30}" placeholder="天前">
                        <span class="date-range-separator">～</span>
                        <input type="number" class="date-range-input" value="${node.dateTo || 0}" placeholder="天前">
                    </div>
                    <div class="condition-row__condition">
                        <select class="cond-op">
                            <option value="gt" ${node.operator === 'gt' ? 'selected' : ''}>></option>
                            <option value="lt" ${node.operator === 'lt' ? 'selected' : ''}><</option>
                            <option value="eq" ${node.operator === 'eq' ? 'selected' : ''}>=</option>
                            <option value="ge" ${node.operator === 'ge' ? 'selected' : ''}>≥</option>
                            <option value="le" ${node.operator === 'le' ? 'selected' : ''}>≤</option>
                        </select>
                        <input type="number" class="cond-val" value="${node.value}" placeholder="条件值">
                    </div>
                `;
                
                containerElement.appendChild(row);
                this.bindConditionRowEvents(row, containerElement, cardId);
            } 
            else if (node.type === 'group') {
                // 构建分组
                const groupElement = this.createConditionGroup(
                    index === 0 ? "AND" : node.relation
                );
                containerElement.appendChild(groupElement);
                
                // 递归构建子项
                const childList = groupElement.querySelector('.conditions-list');
                this.buildUIFromTree(node.children, childList, cardId);
            }
        });
    }
};


