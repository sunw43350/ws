

## blofin

General Info
Root URL for REST access: https://openapi.blofin.com
Public WebSocket：wss://openapi.blofin.com/ws/public
Private WebSocket：wss://openapi.blofin.com/ws/private
All time and timestamp related fields are in milliseconds.
All endpoints return either a JSON object or array.
Data is returned in descending order. Newest first, oldest last.
Demo Trading
Root URL for demo-trading REST access: https://demo-trading-openapi.blofin.com
Public WebSocket for demo-trading：wss://demo-trading-openapi.blofin.com/ws/public
Private WebSocket for demo-trading：wss://demo-trading-openapi.blofin.com/ws/private
General Information on Endpoints
For GET endpoints, parameters must be sent as a query string.
Parameters may be sent in any order.
Copy Trading
Private WebSocket：wss://openapi.blofin.com/ws/copytrading/private

https://docs.blofin.com/index.html#websocket



WebSocket Connection Management
Connection Limits
New Connections: 1 per second per IP
Channel Types:
Public channels via public service endpoint
Private channels via private service endpoint
If there’s a network problem, the system will automatically disable the connection.

The connection will break automatically if the subscription is not established or data has not been pushed for more than 30 seconds.

To keep the connection stable:

1.Set a timer of N seconds whenever a response message is received, where N is less than 30.

2.If the timer is triggered, which means that no new message is received within N seconds, send the String ‘ping’.

3.Expect a ‘pong’ as a response. If the response message is not received within N seconds, please raise an error or reconnect.