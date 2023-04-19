# Copyright 2023 Lucy Loerker, Maxwell Parker-Blue
# SPDX-License-Identifier: GPL-2.0-or-later

from bmpExtract import BMPExtract

filename = input("what file would you like to open? (type EXIT to close program) ")
if(filename.upper() == "EXIT"):
    print("goodbye!")
    quit()
bmp = BMPExtract(filename)
if(bmp.getValid()):
    print("it's valid!:3")
    print("size = " + str(bmp.getSize()) + " bytes")
    print("pixel array starting address: " + str(bmp.getStartingAddress()))
    print("width = " + str(bmp.getWidth()) + " pixels")
    print("height = " + str(bmp.getHeight()) + " pixels")
    print("color planes = " + str(bmp.getPlanes()))
    print("bits per pixel = " + str(bmp.getBPP()))
    print("compression method = " + str(bmp.getCompression()))
    print("image size = " + str(bmp.getImgSize()))
    print("horizonal resolution = " + str(bmp.getHorizontalRes()))
    print("vertical resolution = " + str(bmp.getVerticalRes()))
    print("colors in palette = " + str(bmp.getPalatte()))
    print("important colors = " + str(bmp.getImportantColors()))
    while(True):
        #NOTE: 1-indexed, may change later
        request = input("what pixel do you want color info on? please answer in the form x y (type EXIT to close program) ")
        if(request.upper() == "EXIT"):
            print("goodbye!")
            quit()
        tokens = request.split()
        if(len(tokens) != 2):
            print("please input exactly two numbers")
        x = int(tokens[0])
        y = int(tokens[1])
        if(x == 0 or y == 0):
            print("please use 1-indexing")
            continue
        if(x > bmp.getWidth() or y > bmp.getHeight()):
            print("please give a pixel that is in range of the image")
            continue
        if(x < 0 or y < 0):
            print("please no negatives :(")
            continue
        pixel = bmp.getPixel(x, y)
        red = pixel[2]
        green = pixel[1]
        blue = pixel[0]
        print(f"R = {red}, G = {green}, B = {blue}; hex code = "+ hex(red)+hex(green).lstrip("0x")+hex(blue).lstrip("0x"))
