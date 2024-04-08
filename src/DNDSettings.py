import os
import sqlite3
import tkinter as tk
from tkinter import ttk


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

    def prompt(self):
        try:
            self.settingsWindow.destroy()
        except AttributeError:
            None
        self.conn.commit()
        self.settingsWindow = tk.Toplevel(self.window)
        self.settingsWindow.title("Session Settings")
        tk.Button(self.settingsWindow, text="Entity Manager", command=self.__entMgr).pack()
        tk.Button(self.settingsWindow, text="Action Manager", command=self.__actMgr).pack()
        tk.Button(self.settingsWindow, text="Initiative Manager", command=self.__iniMgr).pack()
        tk.Button(self.settingsWindow, text="Set Background", command=self.__bckMgr).pack()
        tk.Button(self.settingsWindow, text="Exit", command=self.__exitSettings).pack()
        tk.Button(self.settingsWindow, text='test', command=self.__info).pack()
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
        self.prompt()

    def __updateEntInDB(self):
        if self.selected[0] is None:
            self.cur.execute("insert into " + self.encounter + "_entities ([name], [role], [hp], [ac], [move_spd], [grid_x], [grid_y], [pix_x], [pix_y]) values (?,?,?,?,?,?,?,?,?);",[self.name.get(), self.role.get(), self.hp.get(), self.ac.get(), self.moveSpeed.get(), self.grid_x.get(), self.grid_y.get(), int(self.grid_x.get()) * self.squareSize, int(self.grid_y.get()) * self.squareSize])
            newInit = self.cur.execute(f"select [initiative] from {self.encounter};").fetchone()[0]
            newInit += str(self.cur.execute(f"select [id] from {self.encounter}_entities order by [id] desc limit 1;").fetchone()[0]) + ","
            self.cur.execute(f"update {self.encounter} set [initiative] = ?;", [newInit])
        else:
            self.cur.execute("update " + self.encounter + "_entities set [name] = ?, [role] = ?, [hp] = ?, [ac] = ?, [move_spd] = ?, [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;",[self.name.get(), self.role.get(), self.hp.get(), self.ac.get(), self.moveSpeed.get(), self.grid_x.get(), self.grid_y.get(), int(self.grid_x.get()) * self.squareSize, int(self.grid_y.get()) * self.squareSize, self.selected[0]])

        self.conn.commit()
        self.__entMgr()

    def __updateActInDB(self):
        if self.action[0] is None:
            self.cur.execute("insert into " + self.encounter + "_actions ([name],[damage],[range],[aoe],[action_tags],[modifiers],[poss_player]) values (?,?,?,?,?,?,-1);",[self.actname.get(),self.actdamg.get(),self.actrang.get(),self.actaoef.get(),self.acttags.get(),self.actmods.get()])
        else:
            self.cur.execute("update " + self.encounter + "_actions set [name] = ?,[damage] = ?,[range] = ?,[aoe] = ?,[action_tags] = ?,[modifiers] = ? where [name] = ?;",[self.actname.get(),self.actdamg.get(),self.actrang.get(),self.actaoef.get(),self.acttags.get(),self.actmods.get(),self.action[1]])
        self.conn.commit()
        self.__actMgr()


    def __remEnt(self, dropIn, frame: tk.Frame):
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

    def __editEnt(self, dropIn, frame: tk.Frame):
        for i in frame.winfo_children():
            i.destroy()

        if dropIn == "New":
            self.selected = [None,None,None,None,None,None,None,None,None,None,None]
        else:
            self.selected = (self.cur.execute("select * from " + self.encounter + "_entities where [id] = ?;",[dropIn[0]]).fetchone())
        vName, vRole, vhp, vac, vms, vgrid_x, vgrid_y = tk.StringVar(value=self.selected[1]),tk.StringVar(value=self.selected[2]),tk.StringVar(value=self.selected[3]),tk.StringVar(value=self.selected[4]),tk.StringVar(value=self.selected[5]),tk.StringVar(value=self.selected[6]),tk.StringVar(value=self.selected[7])
        tk.Label(frame, text="Name:").grid(row=0, column=0)
        tk.Label(frame, text="Role:").grid(row=1, column=0)
        tk.Label(frame, text="HP:").grid(row=2, column=0)
        tk.Label(frame, text="AC:").grid(row=3, column=0)
        tk.Label(frame, text="Move Spd:").grid(row=4, column=0)
        tk.Label(frame, text="Grid X:").grid(row=5, column=0)
        tk.Label(frame, text="Grid Y:").grid(row=6, column=0)
        self.name = tk.Entry(frame, textvariable=vName)
        self.name.grid(row=0, column=1)
        self.role = tk.Entry(frame, textvariable=vRole)
        self.role.grid(row=1, column=1)
        self.hp = tk.Entry(frame, textvariable=vhp)
        self.hp.grid(row=2, column=1)
        self.ac = tk.Entry(frame, textvariable=vac)
        self.ac.grid(row=3, column=1)
        self.moveSpeed = tk.Entry(frame, textvariable=vms)
        self.moveSpeed.grid(row=4, column=1)
        self.grid_x = tk.Entry(frame, textvariable=vgrid_x)
        self.grid_x.grid(row=5, column=1)
        self.grid_y = tk.Entry(frame, textvariable=vgrid_y)
        self.grid_y.grid(row=6, column=1)
        if self.selected[0] is None:
            tk.Label(frame, text="Submit to add actions").grid(row=7, column=1, columnspan=2)
        else:
            actFrame = tk.LabelFrame(frame, text="Actions")
            actFrame.grid(row=8, column=0, columnspan=2)
            butFrame = tk.Frame(actFrame)
            butFrame.grid(row=0,column=1)
            lb1 = tk.Listbox(actFrame)
            lb1.grid(row=0, column=0)
            for i in self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = ?;",[self.selected[0]]):
                lb1.insert(tk.END, i)
                #temp = tk.Label(actFrame, text=i[0])
                #temp.grid(row=count1, column=0)
                #temp.bind("<Button-1>", lambda event: print(event))
            lb2 = tk.Listbox(actFrame)
            lb2.grid(row=0, column=2)
            for i in self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = -1 and [name] not in (select [name] from " + self.encounter + "_actions where [poss_player] = ?);",[self.selected[0]]):
                lb2.insert(tk.END, i)
                #temp = tk.Label(actFrame, text=i[0])
                #temp.grid(row=count2, column=1)
                #temp.bind("<Button-1>", lambda event: print(event))

            def __addAct(lb1: tk.Listbox, lb2: tk.Listbox):
                self.cur.execute("insert into " + self.encounter + "_actions ([poss_player],[name],[damage],[range],[aoe],[action_tags],[modifiers]) select ?,[name],[damage],[range],[aoe],[action_tags],[modifiers] from " + self.encounter + "_actions where [name] = ? and [poss_player] = -1;", [self.selected[0], lb2.get(lb2.curselection())[0]]) 
                name = lb2.get(lb2.curselection())
                lb2.delete(lb2.curselection()[0])
                lb1.insert(tk.END, name)

            def __remAct(lb1: tk.Listbox, lb2: tk.Listbox):
                self.cur.execute("delete from " + self.encounter + "_actions where [name] = ? and [poss_player] = ?;", [lb1.get(lb1.curselection())[0], self.selected[0]]) 
                name = lb1.get(lb1.curselection())
                lb1.delete(lb1.curselection()[0])
                lb2.insert(tk.END, name)
            add = tk.Button(butFrame, text="<", command=lambda:__addAct(lb1, lb2))
            add.grid(row=0, column=0)
            rem = tk.Button(butFrame, text=">", command=lambda:__remAct(lb1, lb2))
            rem.grid(row=1, column=0)

        tk.Button(frame, text="Submit", command= self.__updateEntInDB).grid(row=9, column=1)
        tk.Button(frame, text="Back", command= self.__entMgr).grid(row=9, column=0)
        #tk.Button(frame, text="Action Manager", command=self.__actMgr).grid(row=10, column=0, columnspan=2)
        tk.Button(frame, text="Exit", command= self.__exitSettings).grid(row=11, column=0, columnspan=2)

    def __actMgr(self):
        self.renderFrame()
        for i in self.settingsWindow.winfo_children():
            i.destroy()
        actFrame = tk.Frame(self.settingsWindow)
        drop = ttk.Combobox(actFrame)
        drop['values'] = self.cur.execute("select [name] from " + self.encounter + "_actions where [poss_player] = -1;").fetchall()
        drop.current(0)
        drop.grid(row=0, column=0)
        tk.Button(actFrame, text="Edit", command=lambda: self.__editAct(drop.get(), actFrame)).grid(row=0, column=1)
        tk.Button(actFrame, text="New Action", command=lambda: self.__editAct("New", actFrame)).grid(row=1, column=0, columnspan=2)
        tk.Button(actFrame, text="Back", command=self.prompt).grid(row=9, column=0, columnspan=2)
        actFrame.pack()

    def __entMgr(self):
        self.renderFrame()
        for i in self.settingsWindow.winfo_children():
            i.destroy()

        entFrame = tk.Frame(self.settingsWindow)
        drop = ttk.Combobox(entFrame)
        drop['values'] = self.cur.execute("select [id],[name] from " + self.encounter + "_entities where id > -1;").fetchall()
        try:
            drop.current(0)
        except tk.TclError:
            None
        drop.grid(row=0, column=0, columnspan=2)
        tk.Button(entFrame, text="Edit", command=lambda: self.__editEnt(drop.get(), entFrame)).grid(row=1, column=1)
        tk.Button(entFrame, text="Delete", command=lambda: self.__remEnt(drop.get(), entFrame)).grid(row=1, column=0)
        tk.Button(entFrame, text="New Entity", command=lambda: self.__editEnt("New", entFrame)).grid(row=2, column=0, columnspan=2)
        tk.Button(entFrame, text="Back", command=self.prompt).grid(row=9, column=0, columnspan=2)
        entFrame.pack()

    def __iniMgr(self):
        init = self.cur.execute(f"select [initiative] from {self.encounter};").fetchone()[0]
        print(init)
        self.renderFrame()
        for i in self.settingsWindow.winfo_children():
            i.destroy()
        iniFrame = tk.Frame(self.settingsWindow)
        butFrame = tk.Frame(iniFrame)
        self.lb = tk.Listbox(iniFrame)

        for i in init.split(','):
            self.lb.insert(tk.END, self.cur.execute("select [name] from " + self.encounter + "_entities where [id] = ?;", [i]).fetchone())

        tk.Button(butFrame, text="▲", command=self.__iniMoveUp).grid(row=0, column=0)
        tk.Button(butFrame, text="▼", command=self.__iniMoveDown).grid(row=1, column=0)

        self.lb.grid(row=0, column=0)
        butFrame.grid(row=0,column=1)
        tk.Button(iniFrame, text="Submit", command=self.__udpateInitInDB).grid(row=8,column=0, columnspan=2)
        tk.Button(iniFrame, text="Back", command=self.prompt).grid(row=9, column=0, columnspan=2)
        iniFrame.pack()

    def __bckMgr(self):
        imagefile = tk.filedialog.askopenfile(mode='r',
                                          initialdir=(os.getcwd() + "/res/maps/"),
                                          filetypes=(("png files", "*.png"), ("all files", "*.*")))
        self.image = tk.PhotoImage(file=imagefile.name)
        if int(self.map.winfo_screenwidth()) != int(self.map.cget('width')):
            scale = int(int(self.map.cget('height')) / int(self.image.height()))
        else:
            scale = int(int(self.map.cget('width')) / int(self.image.width()))
        self.image = self.image.zoom(scale)
        self.map.create_image(0,0, anchor=tk.NW, image=self.image)

    def __info(self):
        print(self.map.winfo_screenwidth(), self.map.winfo_screenheight(), self.map.cget('width'), self.map.cget('height'))
