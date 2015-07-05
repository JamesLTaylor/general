

#for i in range(20):#range(int(round(len(data)/10000))):
#    plt.clf()
#    plt.plot(data[i*10000:(i+1)*10000])
#    plt.draw()
#    time.sleep(2)    

#1, 2, and 5 are picking up second harmonic

rate = 44100.0
data = np.load(r"C:\Dev\python\general\sound\data002.npy")
frequencies = (np.arange(0, len(data)/2+1))*rate/len(data)

window = np.blackman(len(data))
data = data*window
fftData=abs(np.fft.rfft(data))**2
plt.figure()
plt.plot(data)
plt.figure()
plt.plot(frequencies, np.log(fftData))
plt.xlim((100, 5000))

y = np.log(fftData[1:-1])
d = np.diff(y)
allpeaks = np.logical_and(d[1:-1]>0, d[2:]<0)
for i in np.where(allpeaks)[0]: 
    if i<10:    
        allpeaks[i] = False
    elif y[i-1]<np.max(y[i-5:i+5]):
        allpeaks[i] = False

peakvals = y[2:][np.where(allpeaks)]
nth_highest = np.sort(peakvals)[-5]
peaks = np.logical_and(allpeaks, y[2:-1]>=nth_highest)
plt.plot(frequencies[2:][peaks], y[2:-1][peaks], 'ro')
