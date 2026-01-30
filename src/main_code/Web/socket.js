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
    LOG : "log",
    LAST_UPDATE_DATA: "last_update_data_time",      // 请求接受上次更新日期
    CS_UPDATE_DATA: "cs_update_data",              // 客户端请求拉取数据
    SC_UPDATE_DATA: "sc_update_data",              // 客户端请求拉取数据
    CS_SELECT_STOCKS: "cs_select_stocks",          // 客户端请求执行股票筛选
    CS_BACK_TEST: "cs_back_test",                  // 客户端请求执行回测
    CS_DIAGNOSE: "cs_diagnose",                    // 客户端请求出仓判断
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
    manager.handleMessage(data.type, data)
    //if(data.type = MessageType.CS_UPDATE_DATA)
    //{
    //    manager.app.log(data.msg)
    //}
    //else if(data.type == MessageType.CS_SELECT_STOCKS){}
    //else if(data.type == MessageType.CS_BACK_TEST){}
    //else if(data.type == MessageType.CS_DIAGNOSE){}
    //else if(data.type == MessageType.LAST_UPDATE_DATA)
    //{
    //    manager.app.log(data.msg)
    //}
        
    //else if(data.type == MessageType.LOG)
    //{
    //    manager.app.log(data.msg)
    //}
}


/**
 * 处理接收到的WebSocket消息
 * @param {string} data - 消息数据（JSON字符串）
 */
function handleWebSocketMessage(data) {
    try {
        const message = JSON.parse(data);

        HandleMessage(message)

    } catch (error) {
        console.error("❌ 消息解析失败:", error);
    }
}



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
        manager.app.log("后端未连接","error")
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
            return false;
        }
    } else {
        manager.app.log("后端未连接","error")
        //console.warn("⚠️ WebSocket未就绪，消息已加入队列");
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
 * 获取调试信息
 */
export function debug() {
    console.log("=== WebSocket 调试信息 ===");
    console.log("连接状态:", getConnectionStatus());
    console.log("是否已连接:", isConnected());
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

