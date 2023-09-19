import DMControls as dm
import tkinter as tk
from tkinter import ttk

class DungeonMap():

    def __init__(self, control: dm.control_scheme):
        self.window = tk.Tk()
        self.window.title = "Dungeons & Dragons"
        try: 
            self.window.attributes("-zoomed", True)
        except:
            self.window.state('zoomed')

        self.control = control
        self.controller = tk.LabelFrame(self.window,
                                        text="controls",
                                        width=200,
                                        height=self.get_screen_size()[1])
        self.controller.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.screensize = self.get_screen_size()

        # GUI items
        self.mv_frame = tk.LabelFrame()
        self.mh_frame = tk.LabelFrame()

        # object bound variables
        self.combat_mode = False
        self.ent_to_act = dm.controllable_entity()
        self.next_ent_index = 0
        self.selected_entity = dm.controllable_entity()
        self.move_order = [self.selected_entity]
        self.square_size = (self.get_screen_size()[0]) / self.control.map_size
        self.mh_radius = tk.IntVar(value=0)
        self.mv_ent_to_move = tk.StringVar(value="")
        self.fl_move_ent = False
        self.fl_draw_target = False

        self.map = tk.Canvas(self.window,
                             width=(self.get_screen_size()[0]),
                             height=self.get_screen_size()[1])
        self.map.pack(side=tk.LEFT)
        self.map.bind('<Button-1>',
                      self.click,
                      add="+")
        self.window.bind('<space>',
                      self.next_turn,
                      add="+")

    def mainloop(self):
        # self.draw_entity_select()
        self.draw_start_combat_button()
        self.draw_next_turn_button()
        self.draw_attack_controls()
        self.draw_move_controls()
        self.window.mainloop()

    # main render functions
    def update_gamescreen(self):
        # create horizontal lines
        for i in range(self.control.map_size):
            self.map.create_line(0, (i * self.square_size),
                                 self.screensize[0], (i * self.square_size))
        # create vertical lines
        for i in range(self.control.map_size):
            self.map.create_line((i * self.square_size),
                                 0,
                                 (i * self.square_size),
                                 self.screensize[1])
        self.update_players()

    def update_players(self):
        l_font = ('sans serif', int(self.square_size / 4), "bold")

        self.map.delete("entity")
        for i in self.control.entities:
            l_pos = self.determine_pixel_pos(int(i.get_grid_x()), int(i.get_grid_y()))
            shift_to_center = int(self.square_size / 2)

            # draw colored circles, might switch the role property to be color instead
            # shouldve done that from the start
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
            # draw outlines, if targetted outline is orange
            if (i.get_targetted() is True):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=3,
                                     outline="orange",
                                     tags="entity")
            elif (i.get_targetted() is False):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=3,
                                     tags="entity")
            self.map.create_text(l_pos[0], l_pos[1], text=(i.get_index()), fill="white", tags="entity", font=l_font)

    def start_combat(self):
        # get initiative list
        self.move_order = self.control.entities
        self.next_turn

    def next_turn(self, event=""):
        self.ent_to_act = self.move_order[self.next_ent_index]
        print(self.ent_to_act.get_name())

        # increment/loop next entity index
        if (self.next_ent_index == len(self.move_order) - 1):
            self.next_ent_index = 0
        else:
            self.next_ent_index += 1

    # display methods
    def draw_start_combat_button(self):
        start_combat_b = tk.Button(self.controller, text="Start Combat", command=self.start_combat)
        start_combat_b.grid(row=0, column=0)

    def draw_next_turn_button(self):
        next_turn_b = tk.Button(self.controller, text="Next Turn", command=self.next_turn)
        next_turn_b.grid(row=9, column=0)

    def draw_attack_controls(self):
        attack_controls_frame = tk.LabelFrame(self.controller, text="Attack")
        attack_controls_frame.grid(row=2, column=0)

        attack_button = tk.Button(attack_controls_frame, text="Attack!", command=lambda: self.raise_draw_target_flag(), width=18)
        attack_button.grid()

        att_range = ttk.Entry(attack_controls_frame, textvariable=self.mh_radius)
        att_range.grid(row=1, column=0)

    def draw_move_controls(self):
        move_controls_frame = tk.LabelFrame(self.controller, text="Movement")
        move_controls_frame.grid(row=1, column=0)

        move_button = tk.Button(move_controls_frame, text="Move",
                                command=lambda: self.raise_move_flag(self.control.entities[self.get_index_from_id()]
                                                                     ), width=18)
        move_button.grid()

    # control methods
    def click(self, event):
        print(str(event))
        self.map.delete("target")
        #cur_ent = self.control.entities[self.get_index_from_id()]
        cur_ent = self.selected_entity
        event_grid = self.determine_grid_pos(event.x, event.y)

        if (self.fl_move_ent is True):
            if (self.ent_in_radius(cur_ent, int(cur_ent.get_move_speed() / 5)  + 0.5, [event.x, event.y])):
                new_pos = self.determine_grid_pos(event.x, event.y)
                cur_ent.set_x(new_pos[0])
                cur_ent.set_y(new_pos[1])
                self.fl_move_ent = False
                self.map.delete("range")

        elif (self.fl_draw_target is True):
            self.draw_target = False
            self.map.delete("range")
        else:
            for i in self.control.entities:
                if (event_grid[1] == i.get_grid_y()):
                    print("y is right")
                    if (event_grid[0] == i.get_grid_x()):
                        print(str(i.get_name()) + " selected")
                        self.selected_entity = i
                        self.raise_move_flag(self.selected_entity)

            if self.fl_move_ent is True:
                self.show_range(self.selected_entity, self.selected_entity.get_move_speed(), "#a8ffa8")

        self.update_gamescreen()
        print("post-click")

    def move_entity(self, cur_ent: dm.controllable_entity):
        # cur_ent.set_x(new_pos[0])
        # cur_ent.set_y(new_pos[1])
        # self.update_players()
        # print("move ent")
        self.show_range(cur_ent, cur_ent.get_move_speed(), "#a8ffa8")


#   def ent_mgmt_panel(self):

    # info gathering methods
    def determine_grid_pos(self, x: int, y: int) -> list[int,int]:
        return [int(x / self.square_size), int(y / self.square_size)]

    def determine_pixel_pos(self, x: int, y: int) -> list[int, int]:
        # not thoroughly tested
        return[int((x * self.square_size) + (self.square_size / 2)), int((y * self.square_size) + (self.square_size / 2))]

    def get_screen_size(self):
        return [self.window.winfo_screenwidth(), self.window.winfo_screenheight()]

    def raise_draw_target_flag(self):
        self.fl_draw_target = True
        #cur_ent = self.control.entities[self.get_index_from_id()]
        #self.show_range(cur_ent, self.mh_radius.get(), "#f6bf51")

    def raise_move_flag(self, cur_ent: dm.controllable_entity):
        self.fl_move_ent = True
        # cur_ent = self.control.entities[self.get_index_from_id()]
        # self.show_range(cur_ent, cur_ent.get_move_speed(), "#a8ffa8")

    def get_index_from_id(self) -> int:
        index = (self.mv_ent_to_move.get())[0:1]
        #print("--" + str(index))
        return int(index)

    # player interactive methods
    def show_range(self, cur_ent: dm.controllable_entity, radius: float, color: str):
        self.map.delete("range")
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
        print("show range")

    def ent_in_radius(self, cur_ent: dm.controllable_entity, radius: float, center: list[int,int]) -> bool:
        ent_pos = self.determine_pixel_pos(cur_ent.get_grid_x(), cur_ent.get_grid_y())
        if (((ent_pos[0] - center[0]) ** 2) + ((ent_pos[1] - center[1]) ** 2) <= (radius * self.square_size) ** 2):
            return True
        else:
            return False



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
#test.update_players()
print("init screen drawn")
test.mainloop()
