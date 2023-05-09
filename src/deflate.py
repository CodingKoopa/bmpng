#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import namedtuple
from huffman import HuffmanTree, CodeSpec
import copy
from bitwriter import BitWriter
from bitreader import BitReader
from lz77 import LzIoInterface

LengthSymbolInfo = namedtuple("LengthSymbolInfo", ["num_extra_bits", "base"])
"""Associates information with a length/distance symbol.

Used to provide each symbol within the alphabet of lengths witg:
- A base length/distance.
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


def _make_dai():
    """Constructs a mapping of distance symbols to their information.

    Orders the dictionary by symbol (increasing)."""
    dai = {}
    eb_ranges = [
        (range(0, 3 + 1), 0),
        (range(4, 5 + 1), 1),
        (range(6, 7 + 1), 2),
        (range(8, 9 + 1), 3),
        (range(10, 11 + 1), 4),
        (range(12, 13 + 1), 5),
        (range(14, 15 + 1), 6),
        (range(16, 17 + 1), 7),
        (range(18, 19 + 1), 8),
        (range(20, 21 + 1), 9),
        (range(22, 23 + 1), 10),
        (range(24, 25 + 1), 11),
        (range(26, 27 + 1), 12),
        (range(28, 29 + 1), 13),
    ]
    base = 1
    for eb_range, eb in eb_ranges:
        for symbol in eb_range:
            dai[symbol] = LengthSymbolInfo(eb, base)
            base += 2**eb
    return dai


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
distance_alphabet = [
    CodeSpec(0, 5, range(0b0_0000, 0b1_1111 + 1)),
]
length_alphabet_info = _make_lai()
distance_alphabet_info = _make_dai()

base_llht = HuffmanTree()
base_llht.add_alphabet(length_alphabet)
fixed_llht = copy.deepcopy(base_llht)
fixed_llht.add_alphabet(fixed_alphabet)
fixed_dht = HuffmanTree()
fixed_dht.add_alphabet(distance_alphabet)


def _get_symbol_info(num, alphabet):
    """Retrieves information associated with a length/distance symbol."""
    # TODO: This could probably be faster.
    ret = None
    for cur_sym, cur_info in alphabet.items():
        if cur_info.base > num:
            break
        ret = (cur_sym, cur_info)
    assert ret is not None, f"symbol {num} not found"
    return ret


# TODO: this is a bad name. it should reflect the fact that it encapsulates IO.
class Deflate(LzIoInterface):
    def __init__(
        self,
        literallength_ht: HuffmanTree,
        distance_ht=HuffmanTree,
        /,
        bw: BitWriter = None,
        br: BitReader = None,
    ):
        self.literallength_ht = literallength_ht
        self.distance_ht = distance_ht
        self.bw = bw
        self.br = br

    def _write_symbol(self, symbol, ht):
        """Writes a symbol from the combined literal/length alphabet."""
        code, code_len = ht.map[symbol]
        # Huffman codes in DEFLATE are written MSB first.
        code_rev = int(f"{code:0{code_len}b}"[::-1], 2)
        self.bw.write_bits(code_rev, code_len)

    def write_literal(self, literal):
        """Writes a literal from the literal/length alphabet."""
        self._write_symbol(literal, self.literallength_ht)

    def write_end(self):
        """Writes an end-of-block code from the literal/length alphabet."""
        self._write_symbol(0x100, self.literallength_ht)

    def write_backref(self, distance, length):
        """Writes a back-reference.

        The back-reference is comprised of:
        - A length symbol from the literal/literal alphabet.
        - Any extra bits for the length.
        - A distance symbol from the distance alphabet.
        - Any extra bits for the distance."""
        (lsym, lsym_info) = _get_symbol_info(length, length_alphabet_info)
        self._write_symbol(lsym, self.literallength_ht)
        self.bw.write_bits(length - lsym_info.base, lsym_info.num_extra_bits)
        (dsym, dsym_info) = _get_symbol_info(distance, distance_alphabet_info)
        # Even though this can be a fixed-length code, it still is a Huffman code
        # and it still gets written MSB first.
        self._write_symbol(dsym, self.distance_ht)
        # TODO: skip this function call if the number of bits is zero
        self.bw.write_bits(distance - dsym_info.base, dsym_info.num_extra_bits)


def main():
    # print(f"{length_alphabet_info=}\n")
    # print(f"{distance_alphabet_info=}")
    # print(f"{base_ht=}")
    # print(f"{fixed_ht=}")
    print(_get_symbol_info(199, length_alphabet_info))
    print(_get_symbol_info(1, distance_alphabet_info))
    print(_get_symbol_info(3, length_alphabet_info))
    print(_get_symbol_info(14200, distance_alphabet_info))


if __name__ == "__main__":
    exit(main())
