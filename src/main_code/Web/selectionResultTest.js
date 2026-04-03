/**
 * selectionResultTest.js - 选股结果功能测试用例
 * 
 * 使用方法：在浏览器控制台执行
 *   window.TestSelectionResult.runAll()
 * 
 * 或单独运行：
 *   window.TestSelectionResult.testSetResult()
 *   window.TestSelectionResult.testSort()
 *   window.TestSelectionResult.testSearch()
 *   window.TestSelectionResult.testDetailModal()
 *   window.TestSelectionResult.testKlineData()
 */

const TestSelectionResult = {

    /**
     * 生成模拟股票数据
     */
    generateMockStocks(count = 50) {
        const industries = ['银行', '电子', '医药', '食品饮料', '新能源', '地产', '计算机', '传媒', '化工', '机械'];
        const names = ['平安银行', '招商银行', '宁德时代', '比亚迪', '贵州茅台', '五粮液', '隆基绿能', '阳光电源', 
                       '恒瑞医药', '药明康德', '海康威视', '大华股份', '中芯国际', '京东方A', '迈瑞医疗',
                       '美的集团', '格力电器', '海尔智家', '万科A', '保利发展'];

        const stocks = [];
        for (let i = 0; i < count; i++) {
            const code = String(600000 + i).padStart(6, '0');
            const name = names[i % names.length] + (i >= names.length ? String(i) : '');
            const industry = industries[i % industries.length];

            stocks.push({
                code: code,
                name: name,
                score: +(Math.random() * 100).toFixed(2),
                industry: industry,
                market_cap: Math.random() * 500000000000,
                change_3d: +(Math.random() * 20 - 10).toFixed(2),
                change_5d: +(Math.random() * 20 - 10).toFixed(2),
                change_10d: +(Math.random() * 30 - 15).toFixed(2),
                change_20d: +(Math.random() * 40 - 20).toFixed(2),
                change_40d: +(Math.random() * 50 - 25).toFixed(2),
                change_60d: +(Math.random() * 60 - 30).toFixed(2),
                change_120d: +(Math.random() * 80 - 40).toFixed(2),
                change_240d: +(Math.random() * 100 - 50).toFixed(2),
                params: {
                    groups: [
                        {
                            name: "📊 基本信息",
                            items: [
                                { label: "股票代码", value: code, type: "text" },
                                { label: "上市日期", value: "2010-06-15", type: "text" },
                                { label: "所属行业", value: industry, type: "text" },
                            ]
                        },
                        {
                            name: "💰 估值指标",
                            items: [
                                { label: "市盈率(PE-TTM)", value: +(Math.random() * 50).toFixed(2), type: "number" },
                                { label: "市净率(PB)", value: +(Math.random() * 5).toFixed(2), type: "number" },
                                { label: "市销率(PS)", value: +(Math.random() * 10).toFixed(2), type: "number" },
                                { label: "市现率(PCF)", value: +(Math.random() * 20).toFixed(2), type: "number" },
                                { label: "股息率", value: +(Math.random() * 8).toFixed(2), type: "percent" },
                                { label: "总市值", value: Math.random() * 1000000000000, type: "market_cap" },
                                { label: "流通市值", value: Math.random() * 500000000000, type: "market_cap" },
                                { label: "EV/EBITDA", value: +(Math.random() * 20).toFixed(2), type: "number" },
                            ]
                        },
                        {
                            name: "📈 盈利能力",
                            items: [
                                { label: "ROE(加权)", value: +(Math.random() * 30).toFixed(2), type: "percent" },
                                { label: "ROA", value: +(Math.random() * 10).toFixed(2), type: "percent" },
                                { label: "ROIC", value: +(Math.random() * 15).toFixed(2), type: "percent" },
                                { label: "净利润率", value: +(Math.random() * 40).toFixed(2), type: "percent" },
                                { label: "毛利润率", value: +(Math.random() * 60).toFixed(2), type: "percent" },
                                { label: "营业利润率", value: +(Math.random() * 35).toFixed(2), type: "percent" },
                                { label: "每股收益(EPS)", value: +(Math.random() * 5).toFixed(2), type: "currency" },
                                { label: "每股净资产(BPS)", value: +(Math.random() * 20).toFixed(2), type: "currency" },
                            ]
                        },
                        {
                            name: "📊 成长性",
                            items: [
                                { label: "营收同比增长", value: +(Math.random() * 60 - 20).toFixed(2), type: "percent" },
                                { label: "净利润同比增长", value: +(Math.random() * 80 - 30).toFixed(2), type: "percent" },
                                { label: "净资产同比增长", value: +(Math.random() * 30).toFixed(2), type: "percent" },
                                { label: "近3年营收CAGR", value: +(Math.random() * 25).toFixed(2), type: "percent" },
                                { label: "近3年利润CAGR", value: +(Math.random() * 30).toFixed(2), type: "percent" },
                            ]
                        },
                        {
                            name: "🏦 财务健康",
                            items: [
                                { label: "资产负债率", value: +(Math.random() * 80).toFixed(2), type: "percent" },
                                { label: "流动比率", value: +(Math.random() * 3).toFixed(2), type: "number" },
                                { label: "速动比率", value: +(Math.random() * 2).toFixed(2), type: "number" },
                                { label: "利息覆盖倍数", value: +(Math.random() * 10).toFixed(2), type: "number" },
                                { label: "经营现金流/营收", value: +(Math.random() * 40).toFixed(2), type: "percent" },
                            ]
                        },
                        {
                            name: "📉 技术指标",
                            items: Array.from({ length: 20 }, (_, j) => ({
                                label: `技术指标_${j + 1}`,
                                value: +(Math.random() * 100 - 50).toFixed(2),
                                type: j % 3 === 0 ? "percent" : "number"
                            }))
                        },
                        {
                            name: "🔧 因子打分明细",
                            items: Array.from({ length: 15 }, (_, j) => ({
                                label: `因子_${j + 1}_得分`,
                                value: +(Math.random() * 100).toFixed(2),
                                type: "number"
                            }))
                        }
                    ]
                }
            });
        }
        return stocks;
    },

    /**
     * 生成模拟K线数据
     */
    generateMockKline(days = 240) {
        const kline = [];
        let basePrice = 15 + Math.random() * 30;
        const baseDate = new Date('2024-03-01');

        for (let i = 0; i < days; i++) {
            const date = new Date(baseDate);
            date.setDate(date.getDate() + i);
            // 跳过周末
            if (date.getDay() === 0 || date.getDay() === 6) continue;

            const change = (Math.random() - 0.48) * 2;
            const open = basePrice + (Math.random() - 0.5) * 0.5;
            const close = open + change;
            const high = Math.max(open, close) + Math.random() * 0.8;
            const low = Math.min(open, close) - Math.random() * 0.8;
            const volume = Math.round(50000 + Math.random() * 500000);

            basePrice = close;

            kline.push({
                date: date.toISOString().split('T')[0],
                open: +open.toFixed(2),
                close: +close.toFixed(2),
                high: +high.toFixed(2),
                low: +low.toFixed(2),
                volume: volume
            });
        }
        return kline;
    },

    // =====================
    // 测试用例
    // =====================

    /**
     * 测试1：设置选股结果数据
     */
    testSetResult() {
        console.log('🧪 [Test 1] 设置选股结果...');
        const stocks = this.generateMockStocks(80);

        // 模拟 AppManager 的消息处理
        if (window.AppManager && window.AppManager.selectionResultManager) {
            window.AppManager.selectionResultManager.setResultData(stocks);
            console.log(`✅ 设置了 ${stocks.length} 只股票`);
            console.log('💡 现在点击"查看结果"按钮查看列表');
        } else {
            console.error('❌ SelectionResultManager 未初始化');
        }
    },

    /**
     * 测试2：排序功能
     */
    testSort() {
        console.log('🧪 [Test 2] 测试排序...');
        if (!window.AppManager?.selectionResultManager) {
            console.error('❌ 请先运行 testSetResult()');
            return;
        }

        const mgr = window.AppManager.selectionResultManager;

        // 先确保有数据
        if (mgr.getResultData().length === 0) {
            this.testSetResult();
        }

        // 切换到结果视图
        mgr.showResultView();

        // 模拟点击排序按钮
        setTimeout(() => {
            const sortBtn = document.querySelector('.sr-sort-btn[data-sort="market_cap"]');
            if (sortBtn) {
                sortBtn.click();
                console.log('✅ 按流通市值降序排序');
                setTimeout(() => {
                    sortBtn.click();
                    console.log('✅ 按流通市值升序排序');
                }, 1000);
            }
        }, 500);
    },

    /**
     * 测试3：搜索过滤
     */
    testSearch() {
        console.log('🧪 [Test 3] 测试搜索...');
        if (!window.AppManager?.selectionResultManager) {
            console.error('❌ 请先运行 testSetResult()');
            return;
        }

        const mgr = window.AppManager.selectionResultManager;
        mgr.showResultView();

        setTimeout(() => {
            const input = document.getElementById('sr-filter-input');
            if (input) {
                input.value = '银行';
                input.dispatchEvent(new Event('input'));
                console.log('✅ 搜索 "银行" 完成');

                setTimeout(() => {
                    input.value = '';
                    input.dispatchEvent(new Event('input'));
                    console.log('✅ 清空搜索完成');
                }, 2000);
            }
        }, 500);
    },

    /**
     * 测试4：个股详情弹窗
     */
    testDetailModal() {
        console.log('🧪 [Test 4] 测试个股详情弹窗...');
        if (!window.AppManager?.selectionResultManager) {
            console.error('❌ 请先运行 testSetResult()');
            return;
        }

        const mgr = window.AppManager.selectionResultManager;
        const stocks = mgr.getResultData();
        if (stocks.length === 0) {
            this.testSetResult();
        }

        // 直接打开第一只股票的详情
        const stock = mgr.getResultData()[0];
        if (stock) {
            mgr.openDetailModal(stock);
            console.log(`✅ 打开详情: ${stock.code} ${stock.name}`);
            console.log('💡 参数分组可折叠，可搜索');
        }
    },

    /**
     * 测试5：K线数据渲染（直接注入）
     */
    testKlineData() {
        console.log('🧪 [Test 5] 测试K线图渲染...');
        if (!window.AppManager?.selectionResultManager) {
            console.error('❌ 请先运行 testSetResult()');
            return;
        }

        const mgr = window.AppManager.selectionResultManager;
        const stocks = mgr.getResultData();
        if (stocks.length === 0) {
            this.testSetResult();
        }

        const stock = mgr.getResultData()[0];
        if (!stock) return;

        // 打开弹窗
        mgr.openDetailModal(stock);

        // 模拟一次性K线数据返回
        setTimeout(() => {
            const kline = this.generateMockKline(240);
            mgr.receiveKlineData({
                code: stock.code,
                kline: kline
            });
            console.log(`✅ K线数据注入完成: ${kline.length} 根`);
        }, 500);
    },

    /**
     * 测试6：流式K线数据
     */
    async testKlineStream() {
        console.log('🧪 [Test 6] 测试流式K线数据...');
        if (!window.AppManager?.selectionResultManager) {
            console.error('❌ 请先运行 testSetResult()');
            return;
        }

        const mgr = window.AppManager.selectionResultManager;
        const stocks = mgr.getResultData();
        if (stocks.length === 0) {
            this.testSetResult();
        }

        const stock = mgr.getResultData()[0];
        if (!stock) return;

        mgr.openDetailModal(stock);

        // 模拟流式发送
        const allKline = this.generateMockKline(240);
        const chunkSize = 30;
        const total = allKline.length;
        let sent = 0;

        const sendChunk = () => {
            const end = Math.min(sent + chunkSize, total);
            const chunk = allKline.slice(sent, end);
            const progress = end / total;
            const isLast = end >= total;

            mgr.receiveKlineChunk({
                code: stock.code,
                chunk: chunk,
                progress: progress,
                is_last: isLast,
                total: total
            });

            sent = end;
            console.log(`📦 发送块: ${sent}/${total} (${(progress * 100).toFixed(0)}%)`);

            if (!isLast) {
                setTimeout(sendChunk, 200);
            } else {
                console.log('✅ 流式K线数据传输完成');
            }
        };

        setTimeout(sendChunk, 500);
    },

    /**
     * 测试7：返回配置视图
     */
    testBackToConfig() {
        console.log('🧪 [Test 7] 返回配置视图...');
        if (window.AppManager?.selectionResultManager) {
            window.AppManager.selectionResultManager.showConfigView();
            console.log('✅ 已返回配置视图');
        }
    },

    /**
     * 运行全部测试
     */
    async runAll() {
        console.log('🚀 ===== 开始选股结果功能测试 =====');

        this.testSetResult();
        await this._wait(1000);

        this.testSort();
        await this._wait(3000);

        this.testSearch();
        await this._wait(4000);

        this.testDetailModal();
        await this._wait(2000);

        this.testKlineData();
        await this._wait(2000);

        // 关闭弹窗
        if (window.AppManager?.selectionResultManager) {
            window.AppManager.selectionResultManager.closeDetailModal();
        }
        await this._wait(500);

        await this.testKlineStream();
        await this._wait(5000);

        this.testBackToConfig();

        console.log('🎉 ===== 全部测试完成 =====');
    },

    _wait(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// 暴露到全局
window.TestSelectionResult = TestSelectionResult;