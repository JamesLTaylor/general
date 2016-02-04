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

edges = cv2.Canny(img,25,100)
cv2.imshow("Canny edges all 100", edges)

lines = cv2.HoughLines(edges,1,np.pi/180,100)
for line in lines:
    for rho,theta in line:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imshow('houghlines3.jpg',img)