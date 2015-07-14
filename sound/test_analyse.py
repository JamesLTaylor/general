import numpy as np
import unittest
import analyse

class Test_analyse(unittest.TestCase):
    def test_peaks(self):
        processor = analyse.ProcessNote()
        sample = np.load("test_sample1.npy")
        for i in range(10):
            note = processor.get_freq(sample)

        self.assertEqual(10, 10)

if __name__ == "__main__":
    #unittest.main(exit=False, )
    test = Test_analyse("test_peaks")
    test.run()
    
    