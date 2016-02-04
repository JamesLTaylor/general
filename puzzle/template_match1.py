from matplotlib import pyplot as plt
import cv2
import numpy as np


def expand_image(blank):
    blank = cv2.resize(blank, None, fx=6, fy=6, interpolation = cv2.INTER_NEAREST)
    (nrows, ncols) = blank.shape
    y = 6
    while y<(nrows-6):
        blank[y,:] = 64
        y+= 6

    x = 6
    while x<(ncols-6):
        blank[:,x] = 64
        x+= 6

    return blank




    
for i in [10]:#range(11):
    piece = cv2.imread("shape"  + str(i+1) + ".bmp")
    piece = cv2.cvtColor(piece,cv2.COLOR_BGR2GRAY)
    
    (finalAngle, edgeType) = get_angle(piece)
    print(finalAngle)



