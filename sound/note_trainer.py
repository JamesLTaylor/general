from Tkinter import *
import get_frequency
import threading
import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np
import time
import get_frequency

class Note():
    available_names = ["A", "B", "C", "D", "E", "F", "G"]
    available_incidentals = ["flat", "natural", "sharp"]
    available_octaves = ["middle +2", "middle +1", "middle", "middle -1"]
    octave_numbers = [2, 1, 0, -1]
    
    # 17 is the C above middle C
    def __init__(self, name, incidental, **kwargs):
        self.name = name
        self.incidental = incidental

        if 'octave_str' in kwargs:
            self.octave = kwargs['octave_str']
            self.octave_number = Note.octave_numbers[Note.available_octaves.index(octave_str)]
        elif 'octave_int' in kwargs:        
            self.octave_number = kwargs['octave_int']
        else:
            raise Exception("either octave_str, or octave_int must be set in the kwargs")
        self.offset = Note.available_names.index(name) + self.octave_number*7 - 7        
    
    def __str__(self):
        return self.name + " " + self.incidental + " " + str(self.octave_number)
    
    def draw(self, caller):
        x = 200
        
        
        if self.offset % 2:
            y = 98 - (self.offset / 2)*11
        else:
            y = 92 - ((self.offset - 1) / 2)*11
            
        caller.get_staff_canvas().create_image(x, y, anchor=NW, image = caller.get_quarter())
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

class Application(Frame):
    
    def __init__(self, master):
        Frame.__init__(self, master)
        self.note = None
        self.setup()
        self.grid(row = 0, column = 1)
        
    def clear_and_draw_staff(self):        
        self.canvas1.delete("all")
        image = self.canvas1.create_image(50, 50, anchor=NW, image=self.staff)                

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
        self.quarter = PhotoImage(file = r"C:\Dev\python\general\sound\quarter.gif")
        self.staff = PhotoImage(file = r"C:\Dev\python\general\sound\grandstaff2.gif")                
        
        self.canvas1 = Canvas(self)
        self.canvas1["height"] = 280
        self.canvas1["width"] = 580
        self.canvas1["bg"] = "white"        
        
        # self.clear_and_draw_staff(no_note = True)
        self.canvas1.grid(row = 0, column=0, columnspan = 5, pady=5, padx=5, sticky=E+W)
        
        self.button1 = Button(self)
        self.button1["text"] = "Start"
        self.button1["command"] = self.start
        self.button1.grid(row = 1, column=0, pady=5, padx=5)
        
        self.button2 = Button(self)
        self.button2["text"] = "******"
        self.button2["command"] = self.test_down
        self.button2.grid(row = 1, column = 1, pady=5, padx=5)

        self.var_name = StringVar(self)        
        self.var_name.set(Note.available_names[0])        
        self.var_name.trace("w", self.note_changed)        
        self.option_name = OptionMenu(self, self.var_name, *Note.available_names)
        self.option_name.grid(row=1, column=2)
        
        self.var_incidental = StringVar(self)
        self.var_incidental.set(Note.available_incidentals[1])        
        self.var_incidental.trace("w", self.note_changed)
        self.option_incidental = OptionMenu(self, self.var_incidental, *Note.available_incidentals)
        self.option_incidental.grid(row=1, column=3)        

        self.var_octave = StringVar(self)
        self.var_octave.set(Note.available_octaves[1])        
        self.var_octave.trace("w", self.note_changed)
        self.option_octave = OptionMenu(self, self.var_octave, *Note.available_octaves)
        self.option_octave.grid(row=1, column=4)  
        
        self.clear_and_draw_staff()
        
    def note_changed(self, *args):
        self.note = Note(self.var_name.get(), self.var_incidental.get(), self.var_octave.get())
        self.clear_and_draw_staff()
        
        
    def test_up(self):
        self.note -= 1 
        #self.clear_and_draw_staff()
        
    def test_down(self):
        self.note += 1 
        #self.clear_and_draw_staff()

    def start(self):
        self.running = True
        #t = threading.Thread(target=get_frequency.simple_test, args=(self, ))
        t = threading.Thread(target=get_frequency.id_from_file, args=(self, ))
        t.start()        
        
    def set_note(self, new_note):
        """ sets a single note and redraws the staff with just that note
        
        :param new_note: an instance of note_trainer.Note
        """
        self.note = new_note
        self.clear_and_draw_staff()

    
if __name__ == "__main__":
    #id_from_file()
    root = Tk()
    root.title("Note Trainer")
    root.geometry("600x340")
    
    app = Application(root)
    
    root.mainloop()        

    
    
    
