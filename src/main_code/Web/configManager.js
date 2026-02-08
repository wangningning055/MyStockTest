

/**
 * configManager.js - 配置导入导出模块（修复版）
 */

import { App, State } from './app.js';
import { UIManagerUtils } from './uiManager.js';
import { FactorManager } from './factorManager.js';
import { ConditionManager } from './conditionManager.js';

let manager = null;

export function setConfigManager(_manager) {
    manager = _manager;
}

export const ConfigManager = {
    /**
     * 获取因子数据（修复：完整的数据收集）
     */
    getFactorData(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`错误：找不到容器 ${containerId}`);
            return [];
        }

        const cards = container.querySelectorAll('.factor-card');
        const data = [];
        
        cards.forEach(card => {
            try {
                const titleElement = card.querySelector('.card-title');
                const weightInput = card.querySelector('.card-weight-input');
                const conditionsList = card.querySelector('.conditions-list');
                
                if (!titleElement || !weightInput || !conditionsList) {
                    console.warn('警告：卡片结构不完整，跳过');
                    return;
                }

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
    },

    /**
     * 导出配置（修复：增加错误处理）
     */
    exportConfig(side) {
        try {
            const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
            const data = this.getFactorData(containerId);
            
            if (!data || data.length === 0) {
                App.log('没有因子配置可导出', 'warning');
                return;
            }
            
            // 验证数据结构
            const jsonString = JSON.stringify(data, null, 2);
            
            // 测试是否能解析
            JSON.parse(jsonString);
            
            const blob = new Blob([jsonString], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${side}_strategy_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            App.log(`${side === 'buy' ? '买入' : '卖出'}策略已导出`, "success");
        } catch (error) {
            console.error('导出配置时出错：', error);
            App.log(`导出失败：${error.message}`, "error");
        }
    },

    /**
     * 导入配置（修复：确保事件正确绑定）
     */
    importConfig(side) {
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
                    
                    // 验证数据格式
                    if (!Array.isArray(data)) {
                        throw new Error('数据格式无效：应该是数组');
                    }
                    
                    this.applyConfigToContainer(data, side);
                    App.log(`${side === 'buy' ? '买入' : '卖出'}策略已导入`, "success");
                } catch (error) {
                    console.error('导入配置时出错：', error);
                    App.log(`导入失败：${error.message}`, "error");
                }
            };
            reader.readAsText(file);
        });
        input.click();
    },

    /**
     * 应用配置到容器（修复：正确的UI重建和事件绑定）
     */
    applyConfigToContainer(configData, side) {
        try {
            const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
            UIManagerUtils.clearFactorCards(containerId);
            
            if (!Array.isArray(configData)) {
                throw new Error('配置数据必须是数组');
            }
            
            configData.forEach(factorGroup => {
                try {
                    const cardId = `card-${Date.now()}-${Math.random()}`;
                    const card = document.createElement('div');
                    card.className = 'factor-card';
                    card.id = cardId;
                    
                    card.innerHTML = `
                        <div class="card-header">
                            <span class="card-title">${factorGroup.factor_group_name || 'Unknown'}</span>
                            <div class="card-weight-group">
                                <label>权重:</label>
                                <input type="number" class="card-weight-input" value="${factorGroup.weight || 0}" min="0">
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
                    
                    document.getElementById(containerId).appendChild(card);
                    
                    // 绑定卡片事件
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
                            App.showFactorModal(side, cardId);
                        });
                    }

                    // 从树形结构重建 UI
                    const conditionsList = card.querySelector('.conditions-list');
                    if (conditionsList && factorGroup.logic_tree) {
                        ConditionManager.buildUIFromTree(factorGroup.logic_tree, conditionsList, cardId);
                    }
                } catch (error) {
                    console.error('应用因子组时出错：', error);
                    App.log(`应用因子组失败：${error.message}`, "error");
                }
            });
        } catch (error) {
            console.error('应用配置时出错：', error);
            App.log(`应用配置失败：${error.message}`, "error");
        }
    },

    /**
     * 加载配置文件（修复：完整的错误处理）
     */
    loadConfigFile(selectId) {
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
                    
                    if (!Array.isArray(data)) {
                        throw new Error('配置文件格式无效');
                    }
                    
                    const fileKey = `config_${Date.now()}`;
                    sessionStorage.setItem(fileKey, JSON.stringify(data));
                    
                    const select = document.getElementById(selectId);
                    if (select) {
                        // 移除旧选项（如果有）
                        Array.from(select.options).forEach(option => {
                            if (option.value.startsWith('config_')) {
                                option.remove();
                            }
                        });
                        
                        const option = document.createElement('option');
                        option.value = fileKey;
                        option.textContent = file.name;
                        select.appendChild(option);
                        select.value = fileKey;
                    }
                    
                    App.log('配置文件已加载', "success");
                } catch (error) {
                    console.error('加载文件时出错：', error);
                    App.log(`文件加载失败：${error.message}`, "error");
                }
            };
            reader.readAsText(file);
        });
        input.click();
    }
};