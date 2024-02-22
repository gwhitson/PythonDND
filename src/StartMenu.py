import os
import csv
import sqlite3
import tkinter as tk
from tkinter import filedialog


class StartMenu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python DND")
        self.window.geometry("200x200")
        self.saveName = tk.StringVar(value="")
        self.mapSize = tk.StringVar(value="")
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
        return [self.saveFile, os.getcwd() + "/res/"]

    def __newGame(self):
        for widg in self.frame.winfo_children():
            widg.destroy()

        tk.Label(self.frame, text="Name Save slot:").grid(row=0, column=0)
        tk.Entry(self.frame, textvariable=self.saveName).grid(row=1, column=0)
        tk.Label(self.frame, text="Map Size:").grid(row=2, column=0)
        tk.Entry(self.frame, textvariable=self.mapSize).grid(row=3, column=0)
        tk.Button(self.frame, text="Enter", command=self.__createGame).grid(row=4, column=0)
        tk.Button(self.frame, text="Cancel", command=self.__reloadMenu).grid(row=5, column=0)

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

        cur.execute("insert into game ([map_size], [mode]) values (?, 'noncombat');", [self.mapSize.get()])
        cur.execute("insert into entities (id, name, role, hp, ac, move_spd, grid_x, grid_y, pix_x, pix_y) values (-1, 'template', 'template', -1, -1, -1, -1, -1, -1, -1);")

        with open("res/defaultActions.csv", 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            count = 0
            for row in data:
                if count != 0:
                    row.append(-1)
                    cur.execute("insert into actions ([name],[range],[damage],[aoe],[action_tags],[modifiers],[poss_player]) values (?,?,?,?,?,?,?);", row)
                else:
                    count += 1

        conn.commit()
        conn.close()

        self.__startGame()

    def __loadActions(self):
        conn = sqlite3.connect(self.saveFile)
        cur = conn.cursor()

        current = cur.execute("select * from actions where [poss_player] = -1;").fetchmany()
        print(current)


        conn.commit()
        conn.close()
        None

    def __loadEnemies(self):
        conn = sqlite3.connect(self.saveFile)
        cur = conn.cursor()

        current = cur.execute("select * from tEnemies;").fetchmany()
        print(current)

        conn.commit()
        conn.close()
        None

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

    def test(self):
        self.__loadActions()
