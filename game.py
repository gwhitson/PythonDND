import DMControls as dm
import math
# import os
# import sys
# import json
import tkinter as tk
from tkinter import ttk
import numpy

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
        self.canvas.bind('<Button-1>', self.draw_circle_on_click)

        self.control = control
        self.controller = tk.LabelFrame(self.window, text="controls",
                                        width=cntrlrsize, height=screensize)
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.square_size = (screensize / self.control.map_size)

        self.targetting = tk.StringVar()
        self.health_change_val = tk.IntVar()
        self.target_radius = tk.IntVar()

    def mainloop(self):
        self.window.mainloop()

    def init_gamescreen(self):
        # create horizontal lines
        for i in range(self.control.map_size):
            self.canvas.create_line(0,
                                    (i * self.square_size),
                                    screensize,
                                    (i * self.square_size))
        # create vertical lines
        for i in range(self.control.map_size + 1):
            self.canvas.create_line((i * self.square_size),
                                    0,
                                    (i * self.square_size),
                                    screensize)

# longest boi here, creates and defines all of the controls schema
    def init_deal_heal(self):
        targetting = tk.StringVar()
        health_change_val = tk.IntVar()
        target_radius = tk.IntVar()

        self.controller.bind('<Button-1>', self.update_targetting_vars(target_radius, targetting, health_change_val))

        deal_heal_dmgbtn = tk.Button(self.controller, text="Deal/Heal Damage")
        deal_heal_dmgbtn.grid(row=0, column=0)

        health_change_label = tk.LabelFrame(self.controller,
                                            text="change in health:")
        health_change_label.grid(row=1, column=0)

        health_change_box = tk.Entry(health_change_label,
                                     textvariable=health_change_val)
        health_change_box.insert(0, "0")
        health_change_box.grid(row=0, column=0)

        dmg_opts_frame = tk.LabelFrame(self.controller,
                                       text="Deal/Heal options")
        dmg_opts_frame.grid(row=2, column=0)

        damage_radius_label = tk.Label(dmg_opts_frame, text="Radius")
        damage_radius_label.grid(row=0, column=0)
        damage_radius = tk.Entry(dmg_opts_frame, width=10,
                                 textvariable=target_radius)
        damage_radius.insert(0, "0")
        damage_radius.grid(row=1, column=0)

        target_type_label = tk.Label(dmg_opts_frame, text="Target Type")
        target_type_label.grid(row=0, column=1)

        target_type = ttk.Combobox(dmg_opts_frame,
                                   width=10,
                                   textvariable=targetting)
        target_type['values'] = ("Players", "Enemies", "All in radius")
        target_type.current(2)
        target_type.grid(row=1, column=1)

#        set_target_radius_btn = tk.Button(self.controller,
#                                          text="Set target radius")
#        set_target_radius_btn.grid(row=3, column=0)

    def update_targetting_vars(self, target_radius, targetting, health_change_val):
        self.target_radius = target_radius
        self.targetting = targetting
        self.health_change_val = health_change_val

    def determine_grid_position(self, pos: list[int, int]):
        pos = numpy.array(pos)
        return (numpy.array(pos // self.square_size, dtype=int))

    def determine_pixel_position(self, pos: list[int, int]):
        position = [(pos[0] * self.square_size) + (0.5 * self.square_size),
                    (pos[1] * self.square_size) + (0.5 * self.square_size)]
        return position

    def draw_circle_on_click(self, event):
        self.canvas.delete("target_circle")
        self.update_players()
        
        if self.target_radius.get() != 0:
            pixel_position = [event.x, event.y]

            grid_pos = self.determine_grid_position(pixel_position)
#           print(str(grid_pos) + str(self.target_radius.get()) + str(self.health_change_val.get()) + self.targetting.get())

            x1 = (grid_pos[0] - self.target_radius.get()) + 0.5
            x2 = (grid_pos[0] + self.target_radius.get()) + 0.5
            y1 = (grid_pos[1] - self.target_radius.get()) + 0.5
            y2 = (grid_pos[1] + self.target_radius.get()) + 0.5

            x1 = x1 * self.square_size
            x2 = x2 * self.square_size
            y1 = y1 * self.square_size
            y2 = y2 * self.square_size

            self.canvas.create_oval(x1, y1, x2, y2, width=3, tags="target_circle")

            tempvar = (0.5 * self.square_size)
            for i in self.control.entities:
                pos = self.determine_pixel_position([i.location_x, i.location_y])
                if (((i.location_x - grid_pos[0]) ** 2) + ((i.location_y - grid_pos[1]) ** 2) <= (self.target_radius.get()) ** 2):
                        #(math.sqrt(i.location_x - grid_pos[0])) + (math.sqrt(i.location_y - grid_pos[1])) >= math.sqrt(self.target_radius.get())):
                    print(str(i.location_x) + ':' + str(i.location_y))
                    self.canvas.create_oval(pos[0] - tempvar,
                                            pos[1] - tempvar,
                                            pos[0] + tempvar,
                                            pos[1] + tempvar,
                                            fill="red",
                                            tags="target_circle")
                    i.targetted = True
                else:
                    i.targetted = False

                i.print()
        else:
            print("radius=0")



    def update_players(self):
        tempvar = (0.5 * self.square_size)
        for i in range(len(self.control.entities)):
            pos = self.determine_pixel_position([self.control.entities[i].location_x,
                                                 self.control.entities[i].location_y])

            self.canvas.create_oval(pos[0] - tempvar,
                                    pos[1] - tempvar,
                                    pos[0] + tempvar,
                                    pos[1] + tempvar,
                                    fill="blue",
                                    tags="target_circle")
            self.canvas.create_text(pos[0], pos[1], text=str(i + 1), fill="white")



##### test code
player1 = dm.controllable_entity("player1", 5, 8, 8, "player")
player2 = dm.controllable_entity("player2", 5, 3, 14, "player")
player3 = dm.controllable_entity("player3", 5, 13, 3, "player")
player4 = dm.controllable_entity("player4", 5, 23, 9, "player")
player5 = dm.controllable_entity("player5", 5, 3, 3, "player")

ents = [player1,player2,player3,player4,player5]

game = dm.control_scheme(ents, 30)


test = DungeonMap(game)
test.init_gamescreen()
test.init_deal_heal()
test.update_players()
test.mainloop()

