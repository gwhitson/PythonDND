import DMControls as dm
import tkinter as tk
from tkinter import ttk
import numpy


class DungeonMap():

    def __init__(self, control: dm.control_scheme):
        self.window = tk.Tk()
        self.window.title = "Dungeons & Dragons"
        self.map = tk.Canvas(self.window,
                             width=(self.get_screen_size()[0] - 200),
                             height=self.get_screen_size()[1])
        self.map.pack(side=tk.LEFT)
#       self.map.bind('<Button-1>',
#                        self.draw_circle_on_click,
#                        add="+")
        self.control = control
        self.controller = tk.LabelFrame(self.window,
                                        text="controls",
                                        width=200,
                                        height=self.get_screen_size()[1])
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.screensize = self.get_screen_size()

    def mainloop(self):
        self.window.mainloop()

    # main render function
    def init_gamescreen(self):
        # create horizontal lines
        o = 0
        while o <= self.screensize[1]:
            o += self.control.square_size
            self.map.create_line(0,
                                 o,
                                 self.screensize[0],
                                 o)

        # create vertical lines
        o = 0
        while o <= self.screensize[0]:
            o += self.control.square_size
            self.map.create_line(o,
                                 0,
                                 o,
                                 self.screensize[1])

    # control methods
#   def init_deal_heal(self):

#   def init_move_panel(self):

#   def draw_circle_on_click(self, event):

#   def update_players(self):

#   def ent_mgmt_panel(self):

    # info gathering methods
#   def update_targetting(self):

#   def determine_grid_pos(self):

#   def determine_pixel_pos(self):

    def get_screen_size(self):
        return [self.window.winfo_screenwidth(), self.window.winfo_screenheight()]


#### test code
player1 = dm.controllable_entity("player1", 5, 8, 8, "player")
player2 = dm.controllable_entity("player2", 5, 3, 14, "player")
player3 = dm.controllable_entity("player3", 5, 13, 3, "player")
player4 = dm.controllable_entity("player4", 5, 23, 9, "player")
player5 = dm.controllable_entity("player5", 5, 3, 3, "player")

ents = [player1,player2,player3,player4,player5]

for i in range(5):
    ents.append(dm.controllable_entity("goblin", (6 + (i * 2)), 9 + (i * 2), 5, "enemy"))

game = dm.control_scheme(ents, 30)


test = DungeonMap(game)
test.init_gamescreen()
test.mainloop()
