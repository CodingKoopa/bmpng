#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

# consumed = 2 (GH)
# this byte: 0bABCD_EFGH
# next byte: 0bIJKL_MNOP

# read byte:
# 0bOPAB_CDEF


class BitReader:
    def __init__(self, f):
        self.f = f
        """File being read from."""
        self.working_byte = None
        """Last byte read from the file.
        
        Populated if and only if there is a nonzero bit offset."""
        self.bit_offset = 0
        """Number of least significant bits consumed within the current byte.
        
        When we read a whole byte, this should remain the same.
        """

    def read_bits(self, bits_needed):
        """Read bits from the file."""
        data = bytearray()
        if bits_needed >= 8:
            data += self.read_bytes(bits_needed // 8)
            bits_needed = bits_needed % 8
        if bits_needed == 0:
            return data
        ret = 0
        # Read the remaining bits of the working byte if we have one.
        if self.working_byte is not None:
            bits_remaining = 8 - self.bit_offset
            # The mask produced by bits_needed may be wider than
            # the remaining bits, which is harmless. It still is necessary
            # in the event that it's *smaller* than the remaining bits.
            ret |= (self.working_byte >> self.bit_offset) & (2**bits_needed - 1)
            if bits_needed <= bits_remaining:
                self.working_byte = None
                self.bit_offset = 0
                data += ret
                return data
            bits_needed -= bits_remaining
        self.working_byte = self.f.read(1)
        self.bit_offset = bits_needed
        # Note the equivalence of this to the high bits when we read a byte.
        ret |= (self.working_byte & (2**self.bit_offset - 1)) << (8 - self.bit_offset)

    def _read_byte(self, next_byte):
        """Read a byte from the file, assuming that the bit offset is nonzero."""
        low_bits = self.working_byte >> self.bit_offset
        self.working_byte = next_byte
        high_bits = (self.working_byte & (2**self.bit_offset - 1)) << (
            8 - self.bit_offset
        )
        return low_bits | high_bits

    def read_byte(self):
        """Read a byte from the file, with the potential that the bit offset is nonzero."""
        if self.working_byte is None:
            assert self.bit_offset == 0
            return self.f.read(1)
        return self._read_byte(self.f.read(1))

    def read_bytes(self, size):
        """Read multiple bytes from the file"""
        data = self.f.read(size)
        if self.bit_offset == 0 or not data:
            self.working_byte = None
            self.bit_offset = 0
            return data
        ret = bytearray()
        for byte in data:
            ret += self._read_byte(byte)
        self.working_byte = ret[-1]
        return ret
