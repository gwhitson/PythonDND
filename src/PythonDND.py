import StartMenu
import EntityMenu
import sqlite3
import tkinter as tk

class PythonDND:
    def __init__(self):
        menu = StartMenu.StartMenu()
        self.save = menu.startMenu()
        self.conn = sqlite3.connect(self.save)
        self.cur = self.conn.cursor()

        self.name = None
        self.role = None
        self.hp = None
        self.ac = None

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
        h = self.map.winfo_height()
        w = self.map.winfo_width()
        # horizontal lines
        for i in range(0, h, 100):
            self.map.create_line(0, i, w, i, fill="black")
        # vertical lines
        for k in range(0, w, 100):
            self.map.create_line(k, 0, k, h, fill="black")

    def renderControlFrame(self):
        tk.Button(self.control, text="Quit", command=self.window.destroy).pack()
        tk.Button(self.control, text="Add Entity", command=self.addEntity).pack()

    def renderFrame(self):
        self.renderMapFrame()
        self.renderControlFrame()

    def click(self, event):
        print('clicked')
        self.test()

    def test(self):
        #self.cur.execute("INSERT INTO entities (name, role, hp, ac, grid_x, grid_y) VALUES ('test', 'player', 5, 15, 1, 1);")
        #self.conn.commit()
        print(self.name.get() + " please work")
        self.add.destroy()

    def addEntity(self):
        self.add = tk.Tk()
        self.add.title("Add Entity")
        namevar = tk.StringVar()
        rolevar = tk.StringVar()
        hpvar = tk.StringVar()
        acvar = tk.StringVar()
        tk.Label(self.add, text="Name:").grid(row=0, column=0)
        self.name = tk.Entry(self.add, textvariable=namevar).grid(row=0, column=1)
        tk.Label(self.add, text="Role:").grid(row=1, column=0)
        self.role = tk.Entry(self.add, textvariable=rolevar).grid(row=1, column=1)
        tk.Label(self.add, text="HP:").grid(row=2, column=0)
        self.hp = tk.Entry(self.add, textvariable=hpvar).grid(row=2, column=1)
        tk.Label(self.add, text="AC:").grid(row=3, column=0)
        self.ac = tk.Entry(self.add, textvariable=acvar).grid(row=3, column=1)
        tk.Button(self.add, text="Submit", command=self.test).grid(row=4,column=0, columnspan=2)
        #print(name.get() + role.get() + hp.get() + ac.get())
