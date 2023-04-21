#!/usr/bin/env python3

# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later


class Bmp:
    def __init__(self, filename):
        in_file = open(filename, "rb")
        bmp = in_file.read()
        in_file.close()
        header = bmp[:14]
        dib = bmp[14 : 14 + int.from_bytes(bmp[14:18], "little")]
        image = bmp[int.from_bytes(header[10:], "little") :]
        self.valid = header.startswith(b"\x42\x4d")
        if not self.valid:
            print("not a valid bitmap")
            pass
        if int.from_bytes(dib[:4], "little") != 40:
            print(
                "program currently only supports BITMAPINFOHEADER bmp files, aborting"
            )
            pass
        self.size = int.from_bytes(header[2:4], "little")
        self.startingAddress = int.from_bytes(header[10:], "little")
        self.width = int.from_bytes(dib[4:8], "little")
        self.height = int.from_bytes(dib[8:12], "little")
        self.planes = int.from_bytes(dib[12:14], "little")
        self.bpp = int.from_bytes(dib[14:16], "little")
        self.compression = int.from_bytes(dib[16:20], "little")
        self.imgSize = int.from_bytes(dib[20:24], "little")
        self.horizontalRes = int.from_bytes(dib[24:28], "little")
        self.verticalRes = int.from_bytes(dib[28:32], "little")
        self.palatte = int.from_bytes(dib[32:36], "little")
        self.importantColors = int.from_bytes(dib[36:40], "little")
        if self.bpp != 24:
            print(
                "only 24 bits per pixel currently supported, "
                + "will not create pixel array"
            )
            pass
        if self.compression == 4:
            print(
                "that...that's a jpeg. you took a jpeg and gave it a bmp header. "
                + "go sit in the corner and think about what you've done."
            )
            pass
        if self.compression == 5:
            print(
                "that...that's a png. you took a png and gave it a bmp header."
                + "go sit in the corner and think about what you've done."
            )
            pass
        if self.compression != 0:
            print("this program only works for uncompressed bitmaps")
            pass
        # now stores pixels as [x][y] from top to bottom
        self.arr = []
        for x in range(self.width):
            self.arr.append([])
            for y in range(self.height):
                self.arr[x].append([])
        # NOTE: colors are stored as (red, green, blue) for png parity
        # MAKE SURE TO REVERSE THIS WHEN MAKING NEW BMP FILES
        rowSize = int((self.bpp * self.width + 31) / 32) * 4
        for y in range(self.width):
            row = y * rowSize
            for x in range(self.height):
                self.arr[x][self.height - 1 - y] = (
                        int(image[row + (x * 3) + 2]),
                        int(image[row + (x * 3) + 1]),
                        int(image[row + (x * 3)]),
                    )

    def getValid(self):
        return self.valid

    def getSize(self):
        return self.size

    def getStartingAddress(self):
        return self.startingAddress

    def getWidth(self):
        return self.width

    def getHeight(self):
        return self.height

    def getPlanes(self):
        return self.planes

    def getBPP(self):
        return self.bpp

    def getCompression(self):
        return self.compression

    def getImgSize(self):
        return self.imgSize

    def getHorizontalRes(self):
        return self.horizontalRes

    def getVerticalRes(self):
        return self.verticalRes

    def getPalatte(self):
        return self.palatte

    def getImportantColors(self):
        return self.importantColors

    def getArr(self):
        return self.arr

    def getPixel(self, x, y):
        x -= 1
        y -= 1
        return self.arr[x][y]
