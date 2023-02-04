import typing
import asyncio
import logging
import wsproto
import wsproto.events
import wsproto.extensions

from tinyws.client.packet import Packet, PacketType


class ImplProtocol(asyncio.Protocol):
    """An Impl of a `asyncio.Protocol`"""

    def __init__(
        self,
        host: str,
        target: str = "/",
        subprotocol: typing.List[str] = [],
        extensions: typing.List[
            wsproto.extensions.Extension
        ] = [],
        extra_headers: typing.List[
            typing.Tuple[bytes, bytes]
        ] = [(b"Server-Provider", b"TinyWS")],
        logger: str = "tinyws.client.protocol"
    ):
        # Init.
        self.host = host
        self.target = target
        self.subprotocol = subprotocol
        self.extensions = extensions
        self.extra_headers = extra_headers
        self.logger = logging.getLogger(
            name=logger
        )
        self.connection = wsproto.WSConnection(
            connection_type=wsproto.ConnectionType.CLIENT
        )
        self.message_queue = asyncio.Queue()
        self.accept_event = asyncio.Event()
        self.transport = None
        self.peername = None
        self.sockname = None
        self.text_buffer = str()
        self.bytes_buffer = bytes()

    def connection_made(self, transport: asyncio.Transport) -> None:
        # When the TCP client connect to the
        # servre and the connection is established
        # this event will trigger.

        self.transport = transport

        request = wsproto.events.Request(
            host=self.host,
            target=self.target,
            extensions=self.extensions,
            extra_headers=self.extra_headers,
            subprotocols=self.subprotocol
        )
        transport.write(
            self.connection.send(
                event=request
            )
        )
    # Receive.

    def data_received(self, data: bytes) -> None:
        # When the client send a data
        # it's eaither handshake, close or
        # regular data.

        self.connection.receive_data(data)

        for event in self.connection.events():
            if isinstance(event, wsproto.events.AcceptConnection):
                self.accept_event.set()
                self.logger.info("Connection accepted.")
            elif isinstance(event, wsproto.events.CloseConnection):
                packet_obj = Packet(
                    packet_type=PacketType.CLOSE,
                    close_code=event.code,
                    reason=event.reason
                )
                self.message_queue.put_nowait(packet_obj)
                self.logger.info(
                    f"Connection closed, close code is {event.code}")
            elif isinstance(event, wsproto.events.Ping):
                if self.transport is not None:
                    self.transport.write(
                        self.connection.send(
                            event=event.response()
                        )
                    )
            elif isinstance(event, wsproto.events.BytesMessage):
                self.bytes_buffer += event.data
                if event.message_finished is True:
                    packet_obj = Packet(
                        packet_type=PacketType.BYTES,
                        data=self.bytes_buffer
                    )
                    self.message_queue.put_nowait(packet_obj)
                    self.bytes_buffer = bytes()
            elif isinstance(event, wsproto.events.TextMessage):
                self.text_buffer += event.data
                if event.message_finished is True:
                    packet_obj = Packet(
                        packet_type=PacketType.TEXT,
                        data=self.text_buffer
                    )
                    self.message_queue.put_nowait(packet_obj)
                    self.text_buffer = str()
    # I/O

    async def send(self, message: typing.Union[str, bytes]) -> None:
        """A method used to send a message to the server."""

        await self.accept_event.wait()
        message_event = wsproto.events.Message(
            data=message  # type: ignore
        )
        if self.transport is not None:
            self.transport.write(
                self.connection.send(
                    event=message_event
                )
            )
    # Read.

    async def receive(self) -> "Packet":
        """A method used to receive data from the server."""
        return await self.message_queue.get() # noqa