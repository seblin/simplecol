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

__author__ = "Sebastian Linke"
__version__ = "0.1-dev"
__license__ = "MIT License"

__all__ = ["columnize", "cprint"]

from .core import FrameBuilder
from .preprocessing import prepare

def columnize(
    values, spacer="  ", width=None, vertical=True, side="left",
    index=None, pattern=None, unique=False, sort=False
):
    """
    Prepare values and return them in a new frame.  Printing the
    frame object will give you the columnized output.

    :values:    An iterable containing the values to be columnized.
                Can be a sequence, mapping or file-like object.

    :spacer:    The column separator.  Can be a string cotaining the
                desired characters or an integer defining the number
                of spaces between two columns.

    :width:     Line width for the resulting output.  If `None`
                (the default), it uses the current terminal width.

    :vertical:  This determines how values are placed in each column.
                `True` means placing them under each other (vertical).
                `False` means placing them side by side.

    :side:      The text aligment for each value ("left" or "right").

    :index:     If not `None`, split values into parts at whitespace
                and select just the part at `index` for columnizing.
                Can be useful when dealing with pre-formatted input.

    :pattern:   If not `None`, it defines the filter criteria for the
                values to be used.  Can be a string with shell-style
                wildcards (i.e. "*" and "?") or a precompiled regular
                expression (then wildcards have no special meaning).

    :unique:    If `True`, the first occurrence of a value will be
                columnized, but any other occurrences are ignored.

    :sort:      Sort the values with respect to the environment's
                locale settings.  If values are given as a mapping,
                then sorting is based on the mapping's keys.
    """
    builder = FrameBuilder(spacer, width, vertical)
    frame = builder.get_frame(
        prepare(values, index, pattern, unique, sort)
    )
    frame.align(side)
    return frame

def cprint(values, **options):
    """
    Shorthand for printing values via columnize().
    See its docstring for details about the available options.
    """
    print(columnize(values, **options))
