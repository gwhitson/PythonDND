import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class PythonDND:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title = "Dungeons & Dragons"
        self.window.geometry("200x200")
        self.saveName = tk.StringVar(value="")
        self.saveFile = ""

    def startMenu(self):
        self.frame = tk.Frame(self.window)
        self.frame.pack()

        tk.Label(self.frame, text="Python DND", width=18).grid(row=0, column=0)
        tk.Button(self.frame, text="new", command=self.newGame, width=18).grid(row=1, column=0)
        tk.Button(self.frame, text="load", command=self.loadGame, width=18).grid(row=2, column=0)
        tk.Button(self.frame, text="settings", command=self.editSettings, width=18).grid(row=3, column=0)
        tk.Button(self.frame, text="quit", command=self.window.destroy, width=18).grid(row=4, column=0)

        self.window.mainloop()

    def newGame(self):
        for widg in self.frame.winfo_children():
            widg.destroy()

        tk.Label(self.frame, text="Name Save slot:").grid(row=0, column=0)
        tk.Entry(self.frame, textvariable=self.saveName).grid(row=1, column=0)
        tk.Button(self.frame, text="Enter", command=self.createGame).grid(row=2, column=0)


    def createGame(self):
        self.saveFile = os.getcwd() + "/res/" + self.saveName.get()

        with open("default_db.txt", "r") as f:
            defaultDBSchema = f.readlines()
        # conn = sqlite3.connect("res/test1.db")
        # cur = conn.cursor()

        for i in defaultDBSchema:
            print(i.replace("\n", ""))
            # cur.execute(i.replace("\n",""))

        # conn.close()
        self.startGame()

    def loadGame(self):
        file = tk.filedialog.askopenfile(mode="r", initialdir="./res/")
        self.saveFile = file.name
        self.startGame()

    def editSettings(self):
        print("do this too")

    def startGame(self):
        print(self.saveFile)
        self.window.destroy()
