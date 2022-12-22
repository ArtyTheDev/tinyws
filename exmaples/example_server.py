import tinyws

@tinyws.app()
async def application(request: tinyws.WebsocketRequest):
    # You should always accept the request
    # or close it if you rejecting the request.
    await request.accept()

    # To send a packet you can use eaither the raw
    # await request.send(...) or our function await request.send_packet(...)

    while True:
        try:
            # await request.recv() raise an error
            # ConnectionClosed when the connection is closed
            # it also raise it when you close the connection.
            print(await request.recv())
        except tinyws.ConnectionClosed:
            break

@application.on_startup
async def on_startup():
    print('hello')

@application.on_shutdown
async def on_shutdown():
    print('bye')

import uvicorn
uvicorn.run(app=application)