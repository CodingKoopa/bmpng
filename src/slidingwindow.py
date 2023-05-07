#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import deque
import itertools


class SlidingWindow:
    BUFFER_SIZE = 8 * 2**10
    MIN_MATCH = 3

    def __init__(self, f, size=32 * 2**10):
        self.f = f
        """File to read into the sliding window."""
        self.size = size
        """Size of the sliding window, in bytes."""
        self.deque = deque(maxlen=self.size)
        self.idx = 0
        """Index within the sliding window, used for processing."""
        self.sliding_window_base = 0
        """Base address of the sliding window.
        
        Used to derive correct relative distances from the hash chain."""

        initial_bytes = self.f.read(self.size)
        self.deque.extend(initial_bytes)
        self.eof = len(initial_bytes) < self.size

    def process_bytes(self, n, outf):
        if self.idx >= len(self.deque):
            # TODO: handle the file size not being a multiple of n
            return False
        # <do thing with byte>
        outf.write(bytes(itertools.islice(self.deque, self.idx, self.idx + n)))
        # Move the index towards the middle before advancing the window.
        if self.idx <= self.size // 2 or self.eof:
            self.idx += n
        else:
            new_data = self.f.read(n)
            # Handle the transition to no longer having new bytes.
            # If not careful, you can end up with a byte being duplicated.
            if not new_data:
                # TODO: we accidentally have a duplicate byte here
                self.idx += n + 1
                self.eof = True
                return True
            orig_len = len(self.deque)
            self.deque.extend(new_data)
            # Check whether we just shifted a byte out of the window.
            if orig_len == self.size:
                # The length will be equal to n, up until the end.
                self.sliding_window_base += len(new_data)
        return True


def main():
    with open("sample/deflate_fixed.png", "rb") as f, open("a", "wb") as outf:
        sw = SlidingWindow(f)
        # print(f"Initialized with {len(sw.deque)}")
        while True:
            if sw.process_bytes(sw.MIN_MATCH, outf) == False:
                break


if __name__ == "__main__":
    exit(main())
