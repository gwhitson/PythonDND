import StartMenu
import DNDSettings
import os
import sqlite3
import tkinter as tk
from tkinter import ttk


class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        menuRet = menu.startMenu()
        self.save = menuRet[0]
        self.resFiles = menuRet[1]
        if self.save == "":
            exit(3)

        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        # vars to be used
        self.selected = [None,None,None,None,None,None,None,None,None]

        if (self.cur.execute("select [initiative] from game;") == None):
            self.initiative = ""
            for i in (self.cur.execute("select [id] from entities where [id] > -1;").fetchall()):
                self.initiative += str(i[0])
                self.initiative += ","
        else:
            self.initiative = self.cur.execute("select [initiative] from game;").fetchone()[0]

        #print(self.initiative)

        self.cur.execute("update game set [initiative] = ?;", [str(self.initiative)])
        self.conn.commit()

        self.selectedActions = None
        self.action = None

        self.gameSettings = self.cur.execute("select * from game;").fetchone()
        spl = self.gameSettings[7].split('x')
        self.mapDimension = [int(spl[0]), int(spl[1])]

        if self.mapDimension[0] <= self.mapDimension[1]:
            self.squareSize = int((self.window.winfo_screenwidth() - 200) / int(min(self.mapDimension[0], self.mapDimension[1])))
        else:
            self.squareSize = int((self.window.winfo_screenheight()) / int(min(self.mapDimension[0], self.mapDimension[1])))
        self.actionButtonSize = self.squareSize / 3

        #print(self.squareSize)

        self.control = tk.Frame(self.window,
                                height=self.window.winfo_screenheight())

        self.mapFrame = tk.Frame(self.window,
                                 width=(self.mapDimension[0] * self.squareSize),
                                 height=(self.mapDimension[1] * self.squareSize))

        if (self.mapDimension[0] <= self.mapDimension[1]):
            #print("x greater than y", self.squareSize)
            self.map = tk.Canvas(self.mapFrame,
                                 width=(self.mapDimension[0] * self.squareSize),
                                 height=(self.mapDimension[1] * self.squareSize),
                                 bg='white',
                                 scrollregion=(0, 0, self.mapDimension[0] * self.squareSize, self.mapDimension[1] * self.squareSize))
            vbar = tk.Scrollbar(self.mapFrame, orient=tk.VERTICAL)
            vbar.config(command=self.map.yview)
            vbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.map.config(yscrollcommand=vbar.set)
        else:
            #print("x less than y", self.squareSize)
            self.map = tk.Canvas(self.mapFrame,
                                 width=(self.mapDimension[0] * self.squareSize),
                                 height=(self.mapDimension[1] * self.squareSize),
                                 bg='white',
                                 scrollregion=(0, 0, self.mapDimension[0] * self.squareSize, self.mapDimension[1] * self.squareSize))
            hbar = tk.Scrollbar(self.mapFrame, orient=tk.HORIZONTAL)
            hbar.config(command=self.map.xview)
            hbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.map.config(xscrollcommand=hbar.set)

        self.map.bind('<Button-1>', self.leftClick, add="+")
        self.map.bind('<Button-4>', self.__scrollUp, add="+")
        self.map.bind('<Button-5>', self.__scrollDown, add="+")
        self.map.bind('<MouseWheel>', self.__windowsScroll, add="+")

        self.control.pack(side=tk.LEFT, fill=tk.BOTH, anchor='ne')
        self.map.pack(side=tk.RIGHT, anchor='w')
        self.mapFrame.pack(side=tk.RIGHT, anchor='w')
        self.initLB = None

        self.map.update()
        self.mapFrame.update()
        self.control.update()

        self.settingsWindow = DNDSettings.DNDSettings(self.save, self.window, self.squareSize)

        self.renderFrame()
        self.window.mainloop()

    # Render Functions
    def renderMapFrame(self):
        self.map.delete("map")
        outline_width = self.squareSize / 12
        w = self.mapDimension[0] * self.squareSize
        h = self.mapDimension[1] * self.squareSize
        # horizontal lines
        for i in range(0, h, self.squareSize):
            self.map.create_line(0, i, w, i, fill="black", tags="map")
        # vertical lines
        for k in range(0, w, self.squareSize):
            self.map.create_line(k, 0, k, h, fill="black", tags="map")

        self.entities = (self.cur.execute("Select [name],[role],[grid_x],[grid_y],[pix_x],[pix_y] from entities where id > -1;")).fetchall()
        for i in self.entities:
            if i[1] == "player":
                self.map.create_oval((int(i[2]) - 1) * self.squareSize,
                                     (int(i[3]) - 1) * self.squareSize,
                                     int(i[2]) * self.squareSize,
                                     int(i[3]) * self.squareSize,
                                     fill="blue",
                                     tags="map")
            if i[1] == "enemy":
                self.map.create_oval((int(i[2]) - 1) * self.squareSize,
                                     (int(i[3]) - 1) * self.squareSize,
                                     int(i[2]) * self.squareSize,
                                     int(i[3]) * self.squareSize,
                                     fill="red",
                                     tags="map")
            self.map.create_oval((int(i[2]) - 1) * self.squareSize,
                                 (int(i[3]) - 1) * self.squareSize,
                                 int(i[2]) * self.squareSize,
                                 int(i[3]) * self.squareSize,
                                 #i[4],i[5],i[4] + self.squareSize,i[5] + self.squareSize,
                                 outline="black",
                                 width=outline_width,
                                 tags="map")

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.__quitGame).pack()
        tk.Button(self.control, text="Session Settings", command=self.__sessSettings).pack()
        #tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        if self.gameSettings[5] == "noncombat":
            #print(self.gameSettings[5])
            tk.Button(self.control, text="Start Combat", command = self.startCombat).pack()
        else:
            tk.Button(self.control, text="Action", command=self.doChooseAction).pack()
            tk.Button(self.control, text="End Combat", command = self.endCombat).pack()

    def renderFrame(self):
        print("rendering frame")
        self.conn.commit()
        self.gameSettings = self.cur.execute("select * from game;").fetchone()
        for widg in self.control.winfo_children():
            widg.destroy()
        self.renderControlFrame()
        self.renderMapFrame()

    # Game State Interactions
    def leftClick(self, event):
        print(self.cur.execute("select [initiative] from game;").fetchone())
        click_x = int((self.map.canvasx(event.x)) / self.squareSize + 1)
        click_y = int((self.map.canvasy(event.y)) / self.squareSize + 1)
        clickedEnt = self.cur.execute("select * from entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchall()
        if clickedEnt != []:
            self.selected = clickedEnt[0]
            #print(clickedEnt[0])
            if self.gameSettings[5] == "noncombat":
                self.moveEnt(click_x, click_y)
        else:
            if self.gameSettings[8] == 'm':
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.selected[8], self.selected[9]], int(((self.selected[5] / 5) + 0.5) * self.squareSize)):
                    self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.selected[0]])
                    self.cur.execute("update entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;", [click_x, click_y, px, py, self.selected[0]])
                    self.map.delete("range")
                    self.selected = None
            elif self.gameSettings[8] == 'a':
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.selected[8], self.selected[9]], ((self.action[3] + 2.5) / 5) * self.squareSize):
                    self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.selected[0]])
                    self.__doAction([self.map.canvasx(event.x), self.map.canvasy(event.y)])
                    self.map.delete("range")
                    self.selected = None

        self.renderFrame()

    def startCombat(self):
        if self.cur.execute("select [initiative] from game;").fetchone() == ('None',):
            self.__chooseInitiative()
        else:
            self.cur.execute("update game set [mode] = 'combat';")
            self.renderFrame()

    def endCombat(self):
        self.cur.execute("update game set [mode] = 'noncombat';")
        self.renderFrame()

    def showRange(self, center: [int, int], radius: float, color: str):
        self.map.delete("range")
        shift = int(self.squareSize / 2)
        lPos = [center[0] * self.squareSize, center[1] * self.squareSize]
        self.map.create_oval(lPos[0] - (int((radius / 5) * self.squareSize) + shift),
                             lPos[1] - (int((radius / 5) * self.squareSize) + shift),
                             lPos[0] + (int((radius / 5) * self.squareSize) - shift),
                             lPos[1] + (int((radius / 5) * self.squareSize) - shift),
                             outline=color,
                             width=3,
                             fill=color,
                             stipple="gray50",
                             tags="range")
        self.renderFrame()

    # Helpers
    def convertGridToPix(self, pos: [int, int]) -> [int, int]:
        return [((pos[0] + 0.5) * self.squareSize), ((pos[1] + 0.5) * self.squareSize)]

    def posInRange(self, pos: [int, int], center: [int, int], radius: float) -> bool:
        if (((pos[0] - center[0]) ** 2) + ((pos[1] - center[1]) ** 2) <= radius ** 2):
            # print("pos is in range")
            return True
        else:
            # print("pos is not in range")
            return False

    # Actions
    def moveEnt(self, x, y):
        self.showRange([x, y], self.selected[5] + 2.5, "#87d987")
        self.cur.execute("update game set [flags] = ?, [curr_ent] = ?;", ['m', self.selected[0]])

    def chooseAction(self):
        self.att_sel = tk.Menu(tearoff=0)
        self.att_sel.event_add('<<event-test>>', '<Button-1>')
        self.att_sel.bind('<<event-test>>', self.__actionHelper)

        if self.selected is not None:
            print(self.selected)
            self.selectedActions = self.cur.execute("select [id], [name], [range], [damage], [action_tags] from actions where [poss_player] = ?;", [self.selected[0]]).fetchall()

            for i in self.selectedActions:
                self.att_sel.add_command(label=i[1])
            self.att_sel.tk_popup(int(self.selected[8] + self.control.winfo_width()),int(self.selected[9]))
            return 1
        else:
            print('no ent selected')
            return 0

    def doChooseAction(self):
        self.chooseAction()
        self.cur.execute("update game set [flags] = ?, [curr_ent] = ?;", ['a', self.selected[0]])

    # Privates
    def __chooseInitiative(self):
        for i in self.control.winfo_children():
            i.destroy()
        iniFrame = tk.Frame(self.control)
        butFrame = tk.Frame(iniFrame)
        self.initLB = tk.Listbox(iniFrame)

        for i in self.cur.execute("select [id] from entities where id > -1;").fetchall():
            self.initLB.insert(tk.END, str(i[0]) + ' - ' +self.cur.execute("select [name] from entities where [id] = ?;",[i[0]]).fetchone()[0])

        tk.Button(butFrame, text="▲", command=self.__iniMoveUp).grid(row=0, column=0)
        tk.Button(butFrame, text="▼", command=self.__iniMoveDown).grid(row=1, column=0)

        self.initLB.grid(row=0, column=0)
        butFrame.grid(row=0,column=1)
        tk.Button(iniFrame, text="Submit", command=self.__startCombat).grid(row=8,column=0, columnspan=2)
        iniFrame.pack()
        tk.Button(self.control, text="Quit", command=self.__quitGame).pack()

    def __iniMoveUp(self):
        #print(self.initLB.curselection())
        if self.initLB.curselection()[0] == 0:
            print("ent at top of order")
        else:
            ind1 = self.initLB.curselection()[0] - 1
            ind2 = self.initLB.curselection()[0]
            temp1 = self.initLB.get(ind1)
            temp2 = self.initLB.get(ind2)
            #print(temp1, temp2)
            self.initLB.delete(ind1, ind2)
            self.initLB.insert(ind1, temp2)
            self.initLB.insert(ind2, temp1)
            self.initLB.selection_set(ind1)

    def __iniMoveDown(self):
        #print(self.initLB.curselection())
        if self.initLB.curselection()[0] == self.initLB.size() - 1:
            print("ent at bottom of order")
        else:
            ind1 = self.initLB.curselection()[0]
            ind2 = self.initLB.curselection()[0] + 1
            temp1 = self.initLB.get(ind1)
            temp2 = self.initLB.get(ind2)
            #print(temp1, temp2)
            self.initLB.delete(ind1, ind2)
            self.initLB.insert(ind1, temp2)
            self.initLB.insert(ind2, temp1)
            self.initLB.selection_set(ind2)

    def __startCombat(self):
        init = ""
        for i in self.initLB.get(0,self.initLB.size() - 1):
            init += (str(i[0]) + ',')

        initArr = init.split(',')
        initArr.remove('')
        self.cur.execute("update game set [mode] = 'combat', [flags] = '', [initiative] = ?, [last_ent] = ?, [curr_ent] = ?, [next_ent] = ?;",[init, initArr[-1], initArr[0], initArr[1]])
        self.map.delete("range")
        self.conn.commit()
        self.renderFrame()


    def __doAction(self, click: [int,int]):
        print(click)

    def __actionHelper(self, event):
        arith = int(self.att_sel.winfo_height() / len(self.selectedActions))
        self.actionID = self.selectedActions[int(int(event.y) / arith)][0]
        print(self.actionID)
        self.action = self.cur.execute("select * from actions where id = ?;", [self.actionID]).fetchone()
        print(self.action)
        print('show range')
        print(self.selected[6])
        print(self.selected[7])
        print(self.action[3])
        self.showRange([self.selected[6], self.selected[7]], self.action[3] + 2.5, "#ff7878")

    def __windowsScroll(self, event):
        if event.delta < 1:
            self.__scrollDown(event)
        else:
            self.__scrollUp(event)

    def __scrollDown(self, event):
        scrollVal = int(self.squareSize / 30)
        if self.mapDimension[0] <= self.mapDimension[1]:
            self.map.yview_scroll(scrollVal, "units")
        else:
            self.map.xview_scroll(scrollVal, "units")

    def __scrollUp(self, event):
        scrollVal = int(self.squareSize / 30)
        if self.mapDimension[0] <= self.mapDimension[1]:
            self.map.yview_scroll(-scrollVal, "units")
        else:
            self.map.xview_scroll(-scrollVal, "units")

    def __sessSettings(self):
        try:
            self.settingsWindow.destroy()
        except AttributeError:
            None
        self.settingsWindow.setRenderFunc(self.renderFrame)
        self.settingsWindow.prompt()
        self.renderFrame()

    def __quitGame(self):
        #self.cur.execute("update game set [flags] = '', [mode] = 'noncombat';")
        self.conn.commit()
        self.window.destroy()
