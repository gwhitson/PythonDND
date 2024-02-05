import StartMenu
import sqlite3
import tkinter as tk

class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        self.save = menu.startMenu()
        if self.save == "":
            exit(3)
        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()
        self.entities = None

        self.name = None
        self.role = None
        self.hp = None
        self.ac = None
        self.grid_x = None
        self.grid_y = None

        self.window = tk.Tk()
        self.window.title("Dungeons and Dragons")
        self.window.attributes("-fullscreen", True)

        self.gameSettings = self.cur.execute("select [map_size],[mode] from game;").fetchone()
        print(self.gameSettings[0])
        self.mapDimension = [40,40] # will need to change the DB interaction on this to have map_size take in a string of format XXxYY or X,Y etc.etc.
        self.square_size = int((self.window.winfo_screenwidth() - 200) / self.mapDimension[0])
        self.mode = self.gameSettings[1]

        self.mapFrame = tk.Frame(self.window,
                                 width=(self.mapDimension[0] * self.square_size),
                                 height=(self.mapDimension[1] * self.square_size))
        self.map = tk.Canvas(self.mapFrame,
                             width=(self.mapDimension[0] * self.square_size),
                             height=(self.mapDimension[1] * self.square_size),
                             bg='white',
                             scrollregion=(0,0,self.mapDimension[0] * self.square_size,self.mapDimension[1] * self.square_size))
        vbar = tk.Scrollbar(self.mapFrame, orient=tk.VERTICAL)
        self.control = tk.Frame(self.window,
                                width=200,
                                height=self.window.winfo_screenheight())

        vbar.config(command=self.map.yview)
        self.map.config(yscrollcommand=vbar.set)
        self.map.bind('<Button-1>', self.click, add="+")

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
        outline_width = self.square_size / 12
        w = self.mapDimension[0] * self.square_size
        h = self.mapDimension[1] * self.square_size
        # horizontal lines
        for i in range(0, h, self.square_size):
            self.map.create_line(0, i, w, i, fill="black")
        # vertical lines
        for k in range(0, w, self.square_size):
            self.map.create_line(k, 0, k, h, fill="black")

        self.entities = (self.cur.execute("Select [name],[role],[grid_x],[grid_y] from entities;")).fetchall()
        for i in self.entities:
            self.map.create_oval((int(i[2]) - 1) * self.square_size,
                                 (int(i[3]) - 1) * self.square_size,
                                 int(i[2]) * self.square_size,
                                 int(i[3]) * self.square_size,
                                 outline="black",
                                 width=outline_width)
            if i[1] == "player":
                self.map.create_oval((int(i[2]) - 1) * self.square_size,
                                     (int(i[3]) - 1) * self.square_size,
                                     int(i[2]) * self.square_size,
                                     int(i[3]) * self.square_size,
                                     fill="blue")
            if i[1] == "enemy":
                self.map.create_oval((int(i[2]) - 1) * self.square_size,
                                     (int(i[3]) - 1) * self.square_size,
                                     int(i[2]) * self.square_size,
                                     int(i[3]) * self.square_size,
                                     fill="red")

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.window.destroy).pack()
        tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()
        if self.gameSettings[1] == "noncombat":
            tk.Button(self.control, text="Start Combat", command = self.startCombat).pack()
        else:
            tk.Button(self.control, text="End Combat", command = self.endCombat).pack()

    def renderFrame(self):
        self.gameSettings = self.cur.execute("select [map_size],[mode] from game;").fetchone()
        for widg in self.control.winfo_children():
            widg.destroy()
        self.renderControlFrame()
        self.renderMapFrame()

    def click(self, event):
        click_x = int((self.map.canvasx(event.x)) / self.square_size) + 1
        click_y = int((self.map.canvasy(event.y)) / self.square_size) + 1
        print(str(click_x) + " - " + str(click_y))
        clickedEnt = self.cur.execute("select * from entities where [grid_x] = ? and [grid_y] = ?", [click_x, click_y]).fetchall()
        if clickedEnt != []:
            print(clickedEnt)
            self.cur.execute("update game set [targetted] = ? where 1 = 1;", [clickedEnt[0][1]])
            self.conn.commit()
        else:
            self.cur.execute("update game set [targetted] = '' where 1 = 1;")
            self.conn.commit()
        self.renderFrame()

    def test(self):
        print(self.name.get() + " - " + self.role.get() + " - " + self.hp.get() + ";")

    def addEntity(self):
        self.add = tk.Tk()
        self.add.title("Add Entity")
        namevar = tk.StringVar()
        rolevar = tk.StringVar()
        hpvar = tk.StringVar()
        acvar = tk.StringVar()
        xvar = tk.StringVar()
        yvar = tk.StringVar()
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
        tk.Label(self.add, text="X:").grid(row=4, column=0)
        self.grid_x = tk.Entry(self.add, textvariable=xvar)
        self.grid_x.grid(row=4, column=1)
        tk.Label(self.add, text="Y:").grid(row=5, column=0)
        self.grid_y = tk.Entry(self.add, textvariable=yvar)
        self.grid_y.grid(row=5, column=1)
        tk.Button(self.add, text="Submit", command=self.addEntToDB).grid(row=6, column=0, columnspan=2)

    def addEntToDB(self):
        self.cur.execute("INSERT INTO entities (name, role, hp, ac, grid_x, grid_y) VALUES (?,?,?,?,?,?);", [self.name.get(), self.role.get(), self.hp.get(), self.ac.get(), self.grid_x.get(), self.grid_y.get()])
        self.conn.commit()
        self.add.destroy()
        self.name = None
        self.role = None
        self.hp = None
        self.ac = None
        self.grid_x = None
        self.grid_y = None
        self.renderFrame()

    def startCombat(self):
        # self.chooseinitiative
        self.cur.execute("update game set [mode] = 'combat' where 1=1;")
        self.conn.commit()
        self.renderFrame()

    def endCombat(self):
        self.cur.execute("update game set [mode] = 'noncombat' where 1=1;")
        self.conn.commit()
        self.renderFrame()
