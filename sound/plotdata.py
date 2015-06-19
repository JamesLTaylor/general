import time
import scipy.io.wavfile
import matplotlib.pyplot as plt

for i = 0:len

# 5.3 - 5.48
a = int(5.3*44100)
b = int(5.48 * 44100)

"""fname = r"C:\Dev\python\general\sound\piano_1_soft.wav"

(rate, data) = scipy.io.wavfile.read(WAVE_OUTPUT_FILENAME, mmap=False)

y = data[a:b]
x = 5.3 + np.arange(0,len(y)) * (5.48-5.3)
plt.plot(x, y)

#for i in range(20):#range(int(round(len(data)/10000))):
#    plt.clf()
#    plt.plot(data[i*10000:(i+1)*10000])
#    plt.draw()
#    time.sleep(2)    
"""

fname = r"C:\Dev\python\general\sound\data043.npy"
rate = 44100.0
data = np.load(r"C:\Dev\python\general\sound\data043.npy")
frequencies = (np.arange(0, len(data)/2)-1)*rate/len(data)
plt.plot(data)

fftData=abs(np.fft.rfft(data))**2
plt.figure()
plt.plot(frequencies, fftData[1:])