"""Application."""

import typing
import logging

from tinyws.server.interface import WebsocketInterface, \
    LifespanInterface
from tinyws.asgi_types import Scope, Receive, Send
from tinyws.server.request import Request
from tinyws.server.middleware import BaseMiddleware

class Server(object):
    """The base class server."""

    def __init__(
        self,
        application: typing.Callable[[Request], None],
        *,
        logger: typing.Optional[logging.Logger] = None,
        on_startup: typing.Optional[typing.Callable] = None,
        on_shutdown: typing.Optional[typing.Callable]  = None,

    ) -> None:
        """Initialize the application."""

        self.application = application

        # Lifespan.
        self.on_startup_func = on_startup
        self.on_shutdown_func = on_shutdown

        # Logging.
        self.logger = logger or \
            logging.Logger('tinyws.server', level=logging.INFO)

        # Interface stuff.
        self.websockets_class = WebsocketInterface
        self.lifespan_class = LifespanInterface

    def on_startup(self, func: typing.Callable):
        """Register a function as on_startup."""

        self.on_startup_func = func

    def on_shutdown(self, func: typing.Callable):
        """Register a function as on_shutdown."""

        self.on_shutdown_func = func

    def middleware(self, md: BaseMiddleware, **init):
        """Register a middleware."""

        self.asgi_app = md(self.asgi_app, **init)

    async def asgi_app(self, scope: Scope, receive: Receive, send: Send):
        """The main app."""

        scope_type = scope['type']

        asgi_handler = None
        if scope_type == 'lifespan':
            asgi_handler = self.lifespan_class(self)
        if scope_type == 'websocket':
            asgi_handler = self.websockets_class(self)

        if asgi_handler is not None:
            await asgi_handler(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """The main function for the asgi server to call."""

        await self.asgi_app(scope, receive, send)

def app(
    logger: typing.Optional[logging.Logger] = None,
    on_startup: typing.Optional[typing.Callable] = None,
    on_shutdown: typing.Optional[typing.Callable]  = None
):
    """To create an app."""

    def __deco__(function: typing.Callable) -> Server:
        return Server(function, logger=logger,
            on_startup=on_startup, on_shutdown=on_shutdown)

    return __deco__
