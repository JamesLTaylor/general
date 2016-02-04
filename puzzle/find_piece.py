from matplotlib import pyplot as plt

pth = r"C:\Dev\python\general\puzzle"
img_full = cv2.imread(pth + "\\" + "pieces_on_white_1.jpg")

#frame = [[1232, 626],
#[1966, 1165]]

full_puzzle_size = (1768, 2485, 3)
reduced_size = (600, 843, 3)
pieces = (500, 20, 25)


# crop
img = img_full

#img = cv2.resize(img,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_AREA)
#img = img_full[0:1000, 0:100, :]
cv2.imshow("single piece", img)

img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

background = np.concatenate((img_hsv[:,0,:], img_hsv[:,-1,:], 
                             img_hsv[0,:,:], img_hsv[-1,:,:])) 
                             
lower_colour =  np.percentile(background, 0.1, 0)
upper_colour =  np.percentile(background, 0.9, 0)                            
mean_colour = np.mean(background, 0)

mask = cv2.inRange(img_hsv, lower_colour-[20, 50, 50], upper_colour+[20, 50, 50]) 

cv2.imshow("mask", mask)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

(rows, cols, _) = img_hsv.shape

dist = img_hsv - np.tile(mean_colour,(rows,cols, 1))
dist = np.sqrt(dist[:,:,0]**2 + dist[:,:,1]**2 + dist[:,:,2]**2)
cv2.imshow("dist", dist/np.max(dist))


"""
gray = np.float32(gray)
dst = cv2.cornerHarris(gray,2,3,0.04)
#result is dilated for marking the corners, not important
dst = cv2.dilate(dst,None)
# Threshold for an optimal value, it may vary depending on the image.
img[dst>0.01*dst.max()]=[0,0,255]
   
cv2.imshow('dst',img)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
"""

"""
edges = cv2.Canny(gray,100,200)
plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
"""

