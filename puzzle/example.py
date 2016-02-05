import puzzle
import puzzle_piece
import time
import cv2
import numpy as np
import json
from matplotlib import pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), './puzzleFunctionsC/'))
import puzzleFunctionsC

def template_match_rgb(img, template):
    (rowsImg, colsImg, _) = img.shape
    (rowsTpl, colsTpl, _) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    t0 = time.time()
    #for row in range(0, rowsImg-rowsTpl, 2):
    for row in range(0, rowsImg-rowsTpl):
        print("row " + str(row) + " of " + str(rowsImg-rowsTpl))
        for col in range(0, colsImg - colsTpl):
            error = (img[row:row+rowsTpl, col:col+colsTpl,0] - template[:,:,0])**2
            error += (img[row:row+rowsTpl, col:col+colsTpl,1] - template[:,:,1])**2
            error += (img[row:row+rowsTpl, col:col+colsTpl,2] - template[:,:,2])**2
            error[template[:,:,0]==0] = 0
            
            result[row, col] = np.sum(error)
    print("time " + str(time.time()-t0))
    return result
    
def template_match_fast(img, template, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize):
    mask = np.logical_not(np.logical_and(np.logical_and(template[:,:,0]==0, template[:,:,1]==0), template[:,:,2]==0)).astype('uint8')

    template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)     
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    result = puzzleFunctionsC.template_match2(img[:,:,0], template[:,:,0], mask, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize)
    result += puzzleFunctionsC.template_match2(img[:,:,1], template[:,:,1], mask, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize)
    result += puzzleFunctionsC.template_match_v2(img[:,:,2], template[:,:,2], mask, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize)
    result[result<1e-6] = np.max(result)
    #result = result - np.min(result)
    #result = result/np.max(result)
    #result = result * 5
    #result[result>1] = 1
    
    return result
    
    
def template_match_hsv(img, template):
    (rowsImg, colsImg, _) = img.shape
    (rowsTpl, colsTpl, _) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    t0 = time.time()    
    template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)     
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
    
    template = template.astype('float')    
    img = img.astype('float')
    temp = template[:,:,2]
    templateMeanBrightness = np.mean(temp[temp>1e-6]);

    #for row in range(0, rowsImg-rowsTpl, 2):
    for row in range(0, rowsImg-rowsTpl):
        if row % 10 == 0:
            print("row " + str(row) + " of " + str(rowsImg-rowsTpl))       
        for col in range(0, colsImg - colsTpl):
            error =  np.abs(img[row:row+rowsTpl, col:col+colsTpl,0] - template[:,:,0])
            error += np.abs(img[row:row+rowsTpl, col:col+colsTpl,1] - template[:,:,1])
            
            temp = img[row:row+rowsTpl, col:col+colsTpl,2]
            imgMeanBrightness = np.mean(temp[temp>0]);
            temp = temp * templateMeanBrightness/imgMeanBrightness;
            temp[temp>255] = 255            
            diff = temp - template[:,:,2]
            #meanVal = np.mean(diff[np.abs(template[:,:,0])<1e-6])
            error += np.abs(diff)
            
            error[np.abs(template[:,:,0])<1e-6] = 0
            
            result[row, col] = np.sum(error)
    print("time " + str(time.time()-t0))
    return result    
    
    
def template_match_hsv_full(img, template, oldMatch):
    """ matches the template but only does so where the previous search found 
    something interesting.
    """
    (rowsImg, colsImg, _) = img.shape
    (rowsTpl, colsTpl, _) = template.shape
    (rowsOld, colsOld) = oldMatch.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    t0 = time.time()    
    template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)     
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 
    
    template = template.astype('float')    
    img = img.astype('float')
    
    for row in range(0, rowsImg-rowsTpl):
        if row % 10 == 0:
            print("row " + str(row) + " of " + str(rowsImg-rowsTpl))        
        if np.any(oldMatch[min(rowsOld-1, row/4),:]<1):
            for col in range(0, colsImg - colsTpl):
                if oldMatch[min(rowsOld-1, row/4),min(colsOld-1, col/4)] < 1:
                    error = np.abs(img[row:row+rowsTpl, col:col+colsTpl,0] - template[:,:,0])
                    error += np.abs(img[row:row+rowsTpl, col:col+colsTpl,1] - template[:,:,1])
                    error += np.abs(img[row:row+rowsTpl, col:col+colsTpl,2] - template[:,:,2])
                    error[np.abs(template[:,:,0])<1e-6] = 0
                    
                    result[row, col] = np.sum(error)
                else:
                    result[row, col] = -1
        else:
            result[row, :] = -1
                        
    print("time " + str(time.time()-t0))
    return result    

def template_match(puzzle_img, orientated_piece, orient, mins, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize):
    
#    # Comparision takes place in HSV space.
    pieceHSV = cv2.cvtColor(pieceShrunk, cv2.COLOR_BGR2HSV)[:,:,2].astype('float')
    puzzleHSV = cv2.cvtColor(puzzleShrunk, cv2.COLOR_BGR2HSV)[:,:,2].astype('float')
    
    # do the template match and find the 5 best fits.
    result = template_match_fast(puzzleShrunk, pieceShrunk, offsetRows, offsetCols, pieceRows, pieceCols, rangeSize)        
#    cv2.imshow("result " + str(orient), result)
    (r, c) = pieceShrunk.shape[:2]
    (R, C) = puzzleShrunk.shape[:2]
    for nMins in range(5):
        ind = np.argmin(result)
        (i, j) = np.unravel_index(np.argmin(result), result.shape)
        diff = pieceHSV - puzzleHSV[i:i+r, j:j+c]
        diff[pieceHSV<1e-6] = 0
        interQRange = np.percentile(diff, 75) - np.percentile(diff, 25)
        mins.append((orient, result[i,j], interQRange, i, j))        
        result[max(0, i-r):min(R, i+r), max(0, j-c):min(C, j+c)] = np.inf
    
    return (puzzleShrunk, pieceShrunk)
    
    

# Select a new puzzle and reshape 
# OR
# Select a previously saved puzzle
puzzleName = 'Soccer1' 
pth = r"C:\Dev\python\general\puzzle"
p = puzzle.OpenExistingPuzzle(puzzleName, pth)

i = 10
img_full = cv2.imread(pth + "\\" + "pieces_on_white_" + str(i+1) + ".jpg")
(rotated, edgeType, x1, y1, x2, y2) = puzzle_piece.Normalize(img_full)
#print((x1, y1, x2, y2))
print(edgeType)

# Get the Dimenstions and rescalings for the puzzle
rows = y2 - y1
cols = x2 - x1
(targetRows, targetCols) = p.GetPieceSize()
scale = (float(targetRows) + targetCols)/(rows+cols)

# shrink the piece to be close to the puzzle image implied size
if scale<1:
    kernelSize = int(2 * np.round(1/scale) - 1)
    rotatedResized = cv2.GaussianBlur(rotated,(kernelSize,kernelSize),0)    
else:
    rotatedResized = np.copy(rotated)
rotatedResized = cv2.resize(rotatedResized, None, fx=scale, fy=scale, interpolation = cv2.INTER_CUBIC)


# Blur and decrease size, remove blur on piece into the black part
puzzleShrunk = cv2.GaussianBlur(p.img_full,(9,9),0)
puzzleShrunk = cv2.resize(puzzleShrunk, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)
pieceShrunk = cv2.GaussianBlur(rotatedResized,(9,9),0)
pieceShrunk[rotatedResized==0] = 0
pieceShrunk = cv2.resize(pieceShrunk, None, fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC)

# find the estimated locatation of the square main piece body
scaleRows = pieceShrunk.shape[0]/float(rotated.shape[0])
scaleCols = pieceShrunk.shape[1]/float(rotated.shape[1])
x1 = x1 * scaleCols
y1 = y1 * scaleRows
x2 = x2 * scaleCols
y2 = y2 * scaleRows
(r, c) = pieceShrunk.shape[:2]
topLeft = []
topLeft.append((x1, y1))
topLeft.append((y1, c-x2))
topLeft.append((c-x2, r-y2))
topLeft.append((r-y2, x1))

# Estimated locations of the puzzle pieces assuming they are all about the 
# same size
pieceRows = float(puzzleShrunk.shape[0])/p.size_pieces[1]
pieceCols = float(puzzleShrunk.shape[1])/p.size_pieces[2]
rangeSize = 5   


mins = []
pieces = []
for orientation in range(4):
    print("orientation angle " + str(orientation*90))
    offsetRows = topLeft[orientation][1]
    offsetCols = topLeft[orientation][0]
    (puzzleShrunk, pieceShrunk) = template_match(p.img_full, pieceShrunk, orientation, mins, 
                                                 offsetRows, offsetCols, pieceRows, pieceCols, rangeSize)
    pieces.append(pieceShrunk)
    pieceShrunk = pieceShrunk.copy()
    pieceShrunk = np.rot90(pieceShrunk)


np.savez('TemplateMatchTest', img=puzzleShrunk, template=pieceShrunk, 
         x1=x1, x2=x2, y1=y1, y2=y2)



npMins = np.array(mins)
order = np.argsort(npMins[:,1])
colors = [(0,0,255), (0,255,0), (255,0,0)]
font = cv2.FONT_HERSHEY_PLAIN
for minNumber in range(10):
    piece = pieces[int(npMins[order[minNumber], 0])]
    (r, c) = piece.shape[:2]
    (i, j) = npMins[order[minNumber], 3:].astype('int')
    cv2.rectangle(puzzleShrunk, (j, i), (j+c, i+r), colors[0],2)
    puzzleShrunk = cv2.putText(puzzleShrunk,str(minNumber+1),(j+c, i+r), font, 1, colors[0], 2)

cv2.imshow("puzzleShrunk", puzzleShrunk)
#rotated = rotated.copy()
#rotated = cv2.rectangle(rotated, (x1, y1), (x2, y2), [0, 255, 255], 4)
cv2.imshow("piece", rotated)

#
## get the 5 best matches from each orientation and do some contour matching on them
#ind = np.argmin(result[0][0])
#(i, j) = np.unravel_index(np.argmin(result[0][0]), result[0][0].shape)
#r, c = result[0][1][0:2]

#mins = []
#for orient in range(4):
#    r, c = result[orient][1][0:2]
#    for nMins in range(5):
#        ind = np.argmin(result[orient][0])
#        (i, j) = np.unravel_index(np.argmin(result[orient][0]), result[orient][0].shape)
#        mins.append((orient, result[orient][0][i,j], i, j))
#        result[orient][0][i-r:i+r, j-c:j+c] = np.inf

    



#result = np.sqrt(result)
#result = result - np.min(result)
#result = result/np.max(result)
#result = result * 5
#result[result>1] = 1
#
#np.save("result_p1", result)
#
#
#cv2.imshow("puzzleShrunk", puzzleShrunk)
#cv2.imshow("pieceShrunk", pieceShrunk)
#cv2.imshow("result", result/np.max(result))


