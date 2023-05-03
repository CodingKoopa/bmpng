#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import namedtuple
from huffman import HuffmanTree, CodeSpec
import copy

LengthSymbolInfo = namedtuple("LengthSymbolInfo", ["num_extra_bits", "base"])
"""Associates information with a length symbol.

Used to provide each symbol within the alphabet of lengths witg:
- A base length.
- A number of extra bits following it, to be added to the base.
"""


def _make_lai():
    """Constructs a mapping of length symbols to their information.

    Orders the dictionary by symbol (increasing)."""
    lai = {}
    eb_ranges = [
        (range(257, 264 + 1), 0),
        (range(265, 268 + 1), 1),
        (range(269, 272 + 1), 2),
        (range(273, 276 + 1), 3),
        (range(277, 280 + 1), 4),
        (range(281, 284 + 1), 5),
    ]
    base = 3
    for eb_range, eb in eb_ranges:
        for symbol in eb_range:
            lai[symbol] = LengthSymbolInfo(eb, base)
            base += 2**eb
    # This is a funny little edge case. See:
    # https://stackoverflow.com/a/27153524/5719930
    lai[285] = LengthSymbolInfo(0, 258)
    return lai


fixed_alphabet = [
    # Literals 0x00 to 0x8F.
    CodeSpec(0, 8, range(0b0011_0000, 0b1011_1111 + 1)),
    # Literals 0x90 to 0xFF.
    CodeSpec(144, 9, range(0b110010000, 0b111111111 + 1)),
]
length_alphabet = [
    # Stop code 0x100, lengths 0x101 to 0x117.
    CodeSpec(256, 7, range(0b000_0000, 0b001_0111 + 1)),
    # Lengths 0x118 to 0x11F.
    CodeSpec(280, 8, range(0b1100_0000, 0b1100_0111 + 1)),
]
length_alphabet_info = _make_lai()

base_ht = HuffmanTree()
base_ht.add_alphabet(length_alphabet)
fixed_ht = copy.deepcopy(base_ht)
fixed_ht.add_alphabet(fixed_alphabet)


def main():
    print(f"{length_alphabet_info=}")
    print(f"{base_ht=}")
    print(f"{fixed_ht=}")


if __name__ == "__main__":
    exit(main())
