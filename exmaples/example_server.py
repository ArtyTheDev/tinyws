import tinyws
import uvicorn
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

uvicorn.run(application, ws="wsproto")