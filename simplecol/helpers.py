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
import re
from collections.abc import Iterable, Sequence
from typing import Any

__all__ = [
    "read_rows_from_stream", "read_rows_from_csv", "_is_numeric_value", 
    "detect_auto_align"
]


def read_rows_from_stream(stream: io.TextIOBase) -> list[list[str]]:
    """Read lines from a text stream and return as rows."""
    rows = []
    for line in stream:
        line = line.rstrip('\n\r')
        if line:  # Skip empty lines
            rows.append([line])
    return rows


def read_rows_from_csv(stream: io.TextIOBase, delimiter: str = ",") -> list[list[str]]:
    """Read CSV data from a stream and return as rows."""
    reader = csv.reader(stream, delimiter=delimiter)
    return [row for row in reader]


def _is_numeric_value(value: str) -> bool:
    """Check if a string represents a numeric value."""
    if not value or value.isspace():
        return False
    
    # Try to parse as int or float
    try:
        float(value)
        return True
    except ValueError:
        return False


def detect_auto_align(items: Iterable[Any]) -> str:
    """Detect appropriate alignment for a sequence of items.
    
    Returns uppercase alignment name: "LEFT", "RIGHT", or "CENTER".
    """
    if not items:
        return "LEFT"
    
    items_list = list(items)
    if not items_list:
        return "LEFT"
    
    # Convert all items to strings for analysis
    str_items = [str(item) for item in items_list]
    
    # Count numeric values
    numeric_count = sum(1 for item in str_items if _is_numeric_value(item))
    total_count = len(str_items)
    
    # If majority are numeric, align right
    if numeric_count > total_count / 2:
        return "RIGHT"
    
    # For center alignment, we need VERY specific conditions:
    # - NO numeric values at all
    # - All items must be exactly the same length
    # - Length should be between 3-8 characters (reasonable for centering)
    # - Must have at least 3 items
    lengths = [len(item) for item in str_items]
    if (lengths and 
        total_count >= 3 and
        numeric_count == 0 and
        len(set(lengths)) == 1 and  # All exactly the same length
        3 <= lengths[0] <= 8):  # Reasonable length for centering
        return "CENTER"
    
    # Default to left alignment
    return "LEFT"