#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import defaultdict
from collections import Counter
from abc import abstractmethod


class LzIoInterface:
    @abstractmethod
    def write_literal(self, literal):
        pass

    @abstractmethod
    def write_backref(self, distance, length):
        pass


# TODO: document these
MIN_MATCH = 3
MAX_MATCH = 258


# TODO: make this work using an actual rolling hash
def _hash_buf(buf, hash_chain):
    if len(buf < MIN_MATCH):
        return
    hash_chain = defaultdict(list)
    for i in range(0, len(buf), step=MIN_MATCH):
        current_triplet = buf[i : i + MIN_MATCH]
        current_hash = hash(current_triplet)
        # TODO: Is there a better hash function to use, since the length is fixed?
        # On even a 32-bit system, the 3 bytes should just fit in a regsiter.
        hash_chain[current_hash].append(i)


def string_search(text, pattern):
    matchidx = None
    matchlen = 1
    for i in range(len(text)):
        num_chars_left = len(text) - i
        curlen = 0
        for j in range(min(len(pattern), num_chars_left)):
            # TODO: special case for repeating past end
            if text[i + j] != pattern[j]:
                break
            curlen += 1
            if curlen == MAX_MATCH:
                break
        # We want to take the last (= closest) match, so allow equality.
        if curlen >= matchlen:
            matchlen = curlen
            matchidx = i
    if matchlen < MIN_MATCH:
        matchidx = None
    if matchidx == None:
        matchlen = 0
    return (matchidx, matchlen)


def _process_next_input(
    lz_io, frequencies, search_buf, lookahead_buf, cur_lookahead_idx
):
    if len(lookahead_buf) - cur_lookahead_idx < 3:
        remaining = lookahead_buf[cur_lookahead_idx:]
        frequencies.update(remaining)
        for byte in remaining:
            lz_io.write_literal(byte)
    matchidx, matchlen = string_search(search_buf, lookahead_buf[cur_lookahead_idx:])
    if not matchidx:
        lz_io.write_literal(lookahead_buf[cur_lookahead_idx])
        frequencies[lookahead_buf[cur_lookahead_idx]] += 1
        cur_lookahead_idx += 1
    else:
        len_to_search_buf = len(search_buf) - matchidx
        lz_io.write_backref(len_to_search_buf + cur_lookahead_idx, matchlen)
        frequencies.update(
            lookahead_buf[cur_lookahead_idx : cur_lookahead_idx + matchlen]
        )
        cur_lookahead_idx += matchlen
    return cur_lookahead_idx


def compress(inf, lz_io, wsize=32 * 2**10):
    # Doesn't *necessarily* have to be the case, but probably should be.
    assert wsize % 2 == 0
    bufsize = wsize // 2
    search_buf = inf.read(bufsize)
    lookahead_buf = inf.read(bufsize)
    frequencies = Counter()
    # We maintain the loop invariant that the contents of the search buffer have:
    # - Been added to the hash table.
    # - Been written to output (as literals or backreferences).
    # To initialize the loop, we write the search buffer as literals.
    for sym in search_buf:
        lz_io.write_literal(sym)
    frequencies.update(search_buf)
    while lookahead_buf:
        print(f"processed {bufsize}")
        # hash_chain = _hash_buf(search_buf)
        cur_lookahead_idx = 0
        # TODO: We don't consider making backreferences within the lookahead buffer,
        # but that fact seems inefficient?
        while cur_lookahead_idx < len(lookahead_buf):
            cur_lookahead_idx = _process_next_input(
                lz_io, frequencies, search_buf, lookahead_buf, cur_lookahead_idx
            )
        # TODO: Maybe slide the window as soon as we have less than MAX_MATCH left?
        search_buf = lookahead_buf
        lookahead_buf = inf.read(bufsize)
