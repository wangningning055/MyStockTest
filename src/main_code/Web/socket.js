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