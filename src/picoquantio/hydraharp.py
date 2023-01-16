import io
from typing import Dict, Tuple, Union
import warnings

import numpy as np
import numpy.lib.recfunctions as rfn

import picoquantio

_base_resolution = 1e-12
_t2_overflow = 33552000
_t3_overflow = 1024
_modes = {
    "interactive": 0,
    "reserved": 1,
    "t2": 2,
    "t3": 3,
}


def load_v10_t2(rawdata: io.BufferedReader) -> picoquantio.T2Records:
    overflow_channel = 2**6 - 1
    raw = rawdata.read()
    record_size = np.dtype("uint32").itemsize
    n_records = len(raw) // record_size
    spare_bytes = len(raw) - n_records * record_size
    if spare_bytes:
        warnings.warn(
            "Got {n_records} but had {spare_bytes} spare bytes. The data may be corrupt"
        )
    records = np.frombuffer(raw, dtype="uint32", count=n_records)

    # see ht2 documentation for the /2: counts are recorded at 0.5ps resolution,
    # and we are converting to 1ps
    timestamps = (
        np.bitwise_and(2**25 - 1, np.right_shift(records, 0)).astype(
            picoquantio._dtype_time
        )
        // 2
    )
    channels = np.bitwise_and(2**6 - 1, np.right_shift(records, 25)).astype(
        picoquantio._dtype_time
    )
    specials = np.bitwise_and(2**1 - 1, np.right_shift(records, 31)).astype(bool)

    picoquantio._correct_overflow(
        timestamps, channels, overflow_channel, _t2_overflow // 2, False
    )
    return {
        "channels": channels,
        "specials": specials,
        "timestamps": timestamps,
    }


def load_v20_t2(rawdata: io.BufferedReader) -> picoquantio.T2Records:
    overflow_channel = 2**6 - 1
    raw = rawdata.read()
    record_size = np.dtype("uint32").itemsize
    n_records = len(raw) // record_size
    spare_bytes = len(raw) - n_records * record_size
    if spare_bytes:
        warnings.warn(
            "Got {n_records} but had {spare_bytes} spare bytes. The data may be corrupt"
        )
    records = np.frombuffer(raw, dtype="uint32", count=n_records)

    timestamps = np.bitwise_and(2**25 - 1, np.right_shift(records, 0)).astype(
        picoquantio._dtype_time
    )
    channels = np.bitwise_and(2**6 - 1, np.right_shift(records, 25)).astype(
        picoquantio._dtype_time
    )
    specials = np.bitwise_and(2**1 - 1, np.right_shift(records, 31)).astype(bool)

    picoquantio._correct_overflow(
        timestamps, channels, overflow_channel, _t2_overflow, True
    )
    return {
        "channels": channels,
        "specials": specials,
        "timestamps": timestamps,
    }


def load_v10_t3(rawdata: io.BufferedReader) -> picoquantio.T3Records:
    raise NotImplementedError


def load_v20_t3(rawdata: io.BufferedReader) -> picoquantio.T3Records:
    raise NotImplementedError


_loaders: Dict = {
    ("1.0", _modes["t2"]): load_v10_t2,
    ("1.0", _modes["t3"]): load_v10_t3,
    ("2.0", _modes["t2"]): load_v20_t2,
    ("2.0", _modes["t3"]): load_v20_t3,
}


def read_hh_header(rawdata: io.BufferedReader) -> picoquantio.Header:
    header_dtype = np.dtype(
        [
            ("Ident", "S16"),
            ("FormatVersion", "S6"),
            ("CreatorName", "S18"),
            ("CreatorVersion", "S12"),
            ("FileTime", "S18"),
            ("CRLF", "S2"),
            ("Comment", "S256"),
            ("NumberOfCurves", "int32"),
            ("BitsPerRecord", "int32"),  # bits in each T3 record
            ("ActiveCurve", "int32"),
            ("MeasurementMode", "int32"),
            ("SubMode", "int32"),
            ("Binning", "int32"),
            ("Resolution", "double"),  # in ps
            ("Offset", "int32"),
            ("Tacq", "int32"),  # in ms
            ("StopAt", "uint32"),
            ("StopOnOvfl", "int32"),
            ("Restart", "int32"),
            ("DispLinLog", "int32"),
            ("DispTimeAxisFrom", "int32"),
            ("DispTimeAxisTo", "int32"),
            ("DispCountAxisFrom", "int32"),
            ("DispCountAxisTo", "int32"),
        ]
    )
    header = np.fromfile(rawdata, dtype=header_dtype, count=1)
    assert header["Ident"] == b"HydraHarp"
    assert header["FormatVersion"][0] in {b"1.0", b"2.0"}

    dispcurve_dtype = np.dtype(
        [("DispCurveMapTo", "int32"), ("DispCurveShow", "int32")]
    )
    dispcurve = np.fromfile(rawdata, dispcurve_dtype, count=8)

    params_dtype = np.dtype(
        [("ParamStart", "f4"), ("ParamStep", "f4"), ("ParamEnd", "f4")]
    )
    params = np.fromfile(rawdata, params_dtype, count=3)

    repeat_dtype = np.dtype(
        [
            ("RepeatMode", "int32"),
            ("RepeatsPerCurve", "int32"),
            ("RepeatTime", "int32"),
            ("RepeatWaitTime", "int32"),
            ("ScriptName", "S20"),
        ]
    )
    repeatgroup = np.fromfile(rawdata, repeat_dtype, count=1)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Hardware information header
    hw_dtype = np.dtype(
        [
            ("HardwareIdent", "S16"),
            ("HardwarePartNo", "S8"),
            ("HardwareSerial", "int32"),
            ("nModulesPresent", "int32"),
        ]
    )  # 10
    hardware = np.fromfile(rawdata, hw_dtype, count=1)

    hw2_dtype = np.dtype([("ModelCode", "int32"), ("VersionCode", "int32")])
    hardware2 = np.fromfile(rawdata, hw2_dtype, count=10)

    hw3_dtype = np.dtype(
        [
            ("BaseResolution", "double"),
            ("InputsEnabled", "uint64"),
            ("InpChansPresent", "int32"),
            ("RefClockSource", "int32"),
            ("ExtDevices", "int32"),
            ("MarkerSettings", "int32"),
            ("SyncDivider", "int32"),
            ("SyncCFDLevel", "int32"),
            ("SyncCFDZeroCross", "int32"),
            ("SyncOffset", "int32"),
        ]
    )
    hardware3 = np.fromfile(rawdata, hw3_dtype, count=1)

    # Channels' information header
    input_dtype = np.dtype(
        [
            ("InputModuleIndex", "int32"),
            ("InputCFDLevel", "int32"),
            ("InputCFDZeroCross", "int32"),
            ("InputOffset", "int32"),
            ("InputRate", "int32"),
        ]
    )
    inputs = np.fromfile(rawdata, input_dtype, count=hardware3["InpChansPresent"][0])

    # Time tagging mode specific header
    ttmode_dtype = np.dtype(
        [
            ("SyncRate", "int32"),
            ("StopAfter", "int32"),
            ("StopReason", "int32"),
            ("ImgHdrSize", "int32"),
            ("nRecords", "uint64"),
        ]
    )
    ttmode = np.fromfile(rawdata, ttmode_dtype, count=1)

    # Special header for imaging. How many of the following ImgHdr
    # array elements are actually present in the file is indicated by
    # ImgHdrSize above.
    ImgHdr = np.fromfile(rawdata, dtype="int32", count=ttmode["ImgHdrSize"][0])

    return picoquantio._merge_arrays_to_header(
        [
            header,
            dispcurve,
            params,
            repeatgroup,
            hardware,
            hardware2,
            hardware3,
            inputs,
            ttmode,
            ImgHdr,
        ]
    )


def _load_hxx(
    path: picoquantio.Path,
) -> Tuple[picoquantio.Header, picoquantio.T2Records]:
    path = picoquantio._sanitize_path(path)
    with path.open("rb") as rawdata:
        peek = rawdata.peek(22)
        identity = peek[:16].rstrip(b"\x00").decode()
        version = peek[16:22].rstrip(b"\x00").decode()
        if identity != "HydraHarp":
            raise ValueError(
                f"This is not a HydraHarp hhd, ht2, or ht3 file: identity={identity}, version={version}"
            )
        if version in {"1.0", "2.0"}:
            header = read_hh_header(rawdata)
            mode = header["MeasurementMode"]
        else:
            raise ValueError(f"Unrecognized Hydraharp version={version}")

        key = (version, mode)
        if key not in _loaders:
            raise NotImplementedError(
                f"Loader not available for for Hydraharp version={version}, mode={mode}"
            )

        loader = _loaders[key]
        return header, loader(rawdata)


def _get_record_loader(hw_version, mode) -> picoquantio.RecordLoader:
    """
    Return the appropriate loader for the hardware version and measurement mode.

    :param hw_version: the harware version
    :param mode: the measurement mode number, one of {_modes}
    :return: a loader for the data
    """
    if (hw_version, mode) in _loaders:
        return _loaders[(hw_version, mode)]

    raise NotImplementedError(
        f"Could not identify loader for HydraHarp version={hw_version}, mode={mode}"
    )
