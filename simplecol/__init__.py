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

import csv
import io
import sys
from collections.abc import Sequence

__author__ = "Sebastian Linke"
__version__ = "0.1-dev"
__license__ = "MIT License"

__all__ = [
    "columnize", "cprint", "Alignment", "Column", "Model", "Screen", "Table",
    "_read_columns_from_text_files", "_read_rows_from_csv_files", "_run_demo"
]

# Import new architecture components
from .core import Alignment, Column, Model, Screen, Table
from .preprocessing import prepare


# Legacy Frame class for backward compatibility  
class Frame:
    def __init__(self, model):
        self.model = model
        self.screen = Screen(model)
    
    def align(self, side):
        # Convert side to Alignment
        if side == "left":
            align = Alignment.LEFT
        elif side == "right":
            align = Alignment.RIGHT
        else:
            align = Alignment.LEFT
        
        # Apply alignment to all columns
        columns = self.model.columns
        for col in columns:
            col.align = align
    
    def __str__(self):
        return str(self.screen)


# Legacy FrameBuilder for backward compatibility 
class FrameBuilder:
    def __init__(self, spacer="  ", line_width=None, vertical=True):
        self.spacer = spacer
        self.line_width = line_width
        self.vertical = vertical

    def get_frame(self, values):
        # Simple implementation for backward compatibility
        if isinstance(values, list) and values:
            model = Model.from_columns([values])
            return Frame(model)
        return Frame(Model([]))


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


def _read_columns_from_text_files(files: Sequence[str], delimiter: str = ",") -> list[list[str]]:
    """Read columns from text files for CLI."""
    if not files:
        files = ["-"]  # stdin
    
    columns = []
    for filename in files:
        if filename == "-":
            stream = sys.stdin
        else:
            stream = open(filename, 'r')
        
        try:
            for line in stream:
                line = line.rstrip('\n\r')
                if line:
                    # Split by delimiter and treat each part as a separate column
                    parts = line.split(delimiter)
                    # Extend columns list as needed
                    while len(columns) < len(parts):
                        columns.append([])
                    # Add parts to respective columns
                    for i, part in enumerate(parts):
                        columns[i].append(part.strip())
        finally:
            if filename != "-":
                stream.close()
    
    return columns


def _read_rows_from_csv_files(files: Sequence[str], delimiter: str = ",") -> list[list[str]]:
    """Read rows from CSV files for CLI."""
    if not files:
        files = ["-"]  # stdin
    
    rows = []
    for filename in files:
        if filename == "-":
            stream = sys.stdin
        else:
            stream = open(filename, 'r')
        
        try:
            reader = csv.reader(stream, delimiter=delimiter)
            for row in reader:
                rows.append(row)
        finally:
            if filename != "-":
                stream.close()
    
    return rows


def _run_demo():
    """Run a demonstration of the columnization features."""
    print("SimpleCOL Demo")
    print("=" * 50)
    
    # Demo 1: Simple list
    print("\n1. Simple list:")
    data = ["apple", "banana", "cherry", "date", "elderberry"]
    model = Model.from_columns([data], align=Alignment.LEFT)
    screen = Screen(model)
    print(screen)
    
    # Demo 2: CSV-like data with headers
    print("\n2. CSV data with headers:")
    rows = [
        ["Name", "Age", "City"],
        ["Alice", "25", "New York"],
        ["Bob", "30", "Los Angeles"],
        ["Charlie", "35", "Chicago"]
    ]
    model = Model.from_rows(rows, headers=True)
    table = Table(model, show_sep=True)
    print(table)
    
    # Demo 3: Auto-alignment
    print("\n3. Auto-alignment (numeric data):")
    numbers = ["123", "45", "6789", "0"]
    model = Model.from_columns([numbers])
    screen = Screen(model)
    print(screen)
