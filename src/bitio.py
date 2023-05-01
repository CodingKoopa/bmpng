#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

# consumed = 2 (GH)
# this byte: 0bABCD_EFGH
# next byte: 0bIJKL_MNOP

# read byte:
# 0bOPAB_CDEF


# it's-a-me,
class BitIO:
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
        last_byte = 0
        # If we are byte-aligned, life is good (for now).
        if self.working_byte is None:
            self.working_byte = self.f.read(1)[0]
            self.bit_offset = bits_needed
            last_byte = self.working_byte & (2**self.bit_offset - 1)
            data.append(last_byte)
            return data
        bits_remaining = 8 - self.bit_offset
        # The mask produced by bits_needed may be wider than
        # the remaining bits, which is harmless. It still is necessary
        # in the event that it's *smaller* than the remaining bits.
        last_byte |= (self.working_byte >> self.bit_offset) & (2**bits_needed - 1)
        # If we did not use the whole working byte.
        if bits_needed < bits_remaining:
            self.bit_offset += bits_needed
        # If we happened to end up byte-aligned.
        elif bits_needed == bits_remaining:
            self.working_byte = None
            self.bit_offset = 0
        # If we have depleted the working byte, and need a new one.
        else:
            bits_needed -= bits_remaining
            self.working_byte = self.f.read(1)[0]
            # Note the equivalence of this to the high bits when we read a byte.
            last_byte |= (self.working_byte & (2**bits_needed - 1)) << bits_remaining
            self.bit_offset = bits_needed
        data.append(last_byte)
        return data

    def _read_byte(self, next_byte):
        """Read a byte from the file, assuming that the bit offset is nonzero."""
        low_bits = self.working_byte >> self.bit_offset
        self.working_byte = next_byte
        high_bits = (self.working_byte & (2**self.bit_offset - 1)) << (
            8 - self.bit_offset
        )
        return low_bits | high_bits

    def read_byte(self):
        """Read a byte from the file, with the potential that the bit offset
        is nonzero."""
        ret = bytearray()
        if self.working_byte is None:
            assert self.bit_offset == 0
            ret.append(self.f.read(1)[0])
        else:
            ret.append(self._read_byte(self.f.read(1)[0]))
        return ret

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


def main():
    import io

    def bindump(data):
        print("".join("{:#010b} ".format(x) for x in data))

    data = bytes([0b0011_1001, 0b1010_0111])

    print("Test 1: Reading bits across boundaries\nData:")
    bindump(data)
    data1 = data[:]
    br1 = BitIO(io.BytesIO(data1))
    actual1 = bytearray()
    actual1 = br1.read_bits(2)
    assert actual1[0] == 0b01
    actual1 = br1.read_bits(3)
    assert actual1[0] == 0b110
    actual1 = br1.read_bits(5)
    assert actual1[0] == 0b11001
    actual1 = br1.read_bits(6)

    print("Test 2: Reading bytes\nData:")
    bindump(data)
    data2 = data[:]
    br2 = BitIO(io.BytesIO(data2))
    actual2 = bytearray()
    actual2 = br2.read_bytes(2)
    assert actual2 == data

    print("Test 3: Reading bytes (alt)\nData:")
    bindump(data)
    data3 = data[:]
    br3 = BitIO(io.BytesIO(data3))
    actual3 = bytearray()
    actual3 = br3.read_byte()
    actual3 += br3.read_byte()
    assert actual3 == data

    return 0


if __name__ == "__main__":
    exit(main())
