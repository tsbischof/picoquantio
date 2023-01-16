import collections
import io
import pathlib
from typing import Any, Callable, List, Tuple, Union

import numpy as np
import numpy.lib.recfunctions as rfn

VERSION = "0.0.1-dev"

Identity = collections.namedtuple("Identity", ["Identity", "Version"])
Path = Union[pathlib.Path, str]
T2Records = dict[str, np.ndarray]
T3Records = dict[str, np.ndarray]
Header = dict[str, Union[str, int, float]]
Records = Union[T2Records, T3Records]
Loader = Callable[[io.BufferedReader], Tuple[Header, Records]]
RecordLoader = Callable[[io.BufferedReader], Records]

_dtype_time = np.uint64
_dtype_pulse = np.uint64
_dtype_channel = np.uint32


def _sanitize_path(path: Path) -> pathlib.Path:
    if isinstance(path, str):
        return pathlib.Path(path)
    else:
        return path


def identify(path: Path) -> Identity:
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
    raw_ident = rawdata.peek(16)[:16]
    if raw_ident[0:6] in {b"PQHIST", b"PQTTTR"}:
        version = raw_ident[8:].rstrip(b"\x00").decode()
        ident = raw_ident[:8].rstrip(b"\x00").decode()
    elif raw_ident.rstrip(b"\x00") in {b"PicoHarp 300", b"TimeHarp 200", b"HydraHarp"}:
        ident = raw_ident.rstrip(b"\x00").decode()
        version = rawdata.peek(22)[16:22].rstrip(b"\x00").decode()
    else:
        raise ValueError(
            f"Could not identify the file type based on the header. Found {ident}, expected one of {list(map(bytes.decode, VALID_IDENTS))}"
        )

    return Identity(ident, version)


def load(path: Path) -> Any:
    """
    Load PicoQuant data from a file, with the file type detected automatically


    :param path: path to the file
    """
    path = _sanitize_path(path)
    identity = identify(path)
    loader = _get_loader(identity)
    return loader(path)


def _get_loader(identity: Identity) -> Any:
    """
    Returns the loader for the given file format, or raises an exception

    :param identity: the Identity tuple containing the hardware identity and version
    :return: a function which loads data from a given path
    """
    if identity.Identity == "PQTTTR":
        return unified.load_ptu
    elif identity.Identity == "PQHIST":
        raise NotImplementedError("Unified file type phu not implemented.")
    else:
        if identity.Identity == "PicoHarp 300":
            return picoharp.load
        elif identity.Identity == "TimeHarp 200":
            return timeharp.load
        elif identity.Identity == "HydraHarp":
            return hydraharp._load_hxx

    raise ValueError(f"Cannot identify a loader for {identity}")


def _correct_overflow(
    timestamps: np.ndarray,
    channels: np.ndarray,
    overflow_channel: int,
    overflow_value: int,
    nsync: bool,
) -> None:
    """
    In v20 the record includes a number of overflow events with each overflow
    event. Update the timestamps to reflect the amount of time including the
    total overflow

    :param nsync: if True, interpret the timestamp for each overflow as a number of overflows. Otherwise, each overflow record is a single overflow event.
    """
    overflow_index = np.where((channels == overflow_channel))
    cum_overflows = np.zeros(timestamps.size, dtype=timestamps.dtype)
    if nsync:
        cum_overflows[overflow_index] = timestamps[overflow_index]
    else:
        cum_overflows[overflow_index] = 1
    np.cumsum(cum_overflows, out=cum_overflows)
    timestamps += cum_overflows * overflow_value


def _merge_arrays_to_header(arrays: List[np.ndarray]) -> Header:
    """
    Merge np structured arrays into a single dict with native Python types,
    suuitable for json serialization.
    """
    result = collections.OrderedDict()

    for array in arrays:
        if len(array) == 0:
            continue

        for field, dtype in array.dtype.fields.items():
            if len(array[field]) == 1:
                result[field] = array[field][0].item()
            else:
                result[field] = list(map(lambda x: x.item(), array[field]))

            if dtype[0].kind == "S":
                result[field] = result[field].decode()

    return result


from .cor import load_cor
from . import hydraharp
from . import picoharp
from . import timeharp
from . import unified
