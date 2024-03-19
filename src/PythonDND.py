import StartMenu
import DNDSettings
import sqlite3
import tkinter as tk
from tkinter import ttk


class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        menuRet = menu.startMenu()
        self.save = menuRet[0]
        self.encounter = menuRet[1]
        self.resFiles = menuRet[2]
        if self.save == "":
            exit(3)

        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        # vars to be used
        self.curr_ent = [None, None, None, None, None, None, None, None, None]

        if (self.cur.execute("select [initiative] from " + self.encounter + ";") == None):
            self.initiative = ""
            for i in (self.cur.execute("select [id] from " + self.encounter + "_entities where [id] > -1;").fetchall()):
                self.initiative += str(i[0])
                self.initiative += ","
        else:
            self.initiative = self.cur.execute("select [initiative] from " + self.encounter + ";").fetchone()[0]

        #print(self.initiative)

        self.cur.execute("update " + self.encounter + " set [initiative] = ?;", [str(self.initiative)])
        self.conn.commit()

        self.selectedActions = None
        self.action = None

        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        print(self.gameSettings)
        spl = self.gameSettings[5].split('x')
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

        self.settingsWindow = DNDSettings.DNDSettings(self.save, self.window, self.squareSize, self.encounter)

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

        self.entities = (self.cur.execute("Select [id],[name],[role],[grid_x],[grid_y],[pix_x],[pix_y] from " + self.encounter + "_entities where id > -1;")).fetchall()
        for i in self.entities:
            if i[2] == "player":
                self.map.create_oval((int(i[3]) - 1) * self.squareSize,
                                     (int(i[4]) - 1) * self.squareSize,
                                     int(i[3]) * self.squareSize,
                                     int(i[4]) * self.squareSize,
                                     fill="blue",
                                     tags="map")
            if i[2] == "enemy":
                self.map.create_oval((int(i[3]) - 1) * self.squareSize,
                                     (int(i[4]) - 1) * self.squareSize,
                                     int(i[3]) * self.squareSize,
                                     int(i[4]) * self.squareSize,
                                     fill="red",
                                     tags="map")
            outline_color = 'orange' if (self.cur.execute("select [curr_ent] from " + self.encounter).fetchone()[0] == i[0]) else 'black'
            self.map.create_oval((int(i[3]) - 1) * self.squareSize,
                                 (int(i[4]) - 1) * self.squareSize,
                                 int(i[3]) * self.squareSize,
                                 int(i[4]) * self.squareSize,
                                 #i[4],i[5],i[4] + self.squareSize,i[5] + self.squareSize,
                                 outline=outline_color,
                                 width=outline_width,
                                 tags="map")

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.__quitGame).pack()
        tk.Button(self.control, text="Session Settings", command=self.__sessSettings).pack()
        #tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        if self.gameSettings[3] == "noncombat":
            #print(self.gameSettings[5])
            tk.Button(self.control, text="Start Combat", command = self.startCombat).pack()
        else:
            tk.Button(self.control, text="Action", command=self.doChooseAction).pack()
            tk.Button(self.control, text="End Combat", command = self.endCombat).pack()

    def renderFrame(self):
        print("rendering frame")
        self.conn.commit()
        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        for widg in self.control.winfo_children():
            widg.destroy()
        self.renderControlFrame()
        self.renderMapFrame()

    # Game State Interactions
    def leftClick(self, event):
        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        click_x = int((self.map.canvasx(event.x)) / self.squareSize + 1)
        click_y = int((self.map.canvasy(event.y)) / self.squareSize + 1)
        clickedEnt = self.cur.execute("select * from " + self.encounter + "_entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchone()
        #print(clickedEnt)

        # check mode
        #print(self.gameSettings)
        if self.gameSettings[3] == 'combat':
            print("combat")
        elif self.gameSettings[3] == 'noncombat':
            #print("noncombat")
            if self.gameSettings[6] == 'm' and clickedEnt is None:
                #print('move')
                #print(self.curr_ent)
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.curr_ent[8], self.curr_ent[9]], int(((self.curr_ent[5] / 5) + 0.5) * self.squareSize)):
                    self.cur.execute("update " + self.encounter + " set [flags] = '';")
                    self.cur.execute("update " +self.encounter + "_entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;", [click_x, click_y, px, py, self.curr_ent[0]])
                    self.map.delete("range")
                self.curr_ent = [None, None, None, None, None, None, None, None, None]
                self.renderFrame()
            else:
                #print('prompt move')
                if clickedEnt is not None:
                    self.moveEnt(click_x, click_y, clickedEnt[0])
        else:
            #print('invalid game mode')
            self.__quitGame()


#   def leftClick(self, event):
#       #print(self.cur.execute("select [initiative] from game;").fetchone())
#       click_x = int((self.map.canvasx(event.x)) / self.squareSize + 1)
#       click_y = int((self.map.canvasy(event.y)) / self.squareSize + 1)
#       clickedEnt = self.cur.execute("select * from entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchall()
#       if clickedEnt != []:
#           self.curr_ent = clickedEnt[0]
#           #print(clickedEnt[0])
#           if self.gameSettings[5] == "noncombat":
#               self.moveEnt(click_x, click_y)
#       else:
#           if self.gameSettings[8] == 'm':
#               px = int(click_x * self.squareSize) - int(self.squareSize / 2)
#               py = int(click_y * self.squareSize) - int(self.squareSize / 2)
#               if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.curr_ent[8], self.curr_ent[9]], int(((self.curr_ent[5] / 5) + 0.5) * self.squareSize)):
#                   self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.curr_ent[0]])
#                   self.cur.execute("update entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;", [click_x, click_y, px, py, self.curr_ent[0]])
#                   self.map.delete("range")
#                   self.curr_ent = None
#           elif self.gameSettings[8] == 'a':
#               px = int(click_x * self.squareSize) - int(self.squareSize / 2)
#               py = int(click_y * self.squareSize) - int(self.squareSize / 2)
#               if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.curr_ent[8], self.curr_ent[9]], ((self.action[3] + 2.5) / 5) * self.squareSize):
#                   self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.curr_ent[0]])
#                   self.__doAction([self.map.canvasx(event.x), self.map.canvasy(event.y)])
#                   self.map.delete("range")
#                   self.curr_ent = None

#       self.renderFrame()

    def startCombat(self):
        if self.gameSettings[0] is None or self.gameSettings[1] is None:
            self.__chooseInitiative()
        else:
            self.cur.execute("update " + self.encounter + " set [mode] = 'combat';")
            self.renderFrame()

    def endCombat(self):
        self.cur.execute("update " + self.encounter + " set [mode] = 'noncombat';")
        self.renderFrame()

    def showRange(self, center: [int, int], color: str, action: (int, str, str, int, int, str, str, int, None)):
        self.map.delete("range")
        if action[-3] == "movement" and action[1] == "Move":
            radius = self.cur.execute(f"select [move_spd] from {self.encounter}_entities where [id] = ?;", [action[-1]]).fetchone()[0]
            color = "#87d987"
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

    def oldshowRange(self, center: [int, int], radius: float, color: str, action: (int, str, str, int, int, str, str, int, None)):
        print("show range")
        self.map.delete("range")
        if action[-3] == "movement" and action[1] == "Move":
            radius = self.cur.execute(f"select [move_spd] from {self.encounter}_entities where [id] = ?;", [action[-1]]).fetchone()[0]
            color = "#87d987"
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
            # #print("pos is in range")
            return True
        else:
            # #print("pos is not in range")
            return False

    # Actions
    def moveEnt(self, x, y, entID):
        self.curr_ent = self.cur.execute("select * from " + self.encounter + "_entities where [id] = ?;", [entID]).fetchone()
        self.showRange([x, y], self.curr_ent[5] + 2.5, "#87d987", self.cur.execute(f"select * from {self.encounter}_actions where [name] = 'Move' and id = ?;", [self.curr_ent[0]]).fetchone())
        self.cur.execute("update " + self.encounter + " set [flags] = ?, [curr_ent] = ?;", ['m', entID])

    def chooseAction(self):
        self.att_sel = tk.Menu(tearoff=0)
        #self.att_sel.event_add('<<event-test>>', '<Button-1>')
        #self.att_sel.bind('<<event-test>>', self.__actionHelper)
        self.curr_ent = self.cur.execute("select * from " + self.encounter + "_entities where [id] = ?;", [self.cur.execute("select [curr_ent] from " + self.encounter + ";").fetchone()[0]]).fetchone()

        if self.curr_ent is not None:
            #print(self.curr_ent)
            self.selectedActions = self.cur.execute("select * from " + self.encounter + "_actions where [poss_player] = ?;", [self.curr_ent[0]]).fetchall()

            for i in self.selectedActions:
                #self.att_sel.add_command(label=i[1], command=lambda val=i: self.cur.execute(f"update {self.encounter} set [curr_action] = ?;", [val[0]]))
                self.att_sel.add_command(label=i[1], command=lambda val=i: self.__actionHelper(val))
            self.att_sel.tk_popup(int(self.curr_ent[8] + self.control.winfo_width()),int(self.curr_ent[9]))
            return 1
        else:
            #print('no ent selected')
            return 0

    def doChooseAction(self):
        if self.cur.execute("select [mode] from " + self.encounter + ";").fetchone()[0] == 'combat':
            print('tester')
            self.chooseAction()

    # Privates
    def __chooseInitiative(self):
        for i in self.control.winfo_children():
            i.destroy()
        iniFrame = tk.Frame(self.control)
        butFrame = tk.Frame(iniFrame)
        self.initLB = tk.Listbox(iniFrame)

        for i in self.cur.execute("select [id] from " + self.encounter + "_entities where id > -1;").fetchall():
            self.initLB.insert(tk.END, str(i[0]) + ' - ' +self.cur.execute("select [name] from " + self.encounter + "_entities where [id] = ?;",[i[0]]).fetchone()[0])

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
            None
            #print("ent at top of order")
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
            None
            #print("ent at bottom of order")
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
        self.cur.execute(f"update {self.encounter} set [mode] = 'combat', [flags] = '', [initiative] = ?, [curr_ent] = ?;",[init, initArr[0]])

        self.map.delete("range")
        self.renderFrame()


    def __doAction(self, click: [int,int]):
        None
        #print(click)

    def __actionHelper(self, action: (int, str, str, int, int ,str, str, int, None)):
        print("action helper")
        print(action)
        self.cur.execute(f"update {self.encounter} set [curr_action] = ?;", [action[0]])
        self.conn.commit()
        self.showRange([self.curr_ent[6], self.curr_ent[7]], action[3] + 2.5, "#ff7878", action)

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
