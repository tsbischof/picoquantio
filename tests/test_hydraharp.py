import io
import pytest

import picoquantio

from . import fetch_files


def test_hh_v30_t2_ptu():
    filename = fetch_files.fetch("hydraharp/v30_t2.ptu")

    identity = picoquantio.identify(filename)
    assert identity == picoquantio.Identity("PQTTTR", "1.0.00")

    with open(filename, "rb") as rawdata:
        rawdata.seek(16)
        tags = picoquantio.unified.read_tags(rawdata)
        assert len(tags) == 58
