import collections
import io
import mmap
import struct
import time
import typing
import warnings

import numpy as np

from .constants import *

UnifiedTag = collections.namedtuple("UnifiedTag", ["ident", "index", "type", "value"])
UnifiedTagStruct = struct.Struct("<32siIq")

_tag_types = {
    PU_TAG_Bool8: bool,
    PU_TAG_Int8: np.int64,
    PU_TAG_BitSet64: np.uint64,
    PU_TAG_Color8: np.uint64,
    PU_TAG_Float8: np.float64,
}


def read_tags(rawdata: io.BufferedReader) -> typing.List[UnifiedTag]:
    tags = list()

    try:
        while True:
            ident, index, _type, value = UnifiedTagStruct.unpack(
                rawdata.read(UnifiedTagStruct.size)
            )
            ident = ident.rstrip(b"\x00").decode("utf-8")
            if _type == PU_TAG_Empty8:
                pass
            elif _type in _tag_types:
                value = _tag_types[_type](value)
            elif _type == PU_TAG_TDateTime:
                float_value = struct.unpack("<d", struct.pack("<q", value))[0]
                value = time.gmtime(int((float(float_value) - 25569) * 86400))
            elif _type == PU_TAG_Float8Array:
                value = rawdata.read(struct.calcsize(f"{value}d"))
            elif _type == PU_TAG_AnsiString:
                value = (
                    rawdata.read(struct.calcsize(f"{value}c"))
                    .rstrip(b"\x00")
                    .decode("utf-8")
                )
            elif _type == PU_TAG_WideString:
                value = (
                    rawdata.read(struct.calcsize(f"{value}c"))
                    .rstrip(b"\x00")
                    .decode("utf-16")
                )
            elif _type == PU_TAG_BinaryBlob:
                value = rawdata.read(value)
            else:
                raise ValueError(
                    f"Found unknown tag type {_type} ({ident}, {index}, {_type}, {value}"
                )

            tags.append(UnifiedTag(ident, index, _type, value))

            if ident == "Header_End":
                break

    except EOFError as err:
        raise EOFError(
            f"Reached EOF before the unified header could be read completely."
        )

    return tags
