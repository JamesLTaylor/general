import puzzle
import puzzle_piece
import time
import cv2
import numpy as np
import json
from matplotlib import pyplot as plt


r = np.load("result_p1.npy")

(rows, cols) = r.shape

mins = []
for row in range(3, rows-4):
    for col in range(4, cols-4):
        pt = np.argmin(r[row-3:row+4, col-3:col+4])
        if pt == 24 and r[row, col] < 1-1e-6:
            mins.append([row, col, r[row, col]])

img = np.copy(p.img_full)
piece = np.copy(rotatedResized)
(rowsPiece, colsPiece, _) = piece.shape
for row in mins:
    r = row[0]*4
    c = row[1]*4
    temp1 = np.copy(img[r:r+rowsPiece, c:c+colsPiece])
    temp1[piece==0] = 0
    temp2 = np.concatenate((piece, temp1),0)
    temp3 = cv2.cvtColor(temp2, cv2.COLOR_BGR2HSV)
    temp4 = np.concatenate((temp2, temp3[:,:,(0,0,0)], temp3[:,:,(1,1,1)], temp3[:,:,(2,2,2)]),1)
    temp5 = (128 + (temp4[:rowsPiece,:,:].astype('float') - temp4[rowsPiece:,:,:].astype('float'))/2).astype('uint8')
    temp6 = np.concatenate((temp4, temp5),0)
    
    d = 128 + (temp3[:rowsPiece,:,2].astype('float') - temp3[rowsPiece:,:,2].astype('float'))/2
    #print(np.std(d[d!=128]))
    print(-np.percentile(d[d!=128], 25) + np.percentile(d[d!=128], 75))

    cv2.imshow("compare", temp6)
    cv2.waitKey()

    
                