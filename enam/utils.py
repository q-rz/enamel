from .header import *

class Dict(dict): # a dict that supports dot indexing
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self

def assert_(cond, err_cls, msg): # customized assertion
    if not cond:
        raise err_cls(msg)

def parse_bool(val: str):
    return val == 'True'

def parse_list(val: str, type_fn = str):
    val = list(map(type_fn, val.split(',')))
    return val

def parse_int_list(val: str):
    return parse_list(val, type_fn = int)

def parse_float_list(val: str):
    return parse_list(val, type_fn = float)
