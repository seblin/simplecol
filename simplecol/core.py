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

from collections.abc import Iterable, Mapping
from contextlib import suppress
from itertools import zip_longest
from math import ceil
from shutil import get_terminal_size

__all__ = ["Item", "Line", "Frame", "FrameBuilder"]

class Item:
    def __init__(self, string, min_width=None, adjuster=str.ljust):
        self.string = string
        self.min_width = min_width
        self.adjuster = adjuster

    def __len__(self):
        string_width = len(self.string)
        if self.min_width is None:
            return string_width
        return max(self.min_width, string_width)

    def __str__(self):
        return self.adjuster(self.string, len(self))

    def get_parted(self):
        if (part_size := self.min_width) is None:
            part_size = len(self.string)
        options = (self.min_width, self.adjuster)
        return [Item(self.string[i:(i + part_size)], *options)
                for i in range(0, len(self.string), part_size)]

    @classmethod
    def from_cached_value(cls, value, cache={}):
        try:
            return cache[value]
        except (KeyError, TypeError):
            item = cls(str(value))
            with suppress(TypeError):
                cache[value] = item
            return item


class Line:
    def __init__(self, items, spacer="  "):
        self.items = items
        self.spacer = spacer
        self.adjusters = {"left": str.ljust, "right": str.rjust}

    def __len__(self):
        if not self.items:
            return 0
        total_spacing = (len(self.items) - 1) * len(self.spacer)
        return sum(map(len, self.items)) + total_spacing

    def __str__(self):
        return self.spacer.join(
            map(str, self.items)
        ).rstrip()

    def __iter__(self):
        return iter(self.items)

    def set_min_widths(self, min_widths):
        if not isinstance(min_widths, Iterable):
            min_widths = len(self.items) * [min_widths]
        for item, width in zip(self.items, min_widths):
            item.min_width = width

    def set_alignment(self, side):
        if not (adjuster := self.adjusters.get(side)):
            raise ValueError(f"Unknown text alignment: {side!r}")
        for item in self.items:
            item.adjuster = adjuster

    def iter_wrapped(self):
        parted_items = (item.get_parted() for item in self.items)
        for line_chunk in zip_longest(*parted_items):
            items = [item or Item("", orig.min_width, orig.adjuster)
                     for item, orig in zip(line_chunk, self.items)]
            yield Line(items, self.spacer)

    @classmethod
    def from_cached_values(cls, values):
        return cls([Item.from_cached_value(v) for v in values])


class Frame:
    def __init__(self, lines):
        self.lines = lines
        self.clear_widths()
        self.justify()

    def __len__(self):
        return max(map(len, self.lines), default=0)

    def __str__(self):
        return "\n".join(
            str(wrapped_line) for line in self.lines
            for wrapped_line in line.iter_wrapped()
        )

    def __iter__(self):
        return iter(self.lines)

    def set_spacer(self, spacer):
        if isinstance(spacer, int):
            spacer = spacer * " "
        for line in self.lines:
            line.spacer = spacer

    def align(self, side):
        for line in self.lines:
            line.set_alignment(side)

    def get_column_widths(self):
        columns = zip_longest(*self.lines, fillvalue="")
        return [max(map(len, items)) for items in columns]

    def clear_widths(self):
        for line in self.lines:
            line.set_min_widths(None)

    def justify(self, column_widths=None):
        if column_widths is None:
            column_widths = self.get_column_widths()
        for line in self.lines:
            line.set_min_widths(column_widths)

    def shrink_columns(self, line_width):
        offset = len(self) - line_width
        widths = self.get_column_widths()
        while offset > 0 and any(w > 1 for w in widths):
            pairs = zip_longest(widths, widths[1:], fillvalue=1)
            for i, (width, next_width) in enumerate(pairs):
                if width > next_width:
                    new_width = max(width - offset, next_width)
                    offset -= width - new_width
                    widths[i] = new_width
        self.justify(widths)

    @classmethod
    def from_chunks(cls, chunks):
        return cls([Line.from_cached_values(chunk) for chunk in chunks])


class FrameBuilder:
    def __init__(self, spacer="  ", line_width=None, vertical=True):
        self.spacer = spacer
        self.line_width = line_width
        self.vertical = vertical

    def get_max_width(self):
        if self.line_width is None:
            return get_terminal_size().columns
        return self.line_width

    def build_frame(self, line_chunks):
        frame = Frame.from_chunks(line_chunks)
        frame.set_spacer(self.spacer)
        return frame

    def get_chunked(self, values, max_columns):
        if self.vertical:
            num_lines = ceil(len(values) / max_columns)
            line_chunks = [values[i::num_lines] for i in range(num_lines)]
        else:
            rng = range(0, len(values), max_columns)
            line_chunks = [values[i:(i + max_columns)] for i in rng]
        return self.build_frame(line_chunks)

    def sequence_to_frame(self, values):
        width = self.get_max_width()
        max_columns = min(width, len(values))
        while max_columns > 0:
            frame = self.get_chunked(values, max_columns)
            if len(frame) <= width:
                return frame
            # Chunking is free to result in a lower number
            # of columns than requested. We rely on that
            # result to avoid some unnecessary extra loops.
            max_columns = len(frame.get_column_widths()) - 1
        return self.get_chunked(values, 1)

    def mapping_to_frame(self, mapping):
        if self.vertical:
            line_chunks = mapping.items()
        else:
            line_chunks = [mapping.keys(), mapping.values()]
        frame = self.build_frame(line_chunks)
        frame.shrink_columns(self.get_max_width())
        return frame

    def get_frame(self, values):
        if isinstance(values, Mapping):
            return self.mapping_to_frame(values)
        return self.sequence_to_frame(list(values))
