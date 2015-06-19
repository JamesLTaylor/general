import numpy as np

def max_abs_multiple_diff(peak_frequencies, number):
    candidate = peak_frequencies[0]/number   
    multiples = peak_frequencies/candidate
    new_candidate = np.mean(peak_frequencies/np.round(multiples))
    new_multiples = peak_frequencies/new_candidate
    return (np.max(np.abs(new_multiples-np.round(new_multiples))), new_candidate)
    
# x = (np.arange(0, len(fftData))-1)*RATE/chunk
def find_lowest_peak_freq(fftData, x):
    window = int(5)
    highest = np.max(fftData)
    peaks = np.zeros((len(fftData)), dtype=bool)
    peaks[window:-window] = np.logical_and(fftData[window:-window] - fftData[0:-2*window] > highest/10, 
                   fftData[window:-window] - fftData[2*window:] > highest/10)
                   
    # lets hope we picked up one of the first 3 harmonics
    peak_frequencies = x[peaks].astype('float')
    number = 1    
    (max_diff, candidate) = max_abs_multiple_diff(peak_frequencies, number)    
    while (max_diff>0.15) and number <= 3:
        number = number + 1
        (max_diff, candidate) = max_abs_multiple_diff(peak_frequencies, number)
        
    if number>3:
        raise Exception("Could not find lowest harmonic")
    else:
        return candidate
    
    