# Tinyws 📡
a tiny tiny tiny lib to build websocket server using the ASGI server protocol.
<br><br>
## ⚠️ Warning
This is not yet a complete project, the `1.0` is long way from release
so please don't use it just learn from my mistakes and my experience.
<br><br>
### Server Usage.
An example usage of it.
```py
import tinyws

@tinyws.app()
async def application(request: tinyws.Request):
    # You should always accept the request
    # or close it if you rejecting the request.
    await request.accept()

    # To send a packet you can use eaither the raw
    # await request.send(...)
    await request.send("Hello!")

    while True:
        try:
            # await request.recv() raise an error
            # ConnectionClosed when the connection is closed
            # it also raise it when you close the connection.
            print(await request.receive())
        except tinyws.ConnectionClosed:
            break
```

### Client usage.
```py
import tinyws
import asyncio

async def main():
    # To create a connect you can use
    # tinyws.Client(...) pr tinyws.connect(...)
    # they are both the same thing.
    ws = await tinyws.connect("ws://localhost:8000/")

    # To send a packet to the server.
    await ws.send("Hi!")

    # The event loop to stay the connection alive.
    while True:
        # To get the message from the queue.
        message = await ws.receive()

        # PacketType to see what's type of message in
        # the queue.
        if message.type is tinyws.PacketType.TEXT:
            print(message)
        elif message.type is tinyws.PacketType.BINARY:
            print(message)
        elif message.type is tinyws.PacketType.CLOSE:
            break

asyncio.run(main())

```

you can run it then using any `ASGI server` like `uvicorn` just like
```s
$ python -m uvicorn app:application
```
