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


def template_match(img, template, mask):
    (rowsImg, colsImg) = img.shape
    (rowsTpl, colsTpl) = template.shape
    result = np.zeros(((rowsImg-rowsTpl), (colsImg - colsTpl)))
    
    template = template.astype('float')    
    img = img.astype('float')
    
    for row in range(0, rowsImg-rowsTpl):
        for col in range(0, colsImg - colsTpl):
            error =  np.abs(img[row:row+rowsTpl, col:col+colsTpl] - template[:,:])            
            error[mask==0] = 0
            
            result[row, col] = np.sum(error)
    
    return result  

npzfile = np.load('TemplateMatchTest.npz')
img = npzfile['img']
template = npzfile['template']
refResult = npzfile['result']

cv2.imshow("puzzle example", img)
cv2.imshow("piece example", template)

mask = np.logical_not(np.logical_and(np.logical_and(template[:,:,0]==0, template[:,:,1]==0), template[:,:,2]==0)).astype('uint8')
template = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)     
img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


#t0 = time.time()
#result = template_match(img[:,:,0], template[:,:,0], mask)
#result += template_match(img[:,:,1], template[:,:,1], mask)
#result += template_match(img[:,:,2], template[:,:,2], mask)
#print("python time = " + str(time.time()-t0))    
#print("python error = " + str(np.mean(np.abs(refResult-result)) / np.mean(refResult)))    
#cv2.imshow("result Python", result/np.max(result))

t0 = time.time()
result = puzzleFunctionsC.template_match(img[:,:,0], template[:,:,0], mask)
result += puzzleFunctionsC.template_match(img[:,:,1], template[:,:,1], mask)
result += puzzleFunctionsC.template_match_v(img[:,:,2], template[:,:,2], mask)

print("C time = " + str(time.time()-t0))    
print("C error = " + str(np.mean(np.abs(refResult-result)) / np.mean(refResult)))  
result = result - np.min(result)
result = result/np.max(result)
result = result * 5
result[result>1] = 1
cv2.imshow("result C", result)


#t0 = time.time()
#result1 = puzzleFunctionsC.template_match_fast(img[:,:,0], template[:,:,0], mask)
#result1 += puzzleFunctionsC.template_match_fast(img[:,:,1], template[:,:,1], mask)
#result1 += puzzleFunctionsC.template_match_fast(img[:,:,2], template[:,:,2], mask)
#print("C time (fast) = " + str(time.time()-t0))    
#print("C error = " + str(np.mean(np.abs(refResult-result1)) / np.mean(refResult)))  
#cv2.imshow("result C (fast)", result1/np.max(result1))


cv2.imshow("result ref", refResult/np.max(refResult))
cv2.waitKey()




