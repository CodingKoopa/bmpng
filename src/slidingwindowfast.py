#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later


class SlidingWindow:
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

    def process_bytes(self, n):
        if self.wbaseidx + self.idx >= len(self.data):
            return None
        ret = self.data[self.wbaseidx + self.idx : self.wbaseidx + self.idx + n]
        # Move the index towards the middle before advancing the window.
        if self.idx <= self.wsize // 2:
            self.idx += n
        else:
            self.wbaseidx += n
        return ret


def main():
    with open("sample/deflate_fixed.png", "rb") as f, open(
        "sample/deflate_fixed_copy.png", "wb"
    ) as outf:
        sw = SlidingWindow(f)
        while new_data := sw.process_bytes(sw.MIN_MATCH):
            outf.write(new_data)


if __name__ == "__main__":
    exit(main())
