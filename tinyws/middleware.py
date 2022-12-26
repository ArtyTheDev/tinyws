from tinyws.asgi_types import Scope, Receive, Send

class BaseMiddleware(object):
    """A base middleware for building other middlewares."""

    def __init__(self, application, scopes=None) -> None:
        self.application = application
        self.scopes = scopes

    async def __process__(self, scope: Scope, receive: Receive, send: Send):
        """The main prcoess of the middleware."""

        raise NotImplemented()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """The process of calling the middleware."""

        if scope['type'] in self.scopes:
            await self.__process__(scope, receive, send)

        await self.application(scope, receive, send)