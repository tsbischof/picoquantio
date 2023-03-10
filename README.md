# picoquantio: Read files generated by PicoQuant hardware
[![PyPI Last Release](https://img.shields.io/pypi/v/picoquantio.svg)](https://pypi.org/project/picoquantio)
[![Package Status](https://img.shields.io/pypi/status/picoquantio.svg)](https://pypi.org/project/picoquantio/)
[![License](https://img.shields.io/pypi/l/picoquantio.svg)](https://github.com/tsbischof/picoquantio/blob/main/LICENSE)
[![Downloads](https://static.pepy.tech/personalized-badge/picoquantio?period=month&units=international_system&left_color=black&right_color=orange&left_text=PyPI%20downloads%20per%20month)](https://pepy.tech/project/picoquantio)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

See also [libpicoquant](https://github.com/tsbischof/libpicoquant) for the C equivalent.

## Main features
* read data from phu, ptu, hhd, ht2, ht3, phd, pt2, pt3, thd, t3r formats
* automatic file type detection
* greedy and lazy loading
* pure Python implementation

## Getting started
The source code is hosted on GitHub at: [https://github.com/tsbischof/picoquantio](https://github.com/tsbischof/picoquantio)

The latest released version is available on pip:
```
pip install picoquantio
```

## Documentation
The official documentation is hosted on [readthedocs](https://picoquantio.readthedocs.io)

## Examples
The library can either be used in Python programs, or as a standalone command-line tool.

### Developer API

```
import picoquantio
t3 = picoquantio.load('data.ht3')
```

### Command-line interface

```
$ picoquant --file-in data.ht3
[...]
```

## Dependencies
* numpy

## License
[BSD 3-clause](https://github.com/tsbischof/picoquantio/LICENSE)

## Contibuting
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

Development is active on [Github](https://github.com/tsbischof/picoquantio)
