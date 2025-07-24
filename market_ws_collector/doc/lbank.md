WebSocket API (Market Data)
Request & subscription instruction
URL: wss://www.lbkex.net/ws/V2/

Hearbeat（ping/pong）

To prevent botch links and reduce server load, server will send a "Ping" message periodically to client connections. When client recieves the "Ping" message, it should response immediately. If a client responds nothing to macth the "Ping" message in one minute, server will close the connection to the client. Meanwhile client can also send a "Ping" message to server to check whether the connection is working. After server recieves the "Ping" message, it should response with a "Pong" message to match the "Ping". Eg:

 ping { "action":"ping", "ping":"0ca8f854-7ba7-4341-9d86-d3327e52804e" }
pong { "action":"pong", "pong":"0ca8f854-7ba7-4341-9d86-d3327e52804e" }


where the value of the key "pong" in the "Pong" message should equal to the value of the key "ping" in correspond "Ping" message.
