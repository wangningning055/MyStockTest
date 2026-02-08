
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
     * 绘制持仓收益图表
     */
    drawPortfolioChart(portfolioData) {
        if (!ChartInstances.portfolioChart) {
            App.log('持仓图表未初始化', 'error');
            return;
        }

        const dates = portfolioData.map(item => item.date);
        const equityData = portfolioData.map(item => item.equity);
        const profitRateData = portfolioData.map(item => item.profitRate);

        const option = {
            backgroundColor: 'transparent',
            title: { text: '收益曲线', left: 'center', textStyle: { color: '#fff', fontSize: 16 } },
            tooltip: { trigger: 'axis' },
            legend: { data: ['账户权益', '收益率'], textStyle: { color: '#999' }, top: '40px' },
            xAxis: { type: 'category', data: dates, axisLine: { lineStyle: { color: '#555' } }, axisLabel: { fontSize: 10, color: '#999' } },
            yAxis: [
                { type: 'value', position: 'left', axisLine: { lineStyle: { color: '#4facfe' } }, axisLabel: { fontSize: 10, color: '#999' } },
                { type: 'value', position: 'right', axisLine: { lineStyle: { color: '#00f2fe' } }, axisLabel: { fontSize: 10, color: '#999' } }
            ],
            series: [
                { name: '账户权益', type: 'line', yAxisIndex: 0, data: equityData, smooth: true, lineStyle: { color: '#4facfe', width: 2.5 }, itemStyle: { color: '#4facfe', borderColor: '#fff', borderWidth: 2 }, symbolSize: 6 },
                { name: '收益率', type: 'line', yAxisIndex: 1, data: profitRateData, smooth: true, lineStyle: { color: '#00f2fe', width: 2.5 }, itemStyle: { color: '#00f2fe', borderColor: '#fff', borderWidth: 2 }, symbolSize: 6 }
            ],
            dataZoom: [
                { type: 'slider', show: true, start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), end: 100 },
                { type: 'inside', start: Math.max(0, 100 - Math.min(50, portfolioData.length * 2)), end: 100 }
            ]
        };

        ChartInstances.portfolioChart.setOption(option);
        App.log(`收益曲线图已绘制，共 ${portfolioData.length} 个交易日`, "success");
    }
};
