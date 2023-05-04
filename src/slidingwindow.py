#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from collections import deque
import sys


class SlidingWindow:
    BUFFER_SIZE = 8 * 2**10

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

    def process_byte(self, outf):
        if self.idx >= len(self.deque):
            return False
        # <do thing with byte>
        outf.write(bytes((self.deque[self.idx],)))
        # Move the index towards the middle before advancing the window.
        if self.idx <= self.size // 2 or self.eof:
            self.idx += 1
        else:
            new_byte = self.f.read(1)
            if not new_byte:
                self.eof = True
                self.idx += 1
                return True
            orig_len = len(self.deque)
            self.deque.extend(new_byte)
            # Check whether we just shifted a byte out of the window.
            if orig_len == self.size:
                self.sliding_window_base += 1
        return True


def main():
    with open("sample/deflate_fixed.png", "rb") as f, open("a", "wb") as outf:
        sw = SlidingWindow(f)
        # print(f"Initialized with {len(sw.deque)}")
        while True:
            if sw.process_byte(outf) == False:
                break


if __name__ == "__main__":
    exit(main())
