/**
 * configManager.js - 配置导入导出模块（修复版）
 * 更新：支持完整的树形结构导出和导入
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
     * 获取因子数据（完整的树形结构）
     * 返回格式：[{ factor_group_name, weight, logic_tree }, ...]
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
     * 导出配置到JSON文件
     * 导出为完整的配置对象，包含metadata
     */
    exportConfig(side) {
        try {
            const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
            const factors = this.getFactorData(containerId);
            
            if (!factors || factors.length === 0) {
                App.log('没有因子配置可导出', 'warning');
                return;
            }
            
            // 创建完整的配置对象
            const config = {
                configs: factors,
                timestamp: new Date().toISOString(),
                version: "1.0",
                description: `${side === 'buy' ? '买入' : '卖出'}策略配置`
            };
            
            // 验证数据结构
            const jsonString = JSON.stringify(config, null, 2);
            JSON.parse(jsonString);
            
            // 创建文件并下载
            const blob = new Blob([jsonString], { type: 'application/json;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${side}_strategy_${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            App.log(`${side === 'buy' ? '买入' : '卖出'}策略已导出 (${factors.length}个因子)`, "success");
            console.log('导出数据:', config);
        } catch (error) {
            console.error('导出配置时出错：', error);
            App.log(`导出失败：${error.message}`, "error");
        }
    },

    /**
     * 导入配置从JSON文件
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
                    
                    // 兼容两种格式：
                    // 1. 直接是数组 [{ factor_group_name, weight, logic_tree }, ...]
                    // 2. 完整配置对象 { configs: [...], timestamp, version }
                    let configsArray;
                    if (Array.isArray(data)) {
                        configsArray = data;
                    } else if (data.configs && Array.isArray(data.configs)) {
                        configsArray = data.configs;
                    } else {
                        throw new Error('数据格式无效：应该是数组或包含configs字段的对象');
                    }
                    
                    this.applyConfigToContainer(configsArray, side);
                    App.log(`${side === 'buy' ? '买入' : '卖出'}策略已导入 (${configsArray.length}个因子)`, "success");
                    console.log('导入的配置:', configsArray);
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
     * 应用配置到容器（重建UI）
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
                                <input type="number" class="card-weight-input" value="${factorGroup.weight || 0}" min="0" step="0.01">
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
                    if (conditionsList && factorGroup.logic_tree && factorGroup.logic_tree.length > 0) {
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
     * 加载配置文件（兼容旧版）
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
                    
                    // 兼容多种格式
                    let configsArray;
                    if (Array.isArray(data)) {
                        configsArray = data;
                    } else if (data.configs && Array.isArray(data.configs)) {
                        configsArray = data.configs;
                    } else {
                        throw new Error('配置文件格式无效');
                    }
                    
                    const fileKey = `config_${Date.now()}`;
                    sessionStorage.setItem(fileKey, JSON.stringify(configsArray));
                    
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
    },

    /**
     * 保存配置到本地存储
     */
    saveToLocal(configKey, side) {
        try {
            const containerId = side === 'buy' ? 'buy-factor-container' : 'sell-factor-container';
            const factors = this.getFactorData(containerId);
            
            const config = {
                configs: factors,
                timestamp: new Date().toISOString(),
                version: "1.0"
            };
            
            localStorage.setItem(configKey, JSON.stringify(config));
            App.log(`配置已保存到本地: ${configKey}`, "success");
            return true;
        } catch (error) {
            console.error('保存配置失败:', error);
            App.log(`保存配置失败: ${error.message}`, "error");
            return false;
        }
    },

    /**
     * 从本地存储读取配置
     */
    loadFromLocal(configKey, side) {
        try {
            const data = localStorage.getItem(configKey);
            if (!data) {
                App.log(`配置不存在: ${configKey}`, "warning");
                return false;
            }
            
            const config = JSON.parse(data);
            let configsArray = Array.isArray(config) ? config : config.configs;
            
            this.applyConfigToContainer(configsArray, side);
            App.log(`配置已从本地加载: ${configKey}`, "success");
            return true;
        } catch (error) {
            console.error('读取配置失败:', error);
            App.log(`读取配置失败: ${error.message}`, "error");
            return false;
        }
    },

    /**
     * 列出所有保存的配置
     */
    listSavedConfigs() {
        const configs = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('stock_config_')) {
                try {
                    const data = JSON.parse(localStorage.getItem(key));
                    configs.push({
                        key: key,
                        name: key.replace('stock_config_', ''),
                        timestamp: data.timestamp,
                        count: data.configs?.length || 0
                    });
                } catch (error) {
                    console.error(`解析配置 ${key} 失败:`, error);
                }
            }
        }
        return configs;
    },

    /**
     * 删除保存的配置
     */
    deleteConfig(configKey) {
        try {
            localStorage.removeItem(configKey);
            App.log(`配置已删除: ${configKey}`, "success");
            return true;
        } catch (error) {
            console.error('删除配置失败:', error);
            return false;
        }
    }
};