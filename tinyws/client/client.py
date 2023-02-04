import ssl
import typing
import asyncio
import functools
import urllib.parse
import wsproto.extensions

from tinyws.client.protocol import ImplProtocol


class Connect(object):
    """A connect object to make the server."""

    def __init__(
        self,
        uri: str,
        subprotocol: typing.List[str] = [],
        extensions: typing.List[
            wsproto.extensions.Extension
        ] = [],
        extra_headers: typing.List[
            typing.Tuple[bytes, bytes]
        ] = [(b"Server-Provider", b"TinyWS")],
        logger: str = "tinyws.client.protocol",
        ssl_context: typing.Optional[
            ssl.SSLContext
        ] = None,
        connect_timeout: float = 25.0
    ):
        # Init.
        self.uri = uri
        self.subprotocols = subprotocol
        self.extensions = extensions
        self.extra_headers = extra_headers
        self.ssl_context = ssl_context
        self.connect_timeout = connect_timeout
        self.logger = logger

    def uri_parse(self):
        # To make the info for the
        # protocol.

        parse_url = urllib.parse.urlsplit(self.uri)
        hostname, port, = parse_url.hostname, \
            parse_url.port

        if port is None:
            if parse_url.scheme == "ws":
                port = 80
            elif parse_url.scheme == "wss":
                port = 443

        is_ssl = False
        if port == 443:
            if self.ssl_context is not None:
                is_ssl = True
            else:
                self.ssl_context = ssl.create_default_context()

        target = parse_url.path + parse_url.query

        return hostname, port, target, is_ssl

    def __await__(self) -> typing.Generator[typing.Any, None, ImplProtocol]:
        # Main function.

        async def __main__():
            return await asyncio.wait_for(
                self.__await_timeout__(),
                self.connect_timeout
            )

        return __main__().__await__()

    async def __await_timeout__(self):
        # Timeout the connection.

        hostname, port, target, is_ssl = self.uri_parse()

        protocol_impl = functools.partial(
            ImplProtocol, host=hostname,
            target=target, subprotocol=self.subprotocols,
            extensions=self.extensions, extra_headers=self.extra_headers,
            logger=self.logger
        )

        loop = asyncio.get_running_loop()
        if is_ssl is True:
            _, protocol = await loop.create_connection(
                protocol_impl, host=hostname,     # type: ignore
                port=port, ssl=self.ssl_context,  # type: ignore
            )
        else:
            _, protocol = await loop.create_connection(
                protocol_impl, host=hostname,     # type: ignore
                port=port,  # type: ignore
            )

        return protocol # noqa