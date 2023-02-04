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
