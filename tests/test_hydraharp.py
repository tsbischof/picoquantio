import io
import pytest

import picoquantio

from . import fetch_files


def test_hh_v10_t2():
    filename = fetch_files.fetch("hydraharp/v10.ht2")
    header, data = picoquantio.load(filename)
    assert data["timestamps"].size == 25


def test_hh_v20_t2():
    filename = fetch_files.fetch("hydraharp/v20.ht2")
    header, data = picoquantio.load(filename)
    assert data["timestamps"].size == 25


def test_hh_v30_t2_ptu():
    filename = fetch_files.fetch("hydraharp/v30_t2.ptu")

    identity = picoquantio.identify(filename)
    assert identity == picoquantio.Identity("PQTTTR", "1.0.00")

    header, data = picoquantio.load(filename)
    assert header["HW_Type"] == "HydraHarp 400"
    assert header["HW_PartNo"] == "930020"
    assert header["CreatorSW_Version"] == "3.0.0.1"
    assert data["timestamps"].size == 435319
    assert data["timestamps"][-1] == 4999617072001


@pytest.mark.xfail
def test_hh_v10_t3():
    filename = fetch_files.fetch("hydraharp/v10.ht3")
    header, data = picoquantio.load(filename)


@pytest.mark.xfail
def test_hh_v20_t3():
    filename = fetch_files.fetch("hydraharp/v20.ht3")
    header, data = picoquantio.load(filename)


@pytest.mark.xfail
def test_hh_v30_t3_ptu():
    filename = fetch_files.fetch("hydraharp/v30_t3.ptu")
    header, data = picoquantio.load(filename)
