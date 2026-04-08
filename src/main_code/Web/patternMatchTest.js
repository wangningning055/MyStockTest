/**
 * patternMatchTest.js - 模式匹配模块前端测试
 * 
 * 在浏览器控制台中使用：
 *   TestPatternMatch.testSetResult()         — 测试接收匹配结果
 *   TestPatternMatch.testExportedParams()    — 测试参数导出结果
 *   TestPatternMatch.testFullFlow()          — 完整流程测试
 * 
 * 
    * // 1. 切换到"模式匹配"页签

    // 2. 测试接收匹配结果（模拟服务器返回）
    TestPatternMatch.testSetResult()

    // 3. 点击页面上出现的"查看匹配结果"按钮

    // 4. 在结果列表中，点击任一行的"K线"按钮，
    //    K线图上会显示绿色"开始"线和红色"结束"线，
    //    以及橙色半透明的匹配区间标注

    // 5. 测试参数导出结果
    TestPatternMatch.testExportedParams()

    // 6. 点击"查看导出结果"按钮，查看参数弹窗

    // 7. 完整流程测试（自动执行步骤2-6）
    TestPatternMatch.testFullFlow()

    // 8. 测试导出JSON文件
    TestPatternMatch.testExportImport()
    // 然后可以用"导入结果JSON"按钮重新导入下载的文件
 * 
 */
window.TestPatternMatch = {

    /**
     * 生成模拟K线数据
     */
    generateKline(startDate, days) {
        const kline = [];
        let date = new Date(startDate);
        date.setDate(date.getDate() - 60); // 往前多生成60天
        let price = 10 + Math.random() * 20;

        for (let i = 0; i < days + 120; i++) {
            const dateStr = date.toISOString().slice(0, 10);
            const change = (Math.random() - 0.45) * 2; // 稍微偏正
            const open = price;
            const close = price * (1 + change / 100);
            const high = Math.max(open, close) * (1 + Math.random() * 0.02);
            const low = Math.min(open, close) * (1 - Math.random() * 0.02);
            const volume = Math.floor(Math.random() * 100000);
            const turn = +(Math.random() * 5).toFixed(2);

            kline.push({
                date: dateStr,
                open: +open.toFixed(2),
                close: +close.toFixed(2),
                high: +high.toFixed(2),
                low: +low.toFixed(2),
                volume: volume,
                turn: turn,
                change_Ratio: +change.toFixed(2)
            });

            price = close;
            date.setDate(date.getDate() + 1);
            // 跳过周末
            if (date.getDay() === 0) date.setDate(date.getDate() + 1);
            if (date.getDay() === 6) date.setDate(date.getDate() + 2);
        }
        return kline;
    },

    /**
     * 生成模拟匹配结果
     */
    generateMockResults(count = 15) {
        const stocks = [
            { code: '600000', name: '浦发银行' },
            { code: '000001', name: '平安银行' },
            { code: '600519', name: '贵州茅台' },
            { code: '000858', name: '五粮液' },
            { code: '002415', name: '海康威视' },
            { code: '600036', name: '招商银行' },
            { code: '601318', name: '中国平安' },
            { code: '000333', name: '美的集团' },
            { code: '002594', name: '比亚迪' },
            { code: '600276', name: '恒瑞医药' },
            { code: '603259', name: '药明康德' },
            { code: '002371', name: '北方华创' },
            { code: '300750', name: '宁德时代' },
            { code: '601012', name: '隆基绿能' },
            { code: '600309', name: '万华化学' }
        ];

        const matches = [];
        for (let i = 0; i < count; i++) {
            const stock = stocks[i % stocks.length];
            const startYear = 2023 + Math.floor(Math.random() * 2);
            const startMonth = Math.floor(Math.random() * 12) + 1;
            const startDay = Math.floor(Math.random() * 28) + 1;
            const matchStart = `${startYear}-${String(startMonth).padStart(2, '0')}-${String(startDay).padStart(2, '0')}`;

            const days = Math.floor(Math.random() * 25) + 5;
            const endDate = new Date(matchStart);
            endDate.setDate(endDate.getDate() + days);
            const matchEnd = endDate.toISOString().slice(0, 10);

            const changePct = +(50 + Math.random() * 100).toFixed(2);

            const kline = this.generateKline(matchStart, days);

            matches.push({
                code: stock.code,
                name: stock.name,
                match_start: matchStart,
                match_end: matchEnd,
                days: days,
                change_pct: changePct,
                kline: kline,
                params: {
                    groups: [
                        {
                            name: '价值指标',
                            items: [
                                { label: '市盈率(PE)', value: +(5 + Math.random() * 50).toFixed(2), type: 'number' },
                                { label: '市净率(PB)', value: +(0.5 + Math.random() * 5).toFixed(2), type: 'number' },
                                { label: '市销率(PS)', value: +(0.3 + Math.random() * 10).toFixed(2), type: 'number' },
                                { label: '市现率(PCF)', value: +(1 + Math.random() * 20).toFixed(2), type: 'number' },
                                { label: 'ROE(%)', value: +(5 + Math.random() * 25).toFixed(2), type: 'percent' },
                            ]
                        },
                        {
                            name: '成长指标',
                            items: [
                                { label: '净利润同比增长率(%)', value: +(-10 + Math.random() * 60).toFixed(2), type: 'percent' },
                                { label: '营收同比增长率(%)', value: +(-5 + Math.random() * 40).toFixed(2), type: 'percent' },
                                { label: '净资产同比增长(%)', value: +(Math.random() * 30).toFixed(2), type: 'percent' },
                            ]
                        },
                        {
                            name: '技术指标',
                            items: [
                                { label: '5日均线偏离度(%)', value: +(-5 + Math.random() * 10).toFixed(2), type: 'percent' },
                                { label: '20日均线偏离度(%)', value: +(-10 + Math.random() * 20).toFixed(2), type: 'percent' },
                                { label: '60日均线偏离度(%)', value: +(-15 + Math.random() * 30).toFixed(2), type: 'percent' },
                                { label: '换手率(%)', value: +(Math.random() * 10).toFixed(2), type: 'number' },
                                { label: '流通市值(亿)', value: +(10 + Math.random() * 5000).toFixed(2), type: 'number' },
                            ]
                        },
                        // ★ 后续可在此添加更多参数分组 ★
                    ]
                }
            });
        }
        return matches;
    },

    /**
     * 测试1：模拟接收匹配结果
     */
    testSetResult() {
        console.log('🧪 测试：设置模拟匹配结果');

        // 动态导入
        import('./patternMatchManager.js').then(module => {
            const mgr = module.PatternMatchManager;

            const mockData = {
                matches: this.generateMockResults(15)
            };

            mgr.setResultData(mockData);
            console.log('✅ 匹配结果已设置，请点击"查看匹配结果"按钮');
            console.log(`   共 ${mockData.matches.length} 条结果`);
            console.log('   可点击表格中的"K线"按钮查看详情');
        });
    },

    /**
     * 测试2：模拟接收参数导出结果
     */
    testExportedParams() {
        console.log('🧪 测试：模拟参数导出结果');

        import('./patternMatchManager.js').then(module => {
            const mgr = module.PatternMatchManager;

            const mockExportData = {
                export_type: 'mean',
                params: [
                    { name: '市盈率(PE)', value: 25.67 },
                    { name: '市净率(PB)', value: 2.34 },
                    { name: '市销率(PS)', value: 4.56 },
                    { name: '市现率(PCF)', value: 8.91 },
                    { name: 'ROE(%)', value: 15.23 },
                    { name: '净利润同比增长率(%)', value: 22.45 },
                    { name: '营收同比增长率(%)', value: 18.67 },
                    { name: '净资产同比增长(%)', value: 12.34 },
                    { name: '5日均线偏离度(%)', value: 2.15 },
                    { name: '20日均线偏离度(%)', value: 5.67 },
                    { name: '60日均线偏离度(%)', value: -3.21 },
                    { name: '换手率(%)', value: 3.45 },
                    { name: '流通市值(亿)', value: 856.78 },
                ]
            };

            mgr.setExportedParamsData(mockExportData);
            console.log('✅ 参数导出结果已设置，请点击"查看导出结果"按钮');
        });
    },

    /**
     * 测试3：完整流程测试
     */
    testFullFlow() {
        console.log('🧪 完整流程测试开始...');
        console.log('步骤1：切换到模式匹配页签');
        console.log('步骤2：模拟接收匹配结果');

        this.testSetResult();

        setTimeout(() => {
            console.log('步骤3：等待2秒后模拟参数导出结果');
            this.testExportedParams();
            console.log('✅ 完整流程测试完成！');
            console.log('   - 点击"查看匹配结果"查看结果列表');
            console.log('   - 点击表格中"K线"查看K线（含标注）');
            console.log('   - 点击"查看导出结果"查看参数导出');
            console.log('   - 点击"导出结果JSON"导出全部结果');
        }, 2000);
    },

    /**
     * 测试4：测试导入导出
     */
    testExportImport() {
        console.log('🧪 测试导出功能...');
        import('./patternMatchManager.js').then(module => {
            module.PatternMatchManager.exportResultJSON();
            console.log('✅ 请检查是否下载了JSON文件');
            console.log('   然后可以用"导入结果JSON"按钮重新导入');
        });
    }
};

console.log('📦 模式匹配测试模块已加载');
console.log('   TestPatternMatch.testSetResult()       - 测试匹配结果');
console.log('   TestPatternMatch.testExportedParams()   - 测试参数导出');
console.log('   TestPatternMatch.testFullFlow()         - 完整流程测试');
console.log('   TestPatternMatch.testExportImport()     - 测试导出');