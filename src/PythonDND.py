import StartMenu
import os
import sqlite3
import tkinter as tk

class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        save = menu.startMenu()
        #self.conn = sqlite3.connect(save)
        #self.cur = self.conn.cursor()
        self.window = tk.Tk()
        tk.Label(self.window, text=save).pack()
        if (os.name == "nt"):
            self.os = "win"
            self.res_location = os.getcwd() + "\\resources"
            self.window.state('zoomed')
        else:
            self.os = "lin"
            self.res_location = os.getcwd() + "/resources"
            self.window.attributes("-zoomed", True)
        self.window.mainloop()

    def renderMapFrame(self):
        print('WIP renderMapFrame')

    def renderControlFrame(self):
        print('WIP renderControlFrame')

    def renderFrame(self):
        self.renderMapFrame()
        self.renderControlFrame()
