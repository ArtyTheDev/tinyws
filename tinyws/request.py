import typing
import enum

from tinyws.exceptions import ConnectionClosed
from tinyws.asgi_types import Scope, Receive, Send

class State(enum.Enum):
    CONNECTING = 1
    CONNECTED = 2
    DISCONNECT = 3

class BaseRequest(object):
    """Base request for all request."""

    __slots__ = (
        "scope",
        "receive",
        "send",
        "session",
        "_headers",
    )

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # Asgi attrs.
        self.scope = scope
        self.receive = receive
        self.send = send

        # Session.
        self.session = {}

        # HTTP attrs.
        self._headers = None

    @property
    def version(self):
        """Return the version of the http protocol."""
        return self.scope['http_version']

    @property
    def scheme(self):
        """Return the scheme of the connection."""
        return self.scope['scheme']

    @property
    def path(self):
        """Return the path of the connection url."""
        return self.scope['path']

    @property
    def query_string(self):
        """Return the path of the connection url."""
        return self.scope['query_string']

    @property
    def subprotocols(self):
        """Return the subprotocols of the connection."""
        return self.scope['subprotocols']

    @property
    def headers(self):
        """Get the headers of the request."""
        if self._headers is None:
            self._headers = {
                key: value
                for (key, value) in self.scope['headers']
            }

        return self._headers

class WebsocketRequest(BaseRequest):
    """Base request for websocket request."""

    __slots__ = (
        "client_state",
        "application_state"
    )

    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # State.
        self.client_state = State.CONNECTING
        self.application_state = State.CONNECTING

        super().__init__(scope, receive, send)

    async def accept(self, subprotocol: str = None):
        """Accept the connection."""

        if self.client_state is State.CONNECTING:
            packet_type = (await self.receive())['type']

            if packet_type == 'websocket.connect':
                self.client_state = State.CONNECTED
            elif packet_type == 'websocket.disconnect':
                self.client_state = State.DISCONNECT

        if self.application_state is State.CONNECTING:
            await self.send({"type": "websocket.accept", "subprotocol": subprotocol})
            self.application_state = State.CONNECTED

    async def send_packet(self, packet: typing.Union[str, bytes]):
        """Send a packet to the client."""

        message = None

        if isinstance(packet, str):
            message = {"type": "websocket.send", "bytes": packet}
        elif isinstance(packet, bytes):
            message = {"type": "websocket.send", "bytes": packet}

        if self.client_state is State.DISCONNECT:
            raise ConnectionClosed("Connection is not established yet.")

        if self.application_state is State.CONNECTED:
            await self.send(message)

    async def recv(self):
        """Receive message from the client."""

        if self.client_state is State.DISCONNECT:
            raise ConnectionClosed(f"Connection has been disconnected.")

        message = await self.receive()

        if message.get('type') == 'websocket.receive':
            return message.get('text', None) or \
                message.get('bytes') or None
        elif message.get('type') == 'websocket.disconnect':
            self.client_state = State.DISCONNECT
            raise ConnectionClosed(f"Connection has been disconnected", code=int(message.get('code')))

    async def recv_iter(self):
        """Receive message as an iter."""

        while True:
            try:
                yield await self.recv()
            except:
                pass

    async def close(self, code: int = 1001):
        """Close the connection."""

        await self.send({"type": "websocket.disconnect", "code": code})
        self.client_state = State.DISCONNECT
        raise ConnectionClosed("Connection has been closed.")
