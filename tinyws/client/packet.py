import dataclasses
import typing
import enum

class PacketType(enum.Enum):
    TEXT = 1
    BINARY = 2
    CLOSE = 3
    ERROR = 4

@dataclasses.dataclass
class Packet:
    """A packet."""

    type: int
    packet: typing.Optional[
        typing.Union[str, bytes]
    ] = None
    code: typing.Optional[int] = None
    reason: typing.Optional[str] = None
