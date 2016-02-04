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
    

pth = r"C:\Dev\python\general\puzzle"
img_full = cv2.imread(pth + "\\" + "pieces_on_white_1.jpg")
#cv2.imshow("original", img_full)
(nx, ny, ncol) = img_full.shape

full_puzzle_size = (1768, 2485, 3)
reduced_size = (600, 843, 3)
pieces = (500, 20, 25)
   

""" Finds a contour around a single puzzle piece on an approximately white background
"""

"""    
Shrink the image and work with something closer to 100x100
Detect edges and regions that are not background
"""     
(old_nx, old_ny, ncol) = img_full.shape    
scale = 100.0/old_nx
img = cv2.resize(img_full, (int(old_ny*scale),int(old_nx*scale)))    

img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)    

_,inside1 = cv2.threshold(img_hsv[:,:,1],0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

edges = cv2.Canny(img,5,100)    
mask1 = edges+inside1
"""Apply a large kernel closure to make sure that we get a single object for the 
puzzle piece.  This also means we lose the propoer holes and will have to find 
them again later"""
kernel = np.ones((7,7),np.uint8)
mask1 = cv2.morphologyEx(mask1, cv2.MORPH_CLOSE, kernel) # same as dilate then erode

"""
appoximate the contours with polygons to straighten the edges to help find 
the dominant square.
"""
temp = cv2.merge((mask1, mask1, mask1))
_, contours, _ = cv2.findContours(mask1,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
new_contours = []
for contour in contours:
    new_contours.append(cv2.approxPolyDP(contour, 3, True))
    
    
#cv2.drawContours(temp, new_contours, -1, (0,255,0), 1)
#temp = cv2.resize(temp, (old_ny, old_nx), interpolation = cv2.INTER_NEAREST)
#cv2.imshow("mask1_big",temp)    
blank = np.zeros(mask1.shape, dtype="uint8")
cv2.drawContours(blank, new_contours, -1, 128)

floodMask = np.zeros((blank.shape[0]+2,blank.shape[1]+2),np.uint8)
floodMask[1:-1,1:-1] = blank

result = cv2.floodFill(blank, floodMask,( 50,50), 65)
blank = result[1]

"""
Go around the edge and check that we have a single contour and look for the 
most likely corner
"""
startRow = 0
while not np.any(blank[startRow,:]>0):
    startRow += 1
startCol = np.where(blank[startRow,:]>0)[0][0]

pRow = -1
pCol = 0



"""
Find the most likely corner
"""
cornerScores = cv2.cornerHarris(blank,5,3,0.04)
blank[cornerScores>(0.8*np.max(cornerScores))] = 255

#[mRow, mCol] = np.unravel_index(cornerScores.argmax(), cornerScores.shape)
#blank[mRow:mRow+2, mCol:mCol+2] += 20
#cornerScores[mRow-1:mRow+2, mCol-1:mCol+2] = 0


blank_big = expand_image(blank)
cv2.imshow("blank",blank_big)