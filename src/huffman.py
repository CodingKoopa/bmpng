#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import namedtuple
import math

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
    print(denom_dict)


def main():
    coins = [
        Coin(1, 20),
        Coin(0.5, 2),
        Coin(0.25, 0.1),
        Coin(0.25, 1000),
        Coin(0.5, 1),
        Coin(0.5, 30),
    ]
    binary_package_merge(1, 1, coins)


if __name__ == "__main__":
    exit(main())
