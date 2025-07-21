import websocket
import json

# Paradex WebSocket 地址（测试网）
WS_URL = "wss://ws.api.testnet.paradex.trade/v1"

# JWT Token（请替换为你自己的）
JWT_TOKEN = "your_jwt_token_here"

# 构造订阅消息
def build_subscribe_msg(channel, msg_id):
    return {
        "jsonrpc": "2.0",
        "method": "subscribe",
        "params": {
            "channel": channel
        },
        "id": msg_id
    }

def on_open(ws):
    print("✅ 已连接 Paradex WebSocket")

    # 发送认证消息
    auth_msg = {
        "jsonrpc": "2.0",
        "method": "auth",
        "params": {
            "bearer": JWT_TOKEN
        },
        "id": 1
    }
    ws.send(json.dumps(auth_msg))
    print("📨 已发送认证请求")

    # 订阅两个合约的 trades 频道
    ws.send(json.dumps(build_subscribe_msg("trades.BTC-USD-PERP", 2)))
    ws.send(json.dumps(build_subscribe_msg("trades.ETH-USD-PERP", 3)))
    print("📨 已订阅 BTC 和 ETH 合约的 trades 频道")

def on_message(ws, message):
    print("📩 收到消息:", message)

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
