import typing

from tinyws.request import WebsocketRequest
from tinyws.asgi_types import Scope, Send, Receive

if typing.TYPE_CHECKING:
    from tinyws.server import Server

class WebsocketInterface:
    """A lifespan impl."""

    def __init__(self, main: "Server") -> None:
        self.main = main

    @property
    def logger(self):
        return self.main.logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Make the magic go :)."""

        request = WebsocketRequest(scope, receive, send)
        self.logger.info(f'Request created complete.')

        await self.main.application(request)