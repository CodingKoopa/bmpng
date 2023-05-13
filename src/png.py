#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

import struct
from dataclasses import dataclass


@dataclass
class Png:
    @dataclass
    class Header:
        FMT = "!Q"
        SIGNATURE = int("0x89504E470D0A1A0A", 16)

        def __init__(self, data=None):
            (self.signature,) = struct.unpack(self.FMT, data.read(8))
            self.valid = self.signature == self.SIGNATURE
            if not self.valid:
                raise ValueError(f"Invalid signature: {hex(self.signature)}")

    @dataclass
    class Chunk:
        FMT = "!I4s"

        def __init__(self, data=None):
            if data is None:
                return
            self.length, self.type = struct.unpack(self.FMT, data.read(8))
            self.data = data.read(self.length)
            self.crc = data.read(4)

        @classmethod
        def make_chunk(cls, data=None):
            if data is None:
                return
            position = data.tell()
            (chunk,) = struct.unpack("!xxxx4s", data.read(8))
            data.seek(position)
            match chunk:
                case b"IHDR":
                    return Png.Ihdr(data)
                case _:
                    return cls(data)

        # Adapted from W3's sample C implementation
        def calc_crc(self):
            crc_table = []
            for n in range(256):
                c = n
                for k in range(8):
                    if c & 1:
                        c = 0xEDB88320 ^ (c >> 1)
                    else:
                        c >>= 1
                crc_table.append(c)
            crc = 0xFFFFFFFF
            for n in range(4):
                crc = crc_table[(crc ^ self.type[n]) & 0xFF] ^ (crc >> 8)
            for n in range(self.length):
                crc = crc_table[(crc ^ self.data[n]) & 0xFF] ^ (crc >> 8)
            return crc ^ 0xFFFFFFFF

    @dataclass
    class Ihdr(Chunk):
        FMT2 = "!LL5B"

        def __init__(self, data=None):
            super().__init__(data)
            (
                self.width,
                self.height,
                self.bit_depth,
                self.color_type,
                self.compression,
                self.filter,
                self.interlace,
            ) = struct.unpack(self.FMT2, self.data)

    compressed_data = None
    ihdr = None
    plte = None

    def __init__(self, filename=None):
        in_file = open(filename, "rb")
        self.header = self.Header(in_file)
        if self.header.valid:
            self.chunks = []
            chunk = self.Chunk.make_chunk(in_file)
            while chunk.type != b"IEND":
                match chunk.type:
                    case b"IHDR":
                        self.ihdr = chunk
                    case b"PLTE":
                        self.plte = chunk
                    case b"IDAT":
                        self.compressed_data += chunk.data
                    case _:
                        self.chunks.append(self.Chunk.make_chunk(in_file))
                chunk = self.Chunk.make_chunk(in_file)
        in_file.close()


if __name__ == "__main__":
    png = Png(filename="sample/bulbasaur.png")
    if png.header.valid:
        print(f"Image width: {png.ihdr.width} pixels")
        print(f"Image height: {png.ihdr.height} pixels")
        print(f"Bit depth: {png.ihdr.bit_depth} bits")
        print(f"Color type: {png.ihdr.color_type}")
        print(f"Compression: {png.ihdr.compression}")
        print(f"Filter: {png.ihdr.filter}")
        print(f"Interlace: {png.ihdr.interlace}")
        print(f"Header size: {png.ihdr.length}")
        print(f"Included header CRC: {hex(int.from_bytes(png.ihdr.crc))}")
        print(f"Calculated header CRC: {hex(png.ihdr.calc_crc())}")
        for chunk in png.chunks:
            print(f"Chunk length: {chunk.length} bytes")
            print(f"Chunk type: {chunk.type}")
            print(f"Included CRC: {hex(int.from_bytes(chunk.crc))}")
        print(f"Calculated CRC: {hex(chunk.calc_crc())}")
    pass
