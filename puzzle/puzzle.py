import cv2
import numpy as np
import json


"""
Mini application to take in a raw puzzle box image and to crop it and set the 
puzzle size
"""    
class PuzzleScaler():
    def __init__(self, img_full):
        # open the puzzle image and set the corners        
        self.img_full = img_full
        
        self.mousedown = False        
        (nx, ny, ncol) = img_full.shape    
        self.scale = 800.0/nx
        img = cv2.resize(img_full, (int(ny*self.scale),int(nx*self.scale)))
        
        self.img = img
        self.corner_held = -1
        
        (nrows, ncols, _) = img.shape
        self.corners = [(int(0.1*ncols), int(0.1*nrows)),
                        (int(0.9*ncols), int(0.1*nrows)),
                        (int(0.9*ncols), int(0.9*nrows)),
                        (int(0.1*ncols), int(0.9*nrows))]
                        
        self.update_rect()
        self.set_corners_gui()
        
        #return an approtiatly cropped puzzle image
        
        
        
    def update_rect(self):
        self.imgoverlay = np.zeros(self.img.shape, np.uint8)
        cv2.line(self.imgoverlay, self.corners[0], self.corners[1], (0, 0, 255), 2)
        cv2.line(self.imgoverlay, self.corners[1], self.corners[2], (0, 0, 255), 2)
        cv2.line(self.imgoverlay, self.corners[2], self.corners[3], (0, 0, 255), 2)
        cv2.line(self.imgoverlay, self.corners[3], self.corners[0], (0, 0, 255), 2)
        if self.corner_held>-1:
            cv2.circle(self.imgoverlay, self.corners[self.corner_held], 5, (0, 0, 255), 2)        

        
    def corner_event_handler(self, event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mousedown = True            
            # check which corner we are near
            for i in range(4):
                dist = np.sqrt((x-self.corners[i][0])**2 + (y-self.corners[i][1])**2)
                if dist<10:
                   self.corner_held = i
                   #print("pressed corner number " + str(i))
    
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mousedown == True:
                self.corners[self.corner_held] = (x, y)
                self.update_rect()
    
        elif event == cv2.EVENT_LBUTTONUP:
            self.mousedown = False
            self.corner_held = -1      
            
            
    """
    """            
    def set_corners(self, new_corner_array = None):        
        
        if new_corner_array:
            self.corners = new_corner_array
            
        corner_array = np.array(self.corners)
        corner_array_full = (corner_array/self.scale)
        avg_cols = (corner_array_full[1][0]-corner_array_full[0][0] + 
                   corner_array_full[2][0]-corner_array_full[3][0])/2
        avg_rows = (corner_array_full[3][1]-corner_array_full[0][1] + 
                   corner_array_full[2][1]-corner_array_full[1][1])/2
        new_corner_array = np.array([[0,0], [avg_cols-1, 0], [avg_cols-1, avg_rows-1], [0, avg_rows-1]])
        
        #print(corner_array)
        #print(corner_array_full)
        #print(new_corner_array)
        
        M = cv2.getPerspectiveTransform(corner_array_full.astype("float32"),new_corner_array.astype("float32"))
        #print(M)
        self.new_img_full = cv2.warpPerspective(self.img_full, M, (int(avg_cols), int(avg_rows)))
        
    
    def set_corners_gui(self):
        print('drag red line corners to puzzle corners')
        print('Press "s" to set the corners and save the puzzle')
        print('')
        cv2.namedWindow('image')
        cv2.setMouseCallback('image',self.corner_event_handler)
        
        while(1):
            try:
                cv2.imshow('image',cv2.add(self.img,self.imgoverlay))
                k = cv2.waitKey(1) & 0xFF
                if k == ord('s'):
                    self.set_corners()
                    cv2.destroyAllWindows()
                    break
                elif k == 27:
                    self.set_corners()
                    cv2.destroyAllWindows()
                    break
            except:
                cv2.destroyAllWindows()
                raise
        
        cv2.destroyAllWindows()
        
    def GetCroppedImage(self):
        return self.new_img_full     
    

"""
A puzzle.  Made up of an image and information about its number of pieces
"""
class Puzzle():    
    def __init__(self, name,  img_full, size_cm, size_pieces):
        self.name = name
        self.img_full = img_full
        self.size_cm = size_cm
        self.size_pieces = size_pieces
        
        
    def __str__(self):        
        str_version = "------------------------------\n" 
        str_version += "Representation of object:\n" 
        
        str_version += "------------------------------\n" 
        return str_version        
        

    def show_with_approx_pieces(self):
        new_img = np.copy(self.img_full)        
        (nrows, ncols, _) = new_img.shape    
        scale = 800.0/nrows
        new_img = cv2.resize(new_img, (int(ncols*scale), int(nrows*scale)))        
        
        (nrows, ncols, _) = new_img.shape
        dy = float(nrows) / (self.size_pieces[1])
        dx = float(ncols) / (self.size_pieces[2])
        
        
        for row in range(self.size_pieces[1]):
            cv2.line(new_img, (0, int(row*dy)), (ncols-1, int(row*dy)), (0, 0, 255), 1)
            
        for col in range(self.size_pieces[2]):
            cv2.line(new_img, (int(col*dx), 0), (int(col*dx), nrows-1), (0, 0, 255), 1)
            
        cv2.imshow("Puzzle with approximate pieces", new_img)
       
       
    def GetPieceSize(self):
        """
        Approximate size of the piece in pixels.  The template that is used to 
        search should be about the same size
        """
        (rows, cols, _) = self.img_full.shape
        return (rows/self.size_pieces[1], cols/self.size_pieces[2])
        
    
    def Save(self, pth):
        img_fname = pth + "\\" + self.name + ".jpg"
        json_fname = pth + "\\" + self.name + ".json"
        
        cv2.imwrite(img_fname, self.img_full)
        d = {}
        d['name'] = self.name
        d['size_cm'] = self.size_cm
        d['size_pieces'] = self.size_pieces
        f = open(json_fname, 'w')
        json.dump(d, f)
        f.close()
       
       
def OpenExistingPuzzle(puzzleName, pth):    
    """ Returns an instance of a puzzle object
    
    The puzzle already has a cropped image and information
    about the puzzle size.
    
    :param puzzleName: String used to id the puzzle when it was created
    :type puzzleName: String
    :param pth: Folder to look for the puzzle information
    
    :returns: a puzzle
    :rtype: puzzle.puzzle
    
    """     
    img_fname = pth + "\\" + puzzleName + ".jpg"
    json_fname = pth + "\\" + puzzleName + ".json"

    img_full = cv2.imread(img_fname)
    f = open(json_fname, 'r')
    d = json.load(f)
    f.close()
    
    return Puzzle(puzzleName,  img_full, d['size_cm'], d['size_pieces'])
    


""" Open a new puzzle from an image
"""
def OpenNewPuzzle(puzzleName, pth, fileName, size_cm, size_pieces):
    img_full = cv2.imread(pth + "\\" + fileName)

    newPuzzle = PuzzleScaler(img_full)

    croppedImage = newPuzzle.GetCroppedImage()    
        
    p = Puzzle(puzzleName, croppedImage, size_cm, size_pieces)
    p.Save(pth)
    
    return p
        


    

if __name__ == "__main__":
    puzzleName = 'Soccer1'
    pth = r"C:\Dev\python\general\puzzle"
    fileName = "puzzle_whole_raw.jpg"
    size_cm = (50.0, 40.0)
    size_pieces = (500, 20, 25)

    #p = OpenNewPuzzle(puzzleName, pth, fileName, size_cm, size_pieces)    

    p = OpenExistingPuzzle(puzzleName, pth)
    
    
#    p = puzzle(img_full, size_cm, size_pieces, name, pth)
#    
#    corners = [[ 299,    4],
#             [1363,    6],
#             [1396,  769],
#             [ 294,  782]]
#
#    p.set_corners_gui()   
#    p.set_corners(corners)   
#    p.show_with_approx_pieces()

