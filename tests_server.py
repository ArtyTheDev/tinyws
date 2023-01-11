import tinyws
import asyncio

@tinyws.app()
async def application(request: tinyws.Request):
    print("Connection made")
    await request.accept()
    await request.send('Hola2')

    while True:
        try:
            print(await request.receive())
        except tinyws.server.ConnectionClosed:
            break

import uvicorn
uvicorn.run(application, ws="wsproto")
