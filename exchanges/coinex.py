import websocket
import json
import gzip

WS_URL = "wss://socket.coinex.com/v2/common"

def on_open(ws):
    print("✅ 已连接 CoinEx 公告频道 WebSocket")

    # 订阅公告通知频道
    sub_msg = {
        "id": 1,
        "method": "notice.subscribe",
        "params": []
    }
    ws.send(json.dumps(sub_msg))
    print("📨 已发送订阅请求:", sub_msg)

def on_message(ws, message):
    try:
        # CoinEx 返回 gzip 压缩数据
        decompressed = gzip.decompress(message).decode("utf-8")
        data = json.loads(decompressed)

        # 示例字段说明：
        # 'title'     : 公告标题
        # 'content'   : 公告内容（可能是 HTML 格式）
        # 'lang'      : 语言（如 'zh-CN'）
        # 'created_at': 发布时间戳（毫秒）
        # 'type'      : 公告类型（如 'system_announcement'）

        if "params" in data and "notice" in data["params"]:
            notice = data["params"]["notice"]
            print(f"📢 公告: {notice['title']} | 类型: {notice['type']} | 时间戳: {notice['created_at']}")
    except Exception as e:
        print("❌ 解码失败:", e)

def on_error(ws, error):
    print("❌ 错误:", error)

def on_close(ws, code, reason):
    print(f"🚪 连接关闭: {code} - {reason}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
