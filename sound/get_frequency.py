import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import time
import threading
import note_trainer

def max_abs_multiple_diff(peak_frequencies, number):
    candidate = peak_frequencies[0]/number   
    multiples = peak_frequencies/candidate
    new_candidate = np.mean(peak_frequencies/np.round(multiples))
    new_multiples = peak_frequencies/new_candidate
    #print(new_multiples)
    #print(new_candidate)
    return (np.max(np.abs(new_multiples-np.round(new_multiples))), new_candidate)
    
# x = (np.arange(0, len(fftData))-1)*RATE/chunk
def find_lowest_peak_freq(fftData, x):
    window = int(5)
    highest = np.max(fftData)
    peaks = np.zeros((len(fftData)), dtype=bool)
    peakheight = fftData[window:-window] - 0.5*(fftData[0:-2*window] + fftData[2*window:])
    
    nth_highest = np.sort(peakheight)[-5]
    
    peaks[window:-window] = peakheight >= nth_highest
                       
    # lets hope we picked up one of the first 3 harmonics
    peak_frequencies = x[peaks].astype('float')
    #print(peak_frequencies)
    if len(peak_frequencies)==0:
        #raise Exception("Could not find lowest harmonic")        
        print("Could not find lowest harmonic")
        np.save(r"C:\Dev\python\general\sound\failure1.npy", fftData)
        return 0.0
        
    number = 1    
    max_divisor = 6
    lowest_freq = 32.0
    (max_diff, candidate) = max_abs_multiple_diff(peak_frequencies, number)    
    while (max_diff>0.1) and number <= max_divisor and candidate>lowest_freq:
        number = number + 1
        (max_diff, candidate) = max_abs_multiple_diff(peak_frequencies, number)
        
    if number>max_divisor or candidate<=lowest_freq:
        #raise Exception("Could not find lowest harmonic")
        print("Could not find lowest harmonic")
        np.save(r"C:\Dev\python\general\sound\failure2.npy", fftData)
        return 0.0
    else:
        return candidate
        
def find_peak(fftData, frequencies, RATE):    
    # find the maximum
    chunk = len(fftData)*2-1
    which = fftData[1:].argmax() + 1
    # use quadratic interpolation around the max
    if which != len(fftData)-1:
        y0,y1,y2 = np.log(fftData[which-1:which+2:])
        x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
        # find the frequency and output it
        thefreq = (which+x1)*RATE/chunk
        print "The freq is %f Hz." % (thefreq)
    
    return thefreq

def get_note(frequency):
    if frequency<10:
        return None        
        
    names = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
    middle_a = 440.0
    count = int(np.round(12*np.log2(frequency/440.0)))
    name_ind = count % 12
    octave_int = count//12 + 1
    if len(names[name_ind])==2:
        name = names[name_ind-1]
        incidental = "sharp"
    else:
        name = names[name_ind]
        incidental = "natural"
    note = note_trainer.Note(name, incidental, octave_int = octave_int)        
    return note
    
def get_freq(indata, rate):
    frequencies = (np.arange(0, len(indata)/2)-1)*rate/len(indata)
    window = np.blackman(len(indata))
    indata = indata*window
    fftData=abs(np.fft.rfft(indata))**2
    fftData = 10*np.log10(fftData)
    
    
    # thefreq = find_lowest_peak_freq(fftData, frequencies)
    thefreq = find_peak(fftData, frequencies, rate)
    print("The freq is %f Hz." % (thefreq))
    note = get_note(thefreq)
    print("The note is : " + str(note))
    
    global global_counter
    np.save(r"C:\Dev\python\general\sound\data" + "{:03}".format(global_counter) + ".npy", indata)
    print("wrote {:03}".format(global_counter))    
    global_counter+=1
    
    return (thefreq, note, frequencies, fftData)
    
    
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
    
    
def get_freq2(sample, rate):
    sample_len = 22100
    frequencies = (np.arange(0, sample_len/2+1)).astype('float')*rate/sample_len
    
    
    avg_sample = np.convolve(sample, np.ones((5,)))
    avg_sample = avg_sample[2:-2]
    window = np.blackman(len(sample))
    fft_data4 = np.log(abs(np.fft.rfft(avg_sample*window, sample_len))**2)

    w = 50
    t = 3

    peaks = []    
    for j in range(0,len(fft_data4)-w):
        mx_i = np.argmax(fft_data4[j:j+w])
        strength = fft_data4[j+mx_i]-np.median(fft_data4[j:j+w])
        if mx_i == w/2 and strength > t:
           d_x = frequencies[j+mx_i]
           y0,y1,y2 = fft_data4[j+mx_i-1:j+mx_i+2]
           x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
           peaks.append([d_x, x1, strength])
           
    peaks = np.array(peaks)
    (freq, new_peaks) = freq_from_harmonics(peaks)
    return get_note(freq)  
    
def id_from_file(fname, gui_caller=None):    
    chunk = 1024*2    
    wf = wave.open(fname, 'rb')
    swidth = wf.getsampwidth()
    rate = wf.getframerate()
    
    get_data_func = lambda chunk : wf.readframes(chunk)    
    id_from_source2(get_data_func, swidth, rate, playback=False, gui_caller=gui_caller )
    
def id_from_mic(gui_caller=None):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    chunk = 2048
    RECORD_SECONDS = 10
     
    audio = pyaudio.PyAudio()
     
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=chunk)
                    
    swidth = 2
    get_data_func = lambda chunk : stream.read(chunk)
    if not gui_caller==None:
        stop_func = lambda t : not gui_caller.is_running()
    else:
        stop_func = lambda t : t > RECORD_SECONDS
    
    id_from_source(get_data_func, chunk, swidth, RATE, playback=False, gui_caller=gui_caller, stop_func=stop_func)
        
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

def id_from_source2(get_data_func, swidth, rate, playback=False, gui_caller=None, stop_func=None):   
    """ Single channel
    """
    chunk = 256 # 11.6ms
    min_note_length = 24 # approx 140ms
    max_note_length = 24
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
    
    if gui_caller==None:
        x = np.arange(0,len(y)) / 44.1 
        plt.figure()
        plt.plot(x,y)
        for (i1, i2) in enumerate(note_inds):
            plt.axvline(x[i2], linewidth=2, color='r')
            plt.axvline(x[i2 + min_note_length*chunk], linewidth=2, color='g')    
    
    
def id_from_source(get_data_func, chunk, swidth, rate, playback=False, gui_caller=None, stop_func=None):   
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
    
    # read some data
    data = get_data_func(chunk)
    
    # some state to find notes    
    prev_volume = 0
    was_note = False
    last_note_time = 0
    min_gap_between_notes = 200
    counter = 1
    time = counter*chunk/44.1    
    temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
    indata = np.array(temp)
    base_volume = np.round(10*np.log10(np.mean(indata*indata)))
    time_steps = np.arange(0, chunk) * chunk/44.1
    
    # process the source, if the source is a file, stop when the file is finished
    # if the source is the microphone then stop when the stop function says so
    while len(data) == chunk*swidth and not stop_func(time):
        if playback:
            stream.write(data)
            
        temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
        indata = np.array(temp)
         
        time = counter*chunk/44.1
        if not gui_caller==None:
            #t = threading.Thread(target=gui_caller.update_signal, args=(time_steps + time, indata))        
            #t.start() 
            if counter % 4 == 0:
                #gui_caller.update_signal(time_steps + time, indata)
                pass
        if was_note: # after the volume picked up get the next chunk as the note
            (freq, note, frequencies, fftData) = get_freq(indata, rate)            
            if gui_caller:
                gui_caller.set_note(note)
                #gui_caller.update_fft(frequencies, fftData)
            was_note = False # reset the note watcher
            print(str(np.round(time)) + "ms")
        
        # note flagged by volume above base and step up in volume and time since last note        
        volume = np.round(10*np.log10(np.mean(indata*indata)))
        if volume-prev_volume>2 and volume-base_volume>5 and time-last_note_time>min_gap_between_notes:
            was_note = True
            last_note_time = time
            
        prev_volume=volume
        data = get_data_func(chunk)
        
        counter += 1
        
    if playback:
        stream.close()
        p.terminate()

def record(fname, time):        
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
     
    audio = pyaudio.PyAudio()
     
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    frames = []
     
    for i in range(0, int(RATE / CHUNK * time)):
        data = stream.read(CHUNK)
        frames.append(data)
     
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
     
    waveFile = wave.open(fname, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close() 

def play(fname):
    """ play back a file
    """
    chunk = 2048
    wf = wave.open(fname, 'rb')
    swidth = wf.getsampwidth()
    RATE = wf.getframerate()
    
    # open stream
    p = pyaudio.PyAudio()
    stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = RATE,
                output = True)

    # read some data
    data = wf.readframes(chunk)

    # play stream and find the frequency of each chunk
    while len(data) == chunk*swidth:       
        # write data out to the audio stream
        stream.write(data)        
        data = wf.readframes(chunk)
    
    if data:
        stream.write(data)
    stream.close()
    p.terminate()          
    


    
def simple_test(caller):
    print(caller.is_running())
    caller.set_note(note_trainer.Note("A", "natural", octave_int=1))
    time.sleep(1)
    caller.set_note(note_trainer.Note("C", "natural", octave_int=0))
    time.sleep(1)
    caller.set_note(note_trainer.Note("E", "natural", octave_int=1))
    time.sleep(1)
    print(caller.is_running())

global_counter = 0
    
if __name__ == "__main__":
    fname = r"C:\Dev\python\general\sound\piano_1_soft.wav"
    id_from_file(fname)
