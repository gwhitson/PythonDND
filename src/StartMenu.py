import os
import csv
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image


class StartMenu:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Python DND")
        self.window.geometry("200x200")
        self.saveName = tk.StringVar(value="")
        self.mapSize = tk.StringVar(value="")
        self.background = tk.StringVar(value="")
        self.encounter = ""
        self.encounterVar = tk.StringVar(value="")
        self.frame = tk.Frame(self.window)
        self.saveFile = ""
        self.encounters = None
        self.selected = None
        self.conn = None
        self.cur = None
        self.load = False
        self.encEntry = None
        self.mpSzEntry = None
        self.cfgFile = "/res/config.ini"
        self.keybinds = {}
        self.buttons = {}
        self.tkother = {}
        self.__loadSettings()
        self.__loadImages()
        self.__setStyling()
        self.window.canvas = tk.Canvas(self.window, width=200, height=200)
        self.window.canvas.pack(fill="both", expand=True)
        self.window.canvas.create_image(0, 0, image=self.images['menu'], anchor=tk.NW)

    def startMenu(self):
        self.__clearCanvas()
        self.buttons['new_c'] = ttk.Button(self.window, image=self.images['new_c'], command=self.__newGame)
        self.buttons['load_c'] = ttk.Button(self.window, image=self.images['load_c'], command=self.__loadGame)
        self.buttons['settings'] = ttk.Button(self.window, image=self.images['settings'], command=self.__editSettings)
        self.buttons['quit'] = ttk.Button(self.window, image=self.images['quit'], command=self.__quitMenu)
        self.window.canvas.create_image(10, 15, anchor=tk.NW, image=self.images['logo'], tags='start')
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.buttons['new_c'], tags='start')
        self.window.canvas.create_window(8, 100, anchor=tk.NW, window=self.buttons['load_c'], tags='start')
        self.window.canvas.create_window(8, 130, anchor=tk.NW, window=self.buttons['settings'], tags='start')
        self.window.canvas.create_window(8, 160, anchor=tk.NW, window=self.buttons['quit'], tags='start')
        self.window.mainloop()
        self.__loadSettings()
        return [self.saveFile, self.encounter, os.getcwd() + "/res/", self.keybinds]

    def __newGame(self):
        self.__clearCanvas()
        self.tkother['save_label'] = ttk.Label(self.window, image=self.images['name_c'])
        self.tkother['save_entry'] = ttk.Entry(self.window, textvariable=self.saveName, width=22)
        self.buttons['enter_but'] = ttk.Button(self.window, image=self.images['enter'], command=self.__createGame)
        self.buttons['cancel'] = ttk.Button(self.window, image=self.images['cancel'], command=self.__reloadMenu)
        self.window.canvas.create_image(10, 15, anchor=tk.NW, image=self.images['logo'], tags='campaign')
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.tkother['save_label'], tags='campaign')
        self.window.canvas.create_window(8, 100, anchor=tk.NW, window=self.tkother['save_entry'], tags='campaign')
        self.window.canvas.create_window(8, 130, anchor=tk.NW, window=self.buttons['enter_but'], tags='campaign')
        self.window.canvas.create_window(8, 160, anchor=tk.NW, window=self.buttons['cancel'], tags='campaign')

    def __createGame(self):
        self.saveFile = (os.getcwd() + "/res/saves/" + self.saveName.get() + ".db")

        if self.saveFile[-6:] == ".db.db":
            self.saveFile = self.saveFile[0:-3]
        if os.path.isfile(self.saveFile):
            exit(3)

        self.__openConnection()

        with open("res/default_db.txt", "r") as f:
            defaultDBSchema = f.readlines()
        for i in defaultDBSchema:
            self.cur.execute(i.replace("\n", ""))

        self.conn.commit()

        self.__loadEnemies()
        self.__loadEncounter()

    def __newEncouter(self):
        self.__clearCanvas()
        self.__openConnection()
        self.encounters = None
        self.tkother['enc_title'] = ttk.Label(self.window, image=self.images['enc_name'])
        self.encEntry = ttk.Entry(self.window, textvariable=self.encounterVar, width=22)
        self.tkother['map_size'] = ttk.Label(self.window, image=self.images['map_size'])
        self.mpSzEntry = ttk.Entry(self.window, textvariable=self.mapSize, width=7)
        self.buttons['enc_create'] = ttk.Button(self.window, image=self.images['slim_create'], command=self.__createEncounter)
        self.buttons['can_enc'] = ttk.Button(self.window, image=self.images['slim_back'], command=self.__quitEncounters)
        self.backgroundEntry = ttk.Combobox(self.window)
        self.backgroundEntry['values'] = os.listdir('res/maps/')
        self.tkother['background'] = ttk.Label(self.window, image=self.images['background_label'])
        self.buttons['can_enc'] = ttk.Button(self.window, image=self.images['slim_back'], command=self.__quitEncounters)

        self.window.canvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['enc_title'], tags='encounter')
        self.window.canvas.create_window(8, 35, anchor=tk.NW, window=self.encEntry, tags='encounter')
        self.window.canvas.create_window(8, 60, anchor=tk.NW, window=self.tkother['map_size'], tags='encounter')
        self.window.canvas.create_window(120, 60, anchor=tk.NW, window=self.mpSzEntry, tags='encounter')
        self.window.canvas.create_window(8, 90, anchor=tk.NW, window=self.tkother['background'], tags='encounter')
        self.window.canvas.create_window(8, 115, anchor=tk.NW, window=self.backgroundEntry, tags='encounter')
        self.window.canvas.create_window(8, 140, anchor=tk.NW, window=self.buttons['enc_create'], tags='encounter')
        self.window.canvas.create_window(8, 170, anchor=tk.NW, window=self.buttons['can_enc'], tags='encounter')

    def __createEncounter(self):
        self.encounter = self.encounterVar.get()
        self.cur.execute("insert into game ([encounters]) values (?);", [self.encounter])
        self.cur.execute("CREATE TABLE " + self.encounter + " (initiative TEXT, curr_ent INTEGER, curr_action INTEGER, mode TEXT not null, targetted TEXT, map_size TEXT not null, flags TEXT, bonus_action INTEGER not null, map TEXT, FOREIGN KEY (curr_ent) REFERENCES entities(id), FOREIGN KEY (curr_action) REFERENCES " + self.encounter + "_actions(id)) STRICT;")
        self.cur.execute("CREATE TABLE " + self.encounter + "_entities (id INTEGER PRIMARY KEY ASC, name TEXT, role TEXT, hp INTEGER, ac INTEGER, move_spd INTEGER not null, grid_x INTEGER not null, grid_y INTEGER not null, pix_x INTEGER not null, pix_y INTEGER not null, sprite TEXT) STRICT;")
        self.cur.execute("CREATE TABLE " + self.encounter + "_actions (id INTEGER PRIMARY KEY ASC, name TEXT, damage TEXT, range INTEGER, aoe INTEGER, action_tags TEXT, modifiers TEXT, poss_player INTEGER, FOREIGN KEY (poss_player) REFERENCES '" + self.encounter + "_entities') STRICT;")
        self.cur.execute("insert into " + self.encounter + " ([map_size], [mode], [bonus_action], [map]) values (?,?, 0, ?);", [self.mapSize.get(), "noncombat", f"res/maps/{self.backgroundEntry.get()}"])
        self.cur.execute("insert into " + self.encounter + "_entities (id, name, role, hp, ac, move_spd, grid_x, grid_y, pix_x, pix_y) values (-1, 'template', 'template', -1, -1, -1, -1, -1, -1, -1);")
        self.conn.commit()
        self.__loadActions()
        self.load = True
        self.__startGame()

    def __loadEncounter(self):
        self.__clearCanvas()
        self.buttons['new_c'] = ttk.Button(self.window, image=self.images['new_c'], command=self.__newGame)
        self.buttons['load_c'] = ttk.Button(self.window, image=self.images['load_c'], command=self.__loadGame)
        self.buttons['settings'] = ttk.Button(self.window, image=self.images['settings'], command=self.__editSettings)
        self.buttons['quit'] = ttk.Button(self.window, image=self.images['quit'], command=self.__quitMenu)
        #self.window.canvas.create_image(10, 15, anchor=tk.NW, image=self.images['logo'], tags='start')
        self.__openConnection()
        self.frame = tk.Frame(self.window)
        self.encounters = tk.Listbox(self.frame, height=3, width=22)
        self.encounters.pack()
        encounters = self.cur.execute("select [encounters] from game;").fetchall()
        if len(encounters) != 0:
            for i in encounters:
                self.encounters.insert(tk.END, i[0])
        self.encounters.selection_set(0)
        self.window.canvas.create_window(10, 10, anchor=tk.NW, window=self.frame, tags='encounter')
        self.buttons['n_enc'] = ttk.Button(self.window, image=self.images['new_enc'], command=self.__newEncouter)
        self.buttons['l_enc'] = ttk.Button(self.window, image=self.images['load_enc'], command=self.__startGame)
        self.buttons['ent_mgr'] = ttk.Button(self.window, image=self.images['ent_mgr'], command=self.__entMgr)
        self.buttons['can_enc'] = ttk.Button(self.window, image=self.images['cancel'], command=self.__quitEncounters)
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.buttons['n_enc'], tags='start')
        self.window.canvas.create_window(8, 100, anchor=tk.NW, window=self.buttons['l_enc'], tags='start')
        self.window.canvas.create_window(8, 130, anchor=tk.NW, window=self.buttons['ent_mgr'], tags='start')
        self.window.canvas.create_window(8, 160, anchor=tk.NW, window=self.buttons['can_enc'], tags='start')

    def __quitEncounters(self):
        self.startMenu()

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
        self.__clearCanvas()
        sel_a, sel_m, exe_a, o_sett = tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
        with open(os.getcwd() + self.cfgFile) as f:
            cont = f.readlines()
            sel_a.set(cont[1][cont[1].find('=') + 1:-1])
            sel_m.set(cont[2][cont[2].find('=') + 1:-1])
            exe_a.set(cont[3][cont[3].find('=') + 1:-1])
            o_sett.set(cont[4][cont[4].find('=') + 1:-1])
        self.tkother['sel_a_l'] = ttk.Label(self.window, image=self.images['sel_a'])
        self.tkother['sel_m_l'] = ttk.Label(self.window, image=self.images['sel_m'])
        self.tkother['exe_a_l'] = ttk.Label(self.window, image=self.images['exe_a'])
        self.tkother['o_sett_l'] = ttk.Label(self.window, image=self.images['o_sett'])
        self.tkother['sel_a'] = ttk.Entry(self.window, textvariable=sel_a, width=5)
        self.tkother['sel_m'] = ttk.Entry(self.window, textvariable=sel_m,width=5)
        self.tkother['exe_a'] = ttk.Entry(self.window, textvariable=exe_a, width=5)
        self.tkother['o_sett'] = ttk.Entry(self.window, textvariable=o_sett, width=5)
        self.buttons['sett_submit'] = ttk.Button(self.window, image=self.images['submit'], command=self.__submitSettings)
        self.buttons['back'] = ttk.Button(self.window, image=self.images['back'], command= self.startMenu)
        self.window.canvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['sel_a_l'], tags='settings')
        self.window.canvas.create_window(8, 30, anchor=tk.NW, window=self.tkother['sel_m_l'], tags='settings')
        self.window.canvas.create_window(8, 50, anchor=tk.NW, window=self.tkother['exe_a_l'], tags='settings')
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.tkother['o_sett_l'], tags='settings')
        self.window.canvas.create_window(135, 10, anchor=tk.NW, window=self.tkother['sel_a'], tags='settings')
        self.window.canvas.create_window(135, 30, anchor=tk.NW, window=self.tkother['sel_m'], tags='settings')
        self.window.canvas.create_window(135, 50, anchor=tk.NW, window=self.tkother['exe_a'], tags='settings')
        self.window.canvas.create_window(135, 70, anchor=tk.NW, window=self.tkother['o_sett'], tags='settings')
        self.window.canvas.create_window(8, 135, anchor=tk.NW, window=self.buttons['sett_submit'], tags='settings')
        self.window.canvas.create_window(8, 165, anchor=tk.NW, window=self.buttons['back'], tags='settings')

    def __loadSettings(self):
        with open(os.getcwd() + self.cfgFile, 'r') as f:
            self.tkother['sett_file_cont'] = f.readlines()
            for i in self.tkother['sett_file_cont']:
                if i[0] != '#':
                    key = (i[0:i.find('=')])
                    val = (i[i.find('=') + 1:-1])
                    self.keybinds[key] = val

    def __submitSettings(self):
        with open(os.getcwd() + self.cfgFile, 'w') as f:
            settingsStringNew = ""
            settingsStringNew += self.tkother['sett_file_cont'][0]
            settingsStringNew += f"sel_attack={self.tkother['sel_a'].get()}\n"
            settingsStringNew += f"sel_move={self.tkother['sel_m'].get()}\n"
            settingsStringNew += f"exe_attack={self.tkother['exe_a'].get()}\n"
            settingsStringNew += f"open_session_settings={self.tkother['o_sett'].get()}\n"
            f.write(settingsStringNew)
        self.startMenu()

    def __openConnection(self):
        self.conn = sqlite3.connect(self.saveFile)
        self.cur = self.conn.cursor()

    def __closeConnection(self):
        self.conn.commit()
        self.conn.close()

    def __startGame(self):
        try:
            if self.encounters.curselection() != ():
                self.load = True
                self.encounter = (self.encounters.get(self.encounters.curselection()[0]))
        except AttributeError:
            None
        if self.load is True:
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
        #print(name, role, hp, ac, moveSpeed, sprite)
        if self.selected[0] is None:
            self.cur.execute("insert into allEntities ([name], [role]) values (?, ?);",[name, role])
            self.cur.execute("insert into " + role + " ([id], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);",[self.cur.execute("select [id] from allEntities where [name] = ?;",[name]).fetchone()[0], hp, ac, moveSpeed, sprite])
        else:
            #print(role)
            #print(self.selected)
            if role == self.cur.execute("select [role] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0]:
                self.cur.execute("update allEntities set [name] = ? where id = ?", [name, self.selected[0]])
                self.cur.execute("update " + role + " set [hp] = ?, [ac] = ?, [move_spd] = ?, [sprite] = ? where [id] = ?;", [hp, ac, moveSpeed, sprite, self.selected[0]])
            else:
                tempname = self.cur.execute("select [name] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0]
                #print(tempname)
                self.cur.execute("delete from " + self.cur.execute("select [role] from allEntities where [id] = ?;", [self.selected[0]]).fetchone()[0] + " where id = ?;", [self.cur.execute("select [id] from allEntities where [name] = ?;", [tempname]).fetchone()[0]])
                self.cur.execute("update allEntities set [name] = ?, [role] = ? where id = ?", [name, role, self.selected[0]])
                self.cur.execute("insert into " + role + " ([id], [hp], [ac], [move_spd], [sprite]) values (?,?,?,?,?);",[self.cur.execute("select [id] from allEntities where [name] = ?;",[name]).fetchone()[0], hp, ac, moveSpeed, sprite])

        self.conn.commit()
        self.__entMgr()

    def __editEnt(self, dropIn, role: str):
        self.__clearCanvas()

        if dropIn == "New":
            self.selected = [None,None,None,None,None]
            entName = None
        else:
            self.selected = (self.cur.execute("select * from " + role + " where [id] = ?;",[dropIn[0]]).fetchone())
            entName = self.cur.execute("select [name] from allEntities where [id] = ?;", [dropIn[0]]).fetchone()[0]
        self.tkother['vName'] = tk.StringVar(value=entName)
        self.tkother['vRole'] = tk.StringVar(value=role)
        self.tkother['vhp'] = tk.StringVar(value=self.selected[1])
        self.tkother['vac'] = tk.StringVar(value=self.selected[2])
        self.tkother['vms'] = tk.StringVar(value=self.selected[3])
        self.tkother['vsp'] = tk.StringVar(value=self.selected[4])
        self.tkother['ename_l'] = ttk.Label(self.window, image=self.images['ename'])
        self.tkother['erole_l'] = ttk.Label(self.window, image=self.images['erole'])
        self.tkother['ehp_l'] = ttk.Label(self.window, image=self.images['ehp'])
        self.tkother['eac_l'] = ttk.Label(self.window, image=self.images['eac'])
        self.tkother['espeed_l'] = ttk.Label(self.window, image=self.images['espeed'])
        self.tkother['esprite_l'] = ttk.Label(self.window, image=self.images['esprite'])
        self.tkother['ename'] = ttk.Entry(self.window, textvariable=self.tkother['vName'], width=12)
        self.tkother['erole'] = ttk.Combobox(self.window, width=10)
        self.tkother['erole']['values'] = ("players", "enemies")
        if role == "enemies":
            self.tkother['erole'].current(1)
        else:
            self.tkother['erole'].current(0)
        self.tkother['ehp'] = ttk.Entry(self.window, textvariable=self.tkother['vhp'], width=12)
        self.tkother['eac'] = ttk.Entry(self.window, textvariable=self.tkother['vac'], width=12)
        self.tkother['espeed'] = ttk.Entry(self.window, textvariable=self.tkother['vms'], width=12)
        self.tkother['esprite'] = ttk.Combobox(self.window, width=10)
        self.tkother['esprite']['values'] = os.listdir('res/sprites/')
        self.tkother['esprite'].current(0)

        self.buttons['esubmit'] = ttk.Button(self.window, image=self.images['submit'], command= lambda: self.__updateEntInDB(self.tkother['vName'].get(),self.tkother['erole'].get(),self.tkother['vhp'].get(),self.tkother['vac'].get(),self.tkother['vms'].get(),self.tkother['esprite'].get()))
        self.buttons['back'] = ttk.Button(self.window, image=self.images['back'], command= self.__entMgr)
        self.window.canvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['ename_l'], tags='entities')
        self.window.canvas.create_window(8, 30, anchor=tk.NW, window=self.tkother['erole_l'], tags='entities')
        self.window.canvas.create_window(8, 50, anchor=tk.NW, window=self.tkother['ehp_l'], tags='entities')
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.tkother['eac_l'], tags='entities')
        self.window.canvas.create_window(8, 90, anchor=tk.NW, window=self.tkother['espeed_l'], tags='entities')
        self.window.canvas.create_window(8, 110, anchor=tk.NW, window=self.tkother['esprite_l'], tags='entities')
        self.window.canvas.create_window(85, 11, anchor=tk.NW, window=self.tkother['ename'], tags='entities')
        self.window.canvas.create_window(85, 31, anchor=tk.NW, window=self.tkother['erole'], tags='entities')
        self.window.canvas.create_window(85, 51, anchor=tk.NW, window=self.tkother['ehp'], tags='entities')
        self.window.canvas.create_window(85, 71, anchor=tk.NW, window=self.tkother['eac'], tags='entities')
        self.window.canvas.create_window(85, 91, anchor=tk.NW, window=self.tkother['espeed'], tags='entities')
        self.window.canvas.create_window(85, 111, anchor=tk.NW, window=self.tkother['esprite'], tags='entities')
        self.window.canvas.create_window(8, 135, anchor=tk.NW, window=self.buttons['esubmit'], tags='entities')
        self.window.canvas.create_window(8, 165, anchor=tk.NW, window=self.buttons['back'], tags='entities')

    def __entMgr(self):
        self.__clearCanvas()
        self.tkother['drop'] = drop = ttk.Combobox(self.window)
        self.tkother['drop']['values'] = (self.cur.execute("select [id],[name] from allEntities;").fetchall())
        try:
            self.tkother['drop'].current(0)
        except tk.TclError:
            None
        role = self.cur.execute("select [role] from allEntities where [id] = ?;", [drop.get()[0]]).fetchone()[0]
        self.buttons['edit_ent'] = ttk.Button(self.window, image=self.images['edit_ent'], command=lambda: self.__editEnt(drop.get(), self.cur.execute("select [role] from allEntities where [id] = ?;", [drop.get()[0]]).fetchone()[0]))
        self.buttons['new_ent'] = ttk.Button(self.window, image=self.images['new_ent'], command=lambda: self.__editEnt("New", ""))
        self.buttons['back'] = ttk.Button(self.window, image=self.images['back'], command=self.__loadEncounter)
        self.window.canvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['drop'], tags='entities')
        self.window.canvas.create_window(8, 35, anchor=tk.NW, window=self.buttons['edit_ent'], tags='entities')
        self.window.canvas.create_window(8, 70, anchor=tk.NW, window=self.buttons['new_ent'], tags='entities')
        self.window.canvas.create_window(8, 160, anchor=tk.NW, window=self.buttons['back'], tags='entities')

    def __loadImages(self):
        self.images = {}
        self.images['menu'] = ImageTk.PhotoImage(Image.open("res/icons/start_menu.png"))
        self.images['logo'] = ImageTk.PhotoImage(Image.open("res/icons/logo.png"))
        self.images['new_c'] = ImageTk.PhotoImage(Image.open("res/icons/new_c.png"))
        self.images['load_c'] = ImageTk.PhotoImage(Image.open("res/icons/load_c.png"))
        self.images['settings'] = ImageTk.PhotoImage(Image.open("res/icons/settings.png"))
        self.images['quit'] = ImageTk.PhotoImage(Image.open("res/icons/quit.png"))
        self.images['enter'] = ImageTk.PhotoImage(Image.open("res/icons/enter.png"))
        self.images['cancel'] = ImageTk.PhotoImage(Image.open("res/icons/cancel.png"))
        self.images['name_c'] = ImageTk.PhotoImage(Image.open("res/icons/name_c.png"))
        self.images['new_enc'] = ImageTk.PhotoImage(Image.open("res/icons/new_enc.png"))
        self.images['load_enc'] = ImageTk.PhotoImage(Image.open("res/icons/load_enc.png"))
        self.images['ent_mgr'] = ImageTk.PhotoImage(Image.open("res/icons/ent_mgr.png"))
        self.images['enc_name'] = ImageTk.PhotoImage(Image.open("res/icons/enc_name.png"))
        self.images['map_size'] = ImageTk.PhotoImage(Image.open("res/icons/map_size.png"))
        self.images['create'] = ImageTk.PhotoImage(Image.open("res/icons/create.png"))
        self.images['back'] = ImageTk.PhotoImage(Image.open("res/icons/back.png"))
        self.images['new_ent'] = ImageTk.PhotoImage(Image.open("res/icons/new_ent.png"))
        self.images['edit_ent'] = ImageTk.PhotoImage(Image.open("res/icons/edit_ent.png"))
        self.images['eac'] = ImageTk.PhotoImage(Image.open("res/icons/eac.png"))
        self.images['ehp'] = ImageTk.PhotoImage(Image.open("res/icons/ehp.png"))
        self.images['ename'] = ImageTk.PhotoImage(Image.open("res/icons/ename.png"))
        self.images['espeed'] = ImageTk.PhotoImage(Image.open("res/icons/espeed.png"))
        self.images['esprite'] = ImageTk.PhotoImage(Image.open("res/icons/esprite.png"))
        self.images['erole'] = ImageTk.PhotoImage(Image.open("res/icons/erole.png"))
        self.images['submit'] = ImageTk.PhotoImage(Image.open("res/icons/submit.png"))
        self.images['sel_a'] = ImageTk.PhotoImage(Image.open("res/icons/sel_a.png"))
        self.images['sel_m'] = ImageTk.PhotoImage(Image.open("res/icons/sel_m.png"))
        self.images['exe_a'] = ImageTk.PhotoImage(Image.open("res/icons/exe_a.png"))
        self.images['o_sett'] = ImageTk.PhotoImage(Image.open("res/icons/o_sett.png"))
        self.images['slim_create'] = ImageTk.PhotoImage(Image.open("res/icons/slim_create.png"))
        self.images['slim_back'] = ImageTk.PhotoImage(Image.open("res/icons/slim_back.png"))
        self.images['background_label'] = ImageTk.PhotoImage(Image.open("res/icons/background_label.png"))

    def __clearCanvas(self):
        self.window.canvas.delete('start')
        self.window.canvas.delete('entities')
        self.window.canvas.delete('campaign')
        self.window.canvas.delete('encounter')
        self.window.canvas.delete('settings')

    def __setStyling(self):
        self.style = ttk.Style(self.window)
        self.style.theme_use("default")
        self.style.theme_settings("default", {
            "TCheckbutton": {
                "configure": {"padding": "0",
                              "background": "#6d6d6d",
                              "foreground": "white",
                              }
            },
            "TEntry": {
                "configure": {"padding": "0",
                              "fieldbackground": "lightgray",
                              "foreground": "black",
                              }
            },
            "TButton": {
                "configure": {"padding": "0",
                              "bordercolor": "#6d6d6d",
                              "relief": "0",
                              "background": "#6d6d6d",
                              "borderwidth": "0"
                              }
            },
            "TLabel": {
                "configure": {"padding": "0",
                              "bordercolor": "#6d6d6d",
                              }
            },
            "TCombobox": {
                "configure": {"padding": "0",
                              "fieldbackground": "lightgray",
                              "foreground": "black",
                              }
            },
        })

    def __quitMenu(self):
        exit(0)
