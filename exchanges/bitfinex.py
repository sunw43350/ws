import websocket
import json
import time

WS_URL = "wss://api-pub.bitfinex.com/ws/2"
CONTRACTS = ["tBTCF0:USTF0", "tETHF0:USTF0", "tSOLF0:USTF0", "tXRPF0:USTF0", "tLTCF0:USTF0"]

def on_open(ws):
    print("✅ 已连接 Bitfinex WebSocket（合约行情）")

    for symbol in CONTRACTS:
        sub_msg = {
            "event": "subscribe",
            "channel": "ticker",
            "symbol": symbol
        }
        ws.send(json.dumps(sub_msg))
        print(f"📨 已订阅: ticker → {symbol}")
        time.sleep(0.3)  # 控制订阅速率

def on_message(ws, message):
    try:
        data = json.loads(message)

        # ✅ ticker 推送结构：[CHAN_ID, [BID, BID_SIZE, ASK, ASK_SIZE, ...]]
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            chan_id = data[0]
            payload = data[1]
            bid = payload[0]
            ask = payload[2]
            print(f"📊 CHAN_ID {chan_id} | 买一: {bid} | 卖一: {ask}")

        elif isinstance(data, dict) and data.get("event") == "subscribed":
            print(f"✅ 订阅成功: {data.get('channel')} → {data.get('symbol')}")

        elif isinstance(data, dict) and data.get("event") == "error":
            print(f"❌ 错误: {data.get('msg')}")

    except Exception as e:
        print(f"❌ 解码失败: {e}")

def on_error(ws, error):
    print(f"❌ WebSocket 错误: {error}")

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
