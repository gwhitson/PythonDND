import StartMenu
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

        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        # vars to be used
        self.selected = None
        self.selectedActions = None
        self.name = None
        self.role = None
        self.hp = None
        self.ac = None
        self.moveSpeed = None
        self.grid_x = None
        self.grid_y = None
        self.sprite = None
        self.entities = None
        self.action = None
        self.actionID = None

        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

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

        self.map.update()
        self.mapFrame.update()
        self.control.update()

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

        self.entities = (self.cur.execute("Select [name],[role],[grid_x],[grid_y],[pix_x],[pix_y] from entities;")).fetchall()
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
        tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        tk.Button(self.control, text="Action", command=self.doAction).pack()
        if self.gameSettings[5] == "noncombat":
            #print(self.gameSettings[5])
            tk.Button(self.control, text="Start Combat", command = self.startCombat).pack()
        else:
            tk.Button(self.control, text="End Combat", command = self.endCombat).pack()

    def renderFrame(self):
        self.conn.commit()
        self.gameSettings = self.cur.execute("select * from game;").fetchone()
        for widg in self.control.winfo_children():
            widg.destroy()
        self.renderControlFrame()
        self.renderMapFrame()

    # Game State Interactions
    def leftClick(self, event):
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
                    self.cur.execute("update entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ?;", [click_x, click_y, px, py])
                    self.map.delete("range")
                    self.selected = None
            elif self.gameSettings[8] == 'a':
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                if self.posInRange([self.map.canvasx(event.x), self.map.canvasy(event.y)], [self.selected[8], self.selected[9]], ((self.action[3] + 2.5) / 5) * self.squareSize):
                    self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.selected[0]])
                    print('do some action!')
                    self.map.delete("range")
                    self.selected = None

        self.renderFrame()

    def addEntity(self):
        self.add = tk.Tk()
        self.add.title("Add Entity")
        namevar = tk.StringVar()
        rolevar = tk.StringVar()
        hpvar = tk.StringVar()
        acvar = tk.StringVar()
        mvspd = tk.StringVar()
        xvar = tk.StringVar()
        yvar = tk.StringVar()
        sprite = tk.StringVar()
        tk.Label(self.add, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self.add, textvariable=namevar)
        self.name.grid(row=0, column=1)
        tk.Label(self.add, text="Role:").grid(row=1, column=0)
        self.role = tk.Entry(self.add, textvariable=rolevar)
        self.role.grid(row=1, column=1)
        tk.Label(self.add, text="HP:").grid(row=2, column=0)
        self.hp = tk.Entry(self.add, textvariable=hpvar)
        self.hp.grid(row=2, column=1)
        tk.Label(self.add, text="AC:").grid(row=3, column=0)
        self.ac = tk.Entry(self.add, textvariable=acvar)
        self.ac.grid(row=3, column=1)
        tk.Label(self.add, text="Speed:").grid(row=4, column=0)
        self.moveSpeed = tk.Entry(self.add, textvariable=mvspd)
        self.moveSpeed.grid(row=4, column=1)
        tk.Label(self.add, text="X:").grid(row=5, column=0)
        self.grid_x = tk.Entry(self.add, textvariable=xvar)
        self.grid_x.grid(row=5, column=1)
        tk.Label(self.add, text="Y:").grid(row=6, column=0)
        self.grid_y = tk.Entry(self.add, textvariable=yvar)
        self.grid_y.grid(row=6, column=1)
        tk.Label(self.add, text="Sprite:").grid(row=7, column=0)
        self.sprite = ttk.Combobox(self.add, textvariable=sprite)
        self.sprite['values'] = (os.listdir(self.resFiles + "sprites"))
        self.sprite.grid(row=7, column=1)
        tk.Button(self.add, text="Submit", command=self.addEntToDB).grid(row=8, column=0, columnspan=2)

    def addEntToDB(self):
        self.cur.execute("INSERT INTO entities (name, role, hp, ac, move_spd, grid_x, grid_y, pix_x, pix_y, sprite) VALUES (?,?,?,?,?,?,?,?,?,?);", [self.name.get(), self.role.get(), self.hp.get(), self.ac.get(), self.moveSpeed.get(), self.grid_x.get(), self.grid_y.get(), int(self.grid_x.get()) * self.squareSize, int(self.grid_y.get()) * self.squareSize, self.sprite.get()])
        self.add.destroy()
        self.name = None
        self.role = None
        self.hp = None
        self.ac = None
        self.moveSpeed = None
        self.grid_x = None
        self.grid_y = None
        self.sprite = None
        self.renderFrame()

    def startCombat(self):
        # self.chooseinitiative
        self.cur.execute("update game set [mode] = 'combat', [flags] = '' where 1=1;")
        self.map.delete("range")
        self.renderFrame()

    def endCombat(self):
        self.cur.execute("update game set [mode] = 'noncombat' where 1=1;")
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
        self.cur.execute("update game set [flags] = ?, [curr_ent] = ? where 1=1;", ['m', self.selected[0]])

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

    def doAction(self):
        print('test')
        self.chooseAction()
        print('pos test?')
        self.cur.execute("update game set [flags] = ?, [curr_ent] = ? where 1=1;", ['a', self.selected[0]])

    # Privates
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
        #print(event)

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

    def __quitGame(self):
        self.cur.execute("update game set [flags] = '', [mode] = 'noncombat';")
        self.conn.commit()
        self.window.destroy()
