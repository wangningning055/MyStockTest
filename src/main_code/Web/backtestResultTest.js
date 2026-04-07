/**
 * backtestResultTest.js - 修复版测试用例
 * 
 * 改动：
 * 1. equity_curve 使用 equity 替代 nav
 * 2. 买卖标记使用 equity 替代 nav
 * 3. 新增 testImportCSV 测试
 */

(function () {
    'use strict';

    function generateTestEquityCurve(days, startDate, initialFund) {
        initialFund = initialFund || 100000;
        const dates = [];
        const equity = [];
        const returns = [];
        const drawdown = [];
        const positions = [];
        const buyMarkers = [];
        const sellMarkers = [];

        let currentEquity = initialFund;
        let maxEquity = initialFund;
        const d = new Date(startDate);

        for (let i = 0; i < days; i++) {
            while (d.getDay() === 0 || d.getDay() === 6) {
                d.setDate(d.getDate() + 1);
            }

            dates.push(d.toISOString().split('T')[0]);

            const change = (Math.random() - 0.48) * 0.03;
            currentEquity = Math.max(initialFund * 0.5, currentEquity * (1 + change));
            equity.push(parseFloat(currentEquity.toFixed(2)));

            maxEquity = Math.max(maxEquity, currentEquity);
            const ret = ((currentEquity - initialFund) / initialFund) * 100;
            returns.push(parseFloat(ret.toFixed(2)));

            const dd = maxEquity > 0 ? ((currentEquity - maxEquity) / maxEquity) * 100 : 0;
            drawdown.push(parseFloat(dd.toFixed(2)));

            const pos = [];
            if (i % 5 < 3 && i > 2) {
                pos.push({ code: '600000', name: '浦发银行', shares: 1000 });
            }
            positions.push(pos);

            d.setDate(d.getDate() + 1);
        }

        return { dates, equity, returns, drawdown, positions, buy_markers: buyMarkers, sell_markers: sellMarkers };
    }

    function generateTestKlineData(startDate, days) {
        const dates = [];
        const ohlc = [];
        const volumes = [];
        let price = 10 + Math.random() * 20;
        const d = new Date(startDate);

        for (let i = 0; i < days; i++) {
            while (d.getDay() === 0 || d.getDay() === 6) {
                d.setDate(d.getDate() + 1);
            }
            dates.push(d.toISOString().split('T')[0]);

            const open = price;
            const change = (Math.random() - 0.48) * price * 0.05;
            const close = parseFloat((open + change).toFixed(2));
            const high = parseFloat((Math.max(open, close) + Math.random() * price * 0.02).toFixed(2));
            const low = parseFloat((Math.min(open, close) - Math.random() * price * 0.02).toFixed(2));

            // ECharts格式: [open, close, low, high]
            ohlc.push([open.toFixed(2) * 1, close, low, high]);
            volumes.push(Math.floor(30000 + Math.random() * 80000));
            price = close;

            d.setDate(d.getDate() + 1);
        }
        return { dates, ohlc, volumes };
    }

    function generateTestTrades(count, equityCurveDates, equityCurveEquity) {
        const stockPool = [
            { code: '600000', name: '浦发银行' },
            { code: '000001', name: '平安银行' },
            { code: '600036', name: '招商银行' },
            { code: '601318', name: '中国平安' },
            { code: '000651', name: '格力电器' },
            { code: '600519', name: '贵州茅台' },
            { code: '000858', name: '五粮液' },
            { code: '002415', name: '海康威视' },
            { code: '600887', name: '伊利股份' },
            { code: '601888', name: '中国中免' },
        ];

        const trades = [];
        for (let i = 0; i < count; i++) {
            const stock = stockPool[i % stockPool.length];
            let buyIdx = Math.floor(Math.random() * (equityCurveDates.length - 30)) + 5;
            const holdDays = Math.floor(Math.random() * 25) + 3;
            const sellIdx = Math.min(buyIdx + holdDays, equityCurveDates.length - 1);

            const buyPrice = parseFloat((8 + Math.random() * 50).toFixed(2));
            const profitPct = parseFloat(((Math.random() - 0.4) * 30).toFixed(2));
            const sellPrice = parseFloat((buyPrice * (1 + profitPct / 100)).toFixed(2));
            const profitMoney = parseFloat(((sellPrice - buyPrice) * 1000).toFixed(2));

            const buyDate = equityCurveDates[buyIdx] || '2024-03-01';
            const sellDate = equityCurveDates[sellIdx] || '2024-04-01';

            const klineStart = new Date(buyDate);
            klineStart.setDate(klineStart.getDate() - 20);
            const klineData = generateTestKlineData(klineStart.toISOString().split('T')[0], holdDays + 40);

            trades.push({
                trade_id: `t${String(i + 1).padStart(3, '0')}`,
                buy_date: buyDate,
                sell_date: sellDate,
                hold_days: holdDays,
                code: stock.code,
                name: stock.name,
                buy_price: buyPrice,
                sell_price: sellPrice,
                profit_pct: profitPct,
                profit_money: profitMoney,
                kline_data: klineData
            });
        }
        return trades;
    }

    function generateFullTestData() {
        const initFund = 100000;
        const totalEquity = generateTestEquityCurve(120, '2024-01-02', initFund);
        const totalTrades = generateTestTrades(15, totalEquity.dates, totalEquity.equity);

        // 补充买卖标记
        totalTrades.forEach(t => {
            const buyIdx = totalEquity.dates.indexOf(t.buy_date);
            if (buyIdx >= 0) {
                totalEquity.buy_markers.push({
                    date: t.buy_date, code: t.code, name: t.name,
                    price: t.buy_price, equity: totalEquity.equity[buyIdx]
                });
            }
            const sellIdx = totalEquity.dates.indexOf(t.sell_date);
            if (sellIdx >= 0) {
                totalEquity.sell_markers.push({
                    date: t.sell_date, code: t.code, name: t.name,
                    price: t.sell_price, equity: totalEquity.equity[sellIdx]
                });
            }
        });

        const wins = totalTrades.filter(t => t.profit_pct > 0).length;
        const finalFund = totalEquity.equity[totalEquity.equity.length - 1] || initFund;
        const totalReturn = ((finalFund - initFund) / initFund) * 100;

        // 分仓1
        const div1Equity = generateTestEquityCurve(120, '2024-01-02', 50000);
        const div1Trades = generateTestTrades(8, div1Equity.dates, div1Equity.equity);
        div1Trades.forEach(t => {
            const idx = div1Equity.dates.indexOf(t.buy_date);
            if (idx >= 0) div1Equity.buy_markers.push({
                date: t.buy_date, code: t.code, name: t.name, price: t.buy_price, equity: div1Equity.equity[idx]
            });
            const si = div1Equity.dates.indexOf(t.sell_date);
            if (si >= 0) div1Equity.sell_markers.push({
                date: t.sell_date, code: t.code, name: t.name, price: t.sell_price, equity: div1Equity.equity[si]
            });
        });

        // 分仓2
        const div2Equity = generateTestEquityCurve(120, '2024-01-02', 50000);
        const div2Trades = generateTestTrades(7, div2Equity.dates, div2Equity.equity);
        div2Trades.forEach(t => {
            const idx = div2Equity.dates.indexOf(t.buy_date);
            if (idx >= 0) div2Equity.buy_markers.push({
                date: t.buy_date, code: t.code, name: t.name, price: t.buy_price, equity: div2Equity.equity[idx]
            });
            const si = div2Equity.dates.indexOf(t.sell_date);
            if (si >= 0) div2Equity.sell_markers.push({
                date: t.sell_date, code: t.code, name: t.name, price: t.sell_price, equity: div2Equity.equity[si]
            });
        });

        return {
            total: {
                division_name: '总仓',
                summary: {
                    initial_fund: initFund,
                    final_fund: parseFloat(finalFund.toFixed(2)),
                    total_return: parseFloat(totalReturn.toFixed(2)),
                    win_rate: parseFloat(((wins / totalTrades.length) * 100).toFixed(1)),
                    annual_return: parseFloat((totalReturn * 2.5).toFixed(2)),
                    annual_volatility: parseFloat((15 + Math.random() * 10).toFixed(2)),
                    monthly_return: parseFloat((totalReturn / 4).toFixed(2)),
                    monthly_volatility: parseFloat((4 + Math.random() * 3).toFixed(2)),
                    max_drawdown: parseFloat(Math.min(...totalEquity.drawdown).toFixed(2)),
                    sharpe_ratio: parseFloat((0.5 + Math.random() * 1.5).toFixed(2)),
                },
                equity_curve: totalEquity,
                trades: totalTrades
            },
            divisions: {
                'div-001-test': {
                    division_name: '价值分仓',
                    summary: {
                        initial_fund: 50000,
                        final_fund: parseFloat((div1Equity.equity[div1Equity.equity.length - 1] || 50000).toFixed(2)),
                        total_return: parseFloat((((div1Equity.equity[div1Equity.equity.length - 1] || 50000) - 50000) / 50000 * 100).toFixed(2)),
                        win_rate: parseFloat((div1Trades.filter(t => t.profit_pct > 0).length / Math.max(1, div1Trades.length) * 100).toFixed(1)),
                        annual_return: 15.2, annual_volatility: 18.5,
                        monthly_return: 1.2, monthly_volatility: 5.1,
                        max_drawdown: parseFloat(Math.min(...div1Equity.drawdown).toFixed(2)),
                        sharpe_ratio: 0.82
                    },
                    equity_curve: div1Equity,
                    trades: div1Trades
                },
                'div-002-test': {
                    division_name: '成长分仓',
                    summary: {
                        initial_fund: 50000,
                        final_fund: parseFloat((div2Equity.equity[div2Equity.equity.length - 1] || 50000).toFixed(2)),
                        total_return: parseFloat((((div2Equity.equity[div2Equity.equity.length - 1] || 50000) - 50000) / 50000 * 100).toFixed(2)),
                        win_rate: 57.1, annual_return: 12.8, annual_volatility: 20.5,
                        monthly_return: 1.1, monthly_volatility: 5.8,
                        max_drawdown: parseFloat(Math.min(...div2Equity.drawdown).toFixed(2)),
                        sharpe_ratio: 0.62
                    },
                    equity_curve: div2Equity,
                    trades: div2Trades
                }
            }
        };
    }

    // ============================
    // 测试用例
    // ============================
    const TestBacktestResult = {

        _testData: null,

        _getTestData() {
            if (!this._testData) {
                this._testData = generateFullTestData();
            }
            return this._testData;
        },

        _getManager() {
            if (window.AppManager && window.AppManager.backtestResultManager) {
                return window.AppManager.backtestResultManager;
            }
            console.error('❌ BacktestResultManager 未找到');
            return null;
        },

        testSetResult() {
            console.log('🧪 测试1: 设置回测结果数据');
            const mgr = this._getManager();
            if (!mgr) return false;

            const data = this._getTestData();
            mgr.setResultData(data);

            const viewBtn = document.getElementById('btn-view-backtest-result');
            console.assert(viewBtn && viewBtn.style.display !== 'none', '查看结果按钮应显示');

            const selector = document.getElementById('bt-result-division-select');
            console.assert(selector && selector.options.length === 3, `选项应3个，实际${selector?.options.length}`);

            mgr.showResultView();

            setTimeout(() => {
                const nameEl = document.getElementById('bt-stat-name');
                console.assert(nameEl?.textContent === '总仓', `应为"总仓"，实际"${nameEl?.textContent}"`);

                const initEl = document.getElementById('bt-stat-init-fund');
                console.assert(initEl?.textContent.includes('100,000'), `初始仓价应包含100,000: ${initEl?.textContent}`);

                // 检查图表是否渲染
                const chart = document.getElementById('bt-equity-chart');
                const instance = chart ? echarts.getInstanceByDom(chart) : null;
                console.assert(instance, '收益率图表应已初始化');

                console.log('✅ testSetResult 通过');
            }, 800);
            return true;
        },

        testDivisionSwitch() {
            console.log('🧪 测试2: 仓位切换');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) this.testSetResult();

            const selector = document.getElementById('bt-result-division-select');

            selector.value = 'div-001-test';
            selector.dispatchEvent(new Event('change'));

            setTimeout(() => {
                const nameEl = document.getElementById('bt-stat-name');
                console.assert(nameEl?.textContent === '价值分仓', `应为"价值分仓": ${nameEl?.textContent}`);

                const initEl = document.getElementById('bt-stat-init-fund');
                console.assert(initEl?.textContent.includes('50,000'), `分仓初始应50000: ${initEl?.textContent}`);

                selector.value = '__total__';
                selector.dispatchEvent(new Event('change'));

                setTimeout(() => {
                    console.assert(document.getElementById('bt-stat-name')?.textContent === '总仓');
                    console.log('✅ testDivisionSwitch 通过');
                }, 300);
            }, 300);
            return true;
        },

        testTradeSort() {
            console.log('🧪 测试3: 成交排序');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) this.testSetResult();

            setTimeout(() => {
                const th = document.querySelector('#bt-trades-table th[data-sort="profit_pct"]');
                if (th) {
                    th.click();
                    setTimeout(() => {
                        console.assert(th.classList.contains('sort-desc'), '应有sort-desc类');
                        const rows = document.querySelectorAll('#bt-trades-tbody tr');
                        console.log(`  排序后行数: ${rows.length}`);

                        th.click();
                        setTimeout(() => {
                            console.assert(th.classList.contains('sort-asc'), '应有sort-asc类');
                            console.log('✅ testTradeSort 通过');
                        }, 200);
                    }, 200);
                }
            }, 500);
            return true;
        },

        testTradeSearch() {
            console.log('🧪 测试4: 成交搜索');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) this.testSetResult();

            const searchInput = document.getElementById('bt-trades-search-input');
            searchInput.value = '银行';
            searchInput.dispatchEvent(new Event('input'));

            setTimeout(() => {
                const rows = document.querySelectorAll('#bt-trades-tbody tr');
                console.log(`  搜索"银行"后行数: ${rows.length}`);

                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
                setTimeout(() => {
                    console.log('✅ testTradeSearch 通过');
                }, 200);
            }, 300);
            return true;
        },

        testKlineModal() {
            console.log('🧪 测试5: K线弹窗');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) this.testSetResult();

            // 清空搜索确保有数据
            const si = document.getElementById('bt-trades-search-input');
            if (si) { si.value = ''; si.dispatchEvent(new Event('input')); }

            setTimeout(() => {
                const btn = document.querySelector('#bt-trades-tbody .td-view-btn');
                if (!btn) {
                    console.warn('⚠️ 无K线按钮');
                    return;
                }
                btn.click();

                setTimeout(() => {
                    const modal = document.getElementById('bt-kline-modal');
                    console.assert(modal?.classList.contains('active'), '弹窗应打开');

                    // 验证K线图表存在
                    const kChart = document.getElementById('bt-kline-chart-container');
                    const kInstance = kChart ? echarts.getInstanceByDom(kChart) : null;
                    console.assert(kInstance, 'K线图表应存在');

                    // 验证Y轴有合理范围
                    if (kInstance) {
                        const opt = kInstance.getOption();
                        if (opt.yAxis && opt.yAxis[0]) {
                            const yMin = opt.yAxis[0].min;
                            const yMax = opt.yAxis[0].max;
                            console.log(`  K线Y轴范围: ${yMin} ~ ${yMax}`);
                            console.assert(yMin > 0 && yMax > yMin, `Y轴范围应合理: ${yMin}~${yMax}`);
                        }
                    }

                    // 检查买卖标记
                    const codeEl = document.getElementById('bt-kline-code');
                    console.assert(codeEl?.textContent !== '--', `代码不应为空: ${codeEl?.textContent}`);

                    setTimeout(() => {
                        document.getElementById('bt-kline-close-btn')?.click();
                        setTimeout(() => {
                            console.assert(!modal?.classList.contains('active'), '弹窗应关闭');
                            console.log('✅ testKlineModal 通过');
                        }, 300);
                    }, 800);
                }, 600);
            }, 500);
            return true;
        },

        testExport() {
            console.log('🧪 测试6: CSV导出');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) this.testSetResult();

            let downloaded = false;
            const origCreate = URL.createObjectURL;
            URL.createObjectURL = (blob) => {
                downloaded = true;
                console.log(`  CSV大小: ${blob.size} bytes`);
                return 'blob:test';
            };

            mgr.exportBacktestJSON();
            URL.createObjectURL = origCreate;

            console.assert(downloaded, '应触发CSV下载');
            console.log('✅ testExport 通过');
            return true;
        },

        testImportCSV() {
            console.log('🧪 测试7: CSV导入');
            const mgr = this._getManager();
            if (!mgr) return false;

            // 模拟CSV文本
            const csvText = `序号,买入日期,卖出日期,持仓天数,股票代码,股票名称,买入价,卖出价,盈利百分比,盈利金额
1,2024-01-15,2024-02-20,36,600000,浦发银行,10.50,11.20,6.67,700.00
2,2024-02-01,2024-03-10,38,000001,平安银行,12.30,11.80,-4.07,-400.00
3,2024-03-01,2024-04-15,45,600036,招商银行,35.20,38.50,9.38,990.00`;


            // 测试rebuildEquityCurveFromTrades
            const trades = parsed.map((row, idx) => ({
                trade_id: `import-${idx}`,
                buy_date: row['买入日期'],
                sell_date: row['卖出日期'],
                hold_days: parseInt(row['持仓天数']) || 0,
                code: row['股票代码'],
                name: row['股票名称'],
                buy_price: parseFloat(row['买入价']) || 0,
                sell_price: parseFloat(row['卖出价']) || 0,
                profit_pct: parseFloat(row['盈利百分比']) || 0,
                profit_money: parseFloat(row['盈利金额']) || 0,
                kline_data: null
            }));

            const curve = mgr.rebuildEquityCurveFromTrades(trades, 100000);
            console.assert(curve.dates.length > 0, `重建日期应>0: ${curve.dates.length}`);
            console.assert(curve.equity.length === curve.dates.length, 'equity长度应等于dates长度');
            console.assert(curve.equity[0] === 100000, `第一天应为100000: ${curve.equity[0]}`);
            console.log(`  重建曲线: ${curve.dates.length}天, 最终仓价: ¥${curve.equity[curve.equity.length - 1]}`);

            // 测试calculateSummaryFromTrades
            const summary = mgr.calculateSummaryFromTrades(trades, curve);
            console.assert(summary.initial_fund === 100000, '初始资金应100000');
            console.assert(typeof summary.total_return === 'number', '总收益率应为number');
            console.assert(typeof summary.win_rate === 'number', '胜率应为number');
            console.log(`  Summary: 收益率=${summary.total_return}%, 胜率=${summary.win_rate}%`);

            // 测试完整导入流程（设置数据并渲染）
            const importedData = {
                total: {
                    division_name: '导入测试',
                    summary: summary,
                    equity_curve: curve,
                    trades: trades
                },
                divisions: {}
            };

            mgr.setResultData(importedData);
            mgr.showResultView();

            setTimeout(() => {
                const nameEl = document.getElementById('bt-stat-name');
                console.assert(nameEl?.textContent === '总仓', '导入后仓位名应为总仓');

                const countEl = document.getElementById('bt-stat-trade-count');
                console.assert(countEl?.textContent === '3' || countEl?.textContent === 3, `成交笔数应为3: ${countEl?.textContent}`);

                console.log('✅ testImportCSV 通过');
            }, 500);

            return true;
        },

        testEmptyData() {
            console.log('🧪 测试8: 空数据');
            const mgr = this._getManager();
            if (!mgr) return false;

            mgr.setResultData({
                total: {
                    division_name: '总仓',
                    summary: {
                        initial_fund: 100000, final_fund: 100000,
                        total_return: 0, win_rate: 0,
                        annual_return: 0, annual_volatility: 0,
                        monthly_return: 0, monthly_volatility: 0,
                        max_drawdown: 0, sharpe_ratio: 0
                    },
                    equity_curve: {
                        dates: ['2024-01-02'],
                        equity: [100000],
                        returns: [0],
                        drawdown: [0],
                        positions: [[]],
                        buy_markers: [],
                        sell_markers: []
                    },
                    trades: []
                },
                divisions: {}
            });
            mgr.showResultView();

            setTimeout(() => {
                console.assert(document.getElementById('bt-stat-trade-count')?.textContent == '0');
                console.assert(document.getElementById('bt-trades-tbody')?.innerHTML.includes('暂无'));
                console.log('✅ testEmptyData 通过');
                this._testData = null;
            }, 500);
            return true;
        },

        testEdgeCases() {
            console.log('🧪 测试9: 边界情况（无K线数据）');
            const mgr = this._getManager();
            if (!mgr) return false;

            mgr.setResultData({
                total: {
                    division_name: '总仓',
                    summary: {
                        initial_fund: 100000, final_fund: 105000,
                        total_return: 5.0, win_rate: 50,
                        annual_return: 10, annual_volatility: 15,
                        monthly_return: 0.8, monthly_volatility: 4,
                        max_drawdown: -3, sharpe_ratio: 0.67
                    },
                    equity_curve: {
                        dates: ['2024-01-02', '2024-01-03'],
                        equity: [100000, 105000],
                        returns: [0, 5],
                        drawdown: [0, 0],
                        positions: [[], []],
                        buy_markers: [],
                        sell_markers: []
                    },
                    trades: [
                        {
                            trade_id: 'e001', buy_date: '2024-01-02', sell_date: '2024-01-03',
                            hold_days: 1, code: '999999', name: '无K线股',
                            buy_price: 10, sell_price: 10.5, profit_pct: 5, profit_money: 500,
                            kline_data: null
                        },
                        {
                            trade_id: 'e002', buy_date: '2024-01-02', sell_date: '2024-01-03',
                            hold_days: 1, code: '888888', name: '空K线股',
                            buy_price: 100, sell_price: 50, profit_pct: -50, profit_money: -50000,
                            kline_data: { dates: [], ohlc: [], volumes: [] }
                        }
                    ]
                },
                divisions: {}
            });
            mgr.showResultView();

            setTimeout(() => {
                const btn = document.querySelector('#bt-trades-tbody .td-view-btn');
                if (btn) {
                    btn.click();
                    setTimeout(() => {
                        const modal = document.getElementById('bt-kline-modal');
                        console.assert(modal?.classList.contains('active'), '无K线弹窗也应打开');
                        document.getElementById('bt-kline-close-btn')?.click();
                        console.log('✅ testEdgeCases 通过');
                        this._testData = null;
                    }, 500);
                } else {
                    console.log('✅ testEdgeCases 通过');
                }
            }, 500);
            return true;
        },

        testViewSwitch() {
            console.log('🧪 测试10: 视图切换');
            const mgr = this._getManager();
            if (!mgr) return false;
            if (!this._testData) {
                this._testData = generateFullTestData();
                mgr.setResultData(this._testData);
            }

            mgr.showResultView();
            setTimeout(() => {
                const rv = document.getElementById('backtest-result-view');
                const cv = document.getElementById('backtest-config-view');
                console.assert(rv?.classList.contains('active'), '结果视图应激活');
                console.assert(!cv?.classList.contains('active'), '配置视图应隐藏');

                mgr.showConfigView();
                setTimeout(() => {
                    console.assert(!rv?.classList.contains('active'));
                    console.assert(cv?.classList.contains('active'));
                    console.log('✅ testViewSwitch 通过');
                }, 200);
            }, 300);
            return true;
        },

        async runAll() {
            console.log('🚀 ===== 开始运行所有回测结果测试 =====\n');

            const tests = [
                { name: 'testSetResult', delay: 1500 },
                { name: 'testDivisionSwitch', delay: 1500 },
                { name: 'testTradeSort', delay: 1200 },
                { name: 'testTradeSearch', delay: 1000 },
                { name: 'testKlineModal', delay: 3000 },
                { name: 'testExport', delay: 500 },
                { name: 'testImportCSV', delay: 1500 },
                { name: 'testViewSwitch', delay: 1200 },
                { name: 'testEmptyData', delay: 1200 },
                { name: 'testEdgeCases', delay: 2000 },
            ];

            let delay = 0;
            for (const t of tests) {
                setTimeout(() => {
                    console.log(`\n--- ${t.name} ---`);
                    this[t.name]();
                }, delay);
                delay += t.delay;
            }

            setTimeout(() => {
                console.log('\n🏁 ===== 全部测试执行完毕 =====');
            }, delay + 500);
        }
    };

    window.TestBacktestResult = TestBacktestResult;
    console.log('📦 回测测试已加载，执行 window.TestBacktestResult.runAll()');
})();