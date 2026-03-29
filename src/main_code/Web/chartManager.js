
/**
 * chartManager.js - 图表管理模块
 * 
 * 职责：
 * - K 线图表初始化与绘制
 * - 持仓图表初始化与绘制
 * - 收益曲线图绘制
 * - 图表实例管理
 */

import { App } from './app.js';

const ChartInstances = {
    klineChart: null,
    portfolioChart: null
};

let manager = null;

export function setChartManager(_manager) {
    manager = _manager;
}

export const ChartManager = {
    /**
     * 初始化图表
     */
    initCharts() {
        const klineContainer = document.getElementById('klineChart');
        const portfolioContainer = document.getElementById('portfolioChart');
        
        if (klineContainer) {
            ChartInstances.klineChart = echarts.init(klineContainer, 'dark');
        }
        if (portfolioContainer) {
            ChartInstances.portfolioChart = echarts.init(portfolioContainer, 'dark');
        }
    },

    /**
     * 绘制K线图表
     */
    drawKlineChart(klineData) {
        if (!ChartInstances.klineChart) {
            App.log('K线图表未初始化', 'error');
            return;
        }

        const dates = klineData.map(item => item.date);
        const opens = klineData.map(item => item.open);
        const closes = klineData.map(item => item.close);
        const highs = klineData.map(item => item.high);
        const lows = klineData.map(item => item.low);

        const option = {
            backgroundColor: 'transparent',
            title: {
                text: 'K线走势',
                left: 'center',
                textStyle: { color: '#fff', fontSize: 16 }
            },
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: '#555' } },
                axisLabel: { fontSize: 10, color: '#999' }
            },
            yAxis: {
                type: 'value',
                axisLine: { lineStyle: { color: '#555' } },
                axisLabel: { fontSize: 10, color: '#999' },
                splitLine: { lineStyle: { color: '#333' } }
            },
            series: [
                {
                    type: 'candlestick',
                    data: klineData.map(item => [item.open, item.close, item.low, item.high]),
                    itemStyle: {
                        color: '#ec0000',
                        color0: '#00da3c',
                        borderColor: '#8A0000',
                        borderColor0: '#008F28'
                    }
                }
            ]
        };

        ChartInstances.klineChart.setOption(option);
        App.log(`K线图表已绘制，共 ${klineData.length} 个交易日`, "success");
    },

    /**
     * 绘制选股页签的收益曲线图
     * @param {Array} portfolioData - 收益数据数组
     * [{date: "2024-01-01", equity: 100000, profitRate: 0}, ...]
     */
    drawSelectionPortfolioChart(portfolioData) {
        const container = document.getElementById('selectionPortfolioChart');
        if (!container) {
            App.log('选股收益图表容器未找到', 'error');
            return;
        }

        let chart = echarts.getInstanceByDom(container);
        if (!chart) {
            chart = echarts.init(container, 'dark');
        }

        const dates = portfolioData.map(item => item.date);
        const equityData = portfolioData.map(item => item.equity);
        const profitRateData = portfolioData.map(item => item.profitRate);

        const option = {
            backgroundColor: 'transparent',
            title: { 
                text: '收益曲线', 
                left: 'center', 
                textStyle: { color: '#fff', fontSize: 16 } 
            },
            tooltip: { 
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#4facfe'
            },
            legend: { 
                data: ['账户权益', '收益率'], 
                textStyle: { color: '#999' }, 
                top: '40px' 
            },
            grid: { left: '5%', right: '5%', top: '80px', bottom: '15%', containLabel: true },
            xAxis: { 
                type: 'category', 
                data: dates,
                axisLine: { lineStyle: { color: '#555' } }, 
                axisLabel: { fontSize: 10, color: '#999', interval: 'auto' }
            },
            yAxis: [
                { 
                    type: 'value', 
                    position: 'left',
                    name: '权益(¥)',
                    nameTextStyle: { color: '#4facfe' },
                    axisLine: { lineStyle: { color: '#4facfe' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                },
                { 
                    type: 'value', 
                    position: 'right',
                    name: '收益率(%)',
                    nameTextStyle: { color: '#00f2fe' },
                    axisLine: { lineStyle: { color: '#00f2fe' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                }
            ],
            series: [
                {
                    name: '账户权益',
                    type: 'line',
                    yAxisIndex: 0,
                    data: equityData,
                    smooth: true,
                    lineStyle: { color: '#4facfe', width: 2.5 },
                    areaStyle: { color: 'rgba(79, 172, 254, 0.1)' },
                    itemStyle: { color: '#4facfe', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 6
                },
                {
                    name: '收益率',
                    type: 'line',
                    yAxisIndex: 1,
                    data: profitRateData,
                    smooth: true,
                    lineStyle: { color: '#00f2fe', width: 2.5 },
                    itemStyle: { color: '#00f2fe', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 6
                }
            ],
            dataZoom: [
                { 
                    type: 'slider', 
                    show: true, 
                    start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), 
                    end: 100,
                    textStyle: { color: '#999' }
                },
                { 
                    type: 'inside', 
                    start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), 
                    end: 100 
                }
            ]
        };

        chart.setOption(option);
        App.log(`选股收益曲线已绘制，共 ${portfolioData.length} 个交易日`, "success");
    },

    /**
     * 绘制回测页签总仓的收益曲线（包含回撤）
     * @param {Object} backtestData - 回测数据对象
     * {
     *   dates: [...],
     *   equity: [...],
     *   profitRate: [...],
     *   drawdown: [...],
     *   cumulativeMaxDrawdown: [...],
     *   trades: 25
     * }
     */
    drawBacktestTotalChart(backtestData) {
        const container = document.getElementById('holdings-total-chart');
        if (!container) {
            App.log('总仓图表容器未找到', 'error');
            return;
        }

        let chart = echarts.getInstanceByDom(container);
        if (!chart) {
            chart = echarts.init(container, 'dark');
        }

        const option = {
            backgroundColor: 'transparent',
            title: { 
                text: `总仓回测结果 (共${backtestData.trades}笔交易)`, 
                left: 'center', 
                textStyle: { color: '#fff', fontSize: 16 } 
            },
            tooltip: { 
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#4facfe'
            },
            legend: { 
                data: ['账户权益', '收益率', '最大回撤'], 
                textStyle: { color: '#999' }, 
                top: '40px' 
            },
            grid: { left: '5%', right: '5%', top: '80px', bottom: '15%', containLabel: true },
            xAxis: { 
                type: 'category', 
                data: backtestData.dates,
                axisLine: { lineStyle: { color: '#555' } }, 
                axisLabel: { fontSize: 10, color: '#999', interval: 'auto' }
            },
            yAxis: [
                { 
                    type: 'value', 
                    position: 'left',
                    name: '权益(¥)',
                    nameTextStyle: { color: '#4facfe' },
                    axisLine: { lineStyle: { color: '#4facfe' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                },
                { 
                    type: 'value', 
                    position: 'right',
                    name: '收益率/回撤(%)',
                    nameTextStyle: { color: '#00f2fe' },
                    axisLine: { lineStyle: { color: '#00f2fe' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                }
            ],
            series: [
                {
                    name: '账户权益',
                    type: 'line',
                    yAxisIndex: 0,
                    data: backtestData.equity,
                    smooth: true,
                    lineStyle: { color: '#4facfe', width: 2.5 },
                    areaStyle: { color: 'rgba(79, 172, 254, 0.1)' },
                    itemStyle: { color: '#4facfe', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 5
                },
                {
                    name: '收益率',
                    type: 'line',
                    yAxisIndex: 1,
                    data: backtestData.profitRate,
                    smooth: true,
                    lineStyle: { color: '#00f2fe', width: 2.5 },
                    itemStyle: { color: '#00f2fe', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 5
                },
                {
                    name: '最大回撤',
                    type: 'line',
                    yAxisIndex: 1,
                    data: backtestData.cumulativeMaxDrawdown,
                    smooth: true,
                    lineStyle: { color: '#ff5252', width: 2, type: 'dashed' },
                    itemStyle: { color: '#ff5252' },
                    symbolSize: 4
                }
            ],
            dataZoom: [
                { 
                    type: 'slider', 
                    show: true, 
                    start: Math.max(0, 100 - Math.min(50, backtestData.dates.length * 2)), 
                    end: 100,
                    textStyle: { color: '#999' }
                },
                { 
                    type: 'inside', 
                    start: Math.max(0, 100 - Math.min(50, backtestData.dates.length * 2)), 
                    end: 100 
                }
            ]
        };

        chart.setOption(option);
        App.log(`总仓回测图表已绘制，共 ${backtestData.dates.length} 个交易日`, "success");
    },

    /**
     * 绘制回测页签分仓的收益曲线
     * @param {Object} divisionData - 分仓回测数据
     * {
     *   divisionName: "分仓1",
     *   dates: [...],
     *   equity: [...],
     *   profitRate: [...],
     *   drawdown: [...],
     *   cumulativeMaxDrawdown: [...],
     *   trades: 10
     * }
     */
    drawBacktestDivisionChart(divisionData) {
        const container = document.getElementById('holdings-division-chart');
        if (!container) {
            App.log('分仓图表容器未找到', 'error');
            return;
        }

        let chart = echarts.getInstanceByDom(container);
        if (!chart) {
            chart = echarts.init(container, 'dark');
        }

        const option = {
            backgroundColor: 'transparent',
            title: { 
                text: `${divisionData.divisionName} - 回测结果 (共${divisionData.trades}笔交易)`, 
                left: 'center', 
                textStyle: { color: '#fff', fontSize: 16 } 
            },
            tooltip: { 
                trigger: 'axis',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#4facfe'
            },
            legend: { 
                data: ['分仓权益', '收益率', '最大回撤'], 
                textStyle: { color: '#999' }, 
                top: '40px' 
            },
            grid: { left: '5%', right: '5%', top: '80px', bottom: '15%', containLabel: true },
            xAxis: { 
                type: 'category', 
                data: divisionData.dates,
                axisLine: { lineStyle: { color: '#555' } }, 
                axisLabel: { fontSize: 10, color: '#999', interval: 'auto' }
            },
            yAxis: [
                { 
                    type: 'value', 
                    position: 'left',
                    name: '权益(¥)',
                    nameTextStyle: { color: '#00f2fe' },
                    axisLine: { lineStyle: { color: '#00f2fe' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                },
                { 
                    type: 'value', 
                    position: 'right',
                    name: '收益率/回撤(%)',
                    nameTextStyle: { color: '#ffb74d' },
                    axisLine: { lineStyle: { color: '#ffb74d' } }, 
                    axisLabel: { fontSize: 10, color: '#999' },
                    splitLine: { lineStyle: { color: '#333' } }
                }
            ],
            series: [
                {
                    name: '分仓权益',
                    type: 'line',
                    yAxisIndex: 0,
                    data: divisionData.equity,
                    smooth: true,
                    lineStyle: { color: '#00f2fe', width: 2.5 },
                    areaStyle: { color: 'rgba(0, 242, 254, 0.1)' },
                    itemStyle: { color: '#00f2fe', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 5
                },
                {
                    name: '收益率',
                    type: 'line',
                    yAxisIndex: 1,
                    data: divisionData.profitRate,
                    smooth: true,
                    lineStyle: { color: '#ffb74d', width: 2.5 },
                    itemStyle: { color: '#ffb74d', borderColor: '#fff', borderWidth: 2 },
                    symbolSize: 5
                },
                {
                    name: '最大回撤',
                    type: 'line',
                    yAxisIndex: 1,
                    data: divisionData.cumulativeMaxDrawdown,
                    smooth: true,
                    lineStyle: { color: '#ff5252', width: 2, type: 'dashed' },
                    itemStyle: { color: '#ff5252' },
                    symbolSize: 4
                }
            ],
            dataZoom: [
                { 
                    type: 'slider', 
                    show: true, 
                    start: Math.max(0, 100 - Math.min(50, divisionData.dates.length * 2)), 
                    end: 100,
                    textStyle: { color: '#999' }
                },
                { 
                    type: 'inside', 
                    start: Math.max(0, 100 - Math.min(50, divisionData.dates.length * 2)), 
                    end: 100 
                }
            ]
        };

        chart.setOption(option);
        App.log(`分仓回测图表已绘制，共 ${divisionData.dates.length} 个交易日`, "success");
    }
    
};
