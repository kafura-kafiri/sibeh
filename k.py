"""
khob in ja ye seri kar darim ke emrooz anjam midim
1. ba db + threshold darmiarim ke aya < ya >
2. un predicted binary search.
3. time user -> set new k for each hang

from start -> we have max of k from boss inserted ->
"""

from ctypes import Structure, c_float, c_double, c_int
from config import common
from datetime import datetime


class K(Structure):
    _fields_ = [
        ('value', c_float),
        ('_date', c_double),
        ('prev_value', c_float),
        ('prev_flag', c_int),
        ('max_value', c_float)
    ]


async def ratio(hang):
    k = common.flash.get_khang(hang.encode())
    now = datetime.now()
    # if no entry _date: -inf
    requests = await common.path.find({
        'hang': hang,
        '_date': {
            'gte': datetime.fromtimestamp(k._date),
            'lt': now
        }
    }).count()

    acks = await common.path.find({
        'hang': hang,
        '_date': {
            'gte': datetime.fromtimestamp(k._date),
            'lt': now
        },
        # acks
    }).count()
    return 0 if acks / requests > .99 else 1


async def binary_search(hang):
    k = common.flash.get_khang(hang.encode())
    now = datetime.now()
    _1_value, _1_flag, _0_value, _0_flag = k.prev_value, k.prev_flag, k.value, await ratio(hang)
    if _0_value > _1_value:
        _1_value, _1_flag, _0_value, _0_flag = _0_value, _0_flag, _1_value, _1_flag
    flag = _1_flag * 2 + _0_flag
    value = 0
    if flag == 0:
        pass  # between min and 1
    if flag == 1:
        pass  # khundan be ham
    if flag == 2:
        pass  # nakhundan be ham
    if flag == 3:
        pass  # between 1 and max
    common.flash.set_khang(hang.encode(), value, now.timestamp())
    return value

