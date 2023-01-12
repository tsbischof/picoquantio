import argparse

import picoquantio


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file-in",
        "-i",
        type=str,
        help="""Read data from this file. The type will be determined automatically, unless otherwise specified with --hardware. 

If this option is not used, data will be read from stdin""",
    )
    parser.add_argument("--file-out", "-o", type=str, help="Write data to this file.")
    parser.add_argument(
        "--header-only",
        "-H",
        action="store_true",
        help="Print the header in json format",
    )
    parser.add_argument(
        "--resolution-only",
        "-r",
        action="store_true",
        help="Only print the time resolution of the measurement(s)",
    )
    parser.add_argument(
        "--hardware",
        "-w",
        type=str,
        help="Treat the raw data as though it comes from the specified model of hardware. This mode assumes that no header exists, and is appropriate for use when data are pulled directly from the PicoQuant hardware using their API. You will also need to specify the version of the data format.",
    )
    parser.add_argument(
        "--data-version",
        "-d",
        type=str,
        help="Treat the raw data as though it comes from the hardware directly, with the specified version. Use along wtih --hardware.",
    )
    parser.add_argument(
        "--mode",
        "-m",
        type=str,
        help="Treat the raw data as though it comes from the hardware directly, with the specified measurement mode (e.g. t2, t3, hist). Use along with --hardware",
    )

    args = parser.parse_args()
