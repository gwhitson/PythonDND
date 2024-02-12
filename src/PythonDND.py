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
        self.entities = None

        self.name = None
        self.role = None
        self.hp = None
        self.ac = None
        self.moveSpeed = None
        self.grid_x = None
        self.grid_y = None
        self.sprite = None

        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

        self.gameSettings = self.cur.execute("select * from game;").fetchone()
        print(self.gameSettings)
        self.mapDimension = [40,40] # will need to change the DB interaction on this to have map_size take in a string of format XXxYY or X,Y etc.etc.
        self.squareSize = int((self.window.winfo_screenwidth() - 200) / self.mapDimension[0])

        self.mapFrame = tk.Frame(self.window,
                                 width=(self.mapDimension[0] * self.squareSize),
                                 height=(self.mapDimension[1] * self.squareSize))
        self.map = tk.Canvas(self.mapFrame,
                             width=(self.mapDimension[0] * self.squareSize),
                             height=(self.mapDimension[1] * self.squareSize),
                             bg='white',
                             scrollregion=(0,0,self.mapDimension[0] * self.squareSize,self.mapDimension[1] * self.squareSize))
        vbar = tk.Scrollbar(self.mapFrame, orient=tk.VERTICAL)
        self.control = tk.Frame(self.window,
                                width=200,
                                height=self.window.winfo_screenheight())

        vbar.config(command=self.map.yview)
        self.map.config(yscrollcommand=vbar.set)
        self.map.bind('<Button-1>', self.leftClick, add="+")

        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.map.pack(side=tk.LEFT, fill=tk.BOTH)
        self.mapFrame.pack(side=tk.LEFT, fill=tk.BOTH)
        self.control.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.map.update()
        self.mapFrame.update()
        self.control.update()

        self.renderFrame()
        self.window.mainloop()

    def renderMapFrame(self):
        self.map.delete("map")
        outline_width = self.squareSize / 12
        w = self.mapDimension[0] * self.squareSize
        h = self.mapDimension[1] * self.squareSize
        # horizontal lines
        for i in range(0, h, self.squareSize):
            self.map.create_line(0, i, w, i, fill="black",tags="map")
        # vertical lines
        for k in range(0, w, self.squareSize):
            self.map.create_line(k, 0, k, h, fill="black",tags="map")

        self.entities = (self.cur.execute("Select [name],[role],[grid_x],[grid_y] from entities;")).fetchall()
        for i in self.entities:
            self.map.create_oval((int(i[2]) - 1) * self.squareSize,
                                 (int(i[3]) - 1) * self.squareSize,
                                 int(i[2]) * self.squareSize,
                                 int(i[3]) * self.squareSize,
                                 outline="black",
                                 width=outline_width,
                                 tags="map")
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

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.__quitGame).pack()
        tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        if self.gameSettings[4] == "noncombat":
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

    def leftClick(self, event):
        click_x = int(event.x / self.squareSize) + 1
        click_y = int(event.y / self.squareSize) + 1
        clickedEnt = self.cur.execute("select * from entities where [grid_x] = ? and [grid_y] = ?;", [click_x, click_y]).fetchall()
        if clickedEnt != []:
            self.selected = clickedEnt[0]
            print(clickedEnt[0])
            if self.gameSettings[4] == "noncombat":
                self.moveEnt(click_x, click_y)
        else:
            print(click_x, click_y)
            if self.gameSettings[7] == 'm':
                px = int(click_x * self.squareSize) - int(self.squareSize / 2)
                py = int(click_y * self.squareSize) - int(self.squareSize / 2)
                print(event.x, px, '---' , event.y, py)
                if self.posInRange([event.x, event.y], [self.selected[8], self.selected[9]], int(((self.selected[5] / 5) + 0.5) * self.squareSize)):
                    self.cur.execute("update game set [flags] = '', [last_ent] = ?, [curr_ent] = null;",[self.selected[0]])
                    self.cur.execute("update entities set [grid_x] = ?, [grid_y] = ?, [pix_x] = ?, [pix_y] = ?;", [click_x, click_y, px, py])
                    self.map.delete("range")

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

    def moveEnt(self, x, y):
        self.showRange([x, y], self.selected[5] + 2.5, "#87d987")
        self.cur.execute("update game set [flags] = ?, [curr_ent] = ? where 1=1;", ['m', self.selected[0]])

    def convertGridToPix(self, pos:[int,int]) -> [int,int]:
        return [((pos[0] + 0.5) * self.squareSize), ((pos[1] + 0.5) * self.squareSize)]

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

    def posInRange(self, pos: [int, int], center: [int, int], radius: float) -> bool:
        if (((pos[0] - center[0]) ** 2) + ((pos[1] - center[1]) ** 2) <= radius ** 2):
            return True
        else:
            return False

    def __quitGame(self):
        self.cur.execute("update game set [flags] = '', [mode] = 'noncombat';")
        self.conn.commit()
        self.window.destroy()
