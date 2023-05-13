#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import namedtuple
import math
from abc import ABC, abstractmethod

CodeSpec = namedtuple("CodeSpec", ["symbol_base", "code_len", "codes"])
"""Specification of one or more codes with contiguous symbols.

symbol_base is the value of the first symbol.
code_len is the length of each code.
codes is an iterable object containing the codes to assign."""


class HuffmanIoInterface(ABC):
    @abstractmethod
    def write_literal(self, literal):
        pass


class HuffmanTree:
    """Implementation of a binary tree for storing Huffman Codes."""

    def __init__(self, is_child=False):
        self.left = None
        self.right = None
        self.symbol = None
        if not is_child:
            self.map = {}
            """Mapping of symbols to codes.
            
            This is the inverse of what we use the binary tree for."""

    def _add_code(self, code, code_len, symbol):
        if code_len == 0:
            self.symbol = symbol
            return
        code_len -= 1
        direction = code >> code_len
        code = code & (2**code_len - 1)
        if direction == 0:
            if not self.left:
                self.left = HuffmanTree(True)
            self.left._add_code(code, code_len, symbol)
        else:
            if not self.right:
                self.right = HuffmanTree(True)
            self.right._add_code(code, code_len, symbol)

    def add_code(self, code, code_len, symbol):
        # We only need this mapping in the root.
        self.map[symbol] = (code, code_len)
        self._add_code(code, code_len, symbol)

    def add_alphabet(self, alphabet):
        for code_group in alphabet:
            symbol = code_group.symbol_base
            for code in code_group.codes:
                self.add_code(code, code_group.code_len, symbol)
                symbol += 1

    def dump_dot(self, depth=0):
        if self.symbol:
            try:
                sym = chr(self.symbol)
                if not sym.isprintable():
                    raise ValueError()
                label = f"{hex(self.symbol)} (\{sym})"
            except ValueError:
                label = str(hex(self.symbol))
            print(f'\t{hash(self)} [label="{label}",fontsize="18pt"]')
        else:
            print(
                f'\t{hash(self)} [label={depth},fontsize="16pt"'
                "style=filled,fontcolor=white,fillcolor=cornflowerblue];"
            )

        rank = "\t{rank=same;"
        if self.left:
            rank += f" {hash(self.left)};"
            print(f'\t{hash(self)} -- {hash(self.left)} [taillabel="0"]')
            self.left.dump_dot(depth + 1)
        if self.right:
            rank += f" {hash(self.right)};"
            print(f'\t{hash(self)} -- {hash(self.right)} [taillabel="1"]')
            self.right.dump_dot(depth + 1)
        rank += "}"
        print(rank)

    def __hash__(self):
        if self.symbol == None:
            return id(self)
        return self.symbol

    def __repr__(self):
        return str(self.__dict__)


Coin = namedtuple("Coin", ["denomination", "numismatic_value"])


def binary_package_merge(largest_denomination, limit, coins):
    """Implementation of the binary version of the Package-merge algorithm.

    For more information on the algorithm, see:
    https://en.wikipedia.org/wiki/Package-merge_algorithm
    """
    assert limit % largest_denomination == 0
    assert math.log(largest_denomination, 2).is_integer()

    min_denom = min(coins, key=lambda c: c.denomination).denomination
    denom_dict = {
        denom: []
        for denom in [2**-n for n in range(0, -int(math.log(min_denom, 2)) + 1)]
    }
    for coin in coins:
        denom_dict[coin.denomination].append(coin)

    def key_coin(c):
        """Serves as the comparison key for a coin or coin package."""
        if type(c) is Coin:
            return c.numismatic_value
        elif type(c) is list:
            return sum(key_coin(inner) for inner in c)
        else:
            raise TypeError()

    for denom in denom_dict.values():
        denom.sort(key=key_coin)
    denom_list = list(reversed(denom_dict.values()))
    for idx, coins in enumerate(denom_list):
        if idx == len(denom_list) - 1:
            break
        while len(coins) > 1:
            denom_list[idx + 1].append([coins.pop(0), coins.pop(0)])
        denom_list[idx + 1].sort(key=key_coin)
    return denom_dict


def test_deflate(dump_dot=False):
    deflate_ht = HuffmanTree()
    fixed_alphabet = [
        CodeSpec(0, 8, range(0b0011_0000, 0b1011_1111)),
        CodeSpec(144, 9, range(0b110010000, 0b111111111)),
    ]
    deflate_ht.add_alphabet(fixed_alphabet)

    if dump_dot:
        print("strict graph {")
        print('\tnode [fontname="Arial",shape=box];')
        print('\tedge [fontname="Arial",fontsize="18pt",shape=box];')
        deflate_ht.dump_dot()
        print("}")


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        test_deflate(True)
        return

    print("Test binary package merge:")
    coins = [
        Coin(1, 20),
        Coin(0.5, 2),
        Coin(0.25, 0.1),
        Coin(0.25, 1000),
        Coin(0.5, 1),
        Coin(0.5, 30),
    ]
    print(binary_package_merge(1, 1, coins))

    print("Test Huffman Tree:")
    ht = HuffmanTree()
    ht.add_code(0b1, 1, "c")
    ht.add_code(0b001, 3, "b")
    ht.add_code(0b000, 3, "a")
    print(ht)

    print("Test Fixed DEFLATE Huffman Tree:")
    test_deflate()


if __name__ == "__main__":
    exit(main())
