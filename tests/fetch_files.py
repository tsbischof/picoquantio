import os
import pathlib
import urllib.parse

import requests

PICOQUANT_SAMPLE_DATA_REPO = "https://github.com/tsbischof/picoquant-sample-data"
SAMPLE_DATA_ROOT = pathlib.Path(os.path.dirname(__file__)) / pathlib.Path("data")


def fetch(filename: str):
    path = SAMPLE_DATA_ROOT / pathlib.Path(filename)
    if not os.path.exists(path):
        url = urllib.parse.urljoin(PICOQUANT_SAMPLE_DATA_REPO + "/raw/main/", filename)
        req = requests.get(url)
        req.raise_for_status()
        os.makedirs(path.parent, exist_ok=True)
        with path.open("wb") as dst:
            dst.write(req.content)

    return path
