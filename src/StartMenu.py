import os
import sqlite3
import tkinter as tk
#from tkinter import filedialog


class StartMenu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python DND")
        self.window.geometry("200x200")
        self.saveName = tk.StringVar(value="")
        self.saveFile = ""
        self.frame = tk.Frame(self.window)
        self.frame.pack()

    def startMenu(self):

        tk.Label(self.frame, text="Python DND", width=18).grid(row=0, column=0)
        tk.Button(self.frame, text="new", command=self.__newGame, width=18).grid(row=1, column=0)
        tk.Button(self.frame, text="load", command=self.__loadGame, width=18).grid(row=2, column=0)
        tk.Button(self.frame, text="settings", command=self.__editSettings, width=18).grid(row=3, column=0)
        tk.Button(self.frame, text="quit", command=self.__quitMenu, width=18).grid(row=4, column=0)

        self.window.mainloop()
        return self.saveFile

    def __newGame(self):
        for widg in self.frame.winfo_children():
            widg.destroy()

        tk.Label(self.frame, text="Name Save slot:").grid(row=0, column=0)
        tk.Entry(self.frame, textvariable=self.saveName).grid(row=1, column=0)
        tk.Button(self.frame, text="Enter", command=self.__createGame).grid(row=2, column=0)
        tk.Button(self.frame, text="Cancel", command=self.__reloadMenu).grid(row=3, column=0)

    def __createGame(self):
        self.saveFile = (os.getcwd() + "/res/saves/" + self.saveName.get() + ".db")

        if self.saveFile[-6:] == ".db.db":
            self.saveFile = self.saveFile[0:-3]
        if os.path.isfile(self.saveFile):
            exit(3)

        conn = sqlite3.connect(self.saveFile)
        cur = conn.cursor()

        with open("res/saves/default_db.txt", "r") as f:
            defaultDBSchema = f.readlines()
        for i in defaultDBSchema:
            cur.execute(i.replace("\n", ""))

        #cur.execute("insert into game ([map_size], [mode]) values (40, 'non-combat');")

        conn.commit()
        conn.close()

        self.__startGame()

    def __loadGame(self):
        file = tk.filedialog.askopenfile(mode="r", initialdir=(os.getcwd()  + "/res/saves/"), filetypes=(("db files", "*.db"), ("all files", "*.*")))
        if file is not None:
            self.saveFile = file.name
            self.__startGame()
        else:
            self.__reloadMenu()

    def __editSettings(self):
        print("do this too")

    def __startGame(self):
        self.window.destroy()

    def __reloadMenu(self):
        for widg in self.frame.winfo_children():
            widg.destroy()
        self.startMenu()

    def __quitMenu(self):
        exit(0)
