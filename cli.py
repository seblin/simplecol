#!/usr/bin/env python3
"""
CLI helper module for simplecol.

Contains CLIParser (subclass of argparse.ArgumentParser) and a module-level
run(parser) function that orchestrates reading input, building a Model and
rendering the Screen. The run function imports from simplecol at runtime
to avoid circular imports.
"""
import argparse
from collections.abc import Sequence
import sys
from typing import Any


class CLIParser(argparse.ArgumentParser):
    """Encapsulate CLI argument declarations.

    Inherits from argparse.ArgumentParser so the normal parsing behaviour is
    available on the instance. Alignment helpers are provided as methods.
    """

    def __init__(self, argv: Sequence[str] | None = None) -> None:
        self.argv = argv
        super().__init__(
            description=("Format 2D data into aligned columns (reads CSV or "
                         "plain text).")
        )
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """Declare CLI arguments on this ArgumentParser instance."""
        self.add_argument(
            "files",
            nargs="*",
            help="Input file(s). If omitted, read from standard input.",
        )
        self.add_argument(
            "--delimiter",
            "-d",
            default=",",
            help="Delimiter for CSV/plain-text input (default: ',').",
        )
        self.add_argument(
            "--spacer",
            "-s",
            default="  ",
            help="String placed between columns (default: two spaces).",
        )
        self.add_argument(
            "--columns",
            action="store_true",
            help=("Treat each input line as a column (default: each line is "
                  "a row)."),
        )
        self.add_argument(
            "--align",
            default="left",
            help=("Alignment for columns. Single value applied to all "
                  "columns or comma-separated per-column values. Allowed "
                  "values: left, right, center or <, >, ^."),
        )
        self.add_argument(
            "--demo",
            action="store_true",
            help="Run the built-in demo instead of reading stdin/files.",
        )

    def parse_alignment_token(self, token: str):
        """Parse a single alignment token into an Alignment value.

        The return type is kept generic to avoid importing Alignment at module
        import time; callers can compare the returned value to Alignment
        values after importing them.
        """
        t = token.strip().lower()
        if t in ("left", "l", "<"):
            return "LEFT"
        if t in ("right", "r", ">"):
            return "RIGHT"
        if t in ("center", "c", "centre", "^"):
            return "CENTER"
        raise argparse.ArgumentTypeError(f"unknown alignment: {token!r}")

    def parse_alignments(self, arg: str, ncols: int):
        """Parse alignment argument into per-column list.

        Returns a list of alignment tokens (strings); the caller in run()
        will map these to Alignment values imported from simplecol.
        """
        parts = [p.strip() for p in arg.split(",") if p.strip()]
        aligns = [self.parse_alignment_token(p) for p in parts]
        if not aligns:
            return ["LEFT"] * ncols
        if len(aligns) == 1:
            return [aligns[0]] * ncols
        if len(aligns) < ncols:
            aligns.extend([aligns[-1]] * (ncols - len(aligns)))
        return aligns[:ncols]


def run(parser: CLIParser) -> int:
    """Module-level run function that executes the CLI workflow.

    The function imports runtime dependencies from simplecol to avoid circular
    imports at module import time.
    """
    # Import runtime components here to avoid circular imports.
    from simplecol import (
        Alignment,
        Column,
        Model,
        Screen,
        _read_columns_from_text_files,
        _read_rows_from_csv_files,
        _run_demo,
    )

    args = parser.parse_args(parser.argv)

    if args.demo:
        _run_demo()
        return 0

    try:
        if args.columns:
            raw_cols = _read_columns_from_text_files(args.files,
                                                     args.delimiter)
            model = Model([list(col) for col in raw_cols],
                          align=Alignment.LEFT)
            aligns = parser.parse_alignments(args.align, len(raw_cols))
            # map token strings back to Alignment values
            token_to_alignment = {
                "LEFT": Alignment.LEFT,
                "RIGHT": Alignment.RIGHT,
                "CENTER": Alignment.CENTER,
            }
            model = Model(
                [
                    Column(col, align=token_to_alignment[aligns[i]])
                    if not isinstance(col, Column) else col
                    for i, col in enumerate(model.data)
                ],
                align=Alignment.LEFT,
            )
        else:
            rows = _read_rows_from_csv_files(args.files, args.delimiter)
            # parser.parse_alignment_token returns a token string; map it
            token = parser.parse_alignment_token(args.align)
            token_to_alignment = {
                "LEFT": Alignment.LEFT,
                "RIGHT": Alignment.RIGHT,
                "CENTER": Alignment.CENTER,
            }
            model = Model.from_rows(rows,
                                    align=token_to_alignment[token])

            if "," in args.align:
                ncols = len(list(model.data))
                per_col_tokens = parser.parse_alignments(args.align, ncols)
                model = Model(
                    [
                        Column(col, align=token_to_alignment[
                            per_col_tokens[i]
                        ]) if not isinstance(col, Column) else col
                        for i, col in enumerate(model.data)
                    ],
                    align=token_to_alignment[
                        parser.parse_alignment_token(args.align.split(",")[0])
                    ],
                )
    except Exception as exc:
        print(f"Error reading input: {exc}", file=sys.stderr)
        return 2

    screen = Screen(model, spacer=args.spacer)
    print(screen)
    return 0
