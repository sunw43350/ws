

https://docs.kraken.com/api/docs/futures-api/websocket/heartbeat


Heartbeat
CHANNEL
wss://futures.kraken.com/ws/v1
heartbeat
The heartbeat feed publishes a heartbeat message at timed intervals.

Request
Request Fields
Example
{
  "event": "subscribe",
  "feed": "heartbeat"
}

Response Success
Response Fields
Successful
{
  "event": "subscribed",
  "feed": "heartbeat"
}

Response Snapshot
Response Fields
Subscription Data
{
  "feed": "heartbeat",
  "time": 1534262350627
}

Response Error
Response Fields
Example Error
{
  "event": "error",
  "message": "Json Error"
}