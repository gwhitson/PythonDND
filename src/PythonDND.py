import StartMenu
import os
import sqlite3
import tkinter as tk

class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        self.save = menu.startMenu()
        #self.conn = sqlite3.connect(self.save)
        #self.cur = self.conn.cursor()

        self.window = tk.Tk()
        self.map = tk.Frame(self.window)
        self.control = tk.Frame(self.window)
        self.map.grid(row=0, column=0)
        self.control.grid(row=0, column=1)
        self.window.attributes("-fullscreen", True)

        self.renderFrame()
        self.window.mainloop()

    def renderMapFrame(self):
        tk.Label(self.map, text=self.save).pack()

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.window.destroy).pack()

    def renderFrame(self):
        self.renderMapFrame()
        self.renderControlFrame()
