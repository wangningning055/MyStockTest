let ws = null

export function SocketInit()
{
    ws = new WebSocket("ws://127.0.0.1:8000/ws")

    ws.onopen = () => {
        console.log("已连接后端 WebSocket");
    };

    ws.onmessage = (event) => {
        console.log("收到了后端消息")
        const data = JSON.parse(event.data);
        if(data.type == "ping")
        {
            console.log("收到后端:", data.msg);

        }
    };

    ws.onclose = () => {
        console.log("连接已关闭");
    };

    ws.onerror = (err) => {
        console.error("WebSocket 错误", err);
    };



}

export function sendMsg() 
{
    console.log("发送消息")
    let data = {type:"ping", msg : "你好 后端"}
    ws.send(JSON.stringify(data));
}

// UIManager.setConnectionStatus(true);设置连接状态
//UIManager.setLastUpdateTime(new Date().toLocaleString('zh-CN')); 设置上次更新日期
//UIManager.updateIndustryAnalysisTable(response.industryAnalysis);更新选股结果的行业状态


//// 股票查询相关事件
//document.getElementById('btn-query-stock')?.addEventListener('click', () => {
//    const code = UIManager.getStockQueryInput();
//    if (!code.trim()) {
//        UIManager.log('请输入股票代码或名称', 'warning');
//        return;
//    }
//    // 调用后端API查询
//    queryStockInfo(code);
//});

//document.getElementById('quick-query-input')?.addEventListener('input', (e) => {
//    const keyword = e.target.value;
//    if (keyword.length >= 1) {
//        // 调用后端API进行快速搜索
//        quickSearchStocks(keyword);
//    }
//});

//// 快速查询结果点击事件
//document.addEventListener('click', (e) => {
//    if (e.target.closest('.query-item')) {
//        const code = e.target.closest('.query-item').dataset.code;
//        document.getElementById('query-stock-input').value = code;
//        queryStockInfo(code);
//    }
//});

//// 辅助函数（需要根据后端API实现）
//async function queryStockInfo(code) {
//    // TODO: 调用后端API获取股票信息
//    // UIManager.setStockQueryResult(data);
//}

//async function quickSearchStocks(keyword) {
//    // TODO: 调用后端API进行快速搜索
//    // UIManager.setQuickQueryResults(results);
//}