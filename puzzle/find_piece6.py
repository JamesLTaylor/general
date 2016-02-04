"""
Grab cut 6 iterations
Open to remove speckles outside piece
Find the contours, approximate them with polygons, merge them and find the smallest bounding rectangle

crop and rotate on the original and resize again to get standardized positions 
and sizes of pieces

"""
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

for i in range(11):
    pth = r"C:\Dev\python\general\puzzle"
    img_full = cv2.imread(pth + "\\" + "pieces_on_white_" + str(i+1) + ".jpg")
    (old_nx, old_ny, ncol) = img_full.shape    
    scale = 150.0/old_nx
    img = cv2.resize(img_full, (int(old_ny*scale),int(old_nx*scale)))
    
    mask = np.zeros(img.shape[:2],np.uint8)
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)
    rect = (3,3,img.shape[1]-6,img.shape[0]-6)
    
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,6,cv2.GC_INIT_WITH_RECT)
    mask = np.where((mask==2)|(mask==0),0,255).astype('uint8')
    img2 = img*mask[:,:,np.newaxis]
    
    """ Remove speckles
    """
    kernel3 = np.ones((3,3),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel3)
    kernel5 = np.ones((3,3),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel5)
    #new_mask = cv2.dilate(mask,kernel3)
    new_mask = mask
    
    
    """ Look for corners
    """
    cornerScores = cv2.cornerHarris(new_mask,10,3,0.04)    

    cspos = np.copy(cornerScores)
    cspos[cspos<0]=0
    cspos = ((cspos/np.max(cornerScores))*255).astype('uint8')    
    #cv2.imshow("pos corners", cspos)
    
    csneg = np.copy(cornerScores)
    csneg = -csneg
    csneg[csneg<0]=0
    csneg = ((csneg/np.max(csneg))*255).astype('uint8')    
    #cv2.imshow("neg corners", csneg)    
    
    cv2.imwrite("shape"+str(i+1)+".bmp", new_mask)

    shape = expand_image(new_mask)
    cv2.imshow("shape", shape)
    
    
    """ Contours
    """
    _, contours, _ = cv2.findContours(new_mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    new_contours = []
    for contour in contours:
        new_contours.append(cv2.approxPolyDP(contour, 3, True))
        
    """ Merge contours
    """
    if len(new_contours)>1:
        merged_contours = np.vstack((new_contours[0], new_contours[1]))
    else:
        merged_contours = new_contours[0]
    for i in range(len(new_contours)-2):
        merged_contours = np.vstack((merged_contours, new_contours[i+2]))
        
    
    """ Rotate and crop on original image
    """
    rect = cv2.minAreaRect(merged_contours)
    box = cv2.boxPoints(rect)
    # Scale box up to full image
    box = np.round(box/scale)
    box = np.int0(box)
    
    center = np.mean(box,0)
    M = cv2.getRotationMatrix2D((center[0],center[1]),90.0+rect[2],1)
    rotated = cv2.warpAffine(img_full,M,(old_nx*2,old_ny*2))
    newBox = np.round(np.transpose(np.dot(M[:,0:2], np.transpose(box))) + np.tile(M[:,2],(4,1))).astype(int)
    minX = np.min(newBox[:,0])
    maxX = np.max(newBox[:,0])
    minY = np.min(newBox[:,1])
    maxY = np.max(newBox[:,1])
    rotated = rotated[minY:maxY+1, minX:maxX+1, :]
    
    cv2.imshow("rotated_cropped", rotated)
    cv2.waitKey()