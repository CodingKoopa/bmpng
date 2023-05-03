#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

import struct
from dataclasses import dataclass


@dataclass
class Bmp:
    @dataclass
    class Header:
        valid: bool = None
        size: int = None
        offset: int = None
        MAGIC = b"BM"
        FMT = "<2sIxxxxI"

        def __init__(self, data=None):
            if data is None:
                return
            valid, self.size, self.offset = struct.unpack(self.FMT, data.read(14))
            self.valid = valid == self.MAGIC

        def __bytes__(self):
            data = bytearray()
            data += struct.pack(self.FMT, self.MAGIC, self.size, self.offset)
            return bytes(data)

    @dataclass
    class Dib:
        dib_size: int = None
        width: int = None
        height: int = None
        planes: int = None
        bpp: int = None
        compression: int = None
        img_size: int = None
        h_res: int = None
        v_res: int = None
        palette: int = None
        important_colors: int = None
        FMT = "<iiHHIIiiII"

        def __init__(self, data=None):
            self.dib_size = struct.unpack("<I", data.read(4))[0]
            if self.dib_size != 40:
                raise ValueError(f"DIB size must be 40, it is {self.dib_size}")
            (
                self.width,
                self.height,
                self.planes,
                self.bpp,
                self.compression,
                self.img_size,
                self.h_res,
                self.v_res,
                self.palette,
                self.important_colors,
            ) = struct.unpack(self.FMT, data.read(self.dib_size - 4))

        def __bytes__(self):
            data = bytearray()
            data += struct.pack("<I", 40) + struct.pack(
                self.FMT,
                self.width,
                self.height,
                self.planes,
                self.bpp,
                self.compression,
                self.img_size,
                self.h_res,
                self.v_res,
                self.palette,
                self.important_colors,
            )
            return bytes(data)

    def __init__(self, filename):
        in_file = open(filename, "rb")
        self.header = self.Header(in_file)
        self.dib = self.Dib(in_file)
        in_file.seek(self.header.offset)
        image = in_file.read()
        in_file.close()
        if self.dib.bpp != 24:
            raise ValueError(
                "only 24 bits per pixel currently supported, "
                + "will not create pixel array"
            )
        if self.dib.compression == 4:
            raise ValueError(
                "that...that's a jpeg. you took a jpeg and gave it a bmp header. "
                + "go sit in the corner and think about what you've done."
            )
        if self.dib.compression == 5:
            raise ValueError(
                "that...that's a png. you took a png and gave it a bmp header."
                + "go sit in the corner and think about what you've done."
            )
        if self.dib.compression != 0:
            raise ValueError("this program only works for uncompressed bitmaps")
        # now stores pixels as [x][y] from top to bottom
        self.arr = []
        for x in range(self.dib.width):
            self.arr.append([])
            for y in range(self.dib.height):
                self.arr[x].append([])
        # NOTE: colors are stored as (red, green, blue) for png parity
        # MAKE SURE TO REVERSE THIS WHEN MAKING NEW BMP FILES
        rowSize = int((self.dib.bpp * self.dib.width + 31) / 32) * 4
        for y in range(self.dib.width):
            row = y * rowSize
            for x in range(self.dib.height):
                self.arr[x][self.dib.height - 1 - y] = (
                    int(image[row + (x * 3) + 2]),
                    int(image[row + (x * 3) + 1]),
                    int(image[row + (x * 3)]),
                )

    def __bytes__(self):
        data = bytearray()
        data += bytes(self.header)
        data += bytes(self.dib)
        padding = "x" * ((self.dib.width * 3) % 4)
        for y in reversed(range(self.dib.width)):
            for x in range(self.dib.height):
                data += struct.pack(
                    "<BBB", self.arr[x][y][2], self.arr[x][y][1], self.arr[x][y][0]
                )
            data += struct.pack(padding)
        extra = self.header.size - len(data)
        if extra > 0:
            data += struct.pack("x"*extra)
        return bytes(data)
