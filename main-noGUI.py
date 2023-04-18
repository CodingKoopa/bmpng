from bmpExtract import BMPExtract

filename = input("what file would you like to open? ")
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