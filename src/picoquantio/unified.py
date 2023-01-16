import collections
import io
import json
import mmap
import struct
import time
from typing import Any, Dict, List, Optional, Union, Tuple
import warnings

import numpy as np

import picoquantio

UnifiedTag = collections.namedtuple("UnifiedTag", ["ident", "index", "type", "value"])
UnifiedTagStruct = struct.Struct("<32siI8s")
TagDict = Dict[str, Union[Any, List[Any]]]

_pu_tag = {
    "Empty8": 0xFFFF0008,
    "Bool8": 0x00000008,
    "Int8": 0x10000008,
    "BitSet64": 0x11000008,
    "Color8": 0x12000008,
    "Float8": 0x20000008,
    "TDateTime": 0x21000008,
    "Float8Array": 0x2001FFFF,
    "AnsiString": 0x4001FFFF,
    "WideString": 0x4002FFFF,
    "BinaryBlob": 0xFFFFFFFF,
}

_pu_record_type = {
    "PH_T3": 0x00010303,
    "PH_T2": 0x00010203,
    "HH_V1_T3": 0x00010304,
    "HH_V1_T2": 0x00010204,
    "HH_V2_T3": 0x01010304,
    "HH_V2_T2": 0x01010204,
    "TH_260_NT3": 0x00010305,
    "TH_260_NT2": 0x00010205,
    "TH_260_PT3": 0x00010306,
    "TH_260_PT2": 0x00010206,
}


def read_magic(rawdata: io.BufferedReader) -> picoquantio.Identity:
    """
    Read the magic bytes from a ptu or phu file, and advance the buffer.

    :param rawdata: an io.BufferedReader of the raw data
    :return: identity of the data
    """
    ident, version = struct.unpack("8s8s", rawdata.read(16))
    return picoquantio.Identity(
        ident.rstrip(b"\x00").decode(), version.rstrip(b"\x00").decode()
    )


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
            if _type == _pu_tag["Empty8"]:
                value = None
            elif _type == _pu_tag["Bool8"]:
                value = bool(struct.unpack("<q", value)[0])
            elif _type == _pu_tag["Int8"]:
                (value,) = struct.unpack("<q", value)
            elif _type == _pu_tag["BitSet64"]:
                (value,) = struct.unpack("<q", value)
            elif _type == _pu_tag["Color8"]:
                (value,) = struct.unpack("<q", value)
            elif _type == _pu_tag["Float8"]:
                (value,) = struct.unpack("<d", value)
            elif _type == _pu_tag["TDateTime"]:
                (float_value,) = struct.unpack("<d", value)
                value = time.gmtime(int((float(float_value) - 25569) * 86400))
            elif _type == _pu_tag["Float8Array"]:
                value = rawdata.read(struct.calcsize(f"{value}d"))
            elif _type == _pu_tag["AnsiString"]:
                (size,) = struct.unpack("<q", value)
                value = (
                    rawdata.read(struct.calcsize(f"{size}c"))
                    .rstrip(b"\x00")
                    .decode("utf-8")
                )
            elif _type == _pu_tag["WideString"]:
                (size,) = struct.unpack("<q", value)
                value = (
                    rawdata.read(struct.calcsize(f"{size}c"))
                    .rstrip(b"\x00")
                    .decode("utf-16")
                )
            elif _type == _pu_tag["BinaryBlob"]:
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


def load_ptu(
    path: picoquantio.Path,
) -> Tuple[picoquantio.Header, picoquantio.Records]:
    """
    Load data from the given ptu file

    :param path: path to the ptu file
    :return: headers and data
    """
    path = picoquantio._sanitize_path(path)
    with path.open("rb") as rawdata:
        identity = read_magic(rawdata)
        tags = read_tags(rawdata)
        tags["magic"] = identity
        hardware = tags["HW_Type"]
        version = tags["HW_Version"]
        mode = tags["Measurement_Mode"]

        if hardware == "HydraHarp 400":
            loader = picoquantio.hydraharp._get_record_loader(version, mode)
        elif hardware == "PicoHarp 300":
            loader = picoquantio.picoharp._get_record_loader(version, mode)
        elif hardware == "TimeHarp 200":
            loader = picoquantio.timeharp._get_record_loader(version, mode)
        else:
            raise ValueError(
                f"Cannot identify hardware with HW_Type={hardware}, HW_Version={version}, Measurement_Mode={mode}"
            )

        return tags, loader(rawdata)
