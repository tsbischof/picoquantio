import mmap
import pathlib
from typing import Union

VERSION = "0.0.1"


def identify(path: Union[pathlib.Path, str]) -> tuple[str, str, str]:
    """
    Return a tuple of (hardware, format, version) describing the kind of file

    :param path: Path to the file
    :return: (hardware, format, version)
    :rtype: tuple[str]
    """
    if isinstance(path, str):
        path = pathlib.Path(path)

    with path.open("r+b") as rawdata:
        return identify_by_header(mmap.mmap(rawdata.fileno(), 0))


def identify_by_header(rawdata: Union[mmap.mmap, bytes]) -> tuple[str, str, str]:
    raise NotImplementedError


def load(path: pathlib.Path):
    raise NotImplementedError
