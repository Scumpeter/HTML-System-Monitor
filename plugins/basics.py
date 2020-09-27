#!/usr/bin/python3

from enum import Enum

class State(Enum):
    UNDEF = "UNDEF"
    ERROR = "ERR"
    OK = "OK"
    WARNING = "WARN"
    CRITICAL = "CRIT"
    STALE = "STALE"

class SummaryType(Enum):
    UNDEF = "UNDEF"
    TIMESTAMP_FOR_AGE = "TIMESTAMP_FOR_AGE"

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

def ago(timediff):
    """Returns a string in the form 
        n <UNIT> ago

    <UNIT> is the biggest unit that is not 0 of
    Seconds, Minutes, Hours, Days, Weeks
    """
    if timediff < 10:
        return "now"
    units = {
        "second": 1,
        "minute": 60,
        "hour": 60,
        "day": 24,
        "week": 7
    }
    result = timediff
    result_unit = list(units.keys())[0]
    divisor = 1
    for unit, unit_size in units.items():
        divisor = divisor * unit_size
        if (timediff / divisor) >= 1:
            result = timediff / divisor
            result_unit = unit
        else:
            break
    plural_appendix = ""
    if int(result) != 1:
        plural_appendix = "s"
    return "{} {}{} ago".format(int(result), result_unit, plural_appendix)