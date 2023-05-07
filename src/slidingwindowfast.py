#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later


class SlidingWindow:
    BUFFER_SIZE = 8 * 2**10
    MIN_MATCH = 3

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

    def process_bytes(self, n, outf):
        if self.wbaseidx + self.idx >= len(self.data):
            return False
        # <do thing with byte>
        outf.write(self.data[self.wbaseidx + self.idx : self.wbaseidx + self.idx + n])
        # Move the index towards the middle before advancing the window.
        if self.idx <= self.wsize // 2:
            self.idx += n
        else:
            self.wbaseidx += n
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
