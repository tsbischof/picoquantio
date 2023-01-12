import picoquantio

from . import fetch_files


def test_hh_v30_t2_ptu():
    filename = fetch_files.fetch("hydraharp/v30_t2.ptu")
    data = picoquantio.load(filename)
