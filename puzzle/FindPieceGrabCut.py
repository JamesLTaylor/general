import numpy as np
import cv2
from matplotlib import pyplot as plt

for i in range(11):

    pth = r"C:\Dev\python\general\puzzle"
    img_full = cv2.imread(pth + "\\" + "pieces_on_white_" + str(i+1) + ".jpg")
    (old_nx, old_ny, ncol) = img_full.shape    
    scale = 100.0/old_nx
    img = cv2.resize(img_full, (int(old_ny*scale),int(old_nx*scale)))
    
    mask = np.zeros(img.shape[:2],np.uint8)
    #mask = np.ones(img.shape[:2],np.uint8)*128
    #mask[0:200,0:200] = 0
    #mask[290:370, 460:560] = 1
    
    bgdModel = np.zeros((1,65),np.float64)
    fgdModel = np.zeros((1,65),np.float64)
    
    rect = (3,3,img.shape[1]-6,img.shape[0]-6)
    
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,2,cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img2 = img*mask2[:,:,np.newaxis]
    cv2.imshow("2 iter", img2)
     
    
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,4,cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img2 = img*mask2[:,:,np.newaxis]
    cv2.imshow("4 iter", img2)
    
    
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,6,cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
    img2 = img*mask2[:,:,np.newaxis]
    cv2.imshow("6 iter", img2)
    
    k = cv2.waitKey()
    
    