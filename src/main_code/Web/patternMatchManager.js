/**
 * patternMatchManager.js - 模式匹配管理模块
 * 
 * 职责：
 * - 匹配条件管理（添加/删除条件行）
 * - 向服务器发送匹配请求 & 接收结果
 * - 结果列表渲染、排序、搜索
 * - K线详情弹窗（含匹配区间标注，数据已有无需请求）
 * - 参数面板渲染（预留扩展位置）
 * - 参数导出请求（均值/中位数/聚合）& 结果查看弹窗
 * - 匹配结果的JSON导入/导出
 */

import { App } from './app.js';
import * as SocketModule from "./socket.js";

let manager = null;
let conditionIdCounter = 0;

// ===== 模块内部状态 =====
const PMState = {
    // 匹配条件列表
    conditions: [],
    // 原始匹配结果
    rawResults: [],
    // 过滤后结果
    filteredResults: [],
    // 排序状态
    sortField: 'match_start',
    sortDirection: 'desc',
    // 搜索关键字
    searchKeyword: '',
    // 当前选中记录（用于K线弹窗）
    selectedRecord: null,
    // K线图表实例
    klineChart: null,
    // 是否正在匹配中
    isMatching: false,
    // 是否正在导出参数
    isExporting: false,
    // 最近一次导出结果
    lastExportedParams: null,
    lastExportedType: '',
};

export function setPatternMatchManager(_manager) {
    manager = _manager;
}

export const PatternMatchManager = {

    // ============================
    // 初始化
    // ============================

    init() {
        this.bindEvents();
        this.addDefaultCondition();
        console.log('✅ PatternMatchManager 初始化完成');
        return this;
    },

    // ============================
    // 事件绑定
    // ============================

    bindEvents() {
        // 添加条件
        const addCondBtn = document.getElementById('pm-add-condition');
        if (addCondBtn) {
            addCondBtn.addEventListener('click', () => this.addCondition());
        }

        // 开始匹配
        const runMatchBtn = document.getElementById('pm-run-match');
        if (runMatchBtn) {
            runMatchBtn.addEventListener('click', () => this.runMatch());
        }

        const stopMatchBtn = document.getElementById('pm-stop-match');
        if (stopMatchBtn) {
            stopMatchBtn.addEventListener('click', () => this.stopMatch());
            stopMatchBtn.addEventListener('click', () => this.sendStopMatch());
        }

        // 查看结果
        const viewResultBtn = document.getElementById('pm-view-result');
        if (viewResultBtn) {
            viewResultBtn.addEventListener('click', () => this.showResultView());
        }

        // 返回配置
        const backBtn = document.getElementById('pm-back-to-config');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.showConfigView());
        }

        // 搜索过滤
        const searchInput = document.getElementById('pm-result-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                PMState.searchKeyword = e.target.value.trim().toLowerCase();
                this.applyFilterAndSort();
            });
        }

        // 排序按钮
        document.querySelectorAll('.pm-sort-btn').forEach(btn => {
            btn.addEventListener('click', () => this.handleSortClick(btn));
        });

        // 导出结果JSON
        const exportBtn = document.getElementById('pm-export-result');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportResultJSON());
        }

        // 导入结果JSON
        const importBtn = document.getElementById('pm-import-result');
        const importFile = document.getElementById('pm-import-file');
        if (importBtn && importFile) {
            importBtn.addEventListener('click', () => importFile.click());
            importFile.addEventListener('change', (e) => this.importResultJSON(e));
        }

        // 参数导出按钮
        document.querySelectorAll('.pm-export-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const exportType = btn.dataset.exportType;
                this.requestParamExport(exportType);
            });
        });

        // 查看导出参数结果
        const viewExportedBtn = document.getElementById('pm-view-exported-params');
        if (viewExportedBtn) {
            viewExportedBtn.addEventListener('click', () => this.openExportedParamsModal());
        }

        // K线详情弹窗关闭
        const detailClose = document.getElementById('pm-detail-close');
        const detailOverlay = document.getElementById('pm-detail-overlay');
        if (detailClose) detailClose.addEventListener('click', () => this.closeDetailModal());
        if (detailOverlay) detailOverlay.addEventListener('click', () => this.closeDetailModal());

        // 导出参数弹窗关闭
        const exportedClose = document.getElementById('pm-exported-close');
        const exportedOverlay = document.getElementById('pm-exported-overlay');
        if (exportedClose) exportedClose.addEventListener('click', () => this.closeExportedModal());
        if (exportedOverlay) exportedOverlay.addEventListener('click', () => this.closeExportedModal());

        // 保存导出结果JSON
        const saveExportedBtn = document.getElementById('pm-save-exported-json');
        if (saveExportedBtn) {
            saveExportedBtn.addEventListener('click', () => this.saveExportedParamsJSON());
        }

        // 参数搜索
        const paramFilter = document.getElementById('pm-detail-param-filter');
        if (paramFilter) {
            paramFilter.addEventListener('input', (e) => {
                this.filterParams(e.target.value.trim().toLowerCase());
            });
        }

        // ESC 关闭弹窗
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDetailModal();
                this.closeExportedModal();
            }
        });
    },

    // ============================
    // 条件管理
    // ============================

    addDefaultCondition() {
        this.addCondition(0, 20, 100, null);
    },

    /**
     * 添加一个匹配条件行
     * @param {number} daysMin - 天数最小值
     * @param {number} daysMax - 天数最大值
     * @param {number} changeMin - 涨幅最小值(%)
     * @param {number|null} changeMax - 涨幅最大值(%)，null表示不限
     */
    addCondition(daysMin = 1, daysMax = 30, changeMin = 0, changeMax = null,  unlimited = false) {
        const id = `pm-cond-${++conditionIdCounter}`;
        const container = document.getElementById('pm-conditions-list');
        if (!container) return;

        const row = document.createElement('div');
        row.className = 'pm-condition-row';
        row.id = id;

        const changeMaxValue = unlimited ? '' : (changeMax !== null ? changeMax : '');
        const isUnlimitedChecked = unlimited || changeMax === null;



        row.innerHTML = `
            <span class="pm-cond-label">天数(前X天-前X天)：</span>
            <input type="number" class="pm-cond-input pm-days-min" value="${daysMin}" min="0" placeholder="最小">
            <span class="pm-cond-separator">~</span>
            <input type="number" class="pm-cond-input pm-days-max" value="${daysMax}" min="1" placeholder="最大">
            <span class="pm-cond-label" style="margin-left:12px;">涨幅(%)：</span>
            <input type="number" class="pm-cond-input pm-change-min" value="${changeMin}" step="1" placeholder="最小">
            <span class="pm-cond-separator">~</span>
            <input type="number" class="pm-cond-input pm-change-max" value="${changeMax !== null ? changeMax : ''}" step="1" placeholder="不限">
            <label style="margin-left: 4px; font-size: 12px; white-space: nowrap;">
                <input type="checkbox" class="pm-change-unlimited" 
                    ${changeMax === null ? 'checked' : ''} title="不限涨幅">
                无限
            </label>

            <button class="pm-cond-delete" title="删除此条件">✕</button>
        `;

        // 绑定删除
        row.querySelector('.pm-cond-delete').addEventListener('click', () => {
            row.remove();
        });

        // 新增：绑定无限制复选框事件
        const unlimitCheckbox = row.querySelector('.pm-change-unlimited');
        const changeMaxInput = row.querySelector('.pm-change-max');
        
        unlimitCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                changeMaxInput.value = '';
                changeMaxInput.disabled = true;
                changeMaxInput.style.opacity = '0.5';
            } else {
                changeMaxInput.disabled = false;
                changeMaxInput.style.opacity = '1';
                changeMaxInput.focus();
            }
        });

        container.appendChild(row);
    },

    /**
     * 收集所有匹配条件
     * @returns {Array} conditions
     */
    collectConditions() {
        const rows = document.querySelectorAll('.pm-condition-row');
        const conditions = [];
        rows.forEach(row => {
            const daysMin = parseInt(row.querySelector('.pm-days-min').value) || 0;
            const daysMax =  parseInt(row.querySelector('.pm-days-max').value) || 30;
            const changeMin = parseFloat(row.querySelector('.pm-change-min').value);


            const isUnlimited = row.querySelector('.pm-change-unlimited')?.checked ?? false;
            const changeMaxStr = row.querySelector('.pm-change-max').value.trim();
            const changeMax = changeMaxStr === '' ? null : parseFloat(changeMaxStr);

            conditions.push({
                days_min: daysMin,
                days_max: daysMax,
                change_min: isNaN(changeMin) ? null : changeMin,
                change_max: isNaN(changeMax) ? null : changeMax,
                unlimited: isUnlimited
            });
        });
        return conditions;
    },

    // ============================
    // 视图切换
    // ============================

    showConfigView() {
        document.getElementById('pm-config-view')?.classList.add('active');
        document.getElementById('pm-result-view')?.classList.remove('active');
    },

    showResultView() {
        document.getElementById('pm-config-view')?.classList.remove('active');
        document.getElementById('pm-result-view')?.classList.add('active');
        this.applyFilterAndSort();
    },

    // ============================
    // 匹配请求
    // ============================

    runMatch() {
        const conditions = this.collectConditions();
        if (conditions.length === 0) {
            App.log('❌ 请至少添加一个匹配条件', 'error');
            return;
        }
        const startDate = document.getElementById('pm-start-date')?.value || '';
        const endDate = document.getElementById('pm-end-date')?.value || '';


        const marketCapMin = document.getElementById('pm-market-cap-min')?.value || '0';
        const marketCapMax = document.getElementById('pm-market-cap-max')?.value;
        const marketCapUnlimited = document.getElementById('pm-market-cap-unlimited')?.checked ?? false;
        
        const priceMin = document.getElementById('pm-price-min')?.value || '0';
        const priceMax = document.getElementById('pm-price-max')?.value;
        const priceUnlimited = document.getElementById('pm-price-unlimited')?.checked ?? false;

        const payload = {
            start_date: startDate.replace(/-/g, ''),
            end_date: endDate ? endDate.replace(/-/g, '') : '',
            conditions: conditions,

            // 新增：市值范围
            market_cap_range: {
                min: parseFloat(marketCapMin) || 0,
                max: marketCapUnlimited ? null : (parseFloat(marketCapMax) || null),
                unlimited: marketCapUnlimited
            },
            // 新增：股价范围
            price_range: {
                min: parseFloat(priceMin) || 0,
                max: priceUnlimited ? null : (parseFloat(priceMax) || null),
                unlimited: priceUnlimited
            },

            exclude_st: document.getElementById('pm-filter-exclude-st')?.checked ?? true,
            exclude_kc: document.getElementById('pm-filter-exclude-kc')?.checked ?? true,
            exclude_cy: document.getElementById('pm-filter-exclude-cy')?.checked ?? true,
            timestamp: new Date().toISOString()
        };

        // 显示loading
        PMState.isMatching = true;
        const loadingEl = document.getElementById('pm-loading');
        const runBtn = document.getElementById('pm-run-match');
        const stopBtn = document.getElementById('pm-stop-match');
        const viewBtn = document.getElementById('pm-view-result');


        if (runBtn) runBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-flex';
        if (loadingEl) loadingEl.style.display = 'inline-flex';
        if (viewBtn) viewBtn.style.display = 'none';

        App.log(`📤 发送模式匹配请求, 条件数: ${conditions.length}`, 'system');
        console.log('模式匹配请求:', JSON.stringify(payload, null, 2));

        if (manager && manager.socket) {
            manager.socket.sendMessage(SocketModule.MessageType.CS_PATTERN_MATCH, payload);
        }
    },


    stopMatch() {
        PMState.isMatching = false;
        App.log('⏹️ 匹配已停止', 'warning');
        
        const loadingEl = document.getElementById('pm-loading');
        const runBtn = document.getElementById('pm-run-match');
        const stopBtn = document.getElementById('pm-stop-match');
        
        if (loadingEl) loadingEl.style.display = 'none';
        if (runBtn) runBtn.style.display = 'inline-flex';
        if (stopBtn) stopBtn.style.display = 'none';


    },
    
    sendStopMatch() {
        
        if (manager && manager.socket) {
            manager.socket.sendMessage(SocketModule.MessageType.CS_PATTERN_MATCH_STOP, {
                timestamp: new Date().toISOString()
            });
        }
    },

    // ============================
    // 接收匹配结果
    // ============================

    /**
     * 接收服务器返回的匹配结果
     * @param {Object} data - 服务器返回的完整数据
     * 
     * 期望格式：
     * {
     *   matches: [
     *     {
     *       code: "600000",
     *       name: "浦发银行",
     *       match_start: "2024-01-05",
     *       match_end: "2024-02-03",
     *       days: 29,
     *       change_pct: 105.3,
     *       kline: [
     *         { date: "2023-12-01", open: 10.0, close: 10.5, high: 10.8, low: 9.9, volume: 50000, turn: 1.2, change_Ratio: 2.5 },
     *         ...
     *       ],
     *       params: {
     *         groups: [
     *           {
     *             name: "基本信息",
     *             items: [
     *               { label: "市盈率", value: 12.5, type: "number" },
     *               { label: "市净率", value: 1.2, type: "number" },
     *               ...
     *             ]
     *           },
     *           ...
     *         ]
     *       }
     *     },
     *     ...
     *   ]
     * }
     */
    setResultData(data) {
        PMState.isMatching = false;
        PMState.rawResults = (data && data.matches) ? data.matches : [];
        PMState.searchKeyword = '';
        PMState.sortField = 'match_start';
        PMState.sortDirection = 'desc';

        const runBtn = document.getElementById('pm-run-match');
        const stopBtn = document.getElementById('pm-stop-match');
        
        if (runBtn) runBtn.style.display = 'inline-flex';
        if (stopBtn) stopBtn.style.display = 'none';
 


        // 隐藏loading
        const loadingEl = document.getElementById('pm-loading');
        if (loadingEl) loadingEl.style.display = 'none';

        // 更新计数
        const countEl = document.getElementById('pm-result-count');
        if (countEl) countEl.textContent = PMState.rawResults.length;

        const totalEl = document.getElementById('pm-result-total');
        if (totalEl) totalEl.textContent = PMState.rawResults.length;

        // 显示查看结果按钮
        const viewBtn = document.getElementById('pm-view-result');
        if (viewBtn) viewBtn.style.display = 'inline-flex';

        // 重置排序按钮
        document.querySelectorAll('.pm-sort-btn').forEach(b => {
            b.classList.remove('active', 'asc', 'desc');
        });
        const defaultSort = document.querySelector('.pm-sort-btn[data-sort="match_start"]');
        if (defaultSort) defaultSort.classList.add('active', 'desc');

        // 清空搜索
        const searchInput = document.getElementById('pm-result-search');
        if (searchInput) searchInput.value = '';

        // 重置导出按钮
        const viewExportedBtn = document.getElementById('pm-view-exported-params');
        if (viewExportedBtn) viewExportedBtn.style.display = 'none';
        PMState.lastExportedParams = null;
        PMState.lastExportedType = '';

        this.applyFilterAndSort();
        App.log(`📊 模式匹配完成，共 ${PMState.rawResults.length} 条结果`, 'success');
    },

    // ============================
    // 过滤与排序
    // ============================

    applyFilterAndSort() {
        let data = [...PMState.rawResults];

        // 搜索过滤
        if (PMState.searchKeyword) {
            const kw = PMState.searchKeyword;
            data = data.filter(r =>
                (r.code && r.code.toLowerCase().includes(kw)) ||
                (r.name && r.name.toLowerCase().includes(kw))
            );
        }

        // 排序
        const field = PMState.sortField;
        const dir = PMState.sortDirection === 'asc' ? 1 : -1;
        data.sort((a, b) => {
            let va = a[field] ?? '';
            let vb = b[field] ?? '';
            if (typeof va === 'string' && typeof vb === 'string') {
                return va.localeCompare(vb) * dir;
            }
            return ((va || 0) - (vb || 0)) * dir;
        });

        PMState.filteredResults = data;

        const totalEl = document.getElementById('pm-result-total');
        if (totalEl) totalEl.textContent = data.length;

        this.renderTable(data);
    },

    handleSortClick(btn) {
        const field = btn.dataset.sort;
        if (PMState.sortField === field) {
            PMState.sortDirection = PMState.sortDirection === 'desc' ? 'asc' : 'desc';
        } else {
            PMState.sortField = field;
            PMState.sortDirection = 'desc';
        }

        document.querySelectorAll('.pm-sort-btn').forEach(b => {
            b.classList.remove('active', 'asc', 'desc');
        });
        btn.classList.add('active', PMState.sortDirection);
        this.applyFilterAndSort();
    },

    // ============================
    // 表格渲染
    // ============================

    renderTable(records) {
        const tbody = document.getElementById('pm-result-tbody');
        if (!tbody) return;

        if (!records || records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" class="pm-empty">暂无匹配结果</td></tr>';
            return;
        }

        const fragment = document.createDocumentFragment();
        records.forEach((record, idx) => {
            const tr = document.createElement('tr');

            const changeCls = (record.change_pct || 0) >= 0 ? 'pm-change-up' : 'pm-change-down';
            const changePrefix = (record.change_pct || 0) >= 0 ? '+' : '';

            tr.innerHTML = `
                <td>${idx + 1}</td>
                <td style="font-family:monospace;color:#4facfe;">${record.code || '--'}</td>
                <td style="color:#e6eaf2;font-weight:500;">${record.name || '--'}</td>
                <td>${record.match_start || '--'}</td>
                <td>${record.match_end || '--'}</td>
                <td>${record.days ?? '--'}</td>
                <td class="${changeCls}">${changePrefix}${(record.change_pct ?? 0).toFixed(2)}%</td>
                <td><button class="pm-view-kline-btn">📈 K线</button></td>
            `;

            tr.querySelector('.pm-view-kline-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.openDetailModal(record);
            });

            fragment.appendChild(tr);
        });

        tbody.innerHTML = '';
        tbody.appendChild(fragment);
    },

    // ============================
    // JSON导入/导出
    // ============================

    exportResultJSON() {
        if (PMState.rawResults.length === 0) {
            App.log('❌ 暂无匹配结果可导出', 'error');
            return;
        }

        const exportData = {
            export_time: new Date().toISOString(),
            start_date: document.getElementById('pm-start-date')?.value || '',
            end_date: document.getElementById('pm-end-date')?.value || '',
            conditions: this.collectConditions(),
            matches: PMState.rawResults
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_match_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);

        App.log(`📥 已导出匹配结果JSON，共 ${PMState.rawResults.length} 条`, 'success');
    },

    importResultJSON(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                if (!data.matches || !Array.isArray(data.matches)) {
                    App.log('❌ JSON格式不正确，缺少matches字段', 'error');
                    return;
                }

                // 恢复配置
                if (data.start_date) {
                    const startEl = document.getElementById('pm-start-date');
                    if (startEl) startEl.value = data.start_date;
                }
                if (data.end_date) {
                    const endEl = document.getElementById('pm-end-date');
                    if (endEl) endEl.value = data.end_date;
                }

                // 恢复条件
                if (data.conditions && Array.isArray(data.conditions)) {
                    const container = document.getElementById('pm-conditions-list');
                    if (container) container.innerHTML = '';
                    data.conditions.forEach(cond => {
                        this.addCondition(
                            cond.days_min,
                            cond.days_max,
                            cond.change_min ?? 0,
                            cond.change_max
                        );
                    });
                }

                // 设置结果
                this.setResultData(data);
                App.log(`📤 已导入匹配结果JSON，共 ${data.matches.length} 条`, 'success');
            } catch (err) {
                App.log(`❌ JSON解析失败: ${err.message}`, 'error');
            }
        };
        reader.readAsText(file);

        // 重置file input以便重复选择同一文件
        event.target.value = '';
    },

    // ============================
    // 参数导出请求
    // ============================

    /**
     * 请求参数导出（发送给服务器）
     * @param {string} exportType - 'mean' | 'median' | 'aggregate'
     */
    requestParamExport(exportType) {
        if (PMState.rawResults.length === 0) {
            App.log('❌ 暂无匹配结果，无法导出参数', 'error');
            return;
        }

        PMState.isExporting = true;
        const exportLoading = document.getElementById('pm-export-loading');
        if (exportLoading) exportLoading.style.display = 'inline-flex';
        const viewExportedBtn = document.getElementById('pm-view-exported-params');
        if (viewExportedBtn) viewExportedBtn.style.display = 'none';

        // 发送匹配结果code列表和类型给服务器
        const matchCodes = PMState.rawResults.map(r => ({
            code: r.code,
            match_start: r.match_start,
            match_end: r.match_end
        }));

        const payload = {
            export_type: exportType,
            matches: matchCodes,
            timestamp: new Date().toISOString()
        };

        App.log(`📤 请求参数导出: ${exportType}`, 'system');

        if (manager && manager.socket) {
            
            manager.socket.sendMessage(SocketModule.MessageType.CS_PATTERN_EXPORT_PARAMS, payload);
        }
    },

    /**
     * 接收参数导出结果
     * @param {Object} data
     * 
     * 期望格式：
     * {
     *   export_type: "mean",
     *   params: [
     *     { name: "市盈率", value: 15.6 },
     *     { name: "市净率", value: 1.8 },
     *     ...
     *   ]
     * }
     */
    setExportedParamsData(data) {
        PMState.isExporting = false;
        const exportLoading = document.getElementById('pm-export-loading');
        if (exportLoading) exportLoading.style.display = 'none';

        if (!data || !data.params) {
            App.log('❌ 参数导出结果为空', 'error');
            return;
        }

        PMState.lastExportedType = data.export_type || 'unknown';
        PMState.lastExportedParams = data.params;

        // 自动保存JSON
        this.autoSaveExportedJSON(data);

        // 显示查看按钮
        const viewExportedBtn = document.getElementById('pm-view-exported-params');
        if (viewExportedBtn) viewExportedBtn.style.display = 'inline-flex';

        App.log(`📋 参数导出完成(${PMState.lastExportedType})，共 ${data.params.length} 个参数`, 'success');
    },

    autoSaveExportedJSON(data) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_params_${data.export_type}_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    saveExportedParamsJSON() {
        if (!PMState.lastExportedParams) {
            App.log('❌ 暂无导出结果', 'error');
            return;
        }
        const data = {
            export_type: PMState.lastExportedType,
            export_time: new Date().toISOString(),
            params: PMState.lastExportedParams
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `pattern_params_${PMState.lastExportedType}_${new Date().toISOString().slice(0, 10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
    },

    // ============================
    // 导出参数查看弹窗
    // ============================

    openExportedParamsModal() {
        if (!PMState.lastExportedParams) {
            App.log('❌ 暂无导出结果', 'error');
            return;
        }

        // 填充信息
        const titleEl = document.getElementById('pm-exported-title');
        if (titleEl) titleEl.textContent = `📋 参数导出结果 - ${PMState.lastExportedType}`;

        const typeEl = document.getElementById('pm-exported-type-label');
        if (typeEl) typeEl.textContent = `类型：${PMState.lastExportedType}`;

        const countEl = document.getElementById('pm-exported-count-label');
        if (countEl) countEl.textContent = `条目数：${PMState.lastExportedParams.length}`;

        // 渲染表格
        const tbody = document.getElementById('pm-exported-tbody');
        if (tbody) {
            if (PMState.lastExportedParams.length === 0) {
                tbody.innerHTML = '<tr><td colspan="2" style="text-align:center;color:#555;">暂无数据</td></tr>';
            } else {
                const fragment = document.createDocumentFragment();
                PMState.lastExportedParams.forEach(p => {
                    const tr = document.createElement('tr');
                    // 新增：检查是否为范围值
                    let displayVal;
                    if (p.value && typeof p.value === 'object' && (p.value.min !== undefined || p.value.max !== undefined)) {
                        // 范围值格式：[min ~ max]
                        const minVal = p.value.min !== undefined ? p.value.min.toFixed(4) : '无限';
                        const maxVal = p.value.max !== undefined ? p.value.max.toFixed(4) : '无限';
                        displayVal = `[${minVal} ~ ${maxVal}]`;
                    } else if (typeof p.value === 'number') {
                        // 单值格式
                        displayVal = p.value.toFixed(4);
                    } else {
                        displayVal = String(p.value);
                    }
                    tr.innerHTML = `
                        <td style="color:#4facfe;font-weight:500;">${p.name || '--'}</td>
                        <td style="font-family:monospace;">${displayVal}</td>
                    `;
                    fragment.appendChild(tr);
                });
                tbody.innerHTML = '';
                tbody.appendChild(fragment);
            }
        }

        document.getElementById('pm-exported-params-modal')?.classList.add('open');
        document.body.style.overflow = 'hidden';
    },

    closeExportedModal() {
        document.getElementById('pm-exported-params-modal')?.classList.remove('open');
        // 不恢复body overflow，因为可能还有K线弹窗打开
        if (!document.querySelector('.pm-detail-modal.open')) {
            document.body.style.overflow = '';
        }
    },

    // ============================
    // K线详情弹窗
    // ============================

    openDetailModal(record) {
        PMState.selectedRecord = record;

        // 填充头部
        document.getElementById('pm-detail-code').textContent = record.code || '--';
        document.getElementById('pm-detail-name').textContent = record.name || '--';
        document.getElementById('pm-detail-match-info').textContent =
            `${record.match_start || '--'} ~ ${record.match_end || '--'}`;

        // 绘制K线（数据已有）
        this.drawKlineChart(record);

        // 渲染参数
        this.renderParams(record.params || {});

        // 清空参数搜索
        const paramFilter = document.getElementById('pm-detail-param-filter');
        if (paramFilter) paramFilter.value = '';

        // 显示弹窗
        document.getElementById('pm-detail-modal')?.classList.add('open');
        document.body.style.overflow = 'hidden';

        App.log(`📈 查看匹配详情: ${record.code} ${record.name}`, 'system');
    },

    closeDetailModal() {
        document.getElementById('pm-detail-modal')?.classList.remove('open');
        document.body.style.overflow = '';
        PMState.selectedRecord = null;

        if (PMState.klineChart) {
            PMState.klineChart.dispose();
            PMState.klineChart = null;
        }
    },

    // ============================
    // K线绘制（含匹配标注）
    // ============================

    drawKlineChart(record) {
        const container = document.getElementById('pm-detail-kline-chart');
        if (!container) return;

        if (PMState.klineChart) {
            PMState.klineChart.dispose();
        }
        PMState.klineChart = echarts.init(container, 'dark');

        const klineData = record.kline || [];
        if (klineData.length === 0) {
            PMState.klineChart.setOption({
                backgroundColor: 'transparent',
                title: { text: '暂无K线数据', left: 'center', textStyle: { color: '#555', fontSize: 14 } }
            });
            return;
        }

        const dates = klineData.map(d => d.date);
        const ohlc = klineData.map(d => ({
            value: [d.open, d.close, d.low, d.high, d.volume],
            ...d
        }));
        const volumes = klineData.map(d => d.volume || 0);

        // 计算MA
        const ma5 = this.calcMA(klineData.map(d => d.close), 5);
        const ma10 = this.calcMA(klineData.map(d => d.close), 10);
        const ma20 = this.calcMA(klineData.map(d => d.close), 20);
        const ma60 = this.calcMA(klineData.map(d => d.close), 60);

        // 匹配区间标注
        const matchStart = record.match_start || '';
        const matchEnd = record.match_end || '';

        const markAreaData = [];
        if (matchStart && matchEnd) {
            markAreaData.push([
                {
                    name: '匹配区间',
                    xAxis: matchStart,
                    itemStyle: {
                        color: 'rgba(255, 183, 77, 0.15)',
                        borderColor: '#ffb74d',
                        borderWidth: 1,
                        borderType: 'dashed'
                    }
                },
                {
                    xAxis: matchEnd
                }
            ]);
        }

        const markLineData = [];
        if (matchStart) {
            markLineData.push({
                name: '匹配开始',
                xAxis: matchStart,
                lineStyle: { color: '#00c853', width: 2, type: 'solid' },
                label: {
                    show: true,
                    formatter: '开始',
                    color: '#00c853',
                    fontSize: 11,
                    position: 'start'
                }
            });
        }
        if (matchEnd) {
            markLineData.push({
                name: '匹配结束',
                xAxis: matchEnd,
                lineStyle: { color: '#ff5252', width: 2, type: 'solid' },
                label: {
                    show: true,
                    formatter: '结束',
                    color: '#ff5252',
                    fontSize: 11,
                    position: 'start'
                }
            });
        }

        const option = {
            backgroundColor: 'transparent',
            title: { show: false },
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'cross' },
                backgroundColor: 'rgba(0,0,0,0.85)',
                borderColor: '#4facfe',
                textStyle: { fontSize: 12 },
                formatter: (params) => {
                    const isMain = params.some(p => p.seriesType === 'candlestick');
                    if (!isMain) {
                        const data = params[0].data;
                        return `成交量（万手）：${data.value}<br/>`;
                    }
                    const data = params[0].data;
                    const color = (data.change_Ratio ?? 0) >= 0 ? '#ec0000' : '#00da3c';
                    return `
                        日期：${data.date}<br/>
                        涨跌：<span style="color:${color}">${(data.change_Ratio ?? 0).toFixed(2)}%</span><br/>
                        换手：${data.turn ?? '--'}%<br/>
                        开：${data.open}<br/>
                        收：${data.close}<br/>
                        高：${data.high}<br/>
                        低：${data.low}<br/>
                    `;
                }
            },
            legend: {
                data: ['K线', 'MA5', 'MA10', 'MA20', 'MA60'],
                textStyle: { color: '#e2e2e2', fontSize: 11 },
                top: 5,
                right: 10
            },
            grid: [
                { left: '8%', right: '3%', top: '12%', height: '58%' },
                { left: '8%', right: '3%', top: '75%', height: '18%' }
            ],
            xAxis: [
                {
                    type: 'category', data: dates, gridIndex: 0,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { show: false },
                    splitLine: { show: false }
                },
                {
                    type: 'category', data: dates, gridIndex: 1,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { fontSize: 10, color: '#c0bfbf', interval: 'auto' },
                    splitLine: { show: false }
                }
            ],
            yAxis: [
                {
                    type: 'value', gridIndex: 0, scale: true,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { fontSize: 10, color: '#c7c7c7' },
                    splitLine: { lineStyle: { color: '#222' } }
                },
                {
                    type: 'value', gridIndex: 1,
                    axisLine: { lineStyle: { color: '#444' } },
                    axisLabel: { show: false },
                    splitLine: { show: false }
                }
            ],
            dataZoom: [
                {
                    type: 'inside', xAxisIndex: [0, 1],
                    start: Math.max(0, 100 - Math.min(80, klineData.length / 2)),
                    end: 100
                },
                {
                    type: 'slider', xAxisIndex: [0, 1],
                    start: Math.max(0, 100 - Math.min(80, klineData.length / 2)),
                    end: 100,
                    top: '95%', height: 15,
                    textStyle: { color: '#cfcfcf' }
                }
            ],
            series: [
                {
                    name: 'K线',
                    type: 'candlestick',
                    data: ohlc,
                    xAxisIndex: 0, yAxisIndex: 0,
                    itemStyle: {
                        color: '#ec0000', color0: '#00da3c',
                        borderColor: '#8A0000', borderColor0: '#008F28'
                    },
                    markArea: markAreaData.length > 0 ? { data: markAreaData } : undefined,
                    markLine: markLineData.length > 0 ? {
                        symbol: 'none',
                        data: markLineData,
                        animation: false
                    } : undefined
                },
                this.maLine('MA5', ma5, '#f5a623'),
                this.maLine('MA10', ma10, '#4facfe'),
                this.maLine('MA20', ma20, '#f093fb'),
                this.maLine('MA60', ma60, '#2ed573'),
                {
                    name: '成交量',
                    type: 'bar',
                    data: volumes.map((v, i) => ({
                        value: v,
                        itemStyle: {
                            color: klineData[i].close >= klineData[i].open
                                ? 'rgba(236,0,0,0.5)'
                                : 'rgba(0,218,60,0.5)'
                        }
                    })),
                    xAxisIndex: 1, yAxisIndex: 1
                }
            ]
        };

        PMState.klineChart.setOption(option, true);

        // 响应resize
        const resizeObserver = new ResizeObserver(() => {
            PMState.klineChart?.resize();
        });
        resizeObserver.observe(container);
    },

    maLine(name, data, color) {
        return {
            name, type: 'line', data,
            xAxisIndex: 0, yAxisIndex: 0,
            smooth: true, showSymbol: false,
            lineStyle: { color, width: 1 }
        };
    },

    calcMA(closes, period) {
        const result = [];
        for (let i = 0; i < closes.length; i++) {
            if (i < period - 1) {
                result.push(null);
            } else {
                let sum = 0;
                for (let j = 0; j < period; j++) sum += closes[i - j];
                result.push(+(sum / period).toFixed(2));
            }
        }
        return result;
    },

    // ============================
    // 参数面板
    // ============================

    /**
     * 渲染参数面板
     * @param {Object} params
     * 
     * 格式同 selectionResultManager:
     * {
     *   groups: [
     *     { name: "分组名", items: [{ label: "参数名", value: 123, type: "number" }, ...] },
     *     ...
     *   ]
     * }
     * 
     * ★ 后续需要添加新参数时，修改服务器返回的 params.groups 即可 ★
     */
    renderParams(params) {
        const container = document.getElementById('pm-detail-params-container');
        if (!container) return;

        let groups = [];
        if (params && params.groups && Array.isArray(params.groups)) {
            groups = params.groups;
        } else if (params && typeof params === 'object') {
            // 扁平对象转成一组
            const items = [];
            const skipKeys = ['code', 'name', 'kline', 'groups', 'match_start', 'match_end', 'days', 'change_pct'];
            for (const [key, val] of Object.entries(params)) {
                if (skipKeys.includes(key)) continue;
                if (typeof val === 'object' && val !== null) continue;
                items.push({
                    label: key,
                    value: val,
                    type: typeof val === 'number' ? 'number' : 'text'
                });
            }
            if (items.length > 0) {
                groups.push({ name: '其他参数', items });
            }
        }

        if (groups.length === 0) {
            container.innerHTML = `
                <div style="color:#555;text-align:center;padding:30px;">
                    暂无参数数据<br>
                    <small style="color:#444;">★ 参数将由服务器返回，此处为预留位置 ★</small>
                </div>`;
            return;
        }

        const fragment = document.createDocumentFragment();
        groups.forEach(group => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'pm-param-group';

            const titleDiv = document.createElement('div');
            titleDiv.className = 'pm-param-group-title';
            titleDiv.innerHTML = `
                <span>${group.name || '未命名'} (${(group.items || []).length})</span>
                <span class="toggle-icon">▼</span>
            `;
            titleDiv.addEventListener('click', () => {
                groupDiv.classList.toggle('collapsed');
            });

            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'pm-param-group-body';

            (group.items || []).forEach(item => {
                const row = document.createElement('div');
                row.className = 'pm-param-row';
                row.dataset.label = (item.label || '').toLowerCase();

                const valStr = this.formatParamValue(item.value, item.type);
                const valCls = this.getParamValueClass(item.value, item.type);

                row.innerHTML = `
                    <span class="pm-param-label" title="${item.label || ''}">${item.label || '--'}</span>
                    <span class="pm-param-value ${valCls}">${valStr}</span>
                `;
                bodyDiv.appendChild(row);
            });

            groupDiv.appendChild(titleDiv);
            groupDiv.appendChild(bodyDiv);
            fragment.appendChild(groupDiv);
        });

        container.innerHTML = '';
        container.appendChild(fragment);
    },

    formatParamValue(value, type) {
        if (value === null || value === undefined) return '--';
        switch (type) {
            case 'percent':
                return (value >= 0 ? '+' : '') + Number(value).toFixed(2) + '%';
            case 'currency':
                return '¥' + Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 });
            case 'number':
                return Number(value).toFixed(2);
            default:
                return String(value);
        }
    },

    getParamValueClass(value, type) {
        if (type === 'percent' || type === 'number') {
            if (Number(value) > 0) return 'positive';
            if (Number(value) < 0) return 'negative';
        }
        return '';
    },

    filterParams(keyword) {
        const container = document.getElementById('pm-detail-params-container');
        if (!container) return;

        const rows = container.querySelectorAll('.pm-param-row');
        const groups = container.querySelectorAll('.pm-param-group');

        if (!keyword) {
            rows.forEach(r => r.style.display = '');
            groups.forEach(g => {
                g.style.display = '';
                g.classList.remove('collapsed');
            });
            return;
        }

        groups.forEach(group => {
            let vis = 0;
            group.querySelectorAll('.pm-param-row').forEach(row => {
                const label = row.dataset.label || '';
                if (label.includes(keyword)) {
                    row.style.display = '';
                    vis++;
                } else {
                    row.style.display = 'none';
                }
            });
            group.style.display = vis > 0 ? '' : 'none';
            if (vis > 0) group.classList.remove('collapsed');
        });
    },

    // ============================
    // 外部接口
    // ============================

    getResultData() {
        return PMState.rawResults;
    },

    getSelectedRecord() {
        return PMState.selectedRecord;
    }
};