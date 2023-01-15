import collections
import io
import pathlib
import typing

from .cor import load_cor
from . import hydraharp
from . import picoharp
from . import timeharp
from . import unified

VERSION = "0.0.1-dev"

Identity = collections.namedtuple("Identity", ["Identity", "Version"])


def identify(path: typing.Union[pathlib.Path, str]) -> Identity:
    """
    Return a tuple of (hardware, format, version) describing the kind of file

    :param path: Path to the file
    :return: (hardware, format, version)
    :rtype: Identity
    """
    if isinstance(path, str):
        path = pathlib.Path(path)

    with path.open("rb") as rawdata:
        return _identify_by_header(rawdata)


def _identify_by_header(rawdata: io.BufferedReader) -> Identity:
    """
    Return a tuple of (hardware, format, version) describing the kind of file

    :param rawdata: mmap or bytes of raw data, starting from the beggining of the file
    :return: (hardware, format, version)
    :rtype: Identity
    """
    VALID_IDENTS = {
        b"PQHIST",
        b"PQTTTR",
        b"PicoHarp 300",
        b"TimeHarp 200",
        b"HydraHarp",
    }
    ident = rawdata.peek(16)[:16]
    if ident[0:6] in {b"PQHIST", b"PQTTTR"}:
        version = ident[8:]
        ident = ident[:8]
    elif ident.rstrip(b"\x00") in {b"PicoHarp 300", b"TimeHarp 200", b"HydraHarp"}:
        version = rawdata.peek(22)[16:]
    else:
        raise ValueError(
            f"Could not identify the file type based on the header. Found {ident.decode()}, expected one of {list(map(bytes.decode, VALID_IDENTS))}"
        )

    return Identity(ident.rstrip(b"\x00").decode(), version.rstrip(b"\x00").decode())


def load(path: pathlib.Path):
    identity = identify(path)
    decoder = _get_decoder(identity)
    return decoder(path)


def _get_decoder(identity: Identity):
    raise NotImplementedError
