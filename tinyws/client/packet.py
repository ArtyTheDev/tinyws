import typing
import dataclasses
import enum


class PacketType(enum.Enum):
    "A packet type enum."

    TEXT = 1
    BYTES = 2
    CLOSE = 3


@dataclasses.dataclass
class Packet(object):
    "A packet object."

    packet_type: PacketType
    data: typing.Optional[
        typing.Union[str, bytes]
    ] = None
    close_code: typing.Optional[int] = None
    reason: typing.Optional[str] = None # noqa