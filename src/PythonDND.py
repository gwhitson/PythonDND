import StartMenu
import DNDSettings
import sqlite3
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        menuRet = menu.startMenu()
        self.save = menuRet[0]
        self.encounter = menuRet[1]
        self.resFiles = menuRet[2]
        if self.save == "":
            exit(127)

        # Tk init
        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

        # Sqlite init
        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        # vars to be used
        self.curr_ent = [None, None, None, None, None, None, None, None, None]
        self.selectedActions = None
        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        spl = self.gameSettings[5].split('x')
        self.mapDimension = [int(spl[0]), int(spl[1])]
        self.atkToHit = None
        self.atkDmg = None
        self.atkBonus = None
        self.sprites = {}

        if self.mapDimension[0] <= self.mapDimension[1]:
            self.squareSize = int((self.window.winfo_screenwidth() - 200) / int(min(self.mapDimension[0], self.mapDimension[1])))
        else:
            self.squareSize = int((self.window.winfo_screenheight()) / int(min(self.mapDimension[0], self.mapDimension[1])))
        self.actionButtonSize = self.squareSize / 3

        self.__setInit()

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

        # Declare settings window
        self.settingsWindow = DNDSettings.DNDSettings(self.save, self.window, self.squareSize, self.encounter, self.map)
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

        self.entities = (self.cur.execute("Select [id],[name],[role],[grid_x],[grid_y],[pix_x],[pix_y],[hp],[sprite] from " + self.encounter + "_entities where id > -1;")).fetchall()
        for i in self.entities:
            print(i)
            # check HP
            if i[7] > 0:
                if i[8] != None:
                    image = Image.open(i[8])
                    image = image.resize((self.squareSize, self.squareSize))
                    self.sprites[i[0]] = ImageTk.PhotoImage(image)
                    self.map.create_image((int(i[3]) - 1) * self.squareSize,
                                         (int(i[4]) - 1) * self.squareSize,
                                          anchor=tk.NW,
                                          image=self.sprites[i[0]])
                else:
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
                self.map.create_text((int(i[3]) - 0.5) * self.squareSize,
                                     (int(i[4]) - 0.5) * self.squareSize,
                                     fill='white',
                                     text=str(i[0]),
                                     font=('sans serif', int(self.squareSize / 4), "bold"),
                                     tags="map")
                if self.gameSettings[4] is not None:
                    if str(i[0]) in self.gameSettings[4].split(','):
                        self.map.create_line((int(i[3]) - 1) * self.squareSize,
                                             (int(i[4]) - 1) * self.squareSize,
                                             (int(i[3])) * self.squareSize,
                                             (int(i[4])) * self.squareSize,
                                             width=self.squareSize / 12 + 3,
                                             fill='black',
                                             tags="map")
                        self.map.create_line((int(i[3])) * self.squareSize,
                                             (int(i[4]) - 1) * self.squareSize,
                                             (int(i[3]) - 1) * self.squareSize,
                                             (int(i[4])) * self.squareSize,
                                             width=self.squareSize / 12 + 3,
                                             fill='black',
                                             tags="map")
                        self.map.create_line(((int(i[3]) - 1) * self.squareSize) + 2,
                                             ((int(i[4]) - 1) * self.squareSize) + 2,
                                             ((int(i[3])) * self.squareSize) - 2,
                                             ((int(i[4])) * self.squareSize) - 2,
                                             width=self.squareSize / 12 - 2,
                                             fill='red',
                                             tags="map")
                        self.map.create_line(((int(i[3])) * self.squareSize) - 2,
                                             ((int(i[4]) - 1) * self.squareSize) + 2,
                                             ((int(i[3]) - 1) * self.squareSize) + 2,
                                             ((int(i[4])) * self.squareSize) - 2,
                                             width=self.squareSize / 12 - 2,
                                             fill='red',
                                             tags="map")

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.__quitGame).pack()
        tk.Button(self.control, text="Session Settings", command=self.__sessSettings).pack()
        #tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        if self.gameSettings[3] == "noncombat":
            #print(self.gameSettings[5])
            tk.Button(self.control, text="Start Combat", command=self.startCombat).pack()
        else:
            dmg = tk.IntVar()
            toHit = tk.IntVar()
            self.atkBonus = tk.BooleanVar()
            actionFrame = tk.Frame(self.control)
            curTurn = self.cur.execute(f"select [name] from {self.encounter}_entities where [id] = ?;", [self.gameSettings[1]]).fetchone()[0]
            tk.Label(actionFrame, text=f"Current Turn: {curTurn}").grid(row=0, column=0)
            #tk.Button(actionFrame, text="Choose Action", command=self.doChooseAction).grid(row=1, column=0)
            tk.Button(actionFrame, text="Move", command=self.__setMoveFlag).grid(row=1, column=0)
            tk.Button(actionFrame, text="Attack", command=self.__setAtkFlag).grid(row=1, column=1)
            if self.gameSettings[6] == 'a':
                tk.Button(actionFrame, text="Clear Targets", command=self.__clearTargets).grid(row=2, column=0)
                tk.Label(actionFrame, text="ATK Roll:").grid(row=3, column=0)
                self.atkToHit = tk.Entry(actionFrame, textvariable=toHit, width=3)
                self.atkToHit.grid(row=3, column=1)
                tk.Label(actionFrame, text="DMG Roll:").grid(row=4, column=0)
                self.atkDmg = tk.Entry(actionFrame, textvariable=dmg, width=3)
                self.atkDmg.grid(row=4, column=1)
                tk.Label(actionFrame, text="DMG Roll:").grid(row=5, column=0)
                atkBonus = tk.Checkbutton(actionFrame, variable=self.atkBonus, width=1)
                atkBonus.grid(row=5, column=1)
                tk.Button(actionFrame, text="Attack!", command=self.__doAction).grid(row=6, column=0)

            turnFrame = tk.Frame(self.control, borderwidth=2)
            tk.Button(turnFrame, text="Prev", command=self.__prevTurn).grid(row=0, column=0)
            tk.Button(turnFrame, text="Next", command=self.__nextTurn).grid(row=0, column=1)
            actionFrame.pack()
            turnFrame.pack()
            tk.Button(self.control, text="End Combat", command=self.endCombat).pack()

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
        self.curr_ent = self.cur.execute(f"select * from {self.encounter}_entities where [id] = ?", [self.gameSettings[1]]).fetchone()
        click_x = int((self.map.canvasx(event.x)) / self.squareSize + 1)
        click_y = int((self.map.canvasy(event.y)) / self.squareSize + 1)
        clickedEnt = self.cur.execute("select * from " + self.encounter + "_entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchone()
        print(self.gameSettings)

        # check mode
        if self.gameSettings[3] == 'combat':
            print("combat")
            if self.gameSettings[6] == 'a':
                if clickedEnt is not None:
                    if self.gameSettings[4] is None:
                        print("if")
                        self.cur.execute(f"update {self.encounter} set [targetted] = ?;", [clickedEnt[0]])
                    else:
                        print("else")
                        temp = self.gameSettings[4].split(',')
                        temp.append(str(clickedEnt[0]))
                        temp = str(','.join(temp))
                        self.cur.execute(f"update {self.encounter} set [targetted] = ?;", [temp])
                    self.conn.commit()

                # decide target, prompt for roll for hit and damage
                try:
                    print(self.gameSettings[4].split(','))
                except AttributeError:
                    print("i tried")
                #self.map.delete("range")
                #self.cur.execute(f"update {self.encounter} set [flags] = '';")
            elif self.gameSettings[6] == 'm':
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.curr_ent[8], self.curr_ent[9]], ((self.curr_ent[5] / 5) + 0.5) * self.squareSize):
                    self.cur.execute(f"update {self.encounter} set [flags] = '';")
                    self.cur.execute("update " + self.encounter + "_entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;", [click_x, click_y, px, py, self.curr_ent[0]])
                    self.map.delete("range")
                self.curr_ent = [None, None, None, None, None, None, None, None, None]
                self.__nextTurn()
            else:
                print("not attacking")
        elif self.gameSettings[3] == 'noncombat':
            if self.gameSettings[6] == 'm' and clickedEnt is None:
                #print('move')
                #print(self.curr_ent)
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.curr_ent[8], self.curr_ent[9]], ((self.curr_ent[5] / 5) + 0.5) * self.squareSize):
                    self.cur.execute(f"update {self.encounter} set [flags] = '';")
                    self.cur.execute("update " + self.encounter + "_entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ? where [id] = ?;", [click_x, click_y, px, py, self.curr_ent[0]])
                    self.map.delete("range")
                self.curr_ent = [None, None, None, None, None, None, None, None, None]
            else:
                #print('prompt move')
                if clickedEnt is not None:
                    self.moveEnt(click_x, click_y, clickedEnt[0])
        else:
            #print('invalid game mode')
            self.__quitGame()
        self.renderFrame()

    def startCombat(self):
        if self.gameSettings[0] is None or self.gameSettings[1] is None:
            self.__chooseInitiative()
        else:
            self.cur.execute("update " + self.encounter + " set [mode] = 'combat';")
            self.renderFrame()

    def endCombat(self):
        self.cur.execute("update " + self.encounter + " set [mode] = 'noncombat';")
        self.renderFrame()

    def showRange(self, center: [int, int], radius: int):
        self.map.delete("range")
        color = "#87d987"
        lPos = [center[0] * self.squareSize, center[1] * self.squareSize]
        print("range pls")
        print(lPos)
        self.map.create_oval(lPos[0] - int((radius / 5) + 0.5) * self.squareSize,
                             lPos[1] - int((radius / 5) + 0.5) * self.squareSize,
                             lPos[0] + int((radius / 5) - 0.5) * self.squareSize,
                             lPos[1] + int((radius / 5) - 0.5) * self.squareSize,
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
        self.showRange([x, y], "#87d987", self.cur.execute(f"select * from {self.encounter}_actions where [name] = 'Move' and id = ?;", [self.curr_ent[0]]).fetchone())
        self.cur.execute("update " + self.encounter + " set [flags] = ?, [curr_ent] = ?;", ['m', entID])

    def doChooseAction(self):
        if self.cur.execute("select [mode] from " + self.encounter + ";").fetchone()[0] == 'combat':
            self.__chooseAction()

    # Privates
    def __chooseAction(self):
        self.att_sel = tk.Menu(tearoff=0)
        self.curr_ent = self.cur.execute("select * from " + self.encounter + "_entities where [id] = ?;", [self.cur.execute("select [curr_ent] from " + self.encounter + ";").fetchone()[0]]).fetchone()

        if self.curr_ent is not None:
            self.selectedActions = self.cur.execute("select * from " + self.encounter + "_actions where [poss_player] = ?;", [self.curr_ent[0]]).fetchall()

            for i in self.selectedActions:
                self.att_sel.add_command(label=i[1], command=lambda val=i: self.__actionHelper(val))
            self.att_sel.tk_popup(int(self.curr_ent[8] + self.control.winfo_width()),int(self.curr_ent[9]))
            return 1
        else:
            return 0

    def __entsInAoe(self, pos: [int,int]):
        print(self.cur.execute(f"select [aoe] from {self.encounter}_actions where [id] = ?;",[self.gameSettings[2]]).fetchone()[0])
        return pos

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


    def __doAction(self):
        self.atkToHit.update()
        self.atkDmg.update()
        print(self.atkToHit.get(), self.atkDmg.get(), self.atkBonus.get())
        # quick guard clause
        if self.gameSettings[4] is None:
            return None
        for i in self.gameSettings[4].split(','):
            print(i)
            if int(self.atkToHit.get()) >= int(self.cur.execute(f"select [ac] from {self.encounter}_entities where [id] = ?;", [i]).fetchone()[0]):
                self.cur.execute(f"update {self.encounter}_entities set [hp] = ? where [id] = ?", [int(self.cur.execute(f"select [hp] from {self.encounter}_entities where [id] = {i};").fetchone()[0] - int(self.atkDmg.get())), i])
        if self.atkBonus.get() is False:
            self.__nextTurn()
        self.atkToHit.setvar(value=0)
        self.atkDmg.setvar(value=0)
        self.atkBonus.set(value=False)
        self.cur.execute(f"update {self.encounter} set [flags] = ?;", [''])
        self.conn.commit()
        self.__clearTargets()
        self.renderFrame()

    def __actionHelper(self, action: (int, str, str, int, int ,str, str, int, None)):
        print("action helper")
        print(action)
        aFlag = 'm' if action[5] == 'movement' else 'a'
        self.cur.execute(f"update {self.encounter} set [curr_action] = ?, [flags] = ?;", [action[0],aFlag])
        self.conn.commit()
        #self.showRange([self.curr_ent[6], self.curr_ent[7]], "#ff7878", action)

    def __nextTurn(self):
        next = None
        init = self.gameSettings[0].split(',')[:-1]
        curr = str(self.gameSettings[1])
        if curr == init[-1]:
            next = init[0]
        else:
            next = init[init.index(curr) + 1]

        self.cur.execute(f"update {self.encounter} set [curr_ent] = ?;", [next])
        self.conn.commit()
        self.renderFrame()

    def __prevTurn(self):
        next = None
        init = self.gameSettings[0].split(',')[:-1]
        curr = str(self.gameSettings[1])
        if curr == init[0]:
            next = init[-1]
        else:
            next = init[init.index(curr) - 1]

        self.cur.execute(f"update {self.encounter} set [curr_ent] = ?;", [next])
        self.conn.commit()
        self.renderFrame()

    def __setAtkFlag(self):
        self.cur.execute(f"update {self.encounter} set [flags] = 'a';")
        self.renderFrame()

    def __setMoveFlag(self):
        ent = self.cur.execute(f"select * from {self.encounter}_entities where [id] = ?;", [self.gameSettings[1]]).fetchone()
        self.cur.execute(f"update {self.encounter} set [flags] = 'm';")
        self.showRange([ent[6], ent[7]], ent[5])
        self.renderFrame()

    def __clearTargets(self):
        self.cur.execute(f"update {self.encounter} set [targetted] = ?;", [None])
        self.renderFrame()

    def __setInit(self):
        if (self.cur.execute("select [initiative] from " + self.encounter + ";").fetchone()[0] is None):
            self.initiative = ""
            for i in (self.cur.execute("select [id] from " + self.encounter + "_entities where [id] > -1;").fetchall()):
                self.initiative += str(i[0])
                self.initiative += ","
        else:
            self.initiative = self.cur.execute("select [initiative] from " + self.encounter + ";").fetchone()[0]

        self.cur.execute("update " + self.encounter + " set [initiative] = ?;", [str(self.initiative)])
        self.conn.commit()

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
