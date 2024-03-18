import os
import csv
import sqlite3
import tkinter as tk
from tkinter import ttk
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
        self.selected = None
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
        self.cur.execute("CREATE TABLE " + self.encounter + " (initiative TEXT, curr_ent INTEGER, curr_action INTEGER, mode TEXT not null, targetted TEXT, map_size TEXT not null, flags TEXT, FOREIGN KEY (curr_ent) REFERENCES entities(id), FOREIGN KEY (curr_action) REFERENCES " + self.encounter + "_actions(id)) STRICT;")
        self.cur.execute("CREATE TABLE " + self.encounter + "_entities (id INTEGER PRIMARY KEY ASC, name TEXT, role TEXT, hp INTEGER, ac INTEGER, move_spd INTEGER not null, grid_x INTEGER not null, grid_y INTEGER not null, pix_x INTEGER not null, pix_y INTEGER not null, sprite TEXT) STRICT;")
        self.cur.execute("CREATE TABLE " + self.encounter + "_actions (id INTEGER PRIMARY KEY ASC, name TEXT, damage TEXT, range INTEGER, aoe INTEGER, action_tags TEXT, modifiers TEXT, poss_player INTEGER, FOREIGN KEY (poss_player) REFERENCES '" + self.encounter + "_entities') STRICT;")
        self.cur.execute("insert into " + self.encounter + " ([map_size], [mode]) values (?,?);", [self.mapSize.get(), "noncombat"])
        self.cur.execute("insert into " + self.encounter + "_entities (id, name, role, hp, ac, move_spd, grid_x, grid_y, pix_x, pix_y) values (-1, 'template', 'template', -1, -1, -1, -1, -1, -1, -1);")
        self.conn.commit()
        self.__loadActions()
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
        tk.Button(frame, text="Entity Manager", command=self.__entMgr).pack(expand=True)
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
                    self.cur.execute("insert into " + self.encounter + "_actions ([name],[range],[damage],[aoe],[action_tags],[modifiers],[poss_player]) values (?,?,?,?,?,?,?);", row)
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
                    self.cur.execute("insert into allEntities ([name], [role]) values (?, 'enemies');", [row[0]])
                    id = self.cur.execute("select [id] from allEntities where [name] = ?;", [row[0]]).fetchone()
                    self.cur.execute("insert into enemies ([id], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);", [id[0], row[1], row[2], row[3], row[4]])
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
        if self.encounters.curselection() != ():
            self.encounter = (self.encounters.get(self.encounters.curselection()[0]))
            self.__closeConnection()
            self.window.destroy()
        else:
            self.__loadEncounter()

    def __reloadMenu(self):
        for widg in self.frame.winfo_children():
            widg.destroy()
        self.startMenu()

    def __remEnt(self, dropIn, role: str):
        self.cur.execute("delete from " + role + " where [id] = ?;", [dropIn[0]])
        self.__entMgr()

    def __updateEntInDB(self, name: str, role: str, hp: str, ac: str, moveSpeed: str, sprite: str):
        if self.selected[0] is None:
            self.cur.execute("insert into allEntities ([name], [role]) values (?, ?);",[name, role])
            self.cur.execute("insert into " + role + " ([id], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);",[self.cur.execute("select [id] from allEntities where [name] = ?;",[name]).fetchone()[0], hp, ac, moveSpeed, sprite])
        else:
            print(role)
            print(self.selected)
            if role == self.cur.execute("select [role] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0]:
                self.cur.execute("update allEntities set [name] = ? where id = ?", [name, self.selected[0]])
                self.cur.execute("update " + role + " set [hp] = ?, [ac] = ?, [move_spd] = ?, [sprite] = ? where [id] = ?;", [hp, ac, moveSpeed, sprite, self.selected[0]])
            else:
                tempname = self.cur.execute("select [name] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0]
                self.cur.execute("delete from " + self.cur.execute("select [role] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0] + " where id = ?;", [self.cur.execute("select [id] from allEntities where [name] = ?;", [tempname]).fetchone()[0]])
                self.cur.execute("update allEntities set [name] = ?, [role] = ? where id = ?", [name, role, self.selected[0]])
                self.cur.execute("insert into " + role + " ([id], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);",[self.cur.execute("select [id] from allEntities where [name] = ?;",[name]).fetchone()[0], hp, ac, moveSpeed, sprite])

        self.conn.commit()
        self.__entMgr()

    def __editEnt(self, dropIn, role: str, frame: tk.Frame):
        for i in frame.winfo_children():
            i.destroy()

        if dropIn == "New":
            self.selected = [None,None,None,None,None]
            entName = None
        else:
            self.selected = (self.cur.execute("select * from " + role + " where [id] = ?;",[dropIn[0]]).fetchone())
            entName = self.cur.execute("select [name] from allEntities where [id] = ?;", [dropIn[0]]).fetchone()
        vName, vRole, vhp, vac, vms, vsp = tk.StringVar(value=entName),tk.StringVar(value=role),tk.StringVar(value=self.selected[1]),tk.StringVar(value=self.selected[2]),tk.StringVar(value=self.selected[3]),tk.StringVar(value=self.selected[4])
        tk.Label(frame, text="Name:").grid(row=0, column=0)
        tk.Label(frame, text="Role:").grid(row=1, column=0)
        tk.Label(frame, text="HP:").grid(row=2, column=0)
        tk.Label(frame, text="AC:").grid(row=3, column=0)
        tk.Label(frame, text="Move Spd:").grid(row=4, column=0)
        tk.Label(frame, text="Sprite:").grid(row=5, column=0)
        name = tk.Entry(frame, textvariable=vName)
        name.grid(row=0, column=1)
        erole = ttk.Combobox(frame)
        erole['values'] = ("players", "enemies")
        if role == "enemies":
            erole.current(1)
        else:
            erole.current(0)
        erole.grid(row=1, column=1)
        hp = tk.Entry(frame, textvariable=vhp)
        hp.grid(row=2, column=1)
        ac = tk.Entry(frame, textvariable=vac)
        ac.grid(row=3, column=1)
        moveSpeed = tk.Entry(frame, textvariable=vms)
        moveSpeed.grid(row=4, column=1)
        sprite = tk.Entry(frame, textvariable=vsp)
        sprite.grid(row=5, column=1)

        tk.Button(frame, text="Submit", command= lambda: self.__updateEntInDB(name.get(), erole.get(), hp.get(), ac.get(), moveSpeed.get(), sprite.get())).grid(row=9, column=1)
        tk.Button(frame, text="Back", command= self.__entMgr).grid(row=9, column=0)
        #tk.Button(frame, text="Action Manager", command=self.__actMgr).grid(row=10, column=0, columnspan=2)
        tk.Button(frame, text="Exit", command= self.__quitMenu).grid(row=11, column=0, columnspan=2)

    def __entMgr(self):
        for i in self.window.winfo_children():
            i.destroy()

        entFrame = tk.Frame(self.window)
        drop = ttk.Combobox(entFrame)
        drop['values'] = (self.cur.execute("select [id],[name] from allEntities;").fetchall())
        try:
            drop.current(0)
        except tk.TclError:
            None
        role = self.cur.execute("select [role] from allEntities where [id] = ?;", [drop.get()[0]]).fetchone()[0]
        drop.grid(row=0, column=0, columnspan=2)
        tk.Button(entFrame, text="Edit", command=lambda: self.__editEnt(drop.get(), self.cur.execute("select [role] from allEntities where [id] = ?;", [drop.get()[0]]).fetchone()[0], entFrame)).grid(row=1, column=1)
        #tk.Button(entFrame, text="Delete", command=lambda: self.__remEnt(drop.get(), entFrame)).grid(row=1, column=0)
        tk.Button(entFrame, text="New Entity", command=lambda: self.__editEnt("New", "", entFrame)).grid(row=2, column=0, columnspan=2)
        tk.Button(entFrame, text="Back", command=self.__loadEncounter).grid(row=9, column=0, columnspan=2)
        tk.Button(entFrame, text="Exit", command= self.__quitMenu).grid(row=11, column=0, columnspan=2)
        entFrame.pack()

    def __quitMenu(self):
        exit(0)
