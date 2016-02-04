from matplotlib import pyplot as plt

pth = r"C:\Dev\python\general\puzzle"
img_full = cv2.imread(pth + "\\" + "pieces_on_white_4.jpg")

#frame = [[1232, 626],
#[1966, 1165]]

full_puzzle_size = (1768, 2485, 3)
reduced_size = (600, 843, 3)
pieces = (500, 20, 25)


# crop
img = img_full

"""imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
imgray = img_hsv[:,:,2]
imgray = img[:,:,1]
imgray = (imgray.astype(float) * 255.0 / np.max(imgray)).astype('uint8')

cv2.imshow("red", img[:,:,0])
cv2.imshow("green", img[:,:,1])
cv2.imshow("blue", img[:,:,2])

#img = cv2.resize(img,None,fx=0.5, fy=0.5, interpolation = cv2.INTER_AREA)
#img = img_full[0:1000, 0:100, :]
cv2.imshow("single piece", imgray)

laplacian = cv2.Laplacian(imgray,cv2.CV_64F)
cv2.imshow("laplacian",np.abs(laplacian)/np.max(np.abs(laplacian)))
"""

#ret,thresh = cv2.threshold(imgray,127,255,0)

img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, -1, (0,255,0), 3)

cv2.imshow("with contours", img)

edges = cv2.Canny(img[:,:,0],100,200)
cv2.imshow("Canny edges red", edges)

edges = cv2.Canny(img[:,:,1],100,200)
cv2.imshow("Canny edges green", edges)

edges = cv2.Canny(img[:,:,2],100,200)
cv2.imshow("Canny edges blue", edges)