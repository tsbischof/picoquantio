import collections
import io
import mmap
import struct
import time
from typing import Any, Dict, List, Optional, Union
import warnings

import numpy as np

from .constants import *

UnifiedTag = collections.namedtuple("UnifiedTag", ["ident", "index", "type", "value"])
UnifiedTagStruct = struct.Struct("<32siI8s")
TagDict = Dict[str, Union[Any, List[Any]]]


def read_tags(rawdata: io.BufferedReader) -> TagDict:
    """
    Read tags from the header of a ptu or phu file, starting after
    the identity header (i.e. from offset 16). The tags are grouped by common
    ident into lists, typically representing the different channels or curves.

    :param rawdata: the raw data from the file, opened in binary format as a buffered reader
    :return: a dict of tags mapping to lists of values
    """
    tags = read_tags_to_list(rawdata)
    return _tag_list_to_dict(tags)


def read_tags_to_list(rawdata: io.BufferedReader) -> List[UnifiedTag]:
    """
    Read tags from the header of a ptu or phu file, starting after
    the identity header (i.e. from offset 16)

    :param rawdata: the raw data from the file, opened in binary format as a buffered reader
    :return: list of tags
    """
    tags = list()
    try:
        while True:
            ident, index, _type, value = UnifiedTagStruct.unpack(
                rawdata.read(UnifiedTagStruct.size)
            )
            ident = ident.rstrip(b"\x00").decode("utf-8")
            if _type == PU_TAG_Empty8:
                value = None
            elif _type == PU_TAG_Bool8:
                value = bool(struct.unpack("<q", value)[0])
            elif _type == PU_TAG_Int8:
                (value,) = struct.unpack("<q", value)
            elif _type == PU_TAG_BitSet64:
                (value,) = struct.unpack("<q", value)
            elif _type == PU_TAG_Color8:
                (value,) = struct.unpack("<q", value)
            elif _type == PU_TAG_Float8:
                (value,) = struct.unpack("<d", value)
            elif _type == PU_TAG_TDateTime:
                (float_value,) = struct.unpack("<d", value)
                value = time.gmtime(int((float(float_value) - 25569) * 86400))
            elif _type == PU_TAG_Float8Array:
                value = rawdata.read(struct.calcsize(f"{value}d"))
            elif _type == PU_TAG_AnsiString:
                (size,) = struct.unpack("<q", value)
                value = (
                    rawdata.read(struct.calcsize(f"{size}c"))
                    .rstrip(b"\x00")
                    .decode("utf-8")
                )
            elif _type == PU_TAG_WideString:
                (size,) = struct.unpack("<q", value)
                value = (
                    rawdata.read(struct.calcsize(f"{size}c"))
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


def _tag_list_to_dict(tags: List[UnifiedTag]) -> TagDict:
    """
    Create a dict of tag.ident -> [tag.value]

    :param tags: a list of UnifiedTag objects
    :return: a dict mapping the tag.ident to the tag values
    """
    result = dict()
    for tag in tags:
        if tag.index < 0:
            if tag.ident in result:
                raise KeyError(f"Found a duplicate tag for ident={tag.ident} ({tag})")
            else:
                result[tag.ident] = tag.value
        else:
            if tag.index == 0:
                if tag.ident in result:
                    raise ValueError(
                        f"Found a tag with index 0 which was not the first of that ident ({tag})"
                    )

                result[tag.ident] = [tag.value]
            else:
                if tag.index == len(result[tag.ident]):
                    result[tag.ident].append(tag.value)
                else:
                    raise ValueError(
                        f"Got an index of {tag.index} for a tag, but we are at len={len(result[tag.ident])} (tag={tag}). Either the tags are out of order or there is some duplication."
                    )

    return result
