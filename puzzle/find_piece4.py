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
img_full = cv2.imread(pth + "\\" + "pieces_on_white_4.jpg")
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
puzzle piece.  This also means we lose the proper holes and will have to find 
them again later"""
kernel = np.ones((9,9),np.uint8)
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

"""
Go around the edge and check that we have a single contour and look for the 
most likely corner
"""
row = 0
while not np.any(blank[row,:]>0):
    row += 1


"""
Find the most likely corner
"""
cornerScores = cv2.cornerHarris(mask1,2,3,0.04)
[mRow, mCol] = np.unravel_index(cornerScores.argmax(), cornerScores.shape)
blank[mRow:mRow+2, mCol:mCol+2] = 255

blank = expand_image(blank)
cv2.imshow("blank",blank)





mask1_big = cv2.resize(mask1, (old_ny, old_nx), interpolation = cv2.INTER_CUBIC) 



img2, contours, hierarchy = cv2.findContours(mask1_big,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
longest_c = []
if len(contours)>1:
    for contour in contours:
        if len(contour)>len(longest_c):
            longest_c = contour
else:
    longest_c = contours[0]

contour = longest_c



""" Now work with the full size image again and crop it
"""

hull = cv2.convexHull(contour)

rect = cv2.minAreaRect(contour)
box = cv2.boxPoints(rect)
box = np.int0(box)

center = np.mean(box,0)

M = cv2.getRotationMatrix2D((center[0],center[1]),90+rect[2],1)
rotated = cv2.warpAffine(img_full,M,(nx*2,ny*2))
newBox = np.round(np.transpose(np.dot(M[:,0:2], np.transpose(box))) + np.tile(M[:,2],(4,1))).astype(int)
minX = np.min(newBox[:,0])
maxX = np.max(newBox[:,0])
minY = np.min(newBox[:,1])
maxY = np.max(newBox[:,1])
rotated = rotated[minY:maxY+1, minX:maxX+1]

newHull = np.zeros(hull.shape, dtype = int)
for (i, point) in enumerate(hull):
    newHull[i] = (np.round(np.transpose(np.dot(M[:,0:2], np.transpose(point))) + M[:,2]) - np.array([minX, minY])).astype(int)
    
newContour = np.zeros(contour.shape, dtype = int)
for (i, point) in enumerate(contour):
    newContour[i] = (np.round(np.transpose(np.dot(M[:,0:2], np.transpose(point))) + M[:,2]) - np.array([minX, minY])).astype(int)


edges = cv2.Canny(rotated,25,100)

#cv2.drawContours(img_full, [hull], -1, (255,0,0), 3)
#cv2.drawContours(img_full, [contour], 0, (0,255,0), 1)
#cv2.drawContours(img_full,[box],0,(0,0,255),2)
rotated_with_extra = cv2.warpAffine(img_full,M,(nx*2,ny*2))
rotated_with_extra = rotated_with_extra[minY:maxY+1, minX:maxX+1]
cv2.drawContours(rotated_with_extra, [newHull], 0, (255,255,0), 1)
cv2.drawContours(rotated_with_extra, [newContour], 0, (0,255,0), 1)
rotated_with_extra[edges==255,:]=255

#cv2.imshow("rotated", rotated)
cv2.imshow("rotated_with_extra", rotated_with_extra)

# smooth the contour a bit

# try to get the type of piece
# If contour is close to hull then edge
# If contour is far from hull in middle of side then hole
# if contour is close to hull in middle of side then bulge


           

        