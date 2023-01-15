import pytest

import picoquantio

from . import fetch_files


def test_cor():
    filename = fetch_files.fetch("picoharp/v30.cor")

    header, data = picoquantio.load_cor(filename)
    assert header["identity"] == "TTTR Correlator Export"
    assert header["version"] == "PicoHarp Software version 3.0.0.3 format version 3.0"
    assert float(header["Tau resolution [s]"]) == 25e-9
    assert list(data.keys()) == ["taustep", "tau/s", "G(A,A)", "G(B,B)", "G(A,B)"]
