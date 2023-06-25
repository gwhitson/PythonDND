import DMControls as dm
# import os
# import sys
# import json
import tkinter as tk
from tkinter import ttk

screensize = 600
cntrlrsize = 200


class DungeonMap():
    def __init__(self, control: dm.control_scheme):
        self.window = tk.Tk()
        self.window.title = "Map"
        self.canvas = tk.Canvas(self.window,
                                width=(screensize),
                                height=screensize)
        self.canvas.pack(side=tk.LEFT)
        # self.window.bind('<Button-1>', self.click)

        self.control = control
        self.controller = tk.LabelFrame(self.window, text="controls",
                                        width=cntrlrsize, height=screensize)
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)

    def mainloop(self):
        self.window.mainloop()

    def init_gamescreen(self):
        square_size = (screensize / self.control.map_size)
        # create horizontal lines
        for i in range(self.control.map_size):
            self.canvas.create_line(0,
                                    (i * square_size),
                                    screensize,
                                    (i * square_size))
        # create vertical lines
        for i in range(self.control.map_size + 1):
            self.canvas.create_line((i * square_size),
                                    0,
                                    (i * square_size),
                                    screensize)

    def init_control_panel(self):
        deal_heal_dmgbtn = tk.Button(self.controller, text="Deal/Heal Damage")
        deal_heal_dmgbtn.grid(row=0, column=0)

        health_change_label = tk.LabelFrame(self.controller,
                                            text="change in health:")
        health_change_label.grid(row=1, column=0)
        health_change_box = ttk.Spinbox(health_change_label,
                                        from_=-40,
                                        to=40)
        health_change_box.grid(row=0, column=0)

        dmg_opts_frame = tk.LabelFrame(self.controller,
                                       text="Deal/Heal options")
        dmg_opts_frame.grid(row=2, column=0)

        damage_radius_label = tk.Label(dmg_opts_frame, text="Radius")
        damage_radius_label.grid(row=0, column=0)
        damage_radius = ttk.Spinbox(dmg_opts_frame, from_=1, to=30, width=10)
        damage_radius.grid(row=1, column=0)

        target_type_label = tk.Label(dmg_opts_frame, text="Target Type")
        target_type_label.grid(row=0, column=1)

        targetting = tk.StringVar()
        target_type = ttk.Combobox(dmg_opts_frame,
                                   width=10,
                                   textvariable=targetting)
        target_type['values'] = ("Players", "Enemies", "All in radius")
        target_type.grid(row=1, column=1)






##### test code
player1 = dm.controllable_entity("player1", 5, 3, 3, "player")
player2 = dm.controllable_entity("player2", 5, 3, 3, "player")
player3 = dm.controllable_entity("player3", 5, 3, 3, "player")
player4 = dm.controllable_entity("player4", 5, 3, 3, "player")
player5 = dm.controllable_entity("player5", 5, 3, 3, "player")

ents = [player1,player2,player3,player4,player5]

game = dm.control_scheme(ents, 30)


test = DungeonMap(game)
test.init_gamescreen()
test.init_control_panel()
test.mainloop()

