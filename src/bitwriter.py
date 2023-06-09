#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later


import math


class BitWriter:
    """Utility for writing bits to a file-like object.

    This is largely based off of BitReader.
    """

    def __init__(self, f):
        self.f = f
        """File being written to from."""
        self.working_byte = None
        # TODO: add a flush method
        """Work-in-progress byte to be written.
        
        Populated if and only if there is a nonzero bit offset."""
        self.bit_offset = 0
        """Number of least significant bits written to current WIP byte.
        
        When we write a whole byte, this should remain the same.
        """

    def __del__(self):
        self.flush()

    def flush(self):
        if self.working_byte is None:
            return
        self.f.write(bytes((self.working_byte,)))
        self.working_byte = None
        self.bit_offset = 0

    def write_bits(self, data, bits_needed):
        """Write bits to the file.

        bits_needed is the number of bits left to write."""
        # print(f"write_bits({data:0{bits_needed}b})")
        if type(data) != bytes:
            data = data.to_bytes(math.ceil(bits_needed / 8), "little")
        if bits_needed % 8 == 0:
            self.write_bytes(data)
            return
        if bits_needed >= 8:
            self.write_bytes(data[:-1])
            bits_needed = bits_needed % 8
        data = data[-1]
        # If we are byte-aligned, life is good (for now).
        if self.working_byte is None:
            self.working_byte = data
            self.bit_offset = bits_needed
            # (we cannot write yet - the user must keep writing, or flush)
            return
        bits_remaining = 8 - self.bit_offset
        last_byte = self.working_byte
        last_byte |= (data & 2**bits_needed - 1) << self.bit_offset
        # Account for mask being too wide (filled working byte).
        last_byte &= 2**8 - 1
        # If we did not fill the whole working byte.
        if bits_needed < bits_remaining:
            self.working_byte = last_byte
            self.bit_offset += bits_needed
            # (we cannot write yet)
        # If we happened to end up byte-aligned.
        elif bits_needed == bits_remaining:
            self.working_byte = None
            self.bit_offset = 0
            self.f.write(bytes((last_byte,)))
        # If we have filled the working byte, and need a new one.
        else:
            self.f.write(bytes((last_byte,)))
            self.working_byte = data >> bits_remaining
            self.bit_offset = bits_needed - bits_remaining

    def _write_byte(self, next_byte):
        low_bits = self.working_byte
        high_bits = (next_byte & (2 ** (8 - self.bit_offset) - 1)) << (self.bit_offset)
        self.working_byte = next_byte >> (8 - self.bit_offset)
        self.f.write(bytes((low_bits | high_bits,)))

    def write_byte(self, byte):
        """Writes a byte to the file.

        byte should be a bytes-like."""
        if self.working_byte is None:
            assert self.bit_offset == 0
            self.f.write(byte)
        else:
            self._write_byte(byte)

    def write_bytes(self, data):
        """Write multiple bytes to the file."""
        if self.working_byte is None:
            assert self.bit_offset == 0
            self.f.write(data)
            return
        for byte in data:
            self._write_byte(byte)


def main():
    import io

    def bindump(data):
        print("".join("{:#010b} ".format(x) for x in data))

    data = bytes([0b0011_1001, 0b1010_0111])

    print("Test 1: Writing less than one byte of bits\nData:")
    f1 = io.BytesIO()
    bw1 = BitWriter(f1)
    # fmt: off
    bw1.write_bits(bytes((0b001, )), 3)
    bw1.write_bits(bytes((0b111, )), 2)
    # fmt: on
    bw1.flush()
    f1.seek(0)
    bindump(f1.read())

    print("Test 2: Writing more than a byte of bits\nData:")
    f2 = io.BytesIO()
    bw2 = BitWriter(f2)
    # fmt: off
    bw2.write_bits(bytes((0b001, )), 3)
    bw2.write_bits(bytes((0b11, )), 2)
    bw2.write_bits(bytes((0b001, )), 3)
    bw2.write_bits(bytes((0b1010_0111, )), 8)
    # fmt: on
    bw2.flush()
    f2.seek(0)
    bindump(f2.read())

    print("Test 3: Writing bits across boundaries\nData:")
    f3 = io.BytesIO()
    bw2 = BitWriter(f3)
    # fmt: off
    bw2.write_bits(bytes((0b001, )), 3)
    bw2.write_bits(bytes((0b0111, )), 4)
    bw2.write_bits(bytes((0b01110, )), 5)
    bw2.write_bits(bytes((0b1010, )), 4)
    # fmt: on
    bw2.flush()
    f3.seek(0)
    f3out = f3.read()
    bindump(f3out)
    assert f3out == data

    return 0


if __name__ == "__main__":
    exit(main())
