/**
 * industryRotationManager.js
 * 管理行业轮动分析的所有逻辑
 */

export const IndustryRotationManager = {
    // 存储分析结果
    analysisData: null,
        /**
     * 初始化子标签页切换
     */
    initTabSwitching() {
        const tabBtns = document.querySelectorAll('.rotation-tab-btn');
        const viewPanes = document.querySelectorAll('.rotation-view-pane');
        console.log("点击点击初始化舒适和")
        
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const viewName = btn.dataset.view;
                console.log("点击点击")
                console.log(viewName)
                // 移除活跃状态
                tabBtns.forEach(b => b.classList.remove('active'));
                viewPanes.forEach(p => p.classList.remove('active'));
                
                // 添加活跃状态
                btn.classList.add('active');
                document.getElementById(`rotation-${viewName}-view`).classList.add('active');
                
                // 切换到热力图时刷新
                if (viewName === 'heatmap') {
                    setTimeout(() => {
                        const container = document.getElementById('industry-heatmap-container');
                        if (container) {
                            const chart = echarts.getInstanceByDom(container);
                            if (chart) chart.resize();
                        }
                    }, 100);
                }
            });
        });
    },
    /**
     * 初始化事件绑定
     */
    init() {
        const analyzeBtn = document.getElementById('btn-analyze-industry-rotation');
        const filterSelect = document.getElementById('rotation-month-filter');
        const minCountInput = document.getElementById('rotation-min-count');
        
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.requestAnalysis());
        }
        
  
        if (filterSelect) {
            filterSelect.addEventListener('change', () => this.refreshTable());
        }
        
        if (minCountInput) {
            minCountInput.addEventListener('change', () => this.refreshTable());
        }
        this.initTabSwitching();
        return this
    },
    
    /**
     * 请求后端分析行业轮动
     */
    requestAnalysis() {
        // 这个函数会通过 AppManager 发送到后端
        if (window.AppManager) {
            window.AppManager.requestIndustryRotationAnalysis();
        }
    },
    
    /**
     * 处理后端返回的分析结果
     * @param {Object} data - 后端返回的数据
     */
    handleAnalysisResult(data) {
        this.analysisData = data;

        // 先检查是否有数据容器
        const heatmapContainer = document.getElementById('industry-heatmap-container');
        const tableView = document.getElementById('rotation-table-view');
        
        if (!heatmapContainer || !tableView) {
            console.error('❌ 容器不存在');
            return;
        }

        this.renderHeatmap();
        this.renderTable();
        this.updateStats();

        const container = document.getElementById('industry-heatmap-container');
        if (container) {
            const chart = echarts.getInstanceByDom(container);
            if (chart) {
                setTimeout(() => chart.resize(), 100);
            }
        }

    },
    
    /**
     * 绘制热力图 (使用 ECharts)
     */
    renderHeatmap() {
        const container = document.getElementById('industry-heatmap-container');
        const heatmapData = this.transformToHeatmapData();

        // 销毁旧实例
        const oldChart = echarts.getInstanceByDom(container);
        if (oldChart) {
            oldChart.dispose();
        }

        // 计算动态高度
        const industryCount = heatmapData.industries.length;
        //const dynamicHeight = Math.max(500, Math.min(800, 30 * industryCount));

        const MIN_CELL_HEIGHT = 20;
        const dynamicHeight = Math.max(500, industryCount * MIN_CELL_HEIGHT);

        container.style.height = dynamicHeight + 'px';

        if (!container || !this.analysisData) return;
        
        // 转换数据格式为 ECharts 热力图需要的格式
        
        const chart = echarts.init(container, 'dark');
        const option = {
            tooltip: { 
                position: 'top', 
                formatter: function (params) {
                    return `
                        行业: ${heatmapData.industries[params.value[1]]}<br/>
                        月份: ${params.value[0] + 1}月<br/>
                        次数: ${params.value[2]}
                        `;
                }
            },
            grid: { 
                height: '85%',
                top: '10%',
                left: '15%',    // 增加左边距
                right: '3%'
            },
            xAxis: {
                type: 'category',
                data: ['1月', '2月', '3月', '4月', '5月', '6月', 
                       '7月', '8月', '9月', '10月', '11月', '12月'],
                splitArea: { show: true },
                axisLabel: {
                    fontSize: 10
                }
                
            },
            yAxis: {
                type: 'category',
                data: heatmapData.industries,
                axisLabel: {
                    fontSize: 10,
                    interval: 0,  // 强制全部显示
                    formatter: function (value) {
                        return value.length > 6 ? value.slice(0, 6) + '...' : value;
                    }
                },

                splitArea: { show: true }
            },
            visualMap: {
                min: 0,
                max: 5,
                calculable: true,
                orient: 'vertical',
                right: '10px',
                inRange: {
                    color: ['#255480', '#0079c2', '#c94c30', '#f47d21', '#f9bf3b', '#ffeb3b']
                }
            },
            series: [{
                name: '上涨次数',
                type: 'heatmap',
                data: heatmapData.values,
                itemStyle: { borderRadius: 0 }
            }],
            dataZoom: [
                {
                    type: 'slider',
                    yAxisIndex: 0,
                    right: 0,
                    width: 12
                },
                {
                    type: 'inside',
                    yAxisIndex: 0
                }
            ],

        };
        
        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },
    
    /**
     * 转换数据为热力图格式
     */
    transformToHeatmapData() {
        const industries = Object.keys(this.analysisData);
        const values = [];
        
        industries.forEach((industry, industryIndex) => {
            for (let month = 1; month <= 12; month++) {
                const count = this.analysisData[industry]?.[month] || 0;
                values.push([month - 1, industryIndex, count]);
            }
        });
        
        return { industries, values };
    },
    

    initTableSorting() {
        const thead = document.querySelector('.rotation-data-table thead');
        if (!thead) return;
        
        const headers = thead.querySelectorAll('th.sortable');
        let currentSort = { column: null, direction: 'asc' };
        
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const sortKey = header.dataset.sort;
                const tbody = document.querySelector('.rotation-data-table tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                
                // 切换排序方向
                if (currentSort.column === sortKey) {
                    currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSort.column = sortKey;
                    currentSort.direction = 'asc';
                }
                
                // 更新样式
                headers.forEach(h => h.classList.remove('sort-asc', 'sort-desc'));
                header.classList.add(`sort-${currentSort.direction}`);
                
                // 排序
                rows.sort((a, b) => {
                    let aVal, bVal;
                    

                    if (sortKey === 'avgChange') {
                        aVal = parseFloat(a.querySelector('.col-avg-change').textContent) || 0;
                        bVal = parseFloat(b.querySelector('.col-avg-change').textContent) || 0;
                    } 
                    
                    return currentSort.direction === 'asc'
                        ? (typeof aVal === 'string' ? aVal.localeCompare(bVal) : aVal - bVal)
                        : (typeof aVal === 'string' ? bVal.localeCompare(aVal) : bVal - aVal);
                });
                
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    },

    /**
     * 渲染数据表格
     */
    renderTable() {
        const tbody = document.getElementById('rotation-table-body');
        if (!tbody || !this.analysisData) return;
        
        const minCount = parseInt(document.getElementById('rotation-min-count').value) || 3;
        const selectedMonth = document.getElementById('rotation-month-filter')?.value || '';

        tbody.innerHTML = '';
        
        Object.entries(this.analysisData).forEach(([industry, monthData]) => {
            const monthUpCount = monthData[selectedMonth] || 0;
            if (selectedMonth && monthUpCount < minCount) {
                return;  // 跳过不符合条件的行业
            }

            const row = document.createElement('tr');
            
            // 计算统计数据
            let qualifiedMonths = 0;
            let totalMonths = 0;
            let sumCount = 0;
            
            let monthCells = '';
            for (let month = 1; month <= 12; month++) {
                const count = monthData[month] || 0;
                if (count > 0) totalMonths++;
                if (count >= minCount) qualifiedMonths++;
                sumCount += count;
                
                const className = `count-${count}`;
                monthCells += `<td class="${className}">${count}</td>`;
            }
            
            const avgMonthChange = monthData.avgChange || 0;
            row.innerHTML = `
                <td class="col-industry">${industry}</td>
                ${monthCells}
            `;
            
            tbody.appendChild(row);
        });
        
        this.initTableSorting();
    },
    
    /**
     * 刷新表格（应用新的筛选条件）
     */
    refreshTable() {
        if (this.analysisData) {
            const tbody = document.getElementById('rotation-table-body');
            tbody.innerHTML = '';
            this.renderTable();
            this.updateStats();
        }
    },
    
    
    /**
     * 更新统计信息
     */
    updateStats() {
        if (!this.analysisData) return;
        
        const minCount = parseInt(document.getElementById('rotation-min-count').value) || 3;
        const selectedMonth = document.getElementById('rotation-month-filter')?.value || '';
        
        let industryCount = 0;
        let satisfyCount = 0
        
        Object.entries(this.analysisData).forEach(([industry, monthData]) => {

            industryCount++;
            const monthUpCount = monthData[selectedMonth] || 0;
            if (selectedMonth && monthUpCount < minCount) {
                return;  // 跳过不符合条件的行业
            }
            satisfyCount++;

        });
        
        
        document.getElementById('stat-industry-count').textContent = industryCount;
        document.getElementById('stat-qualified-count').textContent = satisfyCount;
        
    },
    
};