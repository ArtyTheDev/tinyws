# Tinyws 📡
a tiny tiny tiny lib to build websocket server using the ASGI server protocol.

### Server Usage.
An example usage of it.
```py
import tinyws
import tinyws.server

@tinyws.server.app()
async def application(request: tinyws.server.WebSocket):
    # Accept the connection.
    await request.accept()

    # While loop for the keep-live connection.
    while True:
        try:
            # read the data.
            recv = await request.receive_text()
            print(recv)
        except tinyws.server.WebSocketDisconnect:
            break
```

### Client usage.
```py
import tinyws
import tinyws.client
import asyncio

async def main():
    # To create a connect you can use
    # tinyws.client.Connect(...)
    # they are both the same thing.
    ws = await tinyws.client.Connect("ws://localhost:8000/")

    # To send a packet to the server.
    await ws.send("Hi!")

    # The event loop to stay the connection alive.
    while True:
        # To get the message from the queue.
        message = await ws.receive()

        # PacketType to see what's type of message in
        # the queue.
        if message.packet_type is tinyws.client.PacketType.TEXT:
            print(message)
        elif message.packet_type is tinyws.client.PacketType.BYTES:
            print(message)
        elif message.packet_type is tinyws.client.PacketType.CLOSE:
            break

asyncio.run(main())

```

you can run it then using any `ASGI server` like `uvicorn` just like
```s
$ python -m uvicorn app:application
```
