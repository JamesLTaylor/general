from Tkinter import *

class Note():
    available_names = ["A", "B", "C", "D", "E", "F", "G"]
    available_incidentals = ["flat", "natural", "sharp"]
    available_octaves = ["middle +2", "middle +1", "middle", "middle -1"]
    
    # 17 is the C above middle C
    def __init__(self, name, incidental, octave):
        self.name = name
        self.incidental = incidental
        self.octave = ocatave        
        self.offset = Note.available_names.index()
        self.quarter = PhotoImage(file = r"C:\Dev\python\general\sound\quarter.gif")
        
    def draw(self, canvas):
        x = 200
        y = 103
        canvas.create_image(x, y, anchor=NW, image = self.quarter)
        canvas.create_line(x, y, x, y+50)
        print("OK")
           

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
            self.note.draw(self.canvas1)
        
        left = 140
        right = 540
        start = 82
        gap = 11
        
        for i in range(5):
            self.canvas1.create_line(left, start+gap*i, right, start+gap*i)
        
        start = 197
        for i in range(5):
            self.canvas1.create_line(left, start+gap*i, right, start+gap*i)                
        
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
        self.button1["text"] = "Test Down"
        self.button1["command"] = self.test_up
        self.button1.grid(row = 1, column=0, pady=5, padx=5)
        
        self.button2 = Button(self)
        self.button2["text"] = "Test Up"
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
        self.var_octave.set(Note.available_octaves[2])        
        self.var_octave.trace("w", self.note_changed)
        self.option_octave = OptionMenu(self, self.var_octave, *Note.available_octaves)
        self.option_octave.grid(row=1, column=4)  
        
        
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
        self.note += 1 
        self.clear_and_draw_staff()
        

    
    
    
root = Tk()
root.title("Note Trainer")
root.geometry("600x340")

app = Application(root)

root.mainloop()