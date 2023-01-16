import collections
import pathlib
from typing import Iterable, List, Tuple, Union

import picoquantio

_base_resolution = 4e-12
_t2_overflow = 210698240
_t3_overflow = 65536
_modes = {"interactive": 0, "reserved": 1, "t2": 2, "t3": 3}


##PHv20DisplayCurve = collections.namedtuple("PHv20DisplayCurve", ["MapTo", "Show"])
##PHv20Param = collections.namedtuple("PHv20Param", ["Start", "Step", "Stop"])
##PHv20RouterChannel = collections.namedtuple(
##    "PHv20RouterChannel",
##    ["InputType", "InputLevel", "InputEdge", "CFDPresent", "CFDLevel", "CFDZCross"],
##)
##
##PHv20Curve = collections.namedtuple(
##    "PHv20Curve",
##    [
##        "CurveIndex",
##        "TimeOfRecording",
##        "HardwareIdent",
##        "HardwareVersion",
##        "HardwareSerial",
##        "SyncDivider",
##        "CFDZeroCross0",
##        "CFDLevel0",
##        "CFDZeroCross1",
##        "CFDLevel1",
##        "Offset",
##        "RoutingChannel",
##        "ExtDevices",
##        "MeasMode",
##        "SubMode",
##        "P1",
##        "P2",
##        "P3",
##        "RangeNo",
##        "Resolution",
##        "Channels",
##        "AcquisitionTime",
##        "StopAfter",
##        "StopReason",
##        "InpRate0",
##        "InpRate1",
##        "HistCountRate",
##        "IntegralCount",
##        "Reserved",
##        "DataOffset",
##        "RouterModelCode",
##        "RouterEnabled",
##        "RtCh_InputType",
##        "RtCh_InputLevel",
##        "RtCh_InputEdge",
##        "RtCh_CFDPresent",
##        "RtCh_CFDLevel",
##        "RtCh_CFDZeroCross",
##    ],
##)
##
##PHv20Board = collections.namedtuple(
##    "PHv20Board",
##    [
##        "HardwareIdent",
##        "HardwareVersion",
##        "HardwareSerial",
##        "SyncDivider",
##        "CFDZeroCross0",
##        "CFDLevel0",
##        "CFDZeroCross1",
##        "CFDLevel1",
##        "Resolution",
##        "RouterModelCode",
##        "RouterEnabled",
##        "RtCh",
##    ],
##)
##
##PHv20Header = collections.namedtuple(
##    "PHv20Header",
##    [
##        "CreatorName",
##        "CreatorVersion",
##        "FileTime",
##        "CRLF",
##        "Comment",
##        "NumberOfCurves",
##        "BitsPerRecord",
##        "RoutingChannels",
##        "NumberOfBoards",
##        "ActiveCurve",
##        "MeasurementMode",
##        "SubMode",
##        "RangeNo",
##        "Offset",
##        "AcquisitionTime",
##        "StopAt",
##        "StopOnOvfl",
##        "Restart",
##        "DisplayLinLog",
##        "DisplayTimeAxisFrom",
##        "DisplayTimeAxisTo",
##        "DisplayCountAxisFrom",
##        "DisplayCountAxisTo",
##        "DisplayCurve",
##        "Param",
##        "RepeatMode",
##        "RepeatsPerCurve",
##        "RepeatTime",
##        "RepeatWaitTime",
##        "ScriptName",
##        "Brd",
##    ],
##)
##
##PHv20Interactive = collections.namedtuple("PHv20Interactive", ["Curve", "Counts"])
##
##PHv20TTTRHeader = collections.namedtuple(
##    "PHv20TTTRHeader",
##    [
##        "ExtDevices",
##        "Reserved",
##        "InpRate0",
##        "InpRate1",
##        "StopAfter",
##        "StopReason",
##        "NumRecords",
##        "ImgHdrSize",
##        "ImgHdr",
##    ],
##)
##
##PHv20T2Record = collections.namedtuple("PHv20T2Record", ["time", "channel"])
##PHv20T3Record = collections.namedtuple("PHv20T3Record", ["nsync", "dtime", "channel"])
##
##
##def read_header_v20():
##    raise NotImplementedError
##
##
##def read_pt3_records_v20():
##    raise NotImplementedError
##
##
def load():
    raise NotImplementedError


def load_phd():
    raise NotImplementedError


def load_pt2():
    raise NotImplementedError


##def load_pt3(
##    path: Union[pathlib.Path, str]
##):  # -> Tuple[List[Header], Iterable[picoquantio.T3]]:
##    """ """
##    if isinstance(path, str):
##        path = pathlib.Path(path)
##
##    with path.open("rb") as rawdata:
##        ident_header = picoquantio.read_identity_header(rawdata)
##        board_header = read_board_header(rawdata)
##        measurement_header = read_measurement_header(rawdata)
##        records = read_pt3_records(rawdata)
##
##    return [ident_header, board_header, measurement_header], records
##
##
def _get_record_loader(version, mode):
    raise NotImplementedError
