_tttr_overflow = 65536
_modes = {"interactive": 0, "continuous": 1, "tttr": 2}


def load():
    raise NotImplementedError


def _get_record_loader(version, mode):
    raise NotImplementedError
