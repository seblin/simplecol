# Copyright (c) 2020, 2021 Sebastian Linke

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections.abc import Mapping
from fnmatch import translate
from io import IOBase
from locale import strxfrm
from pathlib import Path
import re

__all__ = [
    "prepare", "extract", "get_filenames", "read_lines",
    "get_column", "get_filtered", "get_unique", "get_sorted"
]

def prepare(values, colidx=None, pattern=None, unique=False, sort=False):
    values = extract(values)
    if colidx is not None:
        values = get_column(values, colidx)
    if pattern is not None:
        values = get_filtered(values, pattern)
    if unique and not isinstance(values, Mapping):
        values = get_unique(values)
    if sort:
        values = get_sorted(values)
    return values

def extract(source):
    if isinstance(source, Path):
        return get_filenames(source)
    if isinstance(source, IOBase):
        return read_lines(source)
    return source

def get_filenames(path):
    if not path.is_dir():
        return [path]
    return list(path.iterdir())

def read_lines(stream, skip_empty=True, skip_comments=True):
    lines = (line.rstrip() for line in stream)
    if skip_empty:
        lines = (line for line in lines if line)
    if skip_comments:
        lines = (line for line in lines if not line.startswith("#"))
    return list(lines)

def get_column(lines, index):
    return [line.split()[index] for line in lines]

def get_unique(values):
    try:
        # Python preserves the order when keys
        # are added to a dict. Can not use a set,
        # since its ordering is undefined.
        result = list(dict.fromkeys(values))
    except TypeError:
        # Fallback for unhashable types. Should be
        # be a relatively rare case, so no further
        # optimizations are made for this.
        result = []
        for value in values:
            if value not in result:
                result.append(value)
    return result

def get_sorted(values):
    try:
        # Locale-dependent sorting.
        result = sorted(values, key=strxfrm)
    except TypeError:
        # Fallback to "default" sorting when dealing
        # with non-string values (e.g. numbers).
        result = sorted(values)
    return set_result(values, result)

def get_filtered(values, pattern):
    if not isinstance(pattern, re.Pattern):
        pattern = re.compile(translate(pattern), re.IGNORECASE)
    result = filter(pattern.fullmatch, values)
    return set_result(values, result)

def set_result(values, result):
    if isinstance(values, Mapping):
        return {key: values[key] for key in result}
    return list(result)
