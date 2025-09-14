"""# Copyright (c) 2020, 2021 Sebastian Linke

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the \"Software\"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""

import csv
import io
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Self

from .helpers import detect_auto_align, read_rows_from_csv, read_rows_from_stream

__all__ = ["Alignment", "Column", "Model", "Screen", "Table"]


class Alignment(StrEnum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    CENTER = "CENTER"

    @classmethod
    def for_items(cls, items: Iterable[Any]) -> Self:
        """Detect appropriate alignment for a sequence of items."""
        name = detect_auto_align(items)
        return cls[name]

@dataclass
class Column:
    data: Sequence[str]
    heading: str | None = None
    width: int | None = None
    align: Alignment | None = None

    def __len__(self) -> int:
        """Return the width needed for this column."""
        if self.width is not None:
            return self.width

        # Consider both data and heading for width calculation
        data_width = max((len(str(item)) for item in self.data), default=0)
        heading_width = len(self.heading) if self.heading else 0
        return max(data_width, heading_width)

    def template(self, align: Alignment | None = None) -> str:
        """Return format template for this column."""
        effective_align = align or self.align or Alignment.LEFT
        width = len(self)

        if effective_align == Alignment.LEFT:
            return f"{{:<{width}}}"
        elif effective_align == Alignment.RIGHT:
            return f"{{:>{width}}}"
        elif effective_align == Alignment.CENTER:
            return f"{{:^{width}}}"
        # Fallback to left
        return f"{{:<{width}}}"

@dataclass
class Model:
    data: Sequence[Column | Sequence[str]]
    headings: Sequence[str] | None = None
    align: Alignment | None = None

    @property
    def columns(self) -> list[Column]:
        """Return list of Column objects, creating them if needed."""
        result = []
        for i, col in enumerate(self.data):
            if isinstance(col, Column):
                result.append(col)
            else:
                # Create Column from sequence data
                heading = None
                if self.headings and i < len(self.headings):
                    heading = self.headings[i]

                # Use auto-detected alignment if none specified
                align = self.align
                if align is None:
                    align = Alignment.for_items(col)

                result.append(Column(data=list(col), heading=heading, align=align))
        return result

    @classmethod
    def from_rows(cls, rows: Sequence[Sequence[str]], headers: bool = False,
                  align: Alignment | None = None) -> Self:
        """Create Model from row data."""
        if not rows:
            return cls(data=[], headings=None, align=align)

        rows_list = list(rows)
        headings = None

        if headers and rows_list:
            headings = list(rows_list[0])
            rows_list = rows_list[1:]

        # If no data rows remain after header extraction, create empty columns
        if not rows_list:
            if headings:
                # Create empty columns for each heading
                empty_columns = [[] for _ in headings]
                return cls(data=empty_columns, headings=headings, align=align)
            else:
                return cls(data=[], headings=headings, align=align)

        # Transpose rows to columns
        max_cols = max(len(row) for row in rows_list)
        columns = []

        for col_idx in range(max_cols):
            column_data = []
            for row in rows_list:
                if col_idx < len(row):
                    column_data.append(row[col_idx])
                else:
                    column_data.append("")
            columns.append(column_data)

        return cls(data=columns, headings=headings, align=align)

    @classmethod
    def from_csv(cls, stream: io.TextIOBase, delimiter: str = ",",
                 headers: bool = False, align: Alignment | None = None) -> Self:
        """Create Model from CSV stream."""
        rows = read_rows_from_csv(stream, delimiter)
        return cls.from_rows(rows, headers=headers, align=align)

    @classmethod
    def from_stream(cls, stream: io.TextIOBase, headers: bool = False,
                    align: Alignment | None = None) -> Self:
        """Create Model from text stream."""
        rows = read_rows_from_stream(stream)
        return cls.from_rows(rows, headers=headers, align=align)

    @classmethod
    def from_columns(cls, columns: Sequence[Sequence[str] | Column],
                     headings: Sequence[str] | None = None,
                     align: Alignment | None = None) -> Self:
        """Create Model from column data."""
        return cls(data=list(columns), headings=headings, align=align)

    def with_aligns(self, aligns: Sequence[Alignment | None]) -> Self:
        """Create new Model with specified alignments per column."""
        new_columns = []
        columns = self.columns

        for i, col in enumerate(columns):
            new_align = aligns[i] if i < len(aligns) else col.align
            new_columns.append(Column(
                data=col.data,
                heading=col.heading,
                width=col.width,
                align=new_align
            ))

        return Model(data=new_columns, headings=self.headings, align=self.align)

class Screen:
    """Renders model data as formatted text."""

    def __init__(self, model: Model, spacer: str = "  "):
        self.model = model
        self.spacer = spacer

    def __str__(self) -> str:
        """Render the model as formatted text."""
        columns = self.model.columns
        if not columns:
            return ""

        lines = []
        max_rows = max(len(col.data) for col in columns) if columns else 0

        # Render data rows
        for row_idx in range(max_rows):
            row_parts = []
            for col in columns:
                if row_idx < len(col.data):
                    value = str(col.data[row_idx])
                else:
                    value = ""

                template = col.template()
                row_parts.append(template.format(value))

            lines.append(self.spacer.join(row_parts).rstrip())

        return "\n".join(lines)

class Table(Screen):
    """Renders model data with optional header row and separator."""

    def __init__(self, model: Model, spacer: str = "  ", show_sep: bool = True):
        super().__init__(model, spacer)
        self.show_sep = show_sep

    def __str__(self) -> str:
        """Render the model with header and optional separator."""
        columns = self.model.columns
        if not columns:
            return ""

        lines = []

        # Check if any column has a heading
        has_headers = any(col.heading for col in columns)

        if has_headers:
            # Render header row
            header_parts = []
            for col in columns:
                heading = col.heading or ""
                template = col.template()
                header_parts.append(template.format(heading))

            lines.append(self.spacer.join(header_parts).rstrip())

            # Render separator line if requested
            if self.show_sep:
                sep_parts = []
                for col in columns:
                    width = len(col)
                    sep_parts.append("-" * width)
                lines.append(self.spacer.join(sep_parts).rstrip())

        # Render data rows
        max_rows = max(len(col.data) for col in columns) if columns else 0
        for row_idx in range(max_rows):
            row_parts = []
            for col in columns:
                if row_idx < len(col.data):
                    value = str(col.data[row_idx])
                else:
                    value = ""

                template = col.template()
                row_parts.append(template.format(value))

            lines.append(self.spacer.join(row_parts).rstrip())

        return "\n".join(lines)