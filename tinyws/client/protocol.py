import typing
import asyncio
import time

import wsproto
import wsproto.extensions
import wsproto.connection

from tinyws.client.exceptions import (
    ConnectionClosed,
    ConnectionRejected,
)
from tinyws.client.packet import Packet, PacketType

Transport = asyncio.Transport
WebsocketState = wsproto.connection.ConnectionState

class WSProtoImpl(asyncio.Protocol):
    """An asyncio.Protocol impl using `wsproto`"""

    def __init__(
        self,
        host: str,
        target: str,
        compression: str = "deflate",
        origin: typing.Optional[str] = None,
        extensions: typing.Optional[wsproto.extensions.Extension] = [],
        extra_headers: typing.Optional[typing.Dict[str, str]] = None,
        subprotocols: typing.Optional[str] = None,
        open_timeout: int = 15,
        ping_timeout: int = 20,
        max_packet_size: int = 1024 * 8 * 2
    ) -> None:
        "Init the protocol."

        # Connect.
        self.host = host
        self.target = target
        self.loop = asyncio.get_event_loop()

        # State of protocol.
        self.connection = wsproto.WSConnection(
            wsproto.ConnectionType.CLIENT
        )
        self.message = asyncio.Queue()
        self.state = self.connection.state
        self.is_reading = False

        # Trasnport attrs.
        self.transport = None
        self.peername = None
        self.sockname = None
        self.scheme = None

        # Packet attrs.
        self.compression = compression
        self.extensions = extensions
        self.origin = origin
        self.subprotocols = subprotocols
        self.extra_headers = extra_headers
        self.max_packet_size = max_packet_size

        self.connection.client

        # Timeout.
        self.open_timeout = open_timeout
        self.is_timeout = False

        # Ping attrs.
        self.first_ping = True
        self.ping_timeout = ping_timeout
        self.ping_timeout_task = None
        self.last_ping = None
        self.last_pong = None

        # Accept.
        self.headers = None

        # Handshake.
        self.handshake_complete = False
        self.accepted_connection = False
        self.accepted_event = asyncio.Event()

        # Buffer.
        self.text = ""
        self.bytes = b""

    def connection_made(self, transport: Transport) -> None:
        # When a connection is established.
        self.transport = transport

        if self.handshake_complete is not True:
            event = wsproto.events.Request(
                host=self.host,
                target=self.target,
                extra_headers=self.extra_headers,
                subprotocols=self.subprotocols
            )
            output = self.connection.send(event=event)
            self.transport.write(output)

            self.handshake_complete = True

    def data_received(self, data: bytes) -> None:
        # feed data to the connection.

        self.connection.receive_data(data)

        def __accept__(event: wsproto.events.AcceptConnection):
            # Called when the connection is accepted.

            self.headers = event.extra_headers

            self.accepted_connection = True
            self.state = WebsocketState.OPEN
            self.accepted_event.set()

        def __rejrect__(event: wsproto.events.RejectConnection):
            # Called when the connection is rejected.

            exc = ConnectionRejected(f"Connection rejected with an error. {event.status_code}")
            self.message.put_nowait(exc)
            self.transport.close()

        def __close__(event: wsproto.events.CloseConnection):
            # Called when the connection is closed.

            packet = Packet(
                type=PacketType.CLOSE,
                code=event.code,
                reason=event.reason
            )
            self.message.put_nowait(packet)

        def __text_message__(event: wsproto.events.TextMessage):
            # Called when the client is receving a text message.

            self.text += event.data
            if event.message_finished is True:
                packet = Packet(
                    type=PacketType.TEXT,
                    packet=self.text
                )
                self.message.put_nowait(packet)
                self.text = ""

        def __byte_message__(event: wsproto.events.BytesMessage):
            # Called when the client is receving a byte message.

            self.bytes += event.data
            if event.message_finished is True:
                packet = Packet(
                    type=PacketType.BINARY,
                    packet=self.bytes
                )
                self.message.put_nowait(packet)
                self.bytes = b""

        def __ping__(event: wsproto.events.Ping):
            # Called when the server send a ping packet.
            if self.first_ping is True:
                self.first_ping = False

            if self.first_ping is False:
                if self.last_ping - self.last_pong > 0:
                    self.transport.write(
                        self.connection.send(event.response())
                    )
                else:
                    raise ValueError('Timeout error.')

            self.last_ping = time.time()

        def __pong__(event: wsproto.events.Pong):
            # Called when recv a pong.
            self.last_pong = time.time()

        events = {
            wsproto.events.AcceptConnection: __accept__,
            wsproto.events.RejectConnection: __rejrect__,
            wsproto.events.CloseConnection: __close__,
            wsproto.events.TextMessage: __text_message__,
            wsproto.events.BytesMessage: __byte_message__,
            wsproto.events.Ping: __ping__,
            wsproto.events.Pong: __pong__
        }

        for event in self.connection.events():
            event_type = type(event)
            event_handler = events.get(event_type, None)

            if event_handler is None:
                break

            event_handler(event)

    @property
    def latency(self):
        """The latency between the client and server."""

        return self.first_ping - self.last_ping

    # Methods.
    async def receive(self) -> Packet:
        # The method to receive messages.

        await self.accepted_event.wait()
        if self.is_reading is True:
            raise RuntimeError("The protocol is reading the queue.")

        message = await self.message.get()
        if isinstance(message, Exception):
            raise message

        return message

    async def send(self, message: typing.Union[str, bytes]) -> None:
        # The method to send messages to the server.

        await self.accepted_event.wait()

        if self.state is not  WebsocketState.OPEN:
            raise ConnectionClosed("Connection is closed.")

        event = wsproto.events.Message(data=message)
        self.transport.write(
            self.connection.send(event=event)
        )

    async def close(self, code: int, reason: typing.Optional[str] = None):
        # To close the connection.

        await self.accepted_event.wait()

        if self.state is not WebsocketState.OPEN:
            raise ConnectionError("Connection is not yet established.")

        event = wsproto.events.CloseConnection(code=code, reason=reason)
        self.transport.write(
            self.connection.send(event=event)
        )
        self.transport.close()

        raise ConnectionClosed("Connection is closed.")

