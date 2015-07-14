import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import time
import threading
import note_trainer

def freq_from_harmonics(peaks):
    """ Get the lowest frequency consistent with the observed harmonics
    
    :param peaks: a Nx3 numpy array of frequency, unused, and peak score 
       
    :returns: the candidate frequency
    """
    max_freq = 7040
    new_peaks = peaks[peaks[:,0]<=max_freq,0:3:2]
    width = 0.03 # approx 2^(1/24)
    for i in range(len(new_peaks)):
        for multiplier in range(2,6):
            f = new_peaks[i,0]*multiplier
            j = i
            while  peaks[j,0]<=f*(1+width) and j<(len(new_peaks)-1):
                j += 1
                if np.abs((peaks[j,0]-f)/f)<width:
                    new_peaks[i,1] += peaks[j,2]
                    break
                
    return (new_peaks[np.argmax(new_peaks[:,1]),0], new_peaks) 

class ProcessNote():
    def __init__(self):
        self.rate = 44100
        self.sample_len = 22100
        self.w = 50 # the width of the data to look at for peaks
        self.t = 3 # the threshold hight that a peak must be taller than
        self.gui_caller = None        
        self.frequencies = (np.arange(0, self.sample_len/2+1)).astype('float')*self.rate/self.sample_len
        self.running = False
    
    def set_caller(self, caller):
        self.gui_caller = caller
        
    def get_freq_async(self, sample):
        """ Queues up request to process notes and places the results on the 
        Gui as soon as they are available
        """
        print("trying to start a new thread")
        while self.running:
            time.sleep(0.01)
            
        t = threading.Thread(target=self.get_freq, args=(sample, ))
        self.running = True
        print("Did start a new thread")
        t.start()
        
        
    def get_freq(self, sample):
        """ does a FFT, looks for peaks, adds the what looks like harmonics of 
        a peak back to the fundamental peak.  Returns the note corresponding to 
        the strongest peak
        """        
        window = np.blackman(len(sample))
        fft_data4 = np.log(abs(np.fft.rfft(sample*window, self.sample_len))**2)        
            
        peaks = []    
        for j in range(0,len(fft_data4)-self.w, self.w/2):
            mx_i = np.argmax(fft_data4[j:j+self.w])
            strength = fft_data4[j+mx_i]-np.median(fft_data4[j:j+self.w])
            if mx_i >= 0.25*self.w and mx_i<=0.75*self.w and strength > self.t:
               d_x = self.frequencies[j+mx_i]
               y0,y1,y2 = fft_data4[j+mx_i-1:j+mx_i+2]
               x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
               if len(peaks)==0:
                   peaks.append([d_x/2, 0, 0])
               peaks.append([d_x, x1, strength])
        
        
        peaks = np.array(peaks)
        (freq, new_peaks) = freq_from_harmonics(peaks)
        
        note = note_trainer.Note.from_frequency(freq)

        if not self.gui_caller==None:                    
            self.gui_caller.set_note(note)
        else:
            print(note)           
       
        self.running = False
        return note  
    

class Listen():
    def __init__(self):
        self.chunk = 256 # 11.6ms
        self.min_note_length = 24 # approx 140ms
        self.max_note_length = 24
        
    def setup_from_file():
        chunk = 1024*2    
        wf = wave.open(fname, 'rb')
        swidth = wf.getsampwidth()
        rate = wf.getframerate()
        
        get_data_func = lambda chunk : wf.readframes(chunk)    
        id_from_source2(get_data_func, swidth, rate, playback=False, gui_caller=gui_caller )
        
    def id_from_source2(get_data_func, swidth, rate, playback=False, gui_caller=None, stop_func=None):   
        """ Single channel
        """
        
        if stop_func==None:
            stop_func = lambda t : False
        
        if playback:
            # open stream to play
            p = pyaudio.PyAudio()
            stream = p.open(format =
                            p.get_format_from_width(swidth),
                            channels = 1,
                            rate = rate,
                            output = True)
        
        # clear out the first bit of the signal and get a base noise reading
        sample = np.zeros((max_note_length*chunk,))
        in_a_note = False
        
        time_counter = 0
        counter = 0
        y=np.zeros((44100*10,))
        note_inds = []
        
        # clear out the first milliseconds
        data = get_data_func(chunk)        
        time_counter += 1
    
        # get the baseline readings:
        for i in range(min_note_length):
            temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
            indata = np.array(temp)
            sample[counter*chunk:(counter+1)*chunk] = indata    
            data = get_data_func(chunk)
            time_counter += 1
            counter += 1
        
        base_volume = np.sqrt(np.mean(sample**2))
        print(base_volume)
        avg_window = np.ones((2,))
        
        data = get_data_func(chunk)
        time_counter += 1
        
        # process the source, if the source is a file, stop when the file is finished
        # if the source is the microphone then stop when the stop function says so
    
        while len(data) == chunk*swidth and not stop_func(time):
            if playback:
                stream.write(data)
                
            temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
            indata = np.array(temp)
            y[time_counter*chunk:(time_counter+1)*chunk] = indata
            
            new_avg = np.sqrt(np.mean(indata**2))
            if new_avg/np.min(avg_window) > 1.7 and new_avg > base_volume*5 and not in_a_note:
                in_a_note = True
            
            avg_window[time_counter%2] = new_avg
           
            if in_a_note:
                sample[counter*chunk:(counter+1)*chunk] = indata
                counter = counter+1
                
            if counter == min_note_length:  # got the minimum sample length
                if np.sqrt(np.mean(sample[-chunk*2:]**2))<base_volume*2:
                    print("rejected on volume")
                    sample = np.zeros((chunk*max_note_length,))
                    counter = 0
                    in_a_note = False
                else:
                    counter = 0                
                    # Get the note here
                    note_inds.append((time_counter-min_note_length)*chunk)
                    note = get_freq2(sample, rate)
                    #note = None
                    if not gui_caller==None:                    
                        gui_caller.set_note(note)
                    else:
                        print(note)                
                    
                    in_a_note = False
                    
            data = get_data_func(chunk)
            time_counter += 1                 
       
            
        if playback:
            stream.close()
            p.terminate()     
