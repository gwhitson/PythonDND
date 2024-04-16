import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class DNDSettings:
    def __init__(self, saveFile: str, window: tk.Tk, squareSize, encounter: str, map: tk.Canvas):
        self.window = window
        self.conn = sqlite3.connect(saveFile)
        self.cur = self.conn.cursor()
        self.squareSize = squareSize
        self.lb = None
        self.renderFrame = None
        self.encounter = encounter
        self.map = map
        self.image = None
        self.images = {}
        self.tkother = {}
        self.buttons = {}
        self.settingsCanvas = None
        self.settingsWindow = None
        self.__loadImages()

    def newPrompt(self):
        self.settingsWindow = None
        self.prompt()

    def prompt(self):
        self.conn.commit()
        if self.settingsWindow is None:
            self.settingsWindow = tk.Toplevel(self.window)
            self.settingsWindow.geometry("200x250")
            self.settingsWindow.title("Session Settings")
            self.settingsCanvas = tk.Canvas(self.settingsWindow, width=200, height=250)
            self.settingsCanvas.pack(fill=tk.BOTH, expand=True)
        else:
            self.__clearCanvas()
        self.settingsCanvas.create_image(0, 0, anchor=tk.NW, image=self.images['background'])
        self.settingsCanvas.create_image(8, 0, anchor=tk.NW, image=self.images['logo'], tags='prompt')
        self.tkother['ent_mgr'] = ttk.Button(self.settingsCanvas, image=self.images['ent_mgr'], command=self.__entMgr)
        #ttk.Button(self.settingsCanvas, text="Action Manager", command=self.__actMgr).pack()
        #ttk.Button(self.settingsCanvas, text="Initiative Manager", command=self.__iniMgr).pack()
        self.tkother['set_bkgrnd'] = ttk.Button(self.settingsCanvas, image=self.images['set_bkgrnd'], command=self.__bckMgr)
        self.tkother['exit'] = ttk.Button(self.settingsCanvas, image=self.images['exit'], command=self.__exitSettings)
        self.settingsCanvas.create_window(8, 60, anchor=tk.NW, window=self.tkother['ent_mgr'], tags='prompt')
        self.settingsCanvas.create_window(8, 100, anchor=tk.NW, window=self.tkother['set_bkgrnd'], tags='prompt')
        self.settingsCanvas.create_window(8, 140, anchor=tk.NW, window=self.tkother['exit'], tags='prompt')
        self.renderFrame()

    def __exitSettings(self):
        self.settingsWindow.destroy()

    def setRenderFunc(self, renderFrame):
        self.renderFrame = renderFrame

    def __udpateInitInDB(self):
        temp = ""
        for i in self.lb.get(0, self.lb.size() - 1):
            temp += str(self.cur.execute("select [id] from " + self.encounter + "_entities where [name] = ?;", [i[0]]).fetchone()[0])
            temp += ','
        self.cur.execute("update game set [initiative] = ?;", [temp])
        self.renderFrame()
        self.prompt()

    def __updateEntInDB(self):
        if self.selected == "New":
            self.cur.execute("insert into " + self.encounter + "_entities ([name], [role], [hp], [ac], [move_spd], [grid_x], [grid_y], [pix_x], [pix_y]) values (?,?,?,?,?,?,?,?,?);",[self.tkother['vName'].get(), self.tkother['erole'].get(), self.tkother['vhp'].get(), self.tkother['vac'].get(), self.tkother['vms'].get(), self.tkother['vgx'].get(), self.tkother['vgy'].get(), int(self.tkother['vgx'].get()) * self.squareSize, int(self.tkother['vgy'].get()) * self.squareSize])
            newInit = self.cur.execute(f"select [initiative] from {self.encounter};").fetchone()[0]
            newInit += str(self.cur.execute(f"select [id] from {self.encounter}_entities order by [id] desc limit 1;").fetchone()[0]) + ","
            self.cur.execute(f"update {self.encounter} set [initiative] = ?;", [newInit])
        else:
            self.cur.execute("update " + self.encounter + "_entities set [name] = ?, [role] = ?, [hp] = ?, [ac] = ?, [move_spd] = ?, [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;",[self.tkother['vName'].get(), self.tkother['erole'].get(), self.tkother['vhp'].get(), self.tkother['vac'].get(), self.tkother['vms'].get(), self.tkother['vgx'].get(), self.tkother['vgy'].get(), int(self.tkother['vgx'].get()) * self.squareSize, int(self.tkother['vgy'].get()) * self.squareSize, self.selected])

        self.conn.commit()
        self.__entMgr()

    def __updateActInDB(self):
        if self.action[0] is None:
            self.cur.execute("insert into " + self.encounter + "_actions ([name],[damage],[range],[aoe],[action_tags],[modifiers],[poss_player]) values (?,?,?,?,?,?,-1);",[self.actname.get(),self.actdamg.get(),self.actrang.get(),self.actaoef.get(),self.acttags.get(),self.actmods.get()])
        else:
            self.cur.execute("update " + self.encounter + "_actions set [name] = ?,[damage] = ?,[range] = ?,[aoe] = ?,[action_tags] = ?,[modifiers] = ? where [name] = ?;",[self.actname.get(),self.actdamg.get(),self.actrang.get(),self.actaoef.get(),self.acttags.get(),self.actmods.get(),self.action[1]])
        self.conn.commit()
        self.__actMgr()

    #def __remEnt(self, dropIn, frame: tk.Frame):
    def __remEnt(self, dropIn):
        #print(dropIn)
        self.cur.execute("delete from " + self.encounter + "_entities where [id] = ?;", [dropIn[0]])
        self.cur.execute("delete from " + self.encounter + "_actions where [poss_player] = ?;", [dropIn[0]])
        init = (self.cur.execute(f"select [initiative] from {self.encounter}").fetchone()[0]).split(',')
        init.remove(dropIn[0])
        self.cur.execute(f"update {self.encounter} set [initiative] = ?;", [",".join(init)])

        self.conn.commit()
        self.__entMgr()

    def __iniMoveUp(self):
        #print(self.lb.curselection())
        if self.lb.curselection()[0] == 0:
            print("ent at top of order")
        else:
            ind1 = self.lb.curselection()[0] - 1
            ind2 = self.lb.curselection()[0]
            temp1 = self.lb.get(ind1)
            temp2 = self.lb.get(ind2)
            print(temp1, temp2)
            self.lb.delete(ind1, ind2)
            self.lb.insert(ind1, temp2)
            self.lb.insert(ind2, temp1)
            self.lb.selection_set(ind1)
        print(self.lb.get(0, self.lb.size() - 1))

    def __iniMoveDown(self):
        print(self.lb.curselection())
        if self.lb.curselection()[0] == self.lb.size() - 1:
            print("ent at bottom of order")
        else:
            ind1 = self.lb.curselection()[0]
            ind2 = self.lb.curselection()[0] + 1
            temp1 = self.lb.get(ind1)
            temp2 = self.lb.get(ind2)
            print(temp1, temp2)
            self.lb.delete(ind1, ind2)
            self.lb.insert(ind1, temp2)
            self.lb.insert(ind2, temp1)
            self.lb.selection_set(ind2)

    def __editAct(self, tag: str, frame: tk.Frame):
        for i in frame.winfo_children():
            i.destroy()

        if tag == "New":
            self.action = [None,None,None,None,None,None,None,None]
        else:
            self.action = self.cur.execute("select * from " + self.encounter + "_actions where [poss_player] = -1 and [name] = ?;", [tag]).fetchone()

        vN, vD, vR, vA, vT, vM = tk.StringVar(value=self.action[1]),tk.StringVar(value=self.action[2]),tk.StringVar(value=self.action[3]),tk.StringVar(value=self.action[4]),tk.StringVar(value=self.action[5]),tk.StringVar(value=self.action[6])
        tk.Label(frame, text="Name:").grid(row=0, column=0)
        tk.Label(frame, text="Damage:").grid(row=1, column=0)
        tk.Label(frame, text="Range:").grid(row=2, column=0)
        tk.Label(frame, text="AOE:").grid(row=3, column=0)
        tk.Label(frame, text="Tags:").grid(row=4, column=0)
        tk.Label(frame, text="Modifier:").grid(row=5, column=0)

        self.actname = tk.Entry(frame, textvariable=vN)
        self.actname .grid(row=0, column=1)
        self.actdamg = tk.Entry(frame, textvariable=vD)
        self.actdamg .grid(row=1, column=1)
        self.actrang = tk.Entry(frame, textvariable=vR)
        self.actrang .grid(row=2, column=1)
        self.actaoef = tk.Entry(frame, textvariable=vA)
        self.actaoef .grid(row=3, column=1)
        self.acttags = tk.Entry(frame, textvariable=vT)
        self.acttags .grid(row=4, column=1)
        self.actmods = tk.Entry(frame, textvariable=vM)
        self.actmods .grid(row=5, column=1)

        tk.Button(frame, text="Submit", command= self.__updateActInDB).grid(row=7, column=1)
        tk.Button(frame, text="Back", command= self.__actMgr).grid(row=7, column=0)
        tk.Button(frame, text="Exit", command= self.__exitSettings).grid(row=10, column=0, columnspan=2)

    def __editEnt(self, dropIn):
        self.__clearCanvas()
        ent = self.cur.execute(f"select * from {self.encounter}_entities where [id] = ?;", [dropIn[0]]).fetchone()
        try:
            self.selected = ent[0]
            self.tkother['vName'] = tk.StringVar(value=ent[1])
            self.tkother['vhp'] = tk.StringVar(value=ent[3])
            self.tkother['vac'] = tk.StringVar(value=ent[4])
            self.tkother['vms'] = tk.StringVar(value=ent[5])
            self.tkother['vsp'] = tk.StringVar(value=ent[10])
            self.tkother['vgx'] = tk.StringVar(value=ent[6])
            self.tkother['vgy'] = tk.StringVar(value=ent[7])
        except TypeError:
            self.selected = 'New'
            self.tkother['vName'] = tk.StringVar(value='')
            self.tkother['vhp'] = tk.StringVar(value='')
            self.tkother['vac'] = tk.StringVar(value='')
            self.tkother['vms'] = tk.StringVar(value='')
            self.tkother['vsp'] = tk.StringVar(value='')
            self.tkother['vgx'] = tk.StringVar(value='')
            self.tkother['vgy'] = tk.StringVar(value='')
        self.tkother['ename_l'] = ttk.Label(self.settingsWindow, image=self.images['ename'])
        self.tkother['erole_l'] = ttk.Label(self.settingsWindow, image=self.images['erole'])
        self.tkother['ehp_l'] = ttk.Label(self.settingsWindow, image=self.images['ehp'])
        self.tkother['eac_l'] = ttk.Label(self.settingsWindow, image=self.images['eac'])
        self.tkother['espeed_l'] = ttk.Label(self.settingsWindow, image=self.images['espeed'])
        self.tkother['esprite_l'] = ttk.Label(self.settingsWindow, image=self.images['esprite'])
        self.tkother['egx_l'] = ttk.Label(self.settingsWindow, image=self.images['egx'])
        self.tkother['egy_l'] = ttk.Label(self.settingsWindow, image=self.images['egy'])
        self.tkother['ename'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vName'], width=12)
        self.tkother['erole'] = ttk.Combobox(self.settingsWindow, width=10)
        self.tkother['erole']['values'] = ("player", "enemy")
        try:
            if ent[2] == "enemy":
                self.tkother['erole'].current(1)
            else:
                self.tkother['erole'].current(0)
        except TypeError:
            self.tkother['erole'].current(0)
        self.tkother['ehp'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vhp'], width=12)
        self.tkother['eac'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vac'], width=12)
        self.tkother['espeed'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vms'], width=12)
        self.tkother['egx'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vgx'], width=12)
        self.tkother['egy'] = ttk.Entry(self.settingsWindow, textvariable=self.tkother['vgy'], width=12)
        self.tkother['esprite'] = ttk.Combobox(self.settingsWindow, width=10)
        self.tkother['esprite']['values'] = os.listdir('res/sprites/')
        self.tkother['esprite'].current(0)

        self.buttons['esubmit'] = ttk.Button(self.settingsWindow, image=self.images['submit'], command=self.__updateEntInDB)
        self.buttons['back'] = ttk.Button(self.settingsWindow, image=self.images['back'], command= self.__entMgr)
        self.settingsCanvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['ename_l'], tags='entities')
        self.settingsCanvas.create_window(85, 11, anchor=tk.NW, window=self.tkother['ename'], tags='entities')
        self.settingsCanvas.create_window(8, 30, anchor=tk.NW, window=self.tkother['erole_l'], tags='entities')
        self.settingsCanvas.create_window(85, 31, anchor=tk.NW, window=self.tkother['erole'], tags='entities')
        self.settingsCanvas.create_window(8, 50, anchor=tk.NW, window=self.tkother['ehp_l'], tags='entities')
        self.settingsCanvas.create_window(85, 51, anchor=tk.NW, window=self.tkother['ehp'], tags='entities')
        self.settingsCanvas.create_window(8, 70, anchor=tk.NW, window=self.tkother['eac_l'], tags='entities')
        self.settingsCanvas.create_window(85, 71, anchor=tk.NW, window=self.tkother['eac'], tags='entities')
        self.settingsCanvas.create_window(8, 90, anchor=tk.NW, window=self.tkother['espeed_l'], tags='entities')
        self.settingsCanvas.create_window(85, 91, anchor=tk.NW, window=self.tkother['espeed'], tags='entities')
        self.settingsCanvas.create_window(8, 110, anchor=tk.NW, window=self.tkother['egx_l'], tags='entities')
        self.settingsCanvas.create_window(85, 111, anchor=tk.NW, window=self.tkother['egx'], tags='entities')
        self.settingsCanvas.create_window(8, 130, anchor=tk.NW, window=self.tkother['egy_l'], tags='entities')
        self.settingsCanvas.create_window(85, 131, anchor=tk.NW, window=self.tkother['egy'], tags='entities')
        self.settingsCanvas.create_window(8, 150, anchor=tk.NW, window=self.tkother['esprite_l'], tags='entities')
        self.settingsCanvas.create_window(85, 151, anchor=tk.NW, window=self.tkother['esprite'], tags='entities')
        self.settingsCanvas.create_window(8, 180, anchor=tk.NW, window=self.buttons['esubmit'], tags='entities')
        self.settingsCanvas.create_window(8, 210, anchor=tk.NW, window=self.buttons['back'], tags='entities')

#        for i in frame.winfo_children():
#            i.destroy()
#
#        if dropIn == "New":
#            self.selected = [None,None,None,None,None,None,None,None,None,None,None]
#        else:
#            self.selected = (self.cur.execute("select * from " + self.encounter + "_entities where [id] = ?;",[dropIn[0]]).fetchone())
#        vName, vRole, vhp, vac, vms, vgrid_x, vgrid_y = tk.StringVar(value=self.selected[1]),tk.StringVar(value=self.selected[2]),tk.StringVar(value=self.selected[3]),tk.StringVar(value=self.selected[4]),tk.StringVar(value=self.selected[5]),tk.StringVar(value=self.selected[6]),tk.StringVar(value=self.selected[7])
#        tk.Label(frame, text="Name:").grid(row=0, column=0)
#        tk.Label(frame, text="Role:").grid(row=1, column=0)
#        tk.Label(frame, text="HP:").grid(row=2, column=0)
#        tk.Label(frame, text="AC:").grid(row=3, column=0)
#        tk.Label(frame, text="Move Spd:").grid(row=4, column=0)
#        tk.Label(frame, text="Grid X:").grid(row=5, column=0)
#        tk.Label(frame, text="Grid Y:").grid(row=6, column=0)
#        self.name = tk.Entry(frame, textvariable=vName)
#        self.name.grid(row=0, column=1)
#        self.role = tk.Entry(frame, textvariable=vRole)
#        self.role.grid(row=1, column=1)
#        self.hp = tk.Entry(frame, textvariable=vhp)
#        self.hp.grid(row=2, column=1)
#        self.ac = tk.Entry(frame, textvariable=vac)
#        self.ac.grid(row=3, column=1)
#        self.moveSpeed = tk.Entry(frame, textvariable=vms)
#        self.moveSpeed.grid(row=4, column=1)
#        self.grid_x = tk.Entry(frame, textvariable=vgrid_x)
#        self.grid_x.grid(row=5, column=1)
#        self.grid_y = tk.Entry(frame, textvariable=vgrid_y)
#        self.grid_y.grid(row=6, column=1)
#        if self.selected[0] is None:
#            tk.Label(frame, text="Submit to add actions").grid(row=7, column=1, columnspan=2)
#        else:
#            actFrame = tk.LabelFrame(frame, text="Actions")
#            actFrame.grid(row=8, column=0, columnspan=2)
#            butFrame = tk.Frame(actFrame)
#            butFrame.grid(row=0,column=1)
#            lb1 = tk.Listbox(actFrame)
#            lb1.grid(row=0, column=0)
#            for i in self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = ?;",[self.selected[0]]):
#                lb1.insert(tk.END, i)
#                #temp = tk.Label(actFrame, text=i[0])
#                #temp.grid(row=count1, column=0)
#                #temp.bind("<Button-1>", lambda event: print(event))
#            lb2 = tk.Listbox(actFrame)
#            lb2.grid(row=0, column=2)
#            for i in self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = -1 and [name] not in (select [name] from " + self.encounter + "_actions where [poss_player] = ?);",[self.selected[0]]):
#                lb2.insert(tk.END, i)
#                #temp = tk.Label(actFrame, text=i[0])
#                #temp.grid(row=count2, column=1)
#                #temp.bind("<Button-1>", lambda event: print(event))
#
#            def __addAct(lb1: tk.Listbox, lb2: tk.Listbox):
#                self.cur.execute("insert into " + self.encounter + "_actions ([poss_player],[name],[damage],[range],[aoe],[action_tags],[modifiers]) select ?,[name],[damage],[range],[aoe],[action_tags],[modifiers] from " + self.encounter + "_actions where [name] = ? and [poss_player] = -1;", [self.selected[0], lb2.get(lb2.curselection())[0]]) 
#                name = lb2.get(lb2.curselection())
#                lb2.delete(lb2.curselection()[0])
#                lb1.insert(tk.END, name)
#
#            def __remAct(lb1: tk.Listbox, lb2: tk.Listbox):
#                self.cur.execute("delete from " + self.encounter + "_actions where [name] = ? and [poss_player] = ?;", [lb1.get(lb1.curselection())[0], self.selected[0]]) 
#                name = lb1.get(lb1.curselection())
#                lb1.delete(lb1.curselection()[0])
#                lb2.insert(tk.END, name)
#            add = tk.Button(butFrame, text="<", command=lambda:__addAct(lb1, lb2))
#            add.grid(row=0, column=0)
#            rem = tk.Button(butFrame, text=">", command=lambda:__remAct(lb1, lb2))
#            rem.grid(row=1, column=0)
#
#        tk.Button(frame, text="Submit", command=self.__updateEntInDB).grid(row=9, column=1)
#        tk.Button(frame, text="Back", command=self.__entMgr).grid(row=9, column=0)
#        #tk.Button(frame, text="Action Manager", command=self.__actMgr).grid(row=10, column=0, columnspan=2)
#        tk.Button(frame, text="Exit", command=self.__exitSettings).grid(row=11, column=0, columnspan=2)

#    def __actMgr(self):
#        self.renderFrame()
#        for i in self.settingsWindow.winfo_children():
#            i.destroy()
#        actFrame = tk.Frame(self.settingsWindow)
#        drop = ttk.Combobox(actFrame)
#        drop['values'] = self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = -1;").fetchall()
#        drop.current(0)
#        drop.grid(row=0, column=0)
#        tk.Button(actFrame, text="Edit", command=lambda: self.__editAct(drop.get(), actFrame)).grid(row=0, column=1)
#        tk.Button(actFrame, text="New Action", command=lambda: self.__editAct("New", actFrame)).grid(row=1, column=0, columnspan=2)
#        tk.Button(actFrame, text="Back", command=self.prompt).grid(row=9, column=0, columnspan=2)
#        actFrame.pack()

    def __entMgr(self):
        self.__clearCanvas()

        self.tkother['drop'] = ttk.Combobox(self.settingsCanvas)
        self.tkother['drop']['values'] = self.cur.execute("select [id],[name] from " + self.encounter + "_entities where id > -1;").fetchall()
        try:
            self.tkother['drop'].current(0)
        except tk.TclError:
            None
        self.tkother['edit_ent'] = ttk.Button(self.settingsCanvas, image=self.images['edit_ent'], command=lambda: self.__editEnt(self.tkother['drop'].get()))
        self.tkother['del'] = ttk.Button(self.settingsCanvas, image=self.images['del'], command=lambda: self.__remEnt(self.tkother['drop'].get()))
        self.tkother['new_ent'] = ttk.Button(self.settingsCanvas, image=self.images['new_ent'], command=lambda: self.__editEnt("New"))
        self.tkother['back'] = ttk.Button(self.settingsCanvas, image=self.images['back'], command=self.prompt)
        self.settingsCanvas.create_window(8, 10, anchor=tk.NW, window=self.tkother['drop'], tags='entities')
        self.settingsCanvas.create_window(8, 50, anchor=tk.NW, window=self.tkother['new_ent'], tags='entities')
        self.settingsCanvas.create_window(8, 90, anchor=tk.NW, window=self.tkother['del'], tags='entities')
        self.settingsCanvas.create_window(8, 130, anchor=tk.NW, window=self.tkother['edit_ent'], tags='entities')
        self.settingsCanvas.create_window(8, 170, anchor=tk.NW, window=self.tkother['back'], tags='entities')

    def __iniMgr(self):
        init = self.cur.execute(f"select [initiative] from {self.encounter};").fetchone()[0]
        print(init)
        self.renderFrame()
        self.__clearCanvas()
        iniFrame = tk.Frame(self.settingsWindow)
        butFrame = tk.Frame(iniFrame)
        self.lb = tk.Listbox(iniFrame)

        for i in init.split(','):
            self.lb.insert(tk.END, self.cur.execute("select [name] from " + self.encounter + "_entities where [id] = ?;", [i]).fetchone())

        tk.Button(butFrame, image=self.images['up_arr'], command=self.__iniMoveUp).grid(row=0, column=0)
        tk.Button(butFrame, image=self.images['dn_arr'], command=self.__iniMoveDown).grid(row=1, column=0)

        self.lb.grid(row=0, column=0)
        butFrame.grid(row=0, column=1)
        tk.Button(iniFrame, text="Submit", command=self.__udpateInitInDB).grid(row=8, column=0, columnspan=2)
        tk.Button(iniFrame, text="Back", command=self.prompt).grid(row=9, column=0, columnspan=2)
        iniFrame.pack()

    def __bckMgr(self):
        self.__clearCanvas()
        imagefile = tk.filedialog.askopenfile(mode='r',
                                              initialdir=(os.getcwd() + "/res/maps/"),
                                              filetypes=(("png files", "*.png"), ("all files", "*.*")))
        image = Image.open(imagefile.name)
        image = image.resize((int(self.map.cget('width')), int(self.map.cget('height'))))
        self.image = ImageTk.PhotoImage(image)
        self.map.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.renderFrame()

    def __clearCanvas(self):
        try:
            self.settingsCanvas.delete("prompt")
            self.settingsCanvas.delete("background")
            self.settingsCanvas.delete("initiative")
            self.settingsCanvas.delete("entities")
        except AttributeError:
            None

    def __loadImages(self):
        self.images['logo'] = ImageTk.PhotoImage(Image.open("res/icons/logo.png"))
        self.images['background'] = ImageTk.PhotoImage(Image.open("res/icons/control_panel.png"))
        self.images['ent_mgr'] = ImageTk.PhotoImage(Image.open("res/icons/ent_mgr_slim.png"))
        self.images['del'] = ImageTk.PhotoImage(Image.open("res/icons/delete.png"))
        self.images['back'] = ImageTk.PhotoImage(Image.open("res/icons/back.png"))
        self.images['exit'] = ImageTk.PhotoImage(Image.open("res/icons/exit.png"))
        self.images['set_bkgrnd'] = ImageTk.PhotoImage(Image.open("res/icons/set_bkgrnd.png"))
        self.images['new_ent'] = ImageTk.PhotoImage(Image.open("res/icons/new_ent.png"))
        self.images['edit_ent'] = ImageTk.PhotoImage(Image.open("res/icons/edit_ent.png"))
        self.images['eac'] = ImageTk.PhotoImage(Image.open("res/icons/eac.png"))
        self.images['ehp'] = ImageTk.PhotoImage(Image.open("res/icons/ehp.png"))
        self.images['egx'] = ImageTk.PhotoImage(Image.open("res/icons/ent_grid_x.png"))
        self.images['egy'] = ImageTk.PhotoImage(Image.open("res/icons/ent_grid_y.png"))
        self.images['ename'] = ImageTk.PhotoImage(Image.open("res/icons/ename.png"))
        self.images['espeed'] = ImageTk.PhotoImage(Image.open("res/icons/espeed.png"))
        self.images['esprite'] = ImageTk.PhotoImage(Image.open("res/icons/esprite.png"))
        self.images['erole'] = ImageTk.PhotoImage(Image.open("res/icons/erole.png"))
        self.images['submit'] = ImageTk.PhotoImage(Image.open("res/icons/submit.png"))
        self.images['up_arr'] = ImageTk.PhotoImage(Image.open("res/icons/up_arr.png"))
        self.images['dn_arr'] = ImageTk.PhotoImage(Image.open("res/icons/dn_arr.png"))
