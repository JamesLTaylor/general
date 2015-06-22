import numpy as np
import cv2
import moviepy.editor

#fname = r'C:\Dev\python\general\video\GBFULL_ORIGINALConverted.avi'
#fname = r'C:\Dev\python\general\video\Gbfull Original mpeg4.mp4'
#fname = r'C:\Dev\python\general\video\GBFULL ORIGINAL MPEG4Converted.avi'
#fname = r'C:\Dev\python\general\video\SAMPLE.avi'

def make_frame_list(clip):
    frames = []
    for i in range(25*20):
        frame = make_frame(i/25.0, clip)
        frame = frame[:,:,::-1]
        frames.append(frame)
        
    return frames

def make_frame_simple(t, clip):
    return clip.get_frame(t)

def make_frame(t, clip):
    print(t)
    thisframe = clip.get_frame(t)
    thisframe = thisframe[:,:,::-1]
    thisframe = cv2.cvtColor(thisframe, cv2.COLOR_BGR2YCrCb)        
    
    prevframe = clip.get_frame(t-1.0/25)
    prevframe = prevframe[:,:,::-1]
    prevframe = cv2.cvtColor(prevframe, cv2.COLOR_BGR2YCrCb)
    
    newframe = np.zeros(thisframe.shape, dtype = 'uint8')
    
    newframe[0::2,:,0] = thisframe[0::2,:,0] 
    newframe[1::2,:,0] = prevframe[1::2,:,0]
    
    newframe[:,:,0] = median_channel_0(newframe[:,:,0])
    
    newframe[:,:,1] = block_and_blur(thisframe[:,:,1], prevframe[:,:,1])
    newframe[:,:,2] = block_and_blur(thisframe[:,:,2], prevframe[:,:,2])
    
    newframe_ycbcr = newframe
    newframe = cv2.cvtColor(newframe, cv2.COLOR_YCrCb2BGR)        
    
    return newframe
        

def mix_lines(clip):
    offset = 0
    nframes = 2000
    slowdown = 1
    thisframe = clip.get_frame(1/25.0)
    newframe = np.zeros(thisframe.shape, dtype = 'uint8')
    
    # for i in range(nframes):
    i = 0
    while i < nframes:
    #while True:
        prevframe = thisframe
        thisframe = clip.get_frame((offset+i)/25.0)
        print("this frame number " + str((offset+i)))  
        thisframe = thisframe[:,:,::-1]
        thisframe = cv2.cvtColor(thisframe, cv2.COLOR_BGR2YCrCb)        
        
        newframe[0::2,:,0] = thisframe[0::2,:,0] 
        newframe[1::2,:,0] = prevframe[1::2,:,0]
        
        newframe[:,:,0] = median_channel_0(newframe[:,:,0])
        
        newframe[:,:,1] = block_and_blur(thisframe[:,:,1], prevframe[:,:,1])
        newframe[:,:,2] = block_and_blur(thisframe[:,:,2], prevframe[:,:,2])
        
        
        
        """newframe[0::4,:,1] = thisframe[0::4,:,1] 
        newframe[1::4,:,1] = thisframe[1::4,:,1] 
        newframe[2::4,:,1] = prevframe[2::4,:,1] 
        newframe[3::4,:,1] = prevframe[3::4,:,1] 
        
        newframe[0::4,:,2] = thisframe[0::4,:,2] 
        newframe[1::4,:,2] = thisframe[1::4,:,2] 
        newframe[2::4,:,2] = prevframe[2::4,:,2] 
        newframe[3::4,:,2] = prevframe[3::4,:,2] """        
        
        newframe_ycbcr = newframe
        newframe = cv2.cvtColor(newframe, cv2.COLOR_YCrCb2BGR)        
        
        
        cv2.imshow('original',cv2.cvtColor(thisframe, cv2.COLOR_YCrCb2BGR))
        cv2.imshow('mixed',newframe) 
        
        cv2.imshow('mixed_0',newframe_ycbcr[:,:,0]) 
        cv2.imshow('mixed_1',newframe_ycbcr[:,:,1]) 
        cv2.imshow('mixed_2',newframe_ycbcr[:,:,2]) 
        
        """k = cv2.waitKey(40*slowdown)
        i = i + 1
        """
        
        k = cv2.waitKey()
        if k == 2424832:
            i = i - 1
        elif k == 27:
            break
        else:
            i = i + 1        
        
    
    cv2.destroyAllWindows()    
    """        
    pth = r'C:\Dev\python\general\video\frames'

    cv2.imwrite(pth + "\\thisframe_0.png",thisframe[:,:,0])         
    cv2.imwrite(pth + "\\thisframe_1.png",thisframe[:,:,1]) 
    cv2.imwrite(pth + "\\thisframe_2.png",thisframe[:,:,2])    
    
    cv2.imwrite(pth + "\\prevframe_0.png",prevframe[:,:,0])         
    cv2.imwrite(pth + "\\prevframe_1.png",prevframe[:,:,1]) 
    cv2.imwrite(pth + "\\prevframe_2.png",prevframe[:,:,2])
    
    cv2.imwrite(pth + "\\mixed.png",newframe)         
    cv2.imwrite(pth + "\\mixed_0.png",newframe_ycbcr[:,:,0]) 
    cv2.imwrite(pth + "\\mixed_1.png",newframe_ycbcr[:,:,1]) 
    cv2.imwrite(pth + "\\mixed_2.png",newframe_ycbcr[:,:,2])
    
    """    

def split_lines(clip):
    pth = r'C:\Dev\python\general\video\frames'
    
    offset = 0
    nframes = 500
    slowdown = 3
    
    for i in range(0,nframes,2):
        frame = clip.get_frame((offset+i)/25.0)
        frame = clip.get_frame((290+i)/25.0)
        frame = frame[:,:,::-1]
        
        odd = np.zeros((584, 718,3), dtype='uint8')    
        odd[0::2,:,:] = frame[0::2,:,:]        
        cv2.imshow('split',odd)
        cv2.imwrite(pth + "\\odd_" + str(i) + ".png", odd)
    
            
        k = cv2.waitKey(100) & 0xFF
        
        even = np.zeros((584, 718,3), dtype='uint8')
        even[1::2,:,:] = frame[1::2,:,:]
        cv2.imshow('split',even)
        cv2.imwrite(pth + "\\even_" + str(i) + ".png", even)
        
        cv2.imshow('frame',frame)
        cv2.imwrite(pth + "\\frame_" + str(i) + ".png", frame)
        k = cv2.waitKey(100) & 0xFF
        
    cv2.destroyAllWindows()
    
    
def show_versions(clip):
    offset = 100
    nframes = 1200
    slowdown = 3
    frame = clip.get_frame(1/25.0)
    (r, c, chanels) = frame.shape
    rmin = r/2 - 100
    rmax = r/2 + 100
    cmin = c/2 - 100
    cmax = c/2 + 100
    vrange = slice(rmin, rmax, 1)
    hrange = slice(cmin, cmax, 1)
    frame = frame[vrange, hrange, :]
    
    
    odd = np.zeros(frame.shape, dtype='uint8')
    even = np.zeros(frame.shape, dtype='uint8')
    odd2 = np.zeros(frame.shape, dtype='uint8')
    even2 = np.zeros(frame.shape, dtype='uint8')
    black = np.zeros(frame.shape, dtype='uint8')
    
    # just make sure they are both visible
    cv2.imshow('odd frames',black)
    cv2.imshow('even frames',black) 
    
    i = 0
    channel = slice(1,2,1)
    while i < nframes:
    
        framenum = (offset+i)
        print(str(framenum))
        
        frame = clip.get_frame(framenum/25.0)
        frame = frame[vrange,hrange,::-1]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        if i % 2:
            cv2.imshow('odd frames', frame[:,:,channel])
            cv2.imshow('even frames', black)
        else:
            cv2.imshow('even frames',frame[:,:,channel])
            cv2.imshow('odd frames', black)
        
        cv2.imshow('all frames',frame[:,:,channel])            
        odd[0::2,:,:] = frame[0::2,:,:]
        odd[1::2,:,:] = frame[0::2,:,:]
        odd2[0::4,:,:] = frame[0::4,:,:]
        odd2[1::4,:,:] = frame[1::4,:,:]
        cv2.imshow('odd lines',odd2[:,:,channel])
        even[0::2,:,:] = frame[1::2,:,:]
        even[1::2,:,:] = frame[1::2,:,:]
        even2[2::4,:,:] = frame[2::4,:,:]
        even2[3::4,:,:] = frame[3::4,:,:]
        cv2.imshow('even lines',even2[:,:,channel])    
        
        #k = cv2.waitKey(40*slowdown) & 0xFF
        k = cv2.waitKey()
        if k == 2424832:
            i = i - 1
        elif k == 27:
            break
        else:
            i = i + 1
        
        
    cv2.destroyAllWindows()    

# 2.681s down to 1.03s     
def block_and_blur(thisframe1, prevframe1):    
    (r, c) = thisframe1.shape    
    newmixed = np.zeros((r/2, c/2), dtype = 'uint8')
    
    thisframe1 = thisframe1.astype('float')
    prevframe1 = prevframe1.astype('float')
    
    avg = (thisframe1[0::4,0::2] + thisframe1[1::4,0::2] + 
            thisframe1[0::4,1::2] + thisframe1[1::4,1::2])/4
    
    newmixed[0::2, :] = avg
    
    avg = (prevframe1[2::4,0::2] + prevframe1[3::4,0::2] + 
            prevframe1[2::4,1::2] + prevframe1[3::4,1::2])/4.0
    
    newmixed[1::2, :] = avg            
    
    kernel = np.ones((3,3))/9
    anchor = (1,1)
    newmixed = cv2.filter2D(newmixed, -1, kernel, anchor=anchor, borderType=cv2.BORDER_REPLICATE)       
    
    newnewmixed = np.zeros((r, c), dtype = 'uint8')
    
    newnewmixed[0::2,0::2] = newmixed
    newnewmixed[1::2,0::2] = newmixed
    newnewmixed[0::2,1::2] = newmixed
    newnewmixed[1::2,1::2] = newmixed        
    
    return newnewmixed
    
    
    
def block_and_blur_test():
    pth = r'C:\Dev\python\general\video\frames'
    thisframe1 = cv2.imread(pth + "\\thisframe_1.png", flags = 0)     
    prevframe1 = cv2.imread(pth + "\\prevframe_1.png", flags = 0)

    newmixed = block_and_blur(thisframe1, prevframe1)   
    cv2.imwrite(pth + "\\newmixed_1.png",newmixed)
    
    #cv2.imshow('newmixed', newmixed)
    #cv2.waitKey()
    #cv2.destroyAllWindows()    
    
def median_channel_0(mixed0):
    mixed0_median = cv2.medianBlur(mixed0, 3)
    return mixed0_median
    
def median_channel_0_test():
    pth = r'C:\Dev\python\general\video\frames'
    mixed0 = cv2.imread(pth + "\\mixed_0.png", flags = 0)
    mixed0_median = median_channel_0(mixed0)
    cv2.imwrite(pth + "\\mixed_0_median.png",mixed0_median)    
    


# fname = r'C:\Dev\python\general\video\GummiBearsV2E04 MyGummiLiesOverTheOcean.m4v'
fname = r'C:\Dev\python\general\video\title00.mkv'
clip = moviepy.editor.VideoFileClip(fname)

outfile = r'C:\Dev\python\general\video\movie3.mp4'
outfilesound = r'C:\Dev\python\general\video\movie3.mp3'

#make_frame_lam = lambda t : make_frame_simple(t, clip)
# newclip = moviepy.editor.VideoClip(make_frame_lam, 5)

framelist = make_frame_list(clip)
newclip = moviepy.editor.ImageSequenceClip(framelist, fps=25)
audioclip = clip.audio.subclip(0,20)
newclip = newclip.set_audio(audioclip)

newclip = newclip.set_duration(20)
audioclip.write_audiofile(outfilesound)
newclip.write_videofile(outfile,fps=25)


#show_versions(clip)
#mix_lines(clip)
#block_and_blur_test()



