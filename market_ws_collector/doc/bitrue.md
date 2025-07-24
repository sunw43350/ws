
https://www.bitrue.com/api_docs_includes_file/delivery/index.html#websocket-market-data

## keeplive

 Recommended format: {"pong":1721131206}

 


The connection method for Websocket is：

Base Url: wss://fmarket-ws.bitrue.com/kline-api/ws
Data is compressed in binary format except for heartbeat data (users need to decompress using the Gzip algorithm).
All trading pairs are in lowercase.
Each connection has a validity period of no more than 24 hours; please handle reconnects properly.
It is not recommended to subscribe to more than 100 streams per single connection.
If the user's messages exceed the limit, the connection will be terminated. Repeated disconnections from the same IP may result in server blocking.
It is advised not to establish more than 100 connections per IP at the same time.
The WebSocket server sends a Ping message every second.
If the WebSocket server does not receive a Pong message response within N seconds, the connection will be terminated (N=1).
Upon receiving a ping message, the client must promptly reply with a pong message.
Unsolicited pong messages are allowed but do not guarantee that the connection will remain open. Recommended format: {"pong":1721131206}
The volume and amount returned by the interface need to be multiplied by the Contract Size (multiplier) manually.
To get the method, you need to read the Current open contract interface: /dapi/v1/contracts