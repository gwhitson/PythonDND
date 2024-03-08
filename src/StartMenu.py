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
        self.encounter = ""
        self.encounterVar = tk.StringVar(value="")
        self.saveFile = ""
        self.frame = tk.Frame(self.window)
        self.frame.pack()
        self.encounters = None
        self.conn = None
        self.cur = None
        self.encEntry = None
        self.mpSzEntry = None

    def startMenu(self):

        tk.Label(self.frame, text="Python DND", width=18).grid(row=0, column=0)
        tk.Button(self.frame, text="new campaign", command=self.__newGame, width=18).grid(row=1, column=0)
        tk.Button(self.frame, text="load campaign", command=self.__loadGame, width=18).grid(row=2, column=0)
        tk.Button(self.frame, text="settings", command=self.__editSettings, width=18).grid(row=3, column=0)
        tk.Button(self.frame, text="quit", command=self.__quitMenu, width=18).grid(row=4, column=0)

        self.window.mainloop()
        return [self.saveFile, self.encounter, os.getcwd() + "/res/"]

    def __newGame(self):
        for widg in self.frame.winfo_children():
            widg.destroy()

        tk.Label(self.frame, text="Name Campaign:").grid(row=0, column=0)
        tk.Entry(self.frame, textvariable=self.saveName).grid(row=1, column=0)
        tk.Button(self.frame, text="Enter", command=self.__createGame).grid(row=4, column=0)
        tk.Button(self.frame, text="Cancel", command=self.__reloadMenu).grid(row=5, column=0)

    def __createGame(self):
        self.saveFile = (os.getcwd() + "/res/saves/" + self.saveName.get() + ".db")

        if self.saveFile[-6:] == ".db.db":
            self.saveFile = self.saveFile[0:-3]
        if os.path.isfile(self.saveFile):
            exit(3)

        self.__openConnection()

        with open("res/saves/default_db.txt", "r") as f:
            defaultDBSchema = f.readlines()
        for i in defaultDBSchema:
            self.cur.execute(i.replace("\n", ""))

        self.conn.commit()

        self.__loadActions()
        self.__loadEnemies()
        self.__loadEncounter()

    def __newEncouter(self):
        self.__openConnection()
        self.encounters = None
        for widg in self.window.winfo_children():
            widg.destroy()
        tk.Label(self.window, text="Encounter Title:").pack()
        self.encEntry = tk.Entry(self.window, textvariable=self.encounterVar)
        self.encEntry.pack()
        tk.Label(self.window, text="Map Size").pack()
        self.mpSzEntry = tk.Entry(self.window, textvariable=self.mapSize)
        self.mpSzEntry.pack()
        tk.Button(self.window, text="Create", command=self.__createEncounter).pack()

    def __createEncounter(self):
        self.encounter = self.encounterVar.get()
        self.cur.execute("insert into game ([encounters]) values (?);", [self.encounter])
        self.cur.execute("CREATE TABLE " + self.encounter + " (initiative TEXT, curr_ent INTEGER, curr_action INTEGER, mode TEXT not null, targetted TEXT, map_size TEXT not null, flags TEXT, FOREIGN KEY (curr_ent) REFERENCES entities(id), FOREIGN KEY (curr_action) REFERENCES actions(id)) STRICT;")
        self.cur.execute("CREATE TABLE " + self.encounter + "_entities (id INTEGER PRIMARY KEY ASC, name TEXT, role TEXT, hp INTEGER, ac INTEGER, move_spd INTEGER not null, grid_x INTEGER not null, grid_y INTEGER not null, pix_x INTEGER not null, pix_y INTEGER not null, sprite TEXT) STRICT;")
        self.cur.execute("insert into " + self.encounter + " ([map_size], [mode]) values (?,?);", ["noncombat", self.mapSize.get()])
        self.cur.execute("insert into " + self.encounter + "_entities (id, name, role, hp, ac, move_spd, grid_x, grid_y, pix_x, pix_y) values (-1, 'template', 'template', -1, -1, -1, -1, -1, -1, -1);")
        self.conn.commit()
        self.__startGame()

    def __loadEncounter(self):
        self.__openConnection()
        for widg in self.window.winfo_children():
            widg.destroy()
        frame = tk.Frame(self.window)
        self.encounters = tk.Listbox(frame, height=5)
        encounters = self.cur.execute("select [encounters] from game;").fetchall()
        if len(encounters) != 0:
            for i in encounters:
                self.encounters.insert(tk.END, i[0])
        self.encounters.pack()
        tk.Button(frame, text="New Encounter", command=self.__newEncouter).pack(expand=True)
        tk.Button(frame, text="Load Encounter", command=self.__startGame).pack(expand=True)
        frame.pack(expand=True)

    def __loadActions(self):
        self.__openConnection()
        with open("res/defaultActions.csv", 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            count = 0
            for row in data:
                if count != 0:
                    row.append(-1)
                    self.cur.execute("insert into actions ([name],[range],[damage],[aoe],[action_tags],[modifiers],[poss_player]) values (?,?,?,?,?,?,?);", row)
                    self.conn.commit()
                else:
                    count += 1

    def __loadEnemies(self):
        self.__openConnection()
        with open("res/defaultEnemies.csv", 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
            count = 0
            for row in data:
                if count != 0:
                    self.cur.execute("insert into enemies ([name], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);", row)
                    self.conn.commit()
                else:
                    count += 1

    def __loadGame(self):
        self.__openConnection()
        file = tk.filedialog.askopenfile(mode="r", initialdir=(os.getcwd()  + "/res/saves/"), filetypes=(("db files", "*.db"), ("all files", "*.*")))
        if file is not None:
            self.saveFile = file.name
            self.__loadEncounter()
        else:
            self.__reloadMenu()

    def __editSettings(self):
        print("do this too")

    def __openConnection(self):
        self.conn = sqlite3.connect(self.saveFile)
        self.cur = self.conn.cursor()

    def __closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def __startGame(self):
        if self.encounters is not None:
            self.encounter = (self.encounters.get(self.encounters.curselection()[0]))
        self.__closeConnection()
        self.window.destroy()

    def __reloadMenu(self):
        for widg in self.frame.winfo_children():
            widg.destroy()
        self.startMenu()

    def __quitMenu(self):
        exit(0)
