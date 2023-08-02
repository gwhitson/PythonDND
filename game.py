import DMControls as dm
import tkinter as tk
from tkinter import ttk
import numpy

class DungeonMap():
    def __init__(self, control: dm.control_scheme):
        self.window = tk.Tk()
        self.window.title = "Dungeons & Dragons"
        self.map = tk.Canvas(self.window,
                             width=screensize_x,
                             height=screensize_y)
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind('<Button-1>',
                         self.draw_circle_on_click,
                         add="+")
        self.control = control
        self.controller = tk.LabelFrame(self.window,
                                        text="controls",
                                        width=cntrl_width,
                                        height=screensize_x)
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)

    def mainloop(self)
    
    ## main render function
    def update_gamescreen(self):

    ## control methods
    def init_deal_heal(self):

    def init_move_panel(self):

    def draw_circle_on_click(self, event):

    def update_players(self):

    def ent_mgmt_panel(self):

    ## info gathering methods
    def update_targetting(self):

    def determine_grid_pos(self):

    def determine_pixel_pos(self):
