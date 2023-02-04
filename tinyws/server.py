import tinyasgi.application
import tinyasgi.websockets
import functools

Application = tinyasgi.application.Application
WebSocket = tinyasgi.websockets.WebSocket
WebSocketClose = tinyasgi.websockets.WebSocketClose
WebSocketDisconnect = tinyasgi.websockets.WebSocketDisconnect
app = functools.partial(
    tinyasgi.application.app, support=("ws")
)

__all__ = (
    "Application",
    "WebSocket",
    "WebSocketClose",
    "app"
) # noqa