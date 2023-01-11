import rich; import builtins; builtins.print = rich.print

import tinyws
import asyncio

async def main():
    ws = await tinyws.connect("ws://localhost:8000/")

    await ws.send("Hello, World!")
    while True:
        message = await ws.receive()
        if message.type is tinyws.PacketType.TEXT:
            print(message)
        elif message.type is tinyws.PacketType.BINARY:
            print(message)
        elif message.type is tinyws.PacketType.CLOSE:
            break

asyncio.run(main())
