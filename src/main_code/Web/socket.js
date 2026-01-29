/**
 * socket.js - WebSocket连接管理模块
 * 
 * 功能：
 * 1. 建立和管理WebSocket连接
 * 2. 处理消息的发送和接收
 * 3. 自动重连机制
 * 4. 消息队列（离线缓存）
 * 
 * 使用示例：
 * import * as Socket from "./socket.js";
 * Socket.SocketInit();
 * Socket.sendMessage({ type: "ping", msg: "hello" });
 */

let ws = null;
export let isConnecting = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3秒
const MESSAGE_QUEUE = []; // 离线消息队列
let manager = null;

export const MessageType = Object.freeze({
    CS_UPDATE_DATA: "cs_update_data",              // 客户端请求拉取数据
    CS_SELECT_STOCKS: "cs_select_stocks",          // 客户端请求执行股票筛选
    CS_BACK_TEST: "cs_back_test",                  // 客户端请求执行回测
    CS_DIAGNOSE: "cs_diagnose",                    // 客户端请求出仓判断
    CS_SEND_LAST_UPDATE_DATA: "sc_last_update_data",// 服务器发送上次更新日期
    LOG : "log"
});

export function SetManager(_manager)
{
    manager = _manager;
}
/**
 * 全局消息处理器
 * 可以在外部注册多个处理器
 */
let messageHandlers = [];
/**
 * WebSocket初始化
 * 建立连接并设置事件处理器
 */
export function SocketInit() {
    if (isConnecting || (ws && ws.readyState === WebSocket.OPEN)) {
        console.log("🔄 WebSocket已连接或正在连接中");
        return;
    }

    isConnecting = true;
    
    try {
        ws = new WebSocket("ws://127.0.0.1:8000/ws");

        ws.onopen = () => {
            console.log("✅ 已连接后端 WebSocket");
            isConnecting = true;
            reconnectAttempts = 0;
            manager.ui.setConnectionStatus(true);
            
            // 发送所有缓存的消息
            flushMessageQueue();
        };

        ws.onmessage = (event) => {
            handleWebSocketMessage(event.data);
        };

        ws.onclose = () => {
            console.log("🔌 连接已关闭");
            isConnecting = false;
            manager.ui.setConnectionStatus(false);
            attemptReconnect();
        };

        ws.onerror = (err) => {
            console.error("❌ WebSocket 错误", err);
            isConnecting = false;
            manager.ui.setConnectionStatus(false);
        };

    } catch (error) {
        console.error("❌ WebSocket初始化失败:", error);
        manager.ui.setConnectionStatus(false);
        isConnecting = false;
        attemptReconnect();
    }
}

function HandleMessage(data){
    console.log("📨 收到后端消息:", data.type);
    if(data.type = MessageType.CS_UPDATE_DATA)
    {
        manager.app.log(data.msg)
    }
    else if(data.type == MessageType.CS_SELECT_STOCKS){}
    else if(data.type == MessageType.CS_BACK_TEST){}
    else if(data.type == MessageType.CS_DIAGNOSE){}
    else if(data.type == MessageType.CS_SEND_LAST_UPDATE_DATA){}
    else if(data.type == MessageType.LOG)
    {
        manager.app.log(data.msg)
    }
}


/**
 * 处理接收到的WebSocket消息
 * @param {string} data - 消息数据（JSON字符串）
 */
function handleWebSocketMessage(data) {
    try {
        const message = JSON.parse(data);

        HandleMessage(message)



        // 触发所有注册的处理器
        messageHandlers.forEach(handler => {
            try {
                handler(message);
            } catch (error) {
                console.error("消息处理器执行出错:", error);
            }
        });

    } catch (error) {
        console.error("❌ 消息解析失败:", error);
    }
}

/**
 * 注册消息处理器
 * @param {function} handler - 处理函数(message) => void
 */
export function onMessage(handler) {
    if (typeof handler === 'function') {
        messageHandlers.push(handler);
        console.log("✅ 消息处理器已注册");
    }
}

/**
 * 移除消息处理器
 * @param {function} handler - 要移除的处理函数
 */
export function offMessage(handler) {
    const index = messageHandlers.indexOf(handler);
    if (index > -1) {
        messageHandlers.splice(index, 1);
        console.log("✅ 消息处理器已移除");
    }
}

///**
// * 发送消息到后端（兼容旧API）
// * 仅发送简单的ping消息
// */
//export function sendMsg() {
//    console.log("📤 发送测试消息");
//    const data = { 
//        type: "ping", 
//        msg: "你好 后端",
//        timestamp: new Date().toISOString()
//    };
//    sendMessage(data);
//}

/**
 * 发送消息到后端（新API）
 * @param {object} message - 消息对象
 * @returns {boolean} 是否发送成功
 */
export function sendMessage(message) {
    if (!message || typeof message !== 'object') {
        console.error("❌ 消息格式无效");
        return false;
    }

    // 确保消息有时间戳
    if (!message.timestamp) {
        message.timestamp = new Date().toISOString();
    }

    if (!ws) {
        console.warn("⚠️ WebSocket未初始化，消息已加入队列");
        MESSAGE_QUEUE.push(message);
        return false;
    }

    if (ws.readyState === WebSocket.OPEN) {
        try {
            const jsonData = JSON.stringify(message);
            ws.send(jsonData);
            console.log("✅ 消息已发送:", message);
            return true;
        } catch (error) {
            console.error("❌ 消息发送失败:", error);
            MESSAGE_QUEUE.push(message);
            return false;
        }
    } else {
        console.warn("⚠️ WebSocket未就绪，消息已加入队列");
        MESSAGE_QUEUE.push(message);
        return false;
    }
}

/**
 * 发送指定类型的消息
 * @param {string} type - 消息类型
 * @param {object} payload - 消息负载
 * @returns {boolean}
 */
export function sendMessageByType(type, payload = {}) {
    const message = {
        type: type,
        payload: payload
    };
    return sendMessage(message);
}

/**
 * 刷新消息队列
 * 当连接恢复时，发送所有缓存的消息
 */
function flushMessageQueue() {
    while (MESSAGE_QUEUE.length > 0) {
        const message = MESSAGE_QUEUE.shift();
        sendMessage(message);
    }
}

/**
 * 尝试重新连接
 */
function attemptReconnect() {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.error("❌ 达到最大重连次数，放弃重连");
        return;
    }

    reconnectAttempts++;
    console.log(`🔄 将在${RECONNECT_DELAY}ms后进行第${reconnectAttempts}次重连...`);

    setTimeout(() => {
        SocketInit();
    }, RECONNECT_DELAY);
}

/**
 * 获取WebSocket连接状态
 * @returns {string} - 连接状态
 */
export function getConnectionStatus() {
    if (!ws) return "未初始化";
    
    switch (ws.readyState) {
        case WebSocket.CONNECTING:
            return "连接中";
        case WebSocket.OPEN:
            return "已连接";
        case WebSocket.CLOSING:
            return "关闭中";
        case WebSocket.CLOSED:
            return "已断开";
        default:
            return "未知";
    }
}

/**
 * 检查连接是否打开
 * @returns {boolean}
 */
export function isConnected() {
    return ws && ws.readyState === WebSocket.OPEN;
}

/**
 * 获取消息队列长度
 * @returns {number}
 */
export function getQueueLength() {
    return MESSAGE_QUEUE.length;
}

/**
 * 手动断开连接
 */
export function disconnect() {
    if (ws) {
        ws.close();
        ws = null;
        isConnecting = false;
        reconnectAttempts = 0;
        console.log("🔌 已主动断开连接");
    }
}

/**
 * 清空消息队列
 */
export function clearQueue() {
    MESSAGE_QUEUE.length = 0;
    console.log("🗑️ 消息队列已清空");
}

/**
 * 获取调试信息
 */
export function debug() {
    console.log("=== WebSocket 调试信息 ===");
    console.log("连接状态:", getConnectionStatus());
    console.log("是否已连接:", isConnected());
    console.log("消息队列长度:", getQueueLength());
    console.log("重连次数:", reconnectAttempts);
    console.log("消息处理器数量:", messageHandlers.length);
}

// 导出调试命令对象
export const Debug = {
    status: () => console.log("连接状态:", getConnectionStatus()),
    queue: () => console.log("消息队列:", MESSAGE_QUEUE),
    handlers: () => console.log("处理器数量:", messageHandlers.length),
    all: debug
};

/**
 * 示例：如何使用这个模块
 * 
 * import * as Socket from "./socket.js";
 * 
 * // 1. 初始化连接
 * Socket.SocketInit();
 * 
 * // 2. 注册消息处理器
 * Socket.onMessage((message) => {
 *     console.log("收到消息:", message);
 *     if (message.type === "ping") {
 *         console.log("后端回应:", message.msg);
 *     }
 * });
 * 
 * // 3. 发送消息
 * Socket.sendMessage({
 *     type: "cs_select_stocks",
 *     payload: {
 *         factors: [...],
 *         threshold: 0.5
 *     }
 * });
 * 
 * // 或使用便捷方法
 * Socket.sendMessageByType("cs_update_data", {
 *     reason: "用户请求"
 * });
 * 
 * // 4. 检查状态
 * console.log("连接状态:", Socket.getConnectionStatus());
 * console.log("已连接:", Socket.isConnected());
 * 
 * // 5. 调试
 * Socket.debug();
 */






//let ws = null

//export function SocketInit()
//{
//    ws = new WebSocket("ws://127.0.0.1:8000/ws")

//    ws.onopen = () => {
//        console.log("已连接后端 WebSocket");
//    };

//    ws.onmessage = (event) => {
//        console.log("收到了后端消息")
//        const data = JSON.parse(event.data);
//        if(data.type == "ping")
//        {
//            console.log("收到后端:", data.msg);

//        }
//    };

//    ws.onclose = () => {
//        console.log("连接已关闭");
//    };

//    ws.onerror = (err) => {
//        console.error("WebSocket 错误", err);
//    };



//}

//export function sendMsg() 
//{
//    console.log("发送消息")
//    let data = {type:"ping", msg : "你好 后端"}
//    ws.send(JSON.stringify(data));
//}

//// UIManager.setConnectionStatus(true);设置连接状态
////UIManager.setLastUpdateTime(new Date().toLocaleString('zh-CN')); 设置上次更新日期
////UIManager.updateIndustryAnalysisTable(response.industryAnalysis);更新选股结果的行业状态


////// 股票查询相关事件
////document.getElementById('btn-query-stock')?.addEventListener('click', () => {
////    const code = UIManager.getStockQueryInput();
////    if (!code.trim()) {
////        UIManager.log('请输入股票代码或名称', 'warning');
////        return;
////    }
////    // 调用后端API查询
////    queryStockInfo(code);
////});

////document.getElementById('quick-query-input')?.addEventListener('input', (e) => {
////    const keyword = e.target.value;
////    if (keyword.length >= 1) {
////        // 调用后端API进行快速搜索
////        quickSearchStocks(keyword);
////    }
////});

////// 快速查询结果点击事件
////document.addEventListener('click', (e) => {
////    if (e.target.closest('.query-item')) {
////        const code = e.target.closest('.query-item').dataset.code;
////        document.getElementById('query-stock-input').value = code;
////        queryStockInfo(code);
////    }
////});

////// 辅助函数（需要根据后端API实现）
////async function queryStockInfo(code) {
////    // TODO: 调用后端API获取股票信息
////    // UIManager.setStockQueryResult(data);
////}

////async function quickSearchStocks(keyword) {
////    // TODO: 调用后端API进行快速搜索
////    // UIManager.setQuickQueryResults(results);
////}