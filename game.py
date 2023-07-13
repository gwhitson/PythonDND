import DMControls as dm
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
        self.canvas.bind('<Button-1>', self.draw_circle_on_click, add="+")

        self.control = control
        self.controller = tk.LabelFrame(self.window, text="controls",
                                        width=cntrlrsize, height=screensize)
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.square_size = (screensize / self.control.map_size)

        self.targetting = tk.StringVar()
        self.health_change_val = tk.IntVar()
        self.target_radius = tk.IntVar()
        self.move_amount = tk.IntVar()
        self.move_amount.set(1)
        self.move_select = tk.StringVar()
        self.move_select.set("0:" + str(self.control.entities[0].get_name()))

        self.entity_dict = {}

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

        deal_heal_frame = tk.Frame(self.controller)
        deal_heal_frame.grid(row=0, column=0)

        deal_heal_frame.bind('<Button-1>', self.update_targetting_vars(target_radius, targetting, health_change_val), add="+")

        deal_heal_dmgbtn = tk.Button(deal_heal_frame, text="Deal/Heal Damage")
        deal_heal_dmgbtn.grid(row=0, column=0)

        health_change_label = tk.LabelFrame(deal_heal_frame,
                                            text="change in health:")
        health_change_label.grid(row=1, column=0)

        health_change_box = tk.Entry(health_change_label,
                                     textvariable=health_change_val)
        health_change_box.insert(0, "0")
        health_change_box.grid(row=0, column=0)

        dmg_opts_frame = tk.LabelFrame(deal_heal_frame,
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

    def update_targetting_vars(self, target_radius, targetting, health_change_val):
        self.target_radius = target_radius
        self.targetting = targetting
        self.health_change_val = health_change_val
        self.update_players()
        self.draw_move_selector()

    def determine_grid_position(self, pos: list[int, int]):
        pos = numpy.array(pos)
        return (numpy.array(pos // self.square_size, dtype=int))

    def determine_pixel_position(self, pos: list[int, int]):
        position = [(pos[0] * self.square_size) + (0.5 * self.square_size),
                    (pos[1] * self.square_size) + (0.5 * self.square_size)]
        return position

    def set_background_image(self):
        img_set_frame = tk.LabelFrame(self.controller, text="Set Background Image")
        img_set_frame.grid(row=6, column=0)

        img_path_label = tk.Label(img_set_frame, text="Path to Background Image:")
        img_path_label.grid(row=0, column=0)

        set_img_button = tk.Button(img_set_frame, text="Set Background")
        set_img_button.grid(row=1, column=0)

    def draw_circle_on_click(self, event):
        self.canvas.delete("target_circle")
        self.update_players()
        self.draw_move_selector()

        if self.target_radius.get() != 0:
            pixel_position = [event.x, event.y]

            grid_pos = self.determine_grid_position(pixel_position)
            radius_translated = self.target_radius.get() / 2

            x1 = (grid_pos[0] - radius_translated) + 0.5
            x2 = (grid_pos[0] + radius_translated) + 0.5
            y1 = (grid_pos[1] - radius_translated) + 0.5
            y2 = (grid_pos[1] + radius_translated) + 0.5

            x1 = (x1) * self.square_size
            x2 = (x2) * self.square_size
            y1 = (y1) * self.square_size
            y2 = (y2) * self.square_size

            self.canvas.create_oval(x1, y1, x2, y2, width=3, tags="target_circle")

            shift_to_middle = (0.5 * self.square_size)
            for i in self.control.entities:
                pos = self.determine_pixel_position([i.location_x, i.location_y])
                if (((i.location_x - grid_pos[0]) ** 2) + ((i.location_y - grid_pos[1]) ** 2) <= (self.target_radius.get()) ** 2):
                    print(str(i.location_x) + ':' + str(i.location_y))
                    self.canvas.create_oval(pos[0] - shift_to_middle,
                                            pos[1] - shift_to_middle,
                                            pos[0] + shift_to_middle,
                                            pos[1] + shift_to_middle,
                                            fill="red",
                                            tags="target_circle")
                    i.targetted = True
                else:
                    i.targetted = False

                # i.print()
        else:
            print("radius=0")

    def update_players(self):
        shift_to_center = (0.5 * self.square_size)
        for i in range(len(self.control.entities)):
            cur_ent = self.control.entities[i]
            cur_ent.set_index(i)
            pos = self.determine_pixel_position([cur_ent.location_x, cur_ent.location_y])
            dict_string = (str(cur_ent.get_index()) + ":" + str(cur_ent.get_name()))
            self.entity_dict.update({dict_string: i})

            if cur_ent.role == "player":
                self.canvas.create_oval(pos[0] - shift_to_center,
                                        pos[1] - shift_to_center,
                                        pos[0] + shift_to_center,
                                        pos[1] + shift_to_center,
                                        fill="blue",
                                        tags=["entity", dict_string])
                self.canvas.create_text(pos[0], pos[1], text=str(i), fill="white", tags=["entity", dict_string])
            else:
                self.canvas.create_oval(pos[0] - shift_to_center,
                                        pos[1] - shift_to_center,
                                        pos[0] + shift_to_center,
                                        pos[1] + shift_to_center,
                                        fill="green",
                                        tags=["entity", dict_string])
                self.canvas.create_text(pos[0], pos[1], text=str(i), fill="white", tags=["entity", dict_string])

    def init_movement_panel(self):
        movement_panel = tk.LabelFrame(self.controller, text="Movement")
        movement_panel.grid(row=1, column=0)
        # may need to add an ID property to controllable entity object to correctly 
        # differentiate between objects with the same name, trying index for now, it should work ...

        ent_select_box = ttk.Combobox(movement_panel, width=20,
                                      textvariable=self.move_select)

        ent_select_box['values'] = self.control.get_name_list()
        ent_select_box.bind('<<ComboboxSelected>>', self.draw_move_selector)
        ent_select_box.grid(row=0, column=0)

        # make a crossbar with the N, S, E, W buttons and entry box for setting how much to move by
        move_comp_frame = tk.Frame(movement_panel)
        move_comp_frame.grid(row=1, column=0)
        move_north_button = tk.Button(move_comp_frame, text="N", command= lambda : self.move_entity('N', self.move_amount.get()))
        move_north_button.pack(side=tk.TOP)

        move_south_button = tk.Button(move_comp_frame, text="S", command= lambda : self.move_entity('S', self.move_amount.get()))
        move_south_button.pack(side=tk.BOTTOM)

        move_east_button = tk.Button(move_comp_frame, text="E" , command= lambda : self.move_entity('E', self.move_amount.get()))
        move_east_button.pack(side=tk.RIGHT)

        move_west_button = tk.Button(move_comp_frame, text="W" , command= lambda : self.move_entity('W', self.move_amount.get()))
        move_west_button.pack(side=tk.LEFT)

        move_val_entry = tk.Entry(move_comp_frame, textvariable= self.move_amount, width=4)
        move_val_entry.pack()

    def draw_move_selector(self, event=""):
        self.canvas.delete("move_selector")
        shift_to_center = 0.5 * self.square_size
        # print(self.entity_dict)
        # print(str(self.move_select.get()))
        char = self.control.entities[self.entity_dict[self.move_select.get()]]
        # char.print()
        pos = self.determine_pixel_position([char.location_x, char.location_y])
        self.canvas.create_oval(pos[0] - shift_to_center,
                                pos[1] - shift_to_center,
                                pos[0] + shift_to_center,
                                pos[1] + shift_to_center,
                                outline="orange",
                                width=3,
                                tags="move_selector")
        # print(str(self.move_select.get()))
        self.display_sel_char_props()

    def display_sel_char_props(self):
        char = self.control.entities[self.entity_dict[self.move_select.get()]]
        
        char_inf_frame = tk.LabelFrame(self.controller, text="Player Info")
        char_inf_frame.grid(row=4, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        name_string = ('{0: <10}'.format("Name:")) + char.name
        char_name = tk.Label(char_inf_frame, text=name_string)
        char_name.grid(row=0,column=0, sticky=tk.W)

        health_string = ('{0: <11}'.format("Health:")) + str(char.HP)
        char_health = tk.Label(char_inf_frame, text=health_string)
        char_health.grid(row=1,column=0, sticky=tk.W)
        
    def move_entity(self, direction: chr, magnitude: int):
        character = self.control.entities[self.entity_dict[self.move_select.get()]]
        if direction == 'N':
            character.location_y -= self.move_amount.get()
        elif direction == 'S':
            character.location_y += self.move_amount.get()
        elif direction == 'E':
            character.location_x += self.move_amount.get()
        elif direction == 'W':
            character.location_x -= self.move_amount.get()
        else:
            print("should not get here")
        self.canvas.delete("target_circle")
        self.canvas.delete("entity")
        self.update_players()
        self.draw_move_selector()

    def init_ent_mgmt_panel(self):
        frame = tk.LabelFrame(self.controller, text="Entity Management")
        frame.grid(row=3, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

        button1 = tk.Button(frame, text="remove selected entitiy", command= lambda : self.remove_entity(self.entity_dict[self.move_select.get()]))
        button1.grid(row=0, column = 0)
        button2 = tk.Button(frame, text="add entitiy", command= lambda : self.ent_prompt())
        button2.grid(row=1, column = 0)

    def ent_prompt(self):
        prompt = tk.Tk()
        name = tk.StringVar()
        health = tk.IntVar()
        x = tk.IntVar()
        y = tk.IntVar()
        role = tk.StringVar()

        name_label = tk.Label(prompt, text="name")
        name_label.grid(row=0,rowspan=1, column=0)

        health_label = tk.Label(prompt, text="health")
        health_label.grid(row=1,rowspan=1, column=0)

        location_x_label = tk.Label(prompt, text="location_x")
        location_x_label.grid(row=2,rowspan=1, column=0)

        location_y_label = tk.Label(prompt, text="location_y")
        location_y_label.grid(row=3,rowspan=1, column=0)

        role_label = tk.Label(prompt, text="role")
        role_label.grid(row=4,rowspan=1, column=0)

        name_entry = tk.Entry(prompt, textvariable=name)
        name_entry.grid(row=0,rowspan=1, column=1)

        health_entry = tk.Entry(prompt, textvariable=health)
        health_entry.grid(row=1,rowspan=1, column=1)

        location_x_entry = tk.Entry(prompt, textvariable=x)
        location_x_entry.grid(row=2,rowspan=1, column=1)

        location_y_entry = tk.Entry(prompt, textvariable=y)
        location_y_entry.grid(row=3,rowspan=1, column=1)

        role_entry = tk.Entry(prompt, textvariable=role)
        role_entry.grid(row=4,rowspan=1, column=1)

        prompt_button = tk.Button(prompt, text="Add Entity", command= lambda: self.add_entity(name.get(), health.get(), x.get(), y.get(), role.get(), prompt))
        prompt_button.grid(row=5, rowspan=2, column=1)

    def remove_entity(self, identifier: int):
        ent_to_remove = self.control.entities[identifier]
        self.control.entities.remove(ent_to_remove)
        self.canvas.delete("target_circle")
        self.canvas.delete("entity")
        self.update_players()
        self.draw_move_selector()
        self.init_movement_panel()

    def add_entity(self, name, health, x, y, role, inprompt):
        self.control.entities.append(dm.controllable_entity(name, health, x, y, role))
        inprompt.destroy()
        self.canvas.delete("target_circle")
        self.canvas.delete("entity")
        self.update_players()
        self.draw_move_selector()
        self.init_movement_panel()





##### test code
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
test.init_deal_heal()
test.update_players()
test.init_movement_panel()
test.init_ent_mgmt_panel()
test.set_background_image()
test.mainloop()
