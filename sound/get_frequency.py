import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np

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
        return "#NA"        
        
    notes = ['A','A#','B','C','C#','D','D#','E','F','F#','G','G#']
    middle_a = 440.0
    count = int(np.round(12*np.log2(frequency/440.0)))
    note_ind = count % 12
    octaves = (count + note_ind)/12
    return notes[note_ind] + " " + str(octaves)
    
def get_freq(indata, rate):
    frequencies = (np.arange(0, len(indata)/2)-1)*rate/len(indata)
    #window = np.blackman(len(indata))
    #indata = indata*window
    fftData=abs(np.fft.rfft(indata))**2
    
    # thefreq = find_lowest_peak_freq(fftData, frequencies)
    thefreq = find_peak(fftData, frequencies, rate)
    print("The freq is %f Hz." % (thefreq))
    print("The note is : " + get_note(thefreq))
    
    global global_counter
    np.save(r"C:\Dev\python\general\sound\data" + "{:03}".format(global_counter) + ".npy", indata)
    print("wrote {:03}".format(global_counter))    
    global_counter+=1
    
def id_from_file():    
    chunk = 1024*2
    fname = r"C:\Dev\python\general\sound\piano_1.wav"
    wf = wave.open(fname, 'rb')
    swidth = wf.getsampwidth()
    rate = wf.getframerate()
    
    get_data_func = lambda chunk : wf.readframes(chunk)    
    id_from_source(get_data_func, chunk, swidth, rate, playback=True)
    
def id_from_source(get_data_func, chunk, swidth, rate, playback=False):   
    """ Single channel
    """
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
    temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
    indata = np.array(temp)
    base_volume = np.round(10*np.log10(np.mean(indata*indata)))
    
    # process the file
    while len(data) == chunk*swidth:
        if playback:
            stream.write(data)
            
        temp = wave.struct.unpack("%dh"%(len(data)/swidth), data)    
        indata = np.array(temp)
         
        time = counter*chunk/44.1
        if was_note: # after the volume picked up get the next chunk as the note
            get_freq(indata, rate)            
            was_note = False
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
    

def id_from_mic():
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
    
    id_from_source(get_data_func, chunk, swidth, RATE, playback=False)
        
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    
    
"""
"""
global_counter = 0
id_from_mic()    