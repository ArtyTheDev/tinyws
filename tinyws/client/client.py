import typing
import functools
import asyncio
import urllib.parse

from tinyws.client.protocol import WSProtoImpl
from wsproto.extensions import Extension

class Client:
    """The client side."""

    def __init__(
        self,
        uri: str,
        compression: str = "deflate",
        origin: typing.Optional[str] = None,
        extensions: typing.Optional[typing.List[Extension]] = [],
        extra_headers: typing.Optional[typing.List[typing.Tuple[bytes,bytes]]] = [],
        subprotocols: typing.Optional[str] = None,
        open_timeout: int = 15,
        ping_timeout: int = 20,
        max_packet_size: int = 1024 * 8 * 2
    ) -> None:

        # Connect.
        self.uri = uri

        # Packet attrs.
        self.compression = compression
        self.origin = origin
        self.extensions = extensions
        self.subprotocols = subprotocols
        self.extra_headers = extra_headers
        self.open_timeout = open_timeout
        self.max_packet_size = max_packet_size

        # Ping attrs.
        self.ping_timeout = ping_timeout

    def __await__(self) -> typing.Generator[typing.Any, None, WSProtoImpl]:
        # Main function.

        async def __main__():
            return await asyncio.wait_for(
                self.__await_timeout__(),
                self.open_timeout
            )

        return __main__().__await__()

    async def __await_timeout__(self):
        # Timeout the connection.

        parse_url = urllib.parse.urlsplit(self.uri)

        if parse_url.path is False:
            parse_url.path = "/"

        protocol_class = functools.partial(
            WSProtoImpl, parse_url.hostname, parse_url.path,
            self.compression, self.origin, self.extensions, self.extra_headers,
            self.subprotocols, self.open_timeout, self.ping_timeout,
            self.max_packet_size
        )

        loop = asyncio.get_running_loop()
        transport, proto = await loop.create_connection(
            protocol_class, parse_url.hostname, parse_url.port
        )

        return proto

connect = Client
