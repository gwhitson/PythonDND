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
        self.keybinds = menuRet[3]
        if self.save == "":
            exit(127)

        # Tk init
        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)
        self.images = {}

        # Sqlite init
        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        # vars to be used
        self.curr_ent = [None, None, None, None, None, None, None, None, None]
        self.selectedActions = None
        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        spl = self.gameSettings[5].split('x')
        self.mapDimension = [int(spl[0]), int(spl[1])]
        self.atkDmg = tk.IntVar()
        self.atkToHit = tk.IntVar()
        self.atkBonus = tk.BooleanVar()
        self.sprites = {}

        if self.mapDimension[0] <= self.mapDimension[1]:
            self.squareSize = int((self.window.winfo_screenwidth() - 200) / int(min(self.mapDimension[0], self.mapDimension[1])))
        else:
            self.squareSize = int((self.window.winfo_screenheight()) / int(min(self.mapDimension[0], self.mapDimension[1])))
        self.actionButtonSize = self.squareSize / 3

        self.__setInit()

        self.mapFrame = ttk.Frame(self.window,
                                  width=int(self.window.winfo_screenwidth()) - 200,
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

        tempImage = Image.open(self.gameSettings[8])
        self.backgroundImage = ImageTk.PhotoImage(tempImage.resize((int(self.map.cget('width')), int(self.map.cget('height')))))
        self.map.create_image(0, 0, anchor=tk.NW, image=self.backgroundImage)

        self.__createImages()
        self.control = tk.Canvas(self.window,
                                 height=self.window.winfo_screenheight(),
                                 width=200)
        self.control.create_image(0, 0, anchor=tk.NW, image=self.images['control_panel'])

        self.map.bind('<Button-1>', self.leftClick, add="+")
        self.control.bind('<Button-1>', self.printPix, add="+")
        self.map.bind('<Button-4>', self.__scrollUp, add="+")
        self.map.bind('<Button-5>', self.__scrollDown, add="+")
        self.map.bind('<MouseWheel>', self.__windowsScroll, add="+")

        self.control.pack(side=tk.LEFT, fill=tk.BOTH, anchor=tk.NW)
        self.map.pack(side=tk.RIGHT, anchor='w')
        self.mapFrame.pack(side=tk.RIGHT, anchor='w')
        self.initLB = None

        self.map.update()
        self.mapFrame.update()
        self.control.update()

        # Declare settings window
        self.settingsWindow = DNDSettings.DNDSettings(self.save, self.window, self.squareSize, self.encounter, self.map)
        self.__setStyling()
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
            #print(i)
            # check HP
            if i[7] > 0:
                if i[8] is not None:
                    image = Image.open(i[8])
                    image = image.resize((self.squareSize, self.squareSize))
                    self.sprites[i[0]] = ImageTk.PhotoImage(image)
                    self.map.create_image((int(i[3]) - 1) * self.squareSize,
                                          (int(i[4]) - 1) * self.squareSize,
                                          anchor=tk.NW,
                                          image=self.sprites[i[0]],
                                          tags="map")
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
                    self.map.create_text((int(i[3]) - 0.5) * self.squareSize,
                                         (int(i[4]) - 0.5) * self.squareSize,
                                         fill='white',
                                         text=str(i[0]),
                                         font=('sans serif', int(self.squareSize / 4), "bold"),
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
        self.__clearControlFrame()
        bottom = int(self.window.winfo_screenheight())
        #print(bottom)
        self.control.create_image(0, 0, anchor=tk.NW, image=self.images['logo'])
        ttk.Button(self.control, image=self.images['quit'], command=self.__quitGame).place(x=8, y=(bottom - 50))
        ttk.Button(self.control, image=self.images['sess_settings'], command=self.__sessSettings).place(x=8, y=(bottom - 90))
        if self.gameSettings[3] == "noncombat":
            ttk.Button(self.control, image=self.images['start_combat'], command=self.startCombat).place(x=8, y=45)
        else:
            curTurn = self.cur.execute(f"select [name] from {self.encounter}_entities where [id] = ?;", [self.gameSettings[1]]).fetchone()[0]
            #tk.Label(actionFrame, text=f"Current Turn: {curTurn}").grid(row=0, column=0)
            # include later when targettingisfixed fixed
            #tk.Button(actionFrame, text="Choose Action", command=self.doChooseAction).grid(row=1, column=0)
            #self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
            if str(self.gameSettings[6]) == "":
                #print(self.gameSettings[6])
                ttk.Button(self.control, image=self.images['move'], command=self.__setMoveFlag).place(x=8, y=200)
                ttk.Button(self.control, image=self.images['choose_target'], command=self.__setAtkFlag).place(x=103,y=200)
            elif self.gameSettings[6] == 'a':
                ttk.Button(self.control, image=self.images['wide_move'], command=self.__setMoveFlag).place(x=8, y=200)
                ttk.Button(self.control, image=self.images['clear_targets'], command=self.__clearTargets).place(x=8, y=230)
                ttk.Label(self.control, image=self.images['atk_roll']).place(x=9, y=270)
                toHit = ttk.Entry(self.control, textvariable=self.atkToHit, width=3).place(x=140, y=273)
                ttk.Label(self.control, image=self.images['dmg_roll']).place(x=9, y=295)
                dmg = ttk.Entry(self.control, textvariable=self.atkDmg, width=3).place(x=140, y=298)
                ttk.Label(self.control, image=self.images['bonus_act']).place(x=9, y=320)
                atkBonus = ttk.Checkbutton(self.control, variable=self.atkBonus, width=1).place(x=145, y=324)
                ttk.Button(self.control, image=self.images['attack'], command=self.__doAction).place(x=8, y=355)
            elif self.gameSettings[6] == 'm':
                ttk.Button(self.control, image=self.images['attack'], command=self.__setAtkFlag).place(x=8,y=200)

            curr = self.cur.execute(f"select [name],[hp] from {self.encounter}_entities where [id] = {self.gameSettings[1]};").fetchone()
            self.control.create_image(8, 80, anchor=tk.NW, image=self.images['current_ent'], tags='control')
            self.control.create_text(100, 86, anchor=tk.NW, text=curr[0], tags='control')
            self.control.create_text(100, 106, anchor=tk.NW, text=str(curr[1]), tags='control')
            ttk.Button(self.control, image=self.images['prev_turn'], command=self.__prevTurn).place(x=8, y=135)
            ttk.Button(self.control, image=self.images['next_turn'], command=self.__nextTurn).place(x=103, y=135)
            ttk.Button(self.control, image=self.images['end_combat'], command=self.endCombat).place(x=8, y=45)

    def renderFrame(self):
        #print("rendering frame")
        self.conn.commit()
        self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        for widg in self.control.winfo_children():
            widg.destroy()
        self.renderControlFrame()
        self.renderMapFrame()
        self.__ensureBound()

    def printPix(self, event):
        print(event)

    # Game State Interactions
    def leftClick(self, event):
        #self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
        self.curr_ent = self.cur.execute(f"select * from {self.encounter}_entities where [id] = ?", [self.gameSettings[1]]).fetchone()
        click_x = int((self.map.canvasx(event.x)) / self.squareSize + 1)
        click_y = int((self.map.canvasy(event.y)) / self.squareSize + 1)
        clickedEnt = self.cur.execute("select * from " + self.encounter + "_entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchone()
        #print(self.gameSettings)

        # check mode
        if self.gameSettings[3] == 'combat':
            #print("combat")
            if self.gameSettings[6] == 'a':
                if clickedEnt is not None:
                    if self.gameSettings[4] is None:
                        #print("if")
                        self.cur.execute(f"update {self.encounter} set [targetted] = ?;", [clickedEnt[0]])
                    else:
                        #print("else")
                        temp = self.gameSettings[4].split(',')
                        temp.append(str(clickedEnt[0]))
                        temp = str(','.join(temp))
                        self.cur.execute(f"update {self.encounter} set [targetted] = ?;", [temp])
                    self.conn.commit()

                # decide target, prompt for roll for hit and damage
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
            #else:
                #print("not attacking")
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
                    self.cur.execute(f"update {self.encounter} set [curr_ent] = '{clickedEnt[0]}';")
                    self.gameSettings = self.cur.execute("select * from " + self.encounter + ";").fetchone()
                    self.__setMoveFlag()
                    #self.moveEnt(click_x, click_y, clickedEnt[0])
        else:
            #print('invalid game mode')
            self.__quitGame()
        self.renderFrame()

    def startCombat(self):
        print(self.gameSettings)
        if self.gameSettings[0] is None or self.gameSettings[1] is None:
            self.__chooseInitiative()
        else:
            self.cur.execute("update " + self.encounter + " set [mode] = 'combat';")
            self.renderFrame()

    def endCombat(self):
        self.cur.execute("update " + self.encounter + " set [mode] = 'noncombat', [targetted] = '';")
        self.renderFrame()

    def showRange(self, center: [int, int], radius: int):
        self.map.delete("range")
        color = "#87d987"
        lPos = [center[0] * self.squareSize, center[1] * self.squareSize]
        #print("range pls")
        #print(lPos)
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
        self.showRange([x, y], self.cur.execute(f"select * from {self.encounter}_actions where [name] = 'Move' and id = ?;", [self.curr_ent[0]]).fetchone()[0])
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
        #print(self.cur.execute(f"select [aoe] from {self.encounter}_actions where [id] = ?;",[self.gameSettings[2]]).fetchone()[0])
        return pos

    def __chooseInitiative(self):
        self.__clearControlFrame()
        #iniFrame = ttk.Frame(self.control)
        #butFrame = ttk.Frame(iniFrame)
        #self.initLB = ttk.Listbox(iniFrame)
        self.initLB = tk.Listbox(self.control, bg='lightgray', fg='black', borderwidth='0')

        for i in self.cur.execute("select [id] from " + self.encounter + "_entities where id > -1;").fetchall():
            self.initLB.insert(tk.END, str(i[0]) + ' - ' + self.cur.execute("select [name] from " + self.encounter + "_entities where [id] = ?;",[i[0]]).fetchone()[0])

        ttk.Button(self.control, image=self.images['up_arr'], command=self.__iniMoveUp).place(x=170, y=74)
        ttk.Button(self.control, image=self.images['dn_arr'], command=self.__iniMoveDown).place(x=170, y=101)

        self.initLB.place(x=8, y=55)
        #ttk.Button(iniFrame, text="Submit", command=self.__startCombat).place(x=8, y=330)
        ttk.Button(self.control, image=self.images['submit'], command=self.__startCombat).place(x=8, y=245)
        ttk.Button(self.control, image=self.images['quit'], command=self.__quitGame).place(x=8, y=(self.window.winfo_height() - 50))

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
        #self.atkToHit.update()
        #self.atkDmg.update()
        #print(self.atkToHit.get(), self.atkDmg.get(), self.atkBonus.get())
        # quick guard clause
        if self.gameSettings[4] is None:
            return None
        print(self.gameSettings[4].split(','))
        for i in self.gameSettings[4].split(','):
            if str(i) == '':
                None
            elif int(self.atkToHit.get()) >= int(self.cur.execute(f"select [ac] from {self.encounter}_entities where [id] = ?;", [i]).fetchone()[0]):
                self.cur.execute(f"update {self.encounter}_entities set [hp] = ? where [id] = ?", [int(self.cur.execute(f"select [hp] from {self.encounter}_entities where [id] = {i};").fetchone()[0] - int(self.atkDmg.get())), i])
        if self.atkBonus.get() is False:
            self.__nextTurn()
        self.atkToHit.set(value=0)
        self.atkDmg.set(value=0)
        self.atkBonus.set(value=False)
        self.cur.execute(f"update {self.encounter} set [flags] = ?;", [''])
        self.conn.commit()
        self.__clearTargets()
        self.renderFrame()

    def __actionHelper(self, action: (int, str, str, int, int ,str, str, int, None)):
        #print("action helper")
        #print(action)
        aFlag = 'm' if action[5] == 'movement' else 'a'
        self.cur.execute(f"update {self.encounter} set [curr_action] = ?, [flags] = , [targetted] = ''?;", [action[0],aFlag])
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

        self.cur.execute(f"update {self.encounter} set [curr_ent] = ?, [flags] = '', [targetted] = '';", [next])
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

    def __setAtkFlag(self, event=None):
        self.map.delete('range')
        print(self.gameSettings)
        self.cur.execute(f"update {self.encounter} set [flags] = 'a', [targetted] = '';")
        self.renderFrame()

    def __setMoveFlag(self, event=None):
        print(self.gameSettings)
        ent = self.cur.execute(f"select * from {self.encounter}_entities where [id] = ?;", [self.gameSettings[1]]).fetchone()
        self.cur.execute(f"update {self.encounter} set [flags] = 'm', [targetted] = '';")
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

    def __ensureBound(self):
        self.window.bind(f"<{self.keybinds['sel_attack']}>", self.__setAtkFlag)
        self.window.bind(f"<{self.keybinds['sel_move']}>", self.__setMoveFlag)
        self.window.bind(f"<{self.keybinds['exe_attack']}>", self.__doAction, add="+")
        self.window.bind(f"<{self.keybinds['open_sess_settings']}>", self.__sessSettings, add="+")

    def __sessSettings(self, event=None):
        try:
            self.settingsWindow.destroy()
        except AttributeError:
            None
        self.settingsWindow.setRenderFunc(self.renderFrame)
        self.settingsWindow.prompt()
        self.renderFrame()

    def __createImages(self):
        self.images['control_panel'] = ImageTk.PhotoImage(Image.open("res/icons/control_panel.png"))
        self.images['start_combat'] = ImageTk.PhotoImage(Image.open("res/icons/start_combat.png"))
        self.images['end_combat'] = ImageTk.PhotoImage(Image.open("res/icons/end_combat.png"))
        self.images['sess_settings'] = ImageTk.PhotoImage(Image.open("res/icons/sess_settings.png"))
        self.images['quit'] = ImageTk.PhotoImage(Image.open("res/icons/quit.png"))
        self.images['move'] = ImageTk.PhotoImage(Image.open("res/icons/move.png"))
        self.images['choose_target'] = ImageTk.PhotoImage(Image.open("res/icons/choose_target.png"))
        self.images['attack'] = ImageTk.PhotoImage(Image.open("res/icons/attack.png"))
        self.images['next_turn'] = ImageTk.PhotoImage(Image.open("res/icons/next_turn.png"))
        self.images['prev_turn'] = ImageTk.PhotoImage(Image.open("res/icons/prev_turn.png"))
        self.images['clear_targets'] = ImageTk.PhotoImage(Image.open("res/icons/clear_targets.png"))
        self.images['atk_roll'] = ImageTk.PhotoImage(Image.open("res/icons/atk_roll.png"))
        self.images['dmg_roll'] = ImageTk.PhotoImage(Image.open("res/icons/dmg_roll.png"))
        self.images['bonus_act'] = ImageTk.PhotoImage(Image.open("res/icons/bonus_act.png"))
        self.images['wide_move'] = ImageTk.PhotoImage(Image.open("res/icons/wide_move.png"))
        self.images['logo'] = ImageTk.PhotoImage(Image.open("res/icons/logo.png"))
        self.images['submit'] = ImageTk.PhotoImage(Image.open("res/icons/submit.png"))
        self.images['current_ent'] = ImageTk.PhotoImage(Image.open("res/icons/current_ent.png"))
        self.images['up_arr'] = ImageTk.PhotoImage(Image.open("res/icons/up_arr.png"))
        self.images['dn_arr'] = ImageTk.PhotoImage(Image.open("res/icons/dn_arr.png"))

    def __setStyling(self):
        self.style = ttk.Style(self.control)
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
                              "background": "black",
                              }
            },
            "TFrame": {
                "configure": {"padding": "0",
                              "bordercolor": "#6d6d6d",
                              "background": "black",
                              }
            },
            "TCanvas": {
                "configure": {"padding": "0",
                              "bordercolor": "#6d6d6d",
                              "background": "black",
                              }
            },
        })

    def __clearControlFrame(self):
        for i in self.control.winfo_children():
            #print(i)
            i.destroy()
        self.control.delete('control')

    def __quitGame(self):
        #self.cur.execute("update game set [flags] = '', [mode] = 'noncombat';")
        self.conn.commit()
        self.window.destroy()
