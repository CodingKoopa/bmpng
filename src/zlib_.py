#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

import io
import math
import struct
from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
import deflate
from bitwriter import BitWriter

# zlib container RFC: https://www.rfc-editor.org/rfc/rfc1950

Z_NO_COMPRESSION = 0
Z_BEST_COMPRESSION = 9
Z_DEFAULT_COMPRESSION = -1

MIN_WBITS = 9
MAX_WBITS = 15


class CompressionMethod(IntEnum):
    DEFLATE = 8
    RESERVED = 15


class CompressionLevel(IntEnum):
    FASTEST = 0
    FAST = 1
    DEFAULT = 2
    # We regard this as uncompressed.
    SLOWEST = 3


@dataclass
class Zlib:
    @dataclass
    class Header:
        cm: CompressionMethod = None
        wbits: int = None
        fdict: bool = None
        flevel: CompressionLevel = None
        dictid: int = None
        FMT = "!BB"
        FMT_DICT = "!I"

        def __init__(self, f=None):
            if f is None:
                return
            cmf, flg = struct.unpack(self.FMT, f.read(2))
            assert (flg | cmf << 8) % 31 == 0
            self.cm = CompressionMethod(cmf & 0b1111)
            cinfo = cmf >> 4 & 0b1111
            self.wbits = cinfo + 8
            self.fdict = flg >> 5 & 0b1
            self.flevel = CompressionLevel(flg >> 6 & 0b11)
            if self.fdict:
                self.dictid = struct.unpack(self.FMT_DICT, f.read(4))

        def __bytes__(self):
            cinfo = self.wbits - 8
            cmf = self.cm | cinfo << 4

            flg = self.fdict << 5 | self.flevel << 6
            # TODO: Do common implementations set fcheck to 0 if the modulus is 0?
            # Us setting it to 31 is correct, but could be unconventional.
            FCHECKBITS = 2**5 - 1
            fcheck = FCHECKBITS - (flg | cmf << 8) % FCHECKBITS
            flg |= fcheck

            data = bytearray()
            data += struct.pack(self.FMT, cmf, flg)
            if self.fdict:
                data += struct.pack(self.FMT_DICT, self.dictid)
            return bytes(data)

    header: Header = None
    compressed_data: bytes = None
    adler32: int = None
    FMT_TRAILER = "!I"
    FMT_UNCOMPHEADER = "<BHH"

    class BlockType(IntEnum):
        NONE = 0b00
        HUFFMAN_FIXED = 0b01
        HUFFMAN_DYNAMIC = 0b10
        RESERVED = 0b11

    def __init__(self, f=None):
        if f is None:
            return
        self.header = self.Header(f)
        remainder = f.read()
        self.compressed_data = remainder[:-4]
        self.adler32 = struct.unpack(self.FMT_TRAILER, remainder[-4:])

    def __bytes__(self):
        data = bytearray()
        data += bytes(self.header)
        data += self.compressed_data
        data += struct.pack(self.FMT_TRAILER, self.adler32)
        return bytes(data)

    def _setup_header(self, level, wbits):
        self.header = self.Header()
        self.header.cm = CompressionMethod.DEFLATE
        self.header.wbits = wbits
        # TODO: Refine the mapping from level [0, 9] to CompressionLevel [0, 3].
        if level == Z_NO_COMPRESSION:
            self.header.flevel = CompressionLevel.FASTEST
        else:
            self.header.flevel = CompressionLevel.DEFAULT
        self.header.fdict = False

    def __compress_nocompression(self, uncompressed_data):
        """Copy the data with no compression."""
        LEN = min(0b1111_1111, len(uncompressed_data))
        NLEN = (~LEN) & 0b11111111_11111111
        nblocks = math.ceil(len(uncompressed_data) / LEN)
        self.compressed_data = bytearray()
        for i in range(nblocks):
            bfinal = i + 1 == nblocks
            start = i * LEN
            if bfinal:
                LEN = len(uncompressed_data) - start
                NLEN = (~LEN) & 0b11111111_11111111
            btype = self.BlockType.NONE
            bheader = bfinal | btype << 1
            self.compressed_data += struct.pack(
                self.FMT_UNCOMPHEADER, bheader, LEN, NLEN
            )
            if bfinal:
                bdata = uncompressed_data[start:]
            else:
                bdata = uncompressed_data[start : (i + 1) * LEN]
            assert len(bdata) == LEN
            self.compressed_data += bdata

    def __compress_huffmanfixed(self, uncompressed_data):
        """Copy the data using the fixed Huffman codes, all in one block."""
        buf = io.BytesIO()
        bw = BitWriter(buf)
        deflate_fixed = deflate.Deflate(deflate.fixed_ht, bw)
        bw.write_bits(True, 1)
        bw.write_bits(self.BlockType.HUFFMAN_FIXED, 2)
        for byte in uncompressed_data:
            deflate_fixed.write_symbol(byte)
        deflate_fixed.write_end()
        bw.flush()
        buf.seek(0)

        def bindump(data):
            print("".join("{:#010b} ".format(x) for x in data))

        bindump(buf.getvalue())
        buf.seek(0)
        self.compressed_data = buf.getvalue()

    def __compress_slow(self, uncompressed_data):
        """Copy the data using the dynamic Huffman codes, all in one block."""
        # TODO: Use dynamic compression
        # Compute the alphabet symbol frequencies.
        c = Counter(uncompressed_data)
        print(c)

    def _compress(self, uncompressed_data):
        import zlib

        if self.header.flevel == CompressionLevel.FASTEST:
            self.__compress_nocompression(uncompressed_data)
        else:
            self.__compress_huffmanfixed(uncompressed_data)

        # TODO: compute this ourselves, remove zlib dep
        self.adler32 = zlib.adler32(uncompressed_data)

    def _decompress(self):
        if self.header.fdict is True:
            raise NotImplementedError()
        # TODO return DECOMPRESSED data
        return self.compressed_data


def compress(f, /, level=Z_DEFAULT_COMPRESSION, wbits=MAX_WBITS):
    if level < Z_DEFAULT_COMPRESSION or level > Z_BEST_COMPRESSION:
        raise ValueError(f"invalid compression level {level}")
    if wbits < 9 or wbits > MAX_WBITS:
        raise ValueError(f"invalid window bits {wbits}")
    if level == Z_DEFAULT_COMPRESSION:
        level = 6

    zlib = Zlib()
    zlib._setup_header(level, wbits)
    zlib._compress(f.read())
    print(f"Created ZLIB container: {zlib}")
    return zlib


def decompress(f, /, wbits=MAX_WBITS):
    # TODO: support custom wbits (currently we take from the file)
    if wbits != 0:
        raise NotImplementedError()

    zlib = Zlib(f)
    print(f"Parsed ZLIB container: {zlib}")
    return zlib._decompress()


def main():
    import sys
    import zlib

    path_in = "sample/input.txt"
    if len(sys.argv) > 1:
        path_in = sys.argv[1]
    path_refout = "sample/output.reference.bin"
    path_out = "sample/output.bin"
    path_decout = "sample/outputdec.bin"
    path_dec2out = "sample/outputdec2.bin"

    # Compression:

    with open(path_in, "rb") as f_in, open(path_refout, "wb") as f_out:
        compressed_ref = zlib.compress(f_in.read(), level=Z_DEFAULT_COMPRESSION)
        b_written = f_out.write(compressed_ref)
        print(f"wrote {b_written} bytes to {path_refout}")
    with open(path_in, "rb") as f_in, open(path_out, "wb") as f_out:
        compressed_us = bytes(compress(f_in, Z_DEFAULT_COMPRESSION))
        b_written = f_out.write(compressed_us)
        print(f"wrote {b_written} bytes to {path_out}")

    # Decompression:

    with open(path_decout, "wb") as f_out:
        decompressed_us = decompress(io.BytesIO(compressed_ref), wbits=0)
        b_written = f_out.write(decompressed_us)
        print(f"wrote {b_written} bytes to {path_decout}")
    with open(path_dec2out, "wb") as f_out:
        decompressed_usthem = zlib.decompress(compressed_us, wbits=0)
        b_written = f_out.write(decompressed_usthem)
        print(f"wrote {b_written} bytes to {path_dec2out}")


if __name__ == "__main__":
    exit(main())
