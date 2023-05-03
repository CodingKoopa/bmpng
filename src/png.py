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
                    #raise ValueError(f"Unrecognized chunk: type {chunk}")
                    return cls(data)

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
    
    @dataclass
    class Idat(Chunk):
        #TODO: Handle image data here
        def __init__(self, data=None):
            super().__init__(data)

    def __init__(self, filename=None):
        in_file = open(filename, "rb")
        self.header = self.Header(in_file)
        if self.header.valid:
            self.chunks = []
            while True:
                self.chunks.append(self.Chunk.make_chunk(in_file))
                if self.chunks[-1].type == b"IEND":
                    break
        in_file.close()

if __name__ == "__main__":
    png = Png("sample/bulbasaur.png")
    if png.header.valid:
        for chunk in png.chunks:
            print(f"\nChunk length: {chunk.length} bytes")
            print(f"Chunk type: {chunk.type}")
            if chunk.type == b"IHDR":
                print(f"Image width: {chunk.width} pixels")
                print(f"Image height: {chunk.height} pixels")
                print(f"Bit depth: {chunk.bit_depth} bits")
                print(f"Color type: {chunk.color_type}")
                print(f"Compression: {chunk.compression}")
                print(f"Filter: {chunk.filter}")
                print(f"Interlace: {chunk.interlace}")
    pass
