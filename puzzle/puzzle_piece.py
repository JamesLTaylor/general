from matplotlib import pyplot as plt
import cv2
import numpy as np

def angle_scores(angles, template, piece):
    """ Rotates the image through the prescribed angles and finds the best fit 
    of the template on the bottom edge.
    
    The template is scaled to fit the piece and the score is scaled by the area 
    of the template
    """
    
    # resize the template
    # rotate the shape
    # remove all black rows and columns
    #and do a template match
    font = cv2.FONT_HERSHEY_PLAIN
    (template_h, template_w) = template.shape
    (nRows, nCols) = piece.shape

    scores = np.zeros(angles.shape)
    offsets = np.zeros(angles.shape)

    for (i, angle) in enumerate(angles):

        # Rotate, crop all black, then crop top 70% of pixels since I am
        # looking for what the bottom looks like
        # 
        M = cv2.getRotationMatrix2D((nCols/2, nRows/2),angle,1)
        rotated = cv2.warpAffine(piece,M,(int(nCols*1.5),int(nRows*1.5)))
        rotated = rotated[:, np.any(rotated>0,0)]
        rotated = rotated[np.any(rotated>0,1), :]
        (cropped_h, cropped_w) = rotated.shape
        rotated = rotated[-cropped_h/3:,:]
        (cropped_h, cropped_w) = rotated.shape
        # try to get rid of horizontal bulges that make the sizing bad.
        enoughPixels = np.sum(rotated>0,0)>cropped_h/10
        trueCols = np.where(enoughPixels)
        if len(trueCols[0])==0:
            print(rotated)
        enoughPixels[trueCols[0][0]:trueCols[0][-1]] = True
        rotated = rotated[:, enoughPixels]
        rotated = rotated[np.any(rotated>0,1), :]
        (cropped_h, cropped_w) = rotated.shape
        
        
        #
        # Padding 
        rotated = cv2.copyMakeBorder(rotated,40,40,40,40,cv2.BORDER_CONSTANT,value=0)

        #
        # Scale the template to be a similar size to the rotated and cropped piece
        scale1 = float(cropped_w)/template_w
        scale2 = float(cropped_h)/template_h
        scale = min(scale1, scale2)
        resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)
        (resized_h, resized_w) = resized_template.shape

        match = cv2.matchTemplate(rotated,resized_template,cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
        
        top_left = min_loc
        bottom_right = (top_left[0] + resized_w, top_left[1] + resized_h)
        cv2.rectangle(rotated,top_left, bottom_right, 128, 1)

        new_rotated = cv2.copyMakeBorder(rotated,0,100,100,0,cv2.BORDER_CONSTANT,value=0)
        new_rotated = cv2.putText(new_rotated,str(np.round(min_val/(resized_h * resized_w),4)),(0,50), font, 1,128)

        scores[i] = min_val/(resized_h * resized_w)
        offsets[i] = top_left[1]


        #
        # Interactive plotting
        #
#        cv2.imshow("new_rotated", new_rotated)
#        cv2.imshow("template", template)        
#        cv2.waitKey()

    return scores
    
def compare_guesses(templates, edgeTypeToUse, rotated):
    # Make a rough sketch of what the piece looks like
    DISPLAY = False
    (h, w) = templates[0].shape
    xOverlap = int(30)
    yOverlap = int(30)
    sketchW = 2*h+w-2*xOverlap
    sketchH = 2*h+w-2*yOverlap
    sketch = np.zeros((sketchH, sketchW), dtype='uint8')
    
    fillY1 = h
    fillY2 = h + w - 2*yOverlap
    fillX1 = h
    fillX2 = h + w - 2*xOverlap
    sketch[fillY1:fillY2, fillX1:fillX2] = 255

    
    y1 = h + w - 2*yOverlap        
    x = h -xOverlap
    
    y = y1 - (int(edgeTypeToUse[0])==1)*24
    sketch[y:y+h,x:x+w] = templates[int(edgeTypeToUse[0])]        
    
    sketch = np.rot90(sketch)
    y = y1 - (int(edgeTypeToUse[1])==1)*24
    sketch[y:y+h,x:x+w] = templates[int(edgeTypeToUse[1])]
    
    sketch = np.rot90(sketch)
    y = y1 - (int(edgeTypeToUse[2])==1)*24
    sketch[y:y+h,x:x+w] = templates[int(edgeTypeToUse[2])]
    
    sketch = np.rot90(sketch)
    y = y1 - (int(edgeTypeToUse[3])==1)*24
    sketch[y:y+h,x:x+w] = templates[int(edgeTypeToUse[3])]
    
    sketch = np.rot90(sketch)
    
    rotated = rotated[:, np.any(rotated>0,0)]
    rotated = rotated[np.any(rotated>0,1), :]
    sketch[sketch<255] = 0
    sketch = sketch[:, np.any(sketch>0,0)]
    sketch = sketch[np.any(sketch>0,1), :]        
    sketch = cv2.resize(sketch, rotated.shape[::-1])
    
    error = rotated-sketch
    error = np.sum(error>0)
        
    if DISPLAY == True:    
        cv2.imshow("final_angle", rotated)
        cv2.imshow("sketch", sketch) 
        cv2.waitKey()
        
    return error        
    
    
# Straight edge fits are always good so the score for those edges is 
# multiplied by a fudge factor to give the holes a chance.  Empirically this 
# is working well but may be very size dependent
def get_angle(piece):
    """ Takes a grayscale estimate of the shape of a puzzle piece.  
    White (255) for the piece and black (0) for the background
    
    Returns a guess at the piece description [a, b, c, d]
        0 = bulge
        1 = hole
        2 = straight
        
    and the angle through which it should be rotated to make its edges parallel 
    to the edges of the screen
    """
    
    fileBulge = "BulgeTemplate1.bmp"
    fileHole = "HoleTemplate1.bmp"
    fileStraight = "StraightTemplate1.bmp"  
    
    angles = np.arange(0, 360, 5)
    
    templates = []
    template = cv2.imread(fileBulge)
    template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    template = template[::-1,:]
    scores_bulge = angle_scores(angles, template, piece)
    #cv2.imshow("bulge", template)
    templates.append(np.copy(template))
    
    template = cv2.imread(fileHole)
    template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    #template = 255 - template
    scores_hole = angle_scores(angles, template, piece)
    #cv2.imshow("hole", template)
    templates.append(np.copy(template))
    
    template = cv2.imread(fileStraight)
    template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    template = template[::-1,:]
    scores_straight = 3*angle_scores(angles, template, piece)
    #cv2.imshow("straight", template)
    templates.append(np.copy(template))
    
    # Loop through all orientations and for each orientation choose the smallest
    # of the 3 edge types at angle, angle+90, angle+180, angle+270.
    # There could be some alternatives that are close to each other so we add them as well
    scores = np.transpose(np.vstack((scores_bulge, scores_hole, scores_straight)))
    #print(scores)
    
    steps = len(angles)/4
    edgeTypes = []
    finalScores = []
    angleList = []
    for i in range(steps):
        candidates = []
        for edge in range(4):
            e = np.argsort(scores[i+edge*steps,:])
            if scores[i+edge*steps,e[1]]<1.5*scores[i+edge*steps,e[0]]:
                candidates.append([e[0], e[1]])
            else:
                candidates.append([e[0]])
        
        for variant in [[i1, i2, i3, i4] for i1 in candidates[0] for i2 in candidates[1] for i3 in candidates[2] for i4 in candidates[3]]:
            edgeTypes.append(variant)
            angleList.append(i)
            finalScores.append(scores[i, edgeTypes[-1][0]] +
                      scores[i+steps, edgeTypes[-1][1]] +
                      scores[i+2*steps, edgeTypes[-1][2]] +
                      scores[i+3*steps, edgeTypes[-1][3]])
    
    orderedInd = np.argsort(finalScores)
    edgeTypes = np.array(edgeTypes)
    angleList = np.array(angleList)
    finalScores = np.array(finalScores)[orderedInd]    

    (nRows, nCols) = piece.shape
    
    # Consider all of the guesses that are close to optimal and compare them 
    # again to the whole puzzle piece.  This fizes some issues with comparing
    # one side at a time above that leads to wrong size guesses for the templates.
    orderedInd = orderedInd[finalScores<1.1*finalScores[0]]
    minError = np.inf
    for ind in orderedInd:        
        angle = angles[angleList[ind]]
        edgeTypeToUse = edgeTypes[ind]        
        M = cv2.getRotationMatrix2D((nCols/2, nRows/2),angle,1)
        rotated = cv2.warpAffine(piece,M,(int(nCols*1.5),int(nRows*1.5)))
        error = compare_guesses(templates, edgeTypeToUse, rotated)
        if error < minError:
            minError = error
            finalAngle = angle
            finalEdgeTypeToUse = edgeTypeToUse    
    
    return (finalAngle, finalEdgeTypeToUse)


"""
Takes in an image of a puzzle piece on a mostly white background and returns
    * image that is 
        * rotated 
        * cropped to just fit the piece
    * a mask of the piece
    * a measure of the size of piece for scaling by the puzzle
"""
def Normalize(img_full):
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
    
    (finalAngle, edgeType) = get_angle(mask)
    
    #
    # Scale the mask back to the original size
    new_mask = cv2.resize(mask, (int(old_ny),int(old_nx)))
    
    img_full[new_mask==0,0] = 0
    img_full[new_mask==0,1] = 0
    img_full[new_mask==0,2] = 0
    
    M = cv2.getRotationMatrix2D((old_ny/2, old_nx/2),finalAngle,1)
    rotated = cv2.warpAffine(img_full,M,(int(old_ny*1.5),int(old_nx*1.5)))
    rotated_mask = cv2.warpAffine(new_mask,M,(int(old_ny*1.5),int(old_nx*1.5)))
    rotated_mask = cv2.erode(rotated_mask, np.ones((11,11),np.uint8))
    
    rotated = rotated[:, np.any(rotated_mask>0,0), :]
    rotated = rotated[np.any(rotated_mask>0,1), :, :]
    
    #
    # Get the approximate size of the piece
    ratio = 1.0/3
    (rows, cols, _) = rotated.shape
    #print(edgeType)
    if edgeType[0]==0 and edgeType[2]==0:
        y1 = int(rows * ratio/(1+2*ratio))
        y2 = rows - y1
    elif not edgeType[0]==0 and edgeType[2]==0:
        y1 = int(rows * ratio/(1+ratio))
        y2 = rows-1
    elif edgeType[0]==0 and not edgeType[2]==0:
        y1 = 1
        y2 = int(rows - rows*ratio/(1+ratio))
    else:
        y1 = 1
        y2 = rows-1

    if edgeType[1]==0 and edgeType[3]==0:
        x1 = int(cols * ratio/(1+2*ratio))
        x2 = cols - x1
    elif edgeType[1]==0 and not edgeType[3]==0:
        x1 = int(cols * ratio/(1+ratio))
        x2 = cols-1
    elif not edgeType[1]==0 and edgeType[3]==0:
        x1 = 1
        x2 = int(cols-cols*ratio/(1+ratio))
    else:
        x1 = 1
        x2 = cols-1
    
   
    return (rotated, edgeType, x1, y1, x2, y2)
    

###############################################################################    
###############################################################################
###############################################################################
if __name__ == "__main__":
    #piece = np.load("piece.npy")
    #print(get_angle(piece))
    
    for i in range(0, 11):
        pth = r"C:\Dev\python\general\puzzle"
        img_full = cv2.imread(pth + "\\" + "pieces_on_white_" + str(i+1) + ".jpg")
        (rotated, edgeType, x1, y1, x2, y2) = Normalize(img_full)
        print(edgeType)
        print((x1, y1, x2, y2))
        

