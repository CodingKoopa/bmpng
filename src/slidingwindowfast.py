#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import defaultdict


class SlidingWindow:
    MIN_MATCH = 3
    MAX_MATCH = 258

    def __init__(self, f, wsize=32 * 2**10):
        self.data = f.read()
        """The entire file contents."""
        self.wsize = wsize
        """Size of the sliding window, in bytes."""
        self.wbaseidx = 0
        """Base index within the data where the window starts."""
        self.idx = 0
        """Index within the sliding window, used for processing.
        
        Relative to the base index,."""
        self.hash_chain = defaultdict(list)

    def _can_advance(self):
        return self.wbaseidx + self.idx < len(self.data)

    def _advance_bytes(self, n):
        """Consumes n bytes."""
        # Move the index towards the middle before advancing the window.
        if self.idx <= self.wsize // 2:
            self.idx += n
        else:
            self.wbaseidx += n

    def get_bytes(self, n):
        if not self._can_advance():
            return None
        ret = self.data[self.wbaseidx + self.idx : self.wbaseidx + self.idx + n]
        self._advance_bytes(n)
        return ret

    def encode(self):
        print("heya")
        while self._can_advance():
            current_triplet = self.data[
                self.wbaseidx + self.idx : self.wbaseidx + self.idx + 3
            ]
            current_hash = hash(current_triplet)
            # TODO: handle end where the size is less than 3 (higher hash conflict chance?)
            hash_chain[current_hash].append(self.wbaseidx + self.idx)
            # TODO: output literal or backref here
            # TODO: compute frequencies here
            self._advance_bytes(1)
        print(hash_chain)


def main():
    with open("sample/deflate_fixed.png", "rb") as f, open(
        "sample/deflate_fixed_copy.png", "wb"
    ) as outf:
        sw = SlidingWindow(f)
        while new_data := sw.get_bytes(sw.MIN_MATCH):
            outf.write(new_data)

    with open("sample/deflate_fixed.png", "rb") as f, open("a", "wb") as outf:
        sw = SlidingWindow(f)
        sw.encode()


if __name__ == "__main__":
    exit(main())
