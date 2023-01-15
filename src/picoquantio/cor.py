"""PicoQuant .cor files"""
import pathlib
from typing import Dict, Tuple, Union
import warnings

import numpy as np
import pandas as pd


def load_cor(path: Union[pathlib.Path, str]) -> Tuple[Dict[str, str], pd.DataFrame]:
    """
    Read data from a PicoQuant .cor file.

    This format consists of a metadata header, a blank line, then a
    whitespace-delimited data header followed by a data array.::

       TTTR Correlator Export
       PicoHarp Software version 3.0.0.3 format version 3.0
       Raw data: c:\\users\\baker lab 432-a\\desktop\\grant fcs\\default_013.ptu
       Recorded: 16/12/22 17:40:13
       Mode: T2
       Routing Mask A: 0 1 0 0 0
       Routing Mask B: 1 0 0 0 0
       Start time [s]: 0.000000
       Time span [s]: 7.545534
       Counts A: 382989
       Counts B: 523316
       Tau resolution [s]: 0.00000002500000

        taustep       tau/s        G(A,A)    G(B,B)    G(A,B)
             6     0.0000001500    0.8375    0.3556    0.1708
             7     0.0000001750    0.6503    0.2652    0.1445
             9     0.0000002250    0.5680    0.2173    0.1264
            11     0.0000002750    0.4836    0.1594    0.1614
            13     0.0000003250    0.3241    0.1528    0.1486
            15     0.0000003750    0.2819    0.1236    0.1641
            17     0.0000004250    0.3591    0.1467    0.1102
       [...]

    :param path: the path to the cor file
    :return: a tuple with two elements:
         1. dict of metadata
         2. pd.DataFrame with the correlation data
    """
    if isinstance(path, str):
        path = pathlib.Path(path)

    corfile = path.open("r", encoding="utf-8")
    header = dict()
    for index, line in enumerate(corfile):
        line = line.strip()
        if index == 0:
            header["identity"] = line
        elif index == 1:
            header["version"] = line
        elif line == "":
            break
        else:
            key, *value = line.split(": ")
            header[key] = ": ".join(value)

    if header["identity"] != "TTTR Correlator Export":
        raise ValueError(
            f'Error while reading {path.name}. Expected the first line to be "TTTR Correlator Export", got "{header["identity"]}"'
        )

    data = pd.read_csv(corfile, delim_whitespace=True)
    return header, data
