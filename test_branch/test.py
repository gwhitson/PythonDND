import DMControls as dm
import os
import tkinter as tk
from tkinter import ttk
# from PIL import Image, ImageTk


class DungeonMap():
    def __init__(self, control: dm.control_scheme):
        self.window = tk.Tk()
        self.window.title = "Dungeons & Dragons"
        self.control = control
        self.controller = tk.LabelFrame(self.window,
                                        text="controls",
                                        width=200,
                                        height=self.get_screen_size()[1])
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)
        if (os.name == "nt"):
            self.os = "win"
            self.res_location = os.getcwd() + "\\resources"
            self.window.state('zoomed')
        else:
            self.os = "lin"
            self.res_location = os.getcwd() + "/resources"
            self.window.attributes("-zoomed", True)

        # GUI items
        # self.sprite = None
        # self.img = None
        self.ent_select = None
        self.edit_frame = None
        self.att_frame = None
        self.new_att_frame = None
        self.ent_sel_button_frame = None
        self.sc_frame = tk.LabelFrame(self.controller, text="")
        self.selected_ent = tk.StringVar()
        self.new_ent_name = tk.StringVar(value="")
        self.new_ent_HP = tk.IntVar(value=0)
        self.new_ent_AC = tk.IntVar(value=0)
        self.new_ent_x = tk.IntVar(value=0)
        self.new_ent_y = tk.IntVar(value=0)
        self.new_ent_role = tk.StringVar(value="")
        self.new_ent_movespd = tk.IntVar(value=0)
        self.cmbt_turn_frame = tk.Frame(self.controller)
        self.att_sel = None
        self.background_color = 'grey'
        self.text_color = 'white'
        self.ent_mgmt = None

        # object bound variables
        self.combat_mode = False
        self.ent_to_act = dm.controllable_entity()
        self.next_ent_index = 0
        self.move_order = [self.control.entities]
        self.square_size = (self.get_screen_size()[0]) / self.control.map_size
        self.mh_radius = tk.IntVar(value=0)
        self.fl_move_ent = False
        self.fl_draw_target = False

        # map element and keybinds
        self.map = tk.Canvas(self.window,
                             width=(self.get_screen_size()[0]),
                             height=(self.get_screen_size()[1]))
        self.map.pack(side=tk.LEFT)
        self.map.bind('<Button-1>',
                      self.click,
                      add="+")
        self.window.bind('<Return>',
                         self.next_turn,
                         add="+")
        self.window.bind('<space>',
                         self.next_turn,
                         add="+")
        self.window.bind('<m>',
                         self.move_entity,
                         add="+")
        self.window.bind('<n>',
                         self.attack_entity,
                         add="+")
        self.window.bind('<p>',
                         self.prev_turn,
                         add="+")

    # main render functions
    def mainloop(self):
        self.test()
        self.set_color_mode('gray', 'white')
        self.draw_start_combat_button()
        self.draw_turn_buttons()
        self.draw_attack_controls()
        self.draw_move_controls()
        self.draw_ent_mgmt_button()
        self.window.mainloop()

    def update_gamescreen(self):
        # create horizontal lines
        for i in range(self.control.map_size):
            self.map.create_line(0,
                                 (i * self.square_size),
                                 (self.get_screen_size())[0],
                                 (i * self.square_size))
        # create vertical lines
        for i in range(self.control.map_size):
            self.map.create_line((i * self.square_size),
                                 0,
                                 (i * self.square_size),
                                 (self.get_screen_size())[1])
        self.update_players()

    # display methods
    def update_players(self):
        l_font = ('sans serif', int(self.square_size / 4), "bold")

        self.map.delete("entity")
        for i in self.control.entities:
            # print(i.get_name() + " -- targetted: " + str(i.get_targetted()))
            l_pos = self.determine_pixel_pos(int(i.get_grid_x()),
                                             int(i.get_grid_y()))
            shift_to_center = int(self.square_size / 2)

            # draw colored circles, might switch the role property to be color
            # instead shouldve done that from the start
            if (i.get_role() == "player"):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     fill="blue",
                                     tags="entity")
            elif (i.get_role() == "enemy"):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     fill="red",
                                     tags="entity")

            # testing sprites
            # if (i.get_name() == "goblin"):
            #    if self.os == "win":
            #         self.sprite = ImageTk.PhotoImage(Image.open(self.res_location + "\\goblin.png"))
            #         self.img = Image.open("resources\\goblin.png")
            #         self.img = self.img.resize((int(self.square_size), int(self.square_size)))
            #         self.sprite = ImageTk.PhotoImage(self.img)

            #     else:
            #         #sprite = ImageTk.PhotoImage(Image.open(self.res_location + "/goblin.png"))
            #         #self.sprite = tk.PhotoImage(file="resources/goblin.png")
            #         self.img = Image.open("resources/goblin.png")
            #         self.img = self.img.resize((int(self.square_size), int(self.square_size)), Image.ANTIALIAS)
            #         self.sprite = ImageTk.PhotoImage(self.img)
            #     print(str(l_pos))
            #     self.map.create_image(l_pos, anchor=tk.CENTER, image=self.sprite, tags="entity")

            # draw outlines, if targetted outline is orange
            self.map.create_oval(l_pos[0] - shift_to_center,
                                 l_pos[1] - shift_to_center,
                                 l_pos[0] + shift_to_center,
                                 l_pos[1] + shift_to_center,
                                 width=3,
                                 tags="entity")
            self.map.create_text(l_pos[0], l_pos[1], text=(i.get_index()),
                                 fill="white", tags="entity", font=l_font)
            if (i.get_targetted() is True):
                self.map.create_line(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=8,
                                     fill='black',
                                     tags="entity")
                self.map.create_line(l_pos[0] + shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] - shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=8,
                                     fill='black',
                                     tags="entity")
                self.map.create_line(l_pos[0] - (shift_to_center - 2),
                                     l_pos[1] - (shift_to_center - 2),
                                     l_pos[0] + (shift_to_center - 2),
                                     l_pos[1] + (shift_to_center - 2),
                                     width=3,
                                     fill='red',
                                     tags="entity")
                self.map.create_line(l_pos[0] + (shift_to_center - 2),
                                     l_pos[1] - (shift_to_center - 2),
                                     l_pos[0] - (shift_to_center - 2),
                                     l_pos[1] + (shift_to_center - 2),
                                     width=3,
                                     fill='red',
                                     tags="entity")

        if self.combat_mode is True:
            l_pos = self.determine_pixel_pos(int(self.ent_to_act.get_grid_x()),
                                             int(self.ent_to_act.get_grid_y()))
            self.map.create_oval(l_pos[0] - shift_to_center,
                                 l_pos[1] - shift_to_center,
                                 l_pos[0] + shift_to_center,
                                 l_pos[1] + shift_to_center,
                                 width=3,
                                 outline="orange",
                                 tags="entity")

    def draw_start_combat_button(self):
        start_combat_b = tk.Button(self.sc_frame, text="Start Combat",
                                   command=self.start_combat,
                                   bg=self.background_color, fg=self.text_color
                                   )
        self.sc_frame.grid(row=0, column=0)
        start_combat_b.grid(row=0, column=0)

    def draw_turn_buttons(self):
        next_turn_b = tk.Button(self.cmbt_turn_frame, text="Next Turn",
                                command=self.next_turn,
                                bg=self.background_color, fg=self.text_color)
        next_turn_b.grid(row=0, column=1)
        prev_turn_b = tk.Button(self.cmbt_turn_frame, text="Prev Turn",
                                command=self.prev_turn,
                                bg=self.background_color, fg=self.text_color)
        prev_turn_b.grid(row=0, column=0)

    def draw_attack_controls(self):
        attack_controls_frame = tk.LabelFrame(self.controller, text="Attack",
                                              bg=self.background_color,
                                              fg=self.text_color)
        attack_controls_frame.grid(row=2, column=0)
        attack_button = tk.Button(attack_controls_frame, text="Attack!",
                                  command=self.attack_entity, width=18,
                                  bg=self.background_color, fg=self.text_color)
        attack_button.grid()

    def draw_move_controls(self):
        move_controls_frame = tk.LabelFrame(self.controller, text="Movement",
                                            bg=self.background_color,
                                            fg=self.text_color)
        move_controls_frame.grid(row=1, column=0)
        move_button = tk.Button(move_controls_frame, text="Move",
                                command=self.move_entity, width=18,
                                bg=self.background_color, fg=self.text_color)
        move_button.grid()

    def draw_attack_select_window(self, cur_ent: dm.controllable_entity):
        print("att_sel")
        print(cur_ent.get_attacks())
        self.att_sel = tk.Menu(tearoff=0,
                               bg=self.background_color, fg=self.text_color)
        pos = self.determine_pixel_pos(cur_ent.get_grid_x(),
                                       cur_ent.get_grid_y() + 1)
        for i in cur_ent.get_attacks():
            i.set_parent_window(self.att_sel)
            i.set_active_ent(cur_ent)
            self.att_sel.add_command(label=i.get_att_name(),
                                     command=i.set_current_attack)
        self.att_sel.tk_popup(pos[0], pos[1])

    def draw_ent_mgmt_button(self):
        ent_mgmt_button_frame = tk.Frame(self.controller)
        ent_mgmt_button_frame.grid(row=9, column=0)
        ent_mgmt_button = tk.Button(ent_mgmt_button_frame,
                                    text="Manage Entities",
                                    width=18,
                                    command=self.draw_entity_management,
                                    bg=self.background_color,
                                    fg=self.text_color)
        ent_mgmt_button.pack()

    def draw_entity_management(self):
        values_list = []
        for i in self.control.entities:
            values_list.append(i.get_name())
        self.ent_mgmt = tk.Tk()
        self.ent_sel_button_frame = tk.Frame(self.ent_mgmt, bg=self.background_color)
        self.ent_select = ttk.Combobox(self.ent_sel_button_frame, width=27)
        self.ent_select['values'] = values_list
        self.ent_select.current(0)
        self.ent_select.grid(row=0, column=0, columnspan=2)

        new_ent_button = tk.Button(self.ent_sel_button_frame, text="New Entity", command=self.add_ent, width=13,
                                    bg=self.background_color,
                                    fg=self.text_color)
        new_ent_button.grid(row=1, column=0)

        mod_ent_button = tk.Button(self.ent_sel_button_frame, text="Modify Selected", command=self.draw_ent_update, width=13,
                                    bg=self.background_color,
                                    fg=self.text_color)
        mod_ent_button.grid(row=1, column=1)

        self.ent_sel_button_frame.grid(row=0, column=0)
        self.ent_mgmt.mainloop()

    def draw_add_attack(self):
        try:
            self.edit_frame.destroy()
        except (tk._tkinter.TclError, AttributeError):
            print("called outside of ent_management")
        self.new_att_frame = tk.Frame(self.ent_mgmt, bg=self.background_color)
        self.new_att_frame.grid(row=7, column=0, columnspan=2)
        # name, range, damage, aoe
        name = tk.Label(self.new_att_frame, text="name:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        name.grid(row=0, column=0)
        name = tk.Entry(self.new_att_frame, width=18)
        name.grid(row=0, column=1)
        att_range = tk.Label(self.new_att_frame, text="att_range:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        att_range.grid(row=1, column=0)
        att_range = tk.Entry(self.new_att_frame, width=18)
        att_range.grid(row=1, column=1)
        damage = tk.Label(self.new_att_frame, text="damage:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        damage.grid(row=2, column=0)
        damage = tk.Entry(self.new_att_frame, width=18)
        damage.grid(row=2, column=1)
        aoe = tk.Label(self.new_att_frame, text="aoe:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        aoe.grid(row=3, column=0)
        aoe = tk.Entry(self.new_att_frame, width=18)
        aoe.grid(row=3, column=1)

        (tk.Button(self.new_att_frame, text='Add Attack', width=27,
                   command=lambda:self.add_attack(dm.attack(name=name.get(), att_range=att_range.get(), damage=damage.get(), aoe=aoe.get())),
                   bg=self.background_color, fg=self.text_color)).grid(row=4, columnspan=2)

    def refresh_ent_mgmt(self, event=None):
        try:
            self.edit_frame.destroy()
        except (tk._tkinter.TclError, AttributeError):
            None
        self.draw_ent_update()

    def draw_ent_update(self):
        self.ent_sel_button_frame.grid_remove()
        ent = self.control.get_ent_by_name(self.ent_select.get())
        self.new_ent_name.set(ent.get_name())
        self.new_ent_HP.set(ent.get_HP())
        self.new_ent_AC.set(ent.get_AC())
        self.new_ent_x.set(ent.get_grid_x())
        self.new_ent_y.set(ent.get_grid_y())
        self.new_ent_role.set(ent.get_role())
        self.new_ent_movespd.set(ent.get_move_speed())

        self.edit_frame = tk.Frame(self.ent_mgmt,
                                   bg=self.background_color)
        self.edit_frame.grid(row=1, column=0)

        edit_name = tk.Label(self.edit_frame, text="Name:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_name.grid(row=0, column=0)
        edit_name = tk.Entry(self.edit_frame, textvariable=self.new_ent_name, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_name.delete(0, len(edit_name.get()))
        edit_name.insert(0, self.ent_select.get())
        edit_name.grid(row=0, column=1)

        edit_HP = tk.Label(self.edit_frame, text="HP:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_HP.grid(row=1, column=0)
        edit_HP = tk.Entry(self.edit_frame, textvariable=self.new_ent_HP, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_HP.delete(0, len(edit_HP.get()))
        edit_HP.insert(0, self.new_ent_HP.get())
        edit_HP.grid(row=1, column=1)

        edit_movespd = tk.Label(self.edit_frame, text="Move Speed:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_movespd.grid(row=2, column=0)
        edit_movespd = tk.Entry(self.edit_frame, textvariable=self.new_ent_movespd, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_movespd.delete(0, len(edit_movespd.get()))
        edit_movespd.insert(0, self.new_ent_movespd.get())
        edit_movespd.grid(row=2, column=1)

        edit_AC = tk.Label(self.edit_frame, text="AC:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_AC.grid(row=3, column=0)
        edit_AC = tk.Entry(self.edit_frame, textvariable=self.new_ent_AC, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_AC.delete(0, len(edit_AC.get()))
        edit_AC.insert(0, self.new_ent_AC.get())
        edit_AC.grid(row=3, column=1)

        edit_x = tk.Label(self.edit_frame, text="x:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_x.grid(row=4, column=0)
        edit_x = tk.Entry(self.edit_frame, textvariable=self.new_ent_x, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_x.delete(0, len(edit_x.get()))
        edit_x.insert(0, self.new_ent_x.get())
        edit_x.grid(row=4, column=1)

        edit_y = tk.Label(self.edit_frame, text="y:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_y.grid(row=5, column=0)
        edit_y = tk.Entry(self.edit_frame, textvariable=self.new_ent_y, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_y.delete(0, len(edit_y.get()))
        edit_y.insert(0, self.new_ent_y.get())
        edit_y.grid(row=5, column=1)

        edit_role = tk.Label(self.edit_frame, text="Role:", width=9,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_role.grid(row=6, column=0)
        edit_role = tk.Entry(self.edit_frame, textvariable=self.new_ent_role, width=18,
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_role.delete(0, len(edit_role.get()))
        edit_role.insert(0, self.new_ent_role.get())
        edit_role.grid(row=6, column=1)

        try:
            self.att_frame.destroy()
        except (tk._tkinter.TclError, AttributeError):
            None
        ent = self.control.get_ent_by_name(self.ent_select.get())
        count1 = 0
        count2 = 0
        self.att_frame = tk.Frame(self.edit_frame, bg=self.background_color)
        self.att_frame.grid(row=7, column=0, columnspan=2)
        have_frame = tk.LabelFrame(self.att_frame, text="Current", width="13",
                                    bg=self.background_color,
                                    fg=self.text_color)
        have_frame.grid(row=0, column=0, sticky="nsew")
        avail_frame = tk.LabelFrame(self.att_frame, text="Available", width="13",
                                    bg=self.background_color,
                                    fg=self.text_color)
        avail_frame.grid(row=0, column=1, sticky="nsew")

        for i in self.control.get_attacks():
            i.set_active_ent(ent)
            i.window_refresh_func(self.refresh_ent_mgmt)
            if i in ent.get_attacks():
                temp = tk.Button(have_frame, text=i.get_att_name(), command=i.remove_attack_on_active_ent,
                                    bg=self.background_color,
                                    fg=self.text_color,
                                    width=13)
                temp.grid(row=count1, column=0)
                count1 += 1
            else:
                temp = tk.Button(avail_frame, text=i.get_att_name(), command=i.add_attack_on_active_ent,
                                    bg=self.background_color,
                                    fg=self.text_color,
                                    width=13)
                temp.grid(row=count2, column=0)
                count2 += 1
        if (count1 == 0):
            (tk.Button(have_frame, text="None", bg=self.background_color, fg=self.text_color, width=13)).grid(row=count1, column=0)
        if (count2 == 0):
            (tk.Button(avail_frame, text="None", bg=self.background_color, fg=self.text_color, width=13)).grid(row=count2, column=0)

        add_attack_button = tk.Button(self.att_frame, text="Add Attack", width="27", command=self.draw_add_attack,
                                    bg=self.background_color,
                                    fg=self.text_color)
        add_attack_button.grid(row=1, column=0, columnspan=2)
       # edit_attacks = tk.Button(self.edit_frame, text="Change Attacks", width=27, command= self.draw_attack_mgmt,
       #                             bg=self.background_color,
       #                             fg=self.text_color)
       # edit_attacks.grid(row=8, column=0, columnspan=2)

        edit_ent_button = tk.Button(self.edit_frame, text="Save", width=27, command=lambda: self.update_ent(ent.get_index(), edit_name.get(), edit_HP.get(), edit_AC.get(), edit_x.get(), edit_y.get(), edit_role.get(), edit_movespd.get()),
                                    bg=self.background_color,
                                    fg=self.text_color)
        edit_ent_button.grid(row=9, column=0, columnspan=2)

        try:
            self.att_frame.update()
        except (tk._tkinter.TclError, AttributeError):
            None

    # control methods
    def attack_entity(self, event=None):
        if (self.combat_mode is True):
            self.clear_status()
            self.clear_targets()
            self.draw_attack_select_window(self.ent_to_act)
            self.att_sel.wait_window()
            self.continue_attack()
        else:
            None
            print("fail in attack entity")

    def continue_attack(self, event=None):
        try:
            # print(self.ent_to_act.current_attack.get_att_name())
            self.show_range(self.ent_to_act,
                            self.ent_to_act.get_curr_atk().get_att_range(),
                            "#db0000")
            self.raise_draw_target_flag()
        except AttributeError:
            None
            print("fail in continue attack")

    def move_entity(self, event=None):
        self.clear_status()
        self.clear_targets()
        self.show_range(self.ent_to_act, self.ent_to_act.get_move_speed(), "#87d987")
        self.raise_move_flag()

    def select_target(self, event=None):
        # print("select target")
        attack = self.ent_to_act.get_curr_atk()
        if attack.get_att_aoe() == 0:
            ent = self.ent_in_square([event.x, event.y])
            if ent is not None:
                ent.raise_targetted_flag()
        else:
            for i in self.list_ents_in_radius(attack.get_att_aoe(), [event.x, event.y]):
                i.raise_targetted_flag()
            self.map.create_oval(event.x - (self.ent_to_act.get_curr_atk().get_att_aoe() * self.square_size),
                                 event.y - (self.ent_to_act.get_curr_atk().get_att_aoe() * self.square_size),
                                 event.x + (self.ent_to_act.get_curr_atk().get_att_aoe() * self.square_size),
                                 event.y + (self.ent_to_act.get_curr_atk().get_att_aoe() * self.square_size),
                                 outline='#db0000', width=3,
                                 fill='#db0000', stipple='gray50',
                                 tags="aoe")
        self.draw_target = False
        self.map.delete("range")
        self.clear_status()

    def start_combat(self):
        # get initiative list
        self.combat_mode = True
        self.move_order = self.control.entities
        self.ent_to_act = self.move_order[0]
        self.next_turn()
        self.sc_frame.grid_remove()
        self.cmbt_turn_frame.grid(row=8, column=0)

    def next_turn(self, event=None):
        self.clear_status()
        self.clear_targets()
        self.ent_to_act = self.move_order[self.next_ent_index]
        self.ent_to_act.lower_chose_action_flag()
        if (self.next_ent_index == len(self.move_order) - 1):
            self.next_ent_index = 0
        else:
            self.next_ent_index += 1
        self.update_gamescreen()

    def prev_turn(self, event=None):
        self.clear_status()
        self.clear_targets()
        self.ent_to_act = self.move_order[self.next_ent_index - 1]
        self.ent_to_act.lower_chose_action_flag()
        if (self.next_ent_index == 0):
            self.next_ent_index = (len(self.move_order) - 1)
        else:
            self.next_ent_index -= 1
        self.update_gamescreen()

    def get_screen_size(self):
        return [self.window.winfo_screenwidth(), self.window.winfo_screenheight()]

    def raise_draw_target_flag(self):
        self.fl_draw_target = True

    def raise_move_flag(self):
        self.fl_move_ent = True

    def clear_targets(self):
        try:
            self.map.delete("aoe")
        except tk._tkinter.TclError:
            None

        for i in self.control.entities:
            i.lower_targetted_flag()

    def clear_status(self):
        self.fl_move_ent = False
        self.fl_draw_target = False

        try:
            self.map.delete("range")
        except tk._tkinter.TclError:
            None

    def deal_attack(self):
        self.map.delete("aoe")
        for i in self.control.entities:
            i.lower_targetted_flag()

    def add_attack(self, attack: dm.attack):
        self.control.add_attack(attack)
        self.refresh_ent_mgmt()
        self.new_att_frame.destroy()

    def add_ent(self):
        new_ent = dm.controllable_entity(name="new entity")
        new_ent.set_index(len(self.control.entities))
        self.control.add_entity(new_ent)
        self.ent_select['values'] += (new_ent.get_name(),)
        self.ent_select.current(len(self.ent_select['values']) - 1)
        self.draw_ent_update()

    def update_ent(self, index: int, name: str, HP: int, AC: int, x: int, y: int, role: str, movespd: int):
        ent_ind = self.control.get_ent_by_name(self.ent_select.get()).get_index()
        # print(str(ent_ind))
        self.control.entities[index].set_name(str(name))
        self.control.entities[index].set_HP(int(HP))
        self.control.entities[index].set_AC(int(AC))
        self.control.entities[index].set_x(int(x))
        self.control.entities[index].set_y(int(y))
        self.control.entities[index].set_role(str(role))
        self.control.entities[index].set_move_speed(int(movespd))
        self.ent_mgmt.destroy()
        self.update_gamescreen()

    # info gathering methods
    def determine_grid_pos(self, x: int, y: int) -> list[int,int]:
        return [int(x / self.square_size), int(y / self.square_size)]

    def determine_pixel_pos(self, x: int, y: int) -> list[int, int]:
        return [int((x * self.square_size) + (self.square_size / 2)), int((y * self.square_size) + (self.square_size / 2))]

    def ent_in_square(self, pos: list[int, int]):
        l_pos = self.determine_grid_pos(pos[0], pos[1])
        # print("ent in square--" + str(l_pos[0]) + "," + str(l_pos[1]))
        for i in self.control.entities:
            # print(i.get_name() + "--" + str(i.get_grid_y()) + "--" + str(i.get_grid_x()))
            if (int(i.get_grid_x()) == l_pos[0]):
                if (int(i.get_grid_y()) == l_pos[1]):
                    return i
            # print("    x: " + str(int(i.get_grid_x())==l_pos[0]) + " y: " + str(int(i.get_grid_y())==l_pos[1]))
        return None

    # player interactive methods
    def click(self, event):
        # print("click" + str(event))
        self.map.delete("target")
        cur_ent = self.ent_to_act
        event_grid = self.determine_grid_pos(event.x, event.y)

        if (self.fl_move_ent is True):
            if (self.ent_in_radius(cur_ent, int(cur_ent.get_move_speed() / 5) + 0.5, [event.x, event.y])):
                new_pos = self.determine_grid_pos(event.x, event.y)
                cur_ent.set_x(new_pos[0])
                cur_ent.set_y(new_pos[1])
                self.fl_move_ent = False
                self.map.delete("range")

        elif (self.fl_draw_target is True):
            self.select_target(event)
        else:
            if (self.combat_mode is False):
                ent = self.ent_in_square([event.x, event.y])
                if ent is not None:
                    # print('testertester')
                    self.ent_to_act = ent
                    self.move_entity()
                else:
                    print("ent is None")
                # self.ent_to_act = self.ent_in_square([event.x, event.y])
                # if (self.ent_to_act is not None):
                #     self.move_entity()
                #     print("test")
            #else:
                #try:
                    # print(self.ent_in_square([event.x, event.y]).get_name())
                #except AttributeError:
                    # print("no ent in click")

        self.update_gamescreen()
        # self.clear_status()
        # print("move-" + str(self.fl_move_ent) + "  -  attk-" + str(self.fl_draw_target))

    def show_range(self, cur_ent: dm.controllable_entity, radius: float, color: str):
        shift = int(self.square_size / 2)
        l_pos = self.determine_pixel_pos(int(cur_ent.get_grid_x()), int(cur_ent.get_grid_y()))
        self.map.create_oval(l_pos[0] - (int((radius / 5) * self.square_size) + shift),
                             l_pos[1] - (int((radius / 5) * self.square_size) + shift),
                             l_pos[0] + (int((radius / 5) * self.square_size) + shift),
                             l_pos[1] + (int((radius / 5) * self.square_size) + shift),
                             width=3,
                             outline=color,
                             fill=color,
                             stipple="gray50",
                             tags="range")
        self.update_gamescreen()
        # print("show range")

    def ent_in_radius(self, cur_ent: dm.controllable_entity, radius: float, center: list[int, int]) -> bool:
        # print("--radius")
        if (radius == 0):
            comparison_rad = 10
        else:
            comparison_rad = (radius * self.square_size)
        ent_pos = self.determine_pixel_pos(cur_ent.get_grid_x(), cur_ent.get_grid_y())
        if (((ent_pos[0] - center[0]) ** 2) + ((ent_pos[1] - center[1]) ** 2) <= comparison_rad ** 2):
            return True
        else:
            return False

    def list_ents_in_radius(self, radius: float, center: list[int, int]):
        # print("-list")
        entities = []
        for i in self.control.entities:
            if self.ent_in_radius(i, radius, center) is True:
                entities.append(i)
        return entities

    def set_color_mode(self, background: str, text: str):
        self.controller.configure(background=background)
        self.map.configure(background=background)

    def test(self):
        att = dm.attack(name="hand crossbow", att_range=40, aoe=0, damage="1d8")
        self.control.add_attack(att)
        att1 = dm.attack(name="slash", att_range=5, aoe=0, damage="1d8")
        self.control.add_attack(att1)
        att1 = dm.attack(name="fireball", att_range=9, aoe=0, damage="1d8")
        self.control.add_attack(att1)
        for i in self.control.entities:
            i.add_attack(self.control.get_attack_by_name("hand crossbow"))
            i.add_attack(self.control.get_attack_by_name("slash"))
        self.control.print_attacks()
        print(self.control.entities[0].get_attacks())
        print("test ran")


#### test code
player1 = dm.controllable_entity(name="player1", HP=5, AC=8, grid_x=1, grid_y=9, role="player")
player2 = dm.controllable_entity(name="player2", HP=5, AC=3, grid_x=2, grid_y=9, role="player")
player3 = dm.controllable_entity(name="player3", HP=5, AC=13, grid_x=3, grid_y=9, role="player")
player4 = dm.controllable_entity(name="player4", HP=5, AC=23, grid_x=4, grid_y=9, role="player")
player5 = dm.controllable_entity(name="player5", HP=5, AC=3, grid_x=5, grid_y=9, role="player")

ents = [player1,player2,player3,player4,player5]

for i in range(5):
    ents.append(dm.controllable_entity(name="goblin", HP=(6 + (i * 2)), AC=9 + (i * 2), grid_x=(5 + i), grid_y=(6 + i), role="enemy"))

for o in ents:
    o.set_move_speed(25)


game = dm.control_scheme(ents, 50)

test = DungeonMap(game)
test.update_gamescreen()
test.mainloop()
test.clear_targets()
