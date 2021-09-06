# Code written here is not mine.
# Its taken from https://github.com/lmmentel/mendeleev

# -*- coding: utf-8 -*-

from .mendeleev import get_all_elements

_elements = {x.symbol: x for x in get_all_elements()}

globals().update(_elements)

__all__ = list(_elements.keys())