#!/usr/bin/env python3
"""
CLI module for simplecol.

Contains CLIParser and a module-level run(parser) function that handles
reading input, building a Model and passing it to the Screen.
"""
from argparse import ArgumentParser, ArgumentTypeError, FileType
from collections.abc import Iterable, Sequence
from pathlib import Path
import sys
from typing import Any

from simplecol import Alignment, Model, Screen

class CLIParser(ArgumentParser):
    def __init__(self):
        super().__init__(description="Format 2D data into aligned columns.")
        self.setup_arguments()

    def setup_arguments(self):
        self.add_argument(
            "infile", nargs="?", type=FileType("r"), default=sys.stdin,
            help="Input file. If omitted, read from standard input.",
        )
        self.add_argument(
            "--csv", action="store_true",
            help="Parse input lines in CSV mode."
        )
        self.add_argument(
            "--delimiter", "-d", default=",",
            help="Delimiter for CSV/plain-text input (default: ',').",
        )
        self.add_argument(
            "--spacer", "-s", default="  ",
            help="String placed between resulting columns (default: 2 spaces).",
        )
        self.add_argument(
            "--aligns", "-a", default="left",
            help=("Alignment for all columns. Can be a single value or a "
                  "comma-separated list to change the alignment for succeeding "
                  "columns. Allowed values: left, right, center or <, >, ^."),
        )

    @staticmethod
    def parse_alignment_tokens(arg: str) -> Iterable[Alignment | None]:
        for num, part in enumerate(arg.split(","), 1):
            token = part.strip().lower()
            match token:
                case "left" | "l" | "<":
                    yield Alignment.LEFT
                case "right" | "r" | ">":
                    yield Alignment.RIGHT
                case "center" | "c" | "^":
                    yield Alignment.CENTER
                case "":
                    yield None
                case _:
                    msg = f"Unknown alignment at token #{num}: {token!r}"
                    raise ArgumentTypeError(msg)

    def get_screen(self) -> Screen:
        args = self.parse_args()
        aligns = self.parse_alignment_tokens(args.aligns)
        build_model = Model.from_csv if args.csv else Model.from_stream
        model = build_model(args.infile, args.delimiter).with_aligns(list(aligns))
        return Screen(model, args.spacer)


def main():
    try:
        print(CLIParser().get_screen())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
