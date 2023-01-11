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
