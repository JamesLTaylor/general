import Tkinter as Tk
import tkFileDialog
import get_frequency
import threading
import pyaudio
import wave
import numpy as np
import time
import get_frequency

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style

style.use("ggplot")
#matplotlib.use('TkAgg')

class Note():
    available_names = ["A", "B", "C", "D", "E", "F", "G"]
    available_incidentals = ["flat", "natural", "sharp"]
    available_octaves = ["middle +2", "middle +1", "middle", "middle -1"]
    octave_numbers = [2, 1, 0, -1]
    
    # 17 is the C above middle C
    def __init__(self, name, incidental, **kwargs):
        self.gui_busy = threading.Lock()        
        
        self.name = name
        self.incidental = incidental

        if 'octave_str' in kwargs:
            self.octave = kwargs['octave_str']
            self.octave_number = Note.octave_numbers[Note.available_octaves.index(self.octave)]
        elif 'octave_int' in kwargs:        
            self.octave_number = kwargs['octave_int']
        else:
            raise Exception("either octave_str, or octave_int must be set in the kwargs")
        self.offset = Note.available_names.index(name) + self.octave_number*7 - 7        
    
    def __str__(self):
        return self.name + " " + self.incidental + " " + str(self.octave_number)
        
    def draw_unsafe(self, caller):
        pass
        
    
    def draw(self, caller):
        x = 200
        
        
        if self.offset % 2:
            y = 98 - (self.offset / 2)*11
        else:
            y = 92 - ((self.offset - 1) / 2)*11
            
        caller.get_staff_canvas().create_image(x, y, anchor=Tk.NW, image = caller.get_quarter())
        if self.offset<0:
            caller.get_staff_canvas().create_line(x+14, y+5, x+14, y-40)
        else:
            caller.get_staff_canvas().create_line(x, y+5, x, y+45)
            
        # add helper lines        
        gap = 11
        if self.offset<-4:
            start = 137
            nlines = (-3 - self.offset)//2
            for i in range(nlines):
                caller.get_staff_canvas().create_line(x-10, start+gap*i, x+24, start+gap*i)
        elif self.offset>6:
            start = 71
            nlines = (self.offset-5)//2
            for i in range(nlines):
                caller.get_staff_canvas().create_line(x-10, start-gap*i, x+24, start-gap*i)

class Application(Tk.Frame):
    
    def __init__(self, master):
        self.gui_busy = threading.Lock()
        Tk.Frame.__init__(self, master)
        self.file_opt = options = {}
        self.path = 'C:\\Dev\\python\\general\\sound\\samples'
        options['defaultextension'] = '.wav'
        options['filetypes'] = [('sound files', '.wav')]
        options['initialdir'] = self.path
        options['initialfile'] = 'temp.wav'
        options['parent'] = root
        options['title'] = 'This is a title'
        self.note = None
        self.setup()
        self.grid(row = 0, column = 0)
        
    def clear_and_draw_staff(self):        
        self.canvas1.delete("all")
        image = self.canvas1.create_image(50, 50, anchor=Tk.NW, image=self.staff)                

        if self.note:
            self.note.draw(self)
        
        left = 140
        right = 540
        start = 82
        gap = 11
        
        for i in range(5):
            self.canvas1.create_line(left, start+gap*i, right, start+gap*i)
        
        start = 197
        for i in range(5):
            self.canvas1.create_line(left, start+gap*i, right, start+gap*i)                
    
    def get_quarter(self):
        return self.quarter
        
    def get_staff_canvas(self):
        return self.canvas1
        
    def setup(self):

        # images to be used
        self.quarter = Tk.PhotoImage(file = r"C:\Dev\python\general\sound\quarter.gif")
        self.staff = Tk.PhotoImage(file = r"C:\Dev\python\general\sound\grandstaff2.gif")                
        
        # the main part of the window
        self.main_frame = Tk.Frame(self)
        
        self.canvas1 = Tk.Canvas(self.main_frame)
        self.canvas1["height"] = 280
        self.canvas1["width"] = 580
        self.canvas1["bg"] = "white"        
        
        # self.clear_and_draw_staff(no_note = True)
        self.canvas1.grid(row = 0, column=0, columnspan = 6, pady=5, padx=5, sticky=Tk.E+Tk.W)
        
        self.button_analyse = Tk.Button(self.main_frame)
        self.button_analyse["text"] = "Analyse (Mic)"
        self.button_analyse["command"] = self.analyse
        self.button_analyse.grid(row = 1, column=0, pady=5, padx=5)
        
        self.button_analyse_f = Tk.Button(self.main_frame)
        self.button_analyse_f["text"] = "Analyse (File)"
        self.button_analyse_f["command"] = self.analyse_f
        self.button_analyse_f.grid(row = 1, column=1, pady=5, padx=5)
        
        self.button_record = Tk.Button(self.main_frame)
        self.button_record["text"] = "Record"
        self.button_record["command"] = self.record
        self.button_record.grid(row = 1, column=2, pady=5, padx=5)
        
        self.button_stop = Tk.Button(self.main_frame)
        self.button_stop["text"] = "Stop"
        self.button_stop["command"] = self.stop
        self.button_stop.grid(row = 1, column=3, pady=5, padx=5)
        
        self.button_test_mic = Tk.Button(self.main_frame)
        self.button_test_mic["text"] = "Test Mic"
        self.button_test_mic["command"] = self.test_mic
        self.button_test_mic.grid(row = 1, column = 4, pady=5, padx=5)
        
        self.button_test_mic = Tk.Button(self.main_frame)
        self.button_test_mic["text"] = "Play"
        self.button_test_mic["command"] = self.play
        self.button_test_mic.grid(row = 1, column = 5, pady=5, padx=5)
        
        self.file_play_frame = Tk.Frame(self.main_frame)
        l = Tk.Label(self.file_play_frame, text="file to play/analyse")
        l.pack(side = Tk.LEFT)
        self.fname_play_var = Tk.StringVar(self.file_play_frame)        
        self.fname_play_var.set(r"C:\Dev\python\general\sound\piano_1_soft.wav")
        self.fname_play = Tk.Entry(self.file_play_frame, width=50)
        self.fname_play["textvariable"] = self.fname_play_var
        self.fname_play.pack(side = Tk.LEFT)
        b = Tk.Button(self.file_play_frame, text="Browse", command=self.get_filename_play)
        b.pack(side = Tk.LEFT)        
        self.file_play_frame.grid(row=2, column=0, pady=10, columnspan = 6)
        
        self.file_record_frame = Tk.Frame(self.main_frame)
        l = Tk.Label(self.file_record_frame, text="file to record")
        l.pack(side = Tk.LEFT)
        self.fname_record_var = Tk.StringVar(self.file_record_frame)        
        self.fname_record_var.set(self.path + "\\new.wav")
        self.fname_play = Tk.Entry(self.file_record_frame, width=50)
        self.fname_play["textvariable"] = self.fname_record_var
        self.fname_play.pack(side = Tk.LEFT)
        b = Tk.Button(self.file_record_frame, text="Browse", command=self.get_filename_record)
        b.pack(side = Tk.LEFT)        
        self.file_record_frame.grid(row=3, column=0, pady=10, columnspan = 6)

        """
        self.var_name = Tk.StringVar(self.main_frame)        
        self.var_name.set(Note.available_names[0])        
        self.var_name.trace("w", self.note_changed)        
        self.option_name = Tk.OptionMenu(self, self.var_name, *Note.available_names)
        self.option_name.grid(row=1, column=2)
        
        self.var_incidental = Tk.StringVar(self.main_frame)
        self.var_incidental.set(Note.available_incidentals[1])        
        self.var_incidental.trace("w", self.note_changed)
        self.option_incidental = Tk.OptionMenu(self, self.var_incidental, *Note.available_incidentals)
        self.option_incidental.grid(row=1, column=3)        

        self.var_octave = Tk.StringVar(self.main_frame)
        self.var_octave.set(Note.available_octaves[1])        
        self.var_octave.trace("w", self.note_changed)
        self.option_octave = Tk.OptionMenu(self, self.var_octave, *Note.available_octaves)
        self.option_octave.grid(row=1, column=4)  
        """

        self.main_frame.grid(row = 0, column = 0)      
        
        self.clear_and_draw_staff()
        
        self.draw_signal()
        self.update_signal([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,10])
        self.draw_fft()
        self.update_fft([1,2,3,4,5,6,7,8],[1,2,3,4,5,6,7,8])
        
    def get_filename_play(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        self.fname_play_var.set(filename)
        
    def get_filename_record(self):
        filename = tkFileDialog.askopenfilename(**self.file_opt)
        self.fname_record_var.set(filename)        
        
    def play(self):
        get_frequency.play(self.fname_play_var.get())
        
    def record(self):
        duration = 10
        self.button_record["text"] = "______"
        t = threading.Thread(target=get_frequency.record, args=(self.fname_record_var.get(), duration))
        t.start() 
        time.sleep(duration)        
        #get_frequency.record(self.fname_record_var.get(), 10)
        
        self.button_record["text"] = "Record"
        
    def update_signal(self, time, signal):        
        self.signal_axis.cla()
        self.signal_axis.plot(time[::8], signal[::8])
        self.signal_axis.set_ylim(-25000,25000)
        self.signal_axis.set_xlabel('time (ms)')
        self.signal_canvas.show()
    
    def update_fft(self, freq, magnitude):
        self.fft_axis.cla()
        ind = np.logical_and(freq>=22.5, freq<=3520.0)
        self.fft_axis.plot(freq[ind], magnitude[ind])
        self.fft_axis.set_ylim(0, 140)
        self.fft_axis.set_xlabel('frequency (Hz)')
        self.fft_canvas.show()
        
    def draw_signal(self):        
        self.signal_frame = Tk.Frame(self)
        f = Figure(figsize=(12,4), dpi=100)
        self.signal_axis = f.add_subplot(111)
        self.signal_axis.set_xlabel('time (ms)')
         
        self.signal_canvas = FigureCanvasTkAgg(f, master=self.signal_frame)
        self.signal_canvas.show()       
        self.signal_canvas.get_tk_widget().pack(side=Tk.TOP)
        
        toolbar = NavigationToolbar2TkAgg(self.signal_canvas, self.signal_frame)
        toolbar.update()        
        self.signal_canvas._tkcanvas.pack(side=Tk.BOTTOM)
        
        self.signal_frame.grid(row = 1, column=0, columnspan = 2)
        
        
        
    def draw_fft(self):
        self.fft_frame = Tk.Frame(self)
        f = Figure(figsize=(5,4), dpi=100)
        self.fft_axis = f.add_subplot(111)        
        self.fft_axis.set_xlabel('frequency (Hz)')
        
        self.fft_canvas = FigureCanvasTkAgg(f, master=self.fft_frame)
        self.fft_canvas.show()       
        self.fft_canvas.get_tk_widget().pack(side=Tk.TOP)
        
        toolbar = NavigationToolbar2TkAgg(self.fft_canvas, self.fft_frame)
        toolbar.update()        
        self.fft_canvas._tkcanvas.pack(side=Tk.BOTTOM)
        
        self.fft_frame.grid(row = 0, column=1, columnspan = 1)
        
        
    def note_changed(self, *args):
        self.note = Note(self.var_name.get(), self.var_incidental.get(), octave_str = self.var_octave.get())
        self.clear_and_draw_staff()        
        
    def test_mic(self):
        """ Record for 2 seconds then play back.
        Used to listen for clipping to set gain on microphone
        
        """
        fname = r"C:\Dev\python\general\sound\test.wav"
        get_frequency.record(fname, 2) 
        get_frequency.play(fname)
        
         
        
        
        
    def test_down(self):
        self.note += 1 
        #self.clear_and_draw_staff()

    def analyse(self):
        self.running = True
        t = threading.Thread(target=get_frequency.id_from_mic, args=(self, ))
        t.start() 
        
    def analyse_f(self):
        self.running = True        
        t = threading.Thread(target=get_frequency.id_from_file, args=(self.fname_play_var.get(), self))        
        t.start()         
        
    def stop(self):
        self.running = False        
        
    def is_running(self):
        return self.running
        
        
    def set_note(self, new_note):
        """ sets a single note and redraws the staff with just that note
        
        :param new_note: an instance of note_trainer.Note
        """
        print(str(new_note))
        self.note = new_note
        self.clear_and_draw_staff()

    
if __name__ == "__main__":
    #id_from_file()
    root = Tk.Tk()
    root.title("Note Trainer")
    #root.geometry("600x640")
    
    app = Application(root)
    root.update()
    
    #canvas = FigureCanvasTkAgg(f, master=root)
    #canvas.show()
    #canvas.get_tk_widget().grid(row = 2, column=0, columnspan = 5)
    #canvas.get_tk_widget().pack()
    #canvas.grid(row = 2, column=0, columnspan = 5)
    #canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    
    #toolbar = NavigationToolbar2TkAgg( canvas, self )
    #toolbar.update()
    #canvas._tkcanvas.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
    root.mainloop()        

    
    
    
