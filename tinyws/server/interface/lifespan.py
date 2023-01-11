import asyncio
import typing

from tinyws.asgi_types import Scope, Send, Receive
if typing.TYPE_CHECKING:
    from tinyws.server import Server

class LifespanInterface:
    """A lifespan impl."""

    def __init__(self, main: "Server") -> None:
        self.main = main

    @property
    def logger(self):
        return self.main.logger

    async def run(self, process: str):
        """Run the middleware."""

        handler = self.main.on_startup_func \
            if process == 'startup' \
                else self.main.on_shutdown_func

        if handler is None:
            return {"type": f"lifespan.{process}.complete"} 

        try:
            h = handler()
            if asyncio.iscoroutine(h):
                await h
        except Exception as exc:
            self.logger.error(f"Lifespan failed on `on_{process}`")
            self.logger.exception(exc)

            return {
                "type": f"lifespan.{process}.failed", 
                "message": str(exc)
            }
            
        return {"type": f"lifespan.{process}.complete"}

            
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Make the magic go :)."""

        # self.main.logger.info("Lifespan started.")

        while True:
            recv = await receive()
            if recv["type"] == "lifespan.startup":
                await send(
                    await self.run('startup')
                )

            elif recv["type"] == "lifespan.shutdown":
                return await send(
                    await self.run('shutdown')
                )
    