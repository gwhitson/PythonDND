import StartMenu
import EntityMenu
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
        self.square_size = 40
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
        self.map = tk.Canvas(self.window,
                             width=(self.window.winfo_screenwidth() - 200),
                             height=(self.window.winfo_screenheight()),
                             bg='white')
        self.control = tk.Frame(self.window,
                                width=200,
                                height=self.window.winfo_screenheight())
        self.map.pack(side=tk.LEFT, fill=tk.BOTH)
        self.map.bind('<Button-1>', self.click, add="+")
        self.map.update()
        self.control.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.control.update()

        self.renderFrame()
        self.window.mainloop()

    def renderMapFrame(self):
        outline_width = self.square_size / 12
        h = self.map.winfo_height()
        w = self.map.winfo_width()
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

    def renderFrame(self):
        self.renderMapFrame()
        self.renderControlFrame()

    def click(self, event):
        click_x = int(event.x / self.square_size) + 1
        click_y = int(event.y / self.square_size) + 1
        print(str(click_x) + " - " + str(click_y))
        clickedEnt = self.cur.execute("select * from entities where [grid_x] = ? and [grid_y] = ?", [click_x, click_y]).fetchall()
        print(clickedEnt)
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
        tk.Label(self.add, text="X:").grid(row=3, column=0)
        self.x = tk.Entry(self.add, textvariable=xvar)
        self.x.grid(row=3, column=1)
        tk.Label(self.add, text="Y:").grid(row=3, column=0)
        self.y = tk.Entry(self.add, textvariable=yvar)
        self.y.grid(row=3, column=1)
        tk.Button(self.add, text="Submit", command=self.addEntToDB).grid(row=4, column=0, columnspan=2)

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
