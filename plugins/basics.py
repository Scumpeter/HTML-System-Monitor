#!/usr/bin/python3

from enum import Enum

class State(Enum):
    UNDEF = "UNDEF"
    ERROR = "ERR"
    OK = "OK"
    WARNING = "WARN"
    CRITICAL = "CRIT"
    STALE = "STALE"

def sizeof_fmt(num, suffix='B'):
    """Convert a value in bytes to a human readable form and add a binary prefix to it.

    copied from https://stackoverflow.com/a/1094933

    Keyword arguments:
    num -- The number to convert
    suffix -- the suffix to append after the binary prefix (default: B for byte)
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)