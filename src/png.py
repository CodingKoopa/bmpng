#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

import io
import struct
from dataclasses import dataclass

import zlib_


@dataclass
class Png:
    @dataclass
    class Header:
        FMT = "!Q"
        SIGNATURE = int("0x89504E470D0A1A0A", 16)

        def __init__(self, data=None):
            if data is not None:
                (self.signature,) = struct.unpack(self.FMT, data.read(8))
                self.valid = self.signature == self.SIGNATURE
                if not self.valid:
                    raise ValueError(f"Invalid signature: {hex(self.signature)}")
            else:
                self.signature = self.SIGNATURE
                self.valid = True

        def __bytes__(self):
            return struct.pack(self.FMT, self.signature)

    @dataclass
    class Chunk:
        FMT = "!I4s"

        # Inclusion of chunk_type signifies creation of chunk, not extraction
        # Empty parameters signifies IEND chunk
        def __init__(self, data=None, chunk_type=None):
            if data is None:
                self.type = b"IEND"
                self.length = 0
                self.data = b""
                self.calc_crc()
                return
            if chunk_type is not None:
                self.length = len(data)
                self.type = chunk_type
                self.data = data
                self.calc_crc()
                return
            self.length, self.type = struct.unpack(self.FMT, data.read(8))
            self.data = data.read(self.length)
            self.crc = data.read(4)

        def __bytes__(self):
            data = bytearray()
            data += struct.pack(self.FMT, self.length, self.type)
            data += self.data
            data += self.crc
            return bytes(data)

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
            crc ^= 0xFFFFFFFF
            self.crc = struct.pack("!I", crc)

    @dataclass
    class Ihdr(Chunk):
        FMT2 = "!LL5B"

        def __init__(self, data=None, width=None, height=None):
            if data is not None:
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
            else:
                self.length = 13
                self.type = b"IHDR"
                self.width = width
                self.height = height
                self.bit_depth = 8
                self.color_type = 2
                self.compression = 0
                self.filter = 0
                self.interlace = 0
                self.data = struct.pack(
                    self.FMT2,
                    self.width,
                    self.height,
                    self.bit_depth,
                    self.color_type,
                    self.compression,
                    self.filter,
                    self.interlace,
                )
                self.calc_crc()

    compressed_data = b""
    chunks = None
    ihdr = None
    plte = None

    def __init__(self, filename=None, array=None):
        if filename is not None:
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
                            self.chunks.append(chunk)
                    chunk = self.Chunk.make_chunk(in_file)
            in_file.close()
        elif array is not None:
            self.header = self.Header()
            self.ihdr = self.Ihdr(width=len(array), height=len(array[0]))
            self.array_to_bytes(array)
            self.compressed_data = bytes(zlib_.compress(io.BytesIO(self.raw_data)))

    def __bytes__(self):
        data = bytearray()
        data += bytes(self.header)
        data += bytes(self.ihdr)
        if self.plte is not None:
            data += bytes(self.plte)
        if self.chunks is not None:
            for chunk in self.chunks:
                data += bytes(chunk)
        for i in range(0, len(self.compressed_data), 8*1024):
            compressed_data = self.compressed_data[i:i+8*1024]
            idat = self.Chunk(data=compressed_data, chunk_type=b"IDAT")
            data += bytes(idat)
        data += bytes(self.Chunk())
        return bytes(data)

    def array_to_bytes(self, array):
        self.raw_data = bytearray()
        for i in range(len(array[0])):
            self.raw_data += struct.pack("x")
            for j in range(len(array)):
                self.raw_data += struct.pack(
                    "!BBB",
                    array[j][i][0],
                    array[j][i][1],
                    array[j][i][2],
                )


if __name__ == "__main__":
    # png = Png(filename="sample/bulbasaur.png")
    # # output = open("png_test.png", "wb")
    # # output.write(bytes(png))
    # # output.close()
    # if png.header.valid:
    #     print(f"Image width: {png.ihdr.width} pixels")
    #     print(f"Image height: {png.ihdr.height} pixels")
    #     print(f"Bit depth: {png.ihdr.bit_depth} bits")
    #     print(f"Color type: {png.ihdr.color_type}")
    #     print(f"Compression: {png.ihdr.compression}")
    #     print(f"Filter: {png.ihdr.filter}")
    #     print(f"Interlace: {png.ihdr.interlace}")
    #     print(f"Header size: {png.ihdr.length}")
    #     print(f"Compressed data: {png.compressed_data}")
    #     for chunk in png.chunks:
    #         print(f"Chunk length: {chunk.length} bytes")
    #         print(f"Chunk type: {chunk.type}")
    image = []
    for x in range(256):
        image.append([])
        for y in range(256):
            image[x].append((x, 0, y))
    png = Png(array=image)
    output = open("png_test.png", "wb")
    output.write(bytes(png))
    output.close()
