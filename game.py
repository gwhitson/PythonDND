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

        self.map = tk.Canvas(self.window,
                             width=(self.get_screen_size()[0]),
                             height=self.get_screen_size()[1])
        self.map.pack(side=tk.LEFT)
        self.map.bind('<Button-1>',
                      self.click,
                         add="+")
        self.square_size = (self.get_screen_size()[0]) / self.control.map_size

        # object bound variables
        self.mh_radius = tk.IntVar(value=0)
        self.mv_ent_to_move = tk.StringVar(value="")
        self.fl_move_ent = False
        self.fl_draw_target = False

    def mainloop(self):
        self.init_mod_health()
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
            if(i.get_role() == "player"):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     fill="blue",
                                     tags="entity")
            elif(i.get_role() == "enemy"):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     fill="red",
                                     tags="entity")
            # draw outlines, if targetted outline is orange
            if(i.get_targetted() == True):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=3,
                                     outline="orange",
                                     tags="entity")
            elif(i.get_targetted() == False):
                self.map.create_oval(l_pos[0] - shift_to_center,
                                     l_pos[1] - shift_to_center,
                                     l_pos[0] + shift_to_center,
                                     l_pos[1] + shift_to_center,
                                     width=3,
                                     tags="entity")
            self.map.create_text(l_pos[0], l_pos[1], text=(i.get_index()), fill="white", tags="entity", font=l_font)

    # display methods
    def init_mod_health(self):
        targetting = tk.IntVar(value=0)
        health_change = tk.IntVar(value=0)

        mh_frame = tk.LabelFrame(self.controller, text="Modify Health")
        mh_frame.grid(row=0, column=0)

        mh_radius_b = tk.Button(mh_frame, text="Draw Radius",
                                command= lambda : self.set_draw_target_flag(), width=10)
        mh_radius_b.grid(row=0, column=1)

        mh_radius_entry = tk.Entry(mh_frame, width=7, textvariable=self.mh_radius)
        mh_radius_entry.grid(row=0, column=0)

        mh_health_change_b = tk.Button(mh_frame, text="Mod Health",
                                       command= lambda : (health_change.set(health_change.get() + 1)), width=10)
        mh_health_change_b.grid(row=1, column=1)

        mh_health_change_entry = tk.Entry(mh_frame, width=7, textvariable=health_change)
        mh_health_change_entry.grid(row=1, column=0)

    def init_move_panel(self):
        dist_to_move = tk.IntVar(value=0)
        
        mv_frame = tk.LabelFrame(self.controller, text="Movement")
        mv_frame.grid(row=1, column=0)
        
        mv_entity_select = ttk.Combobox(mv_frame, width=18, textvariable=self.mv_ent_to_move)
        mv_entity_select['values'] = self.control.ent_list()
        self.mv_ent_to_move.set((mv_entity_select['values'])[0])

        print(self.control.ent_list())
        mv_entity_select.grid(row=0, column=0, columnspan=2)
        
        mv_move_dist_b = tk.Button(mv_frame, text="Move",
                                   command= lambda : self.show_movement_radius(self.control.entities[self.get_index_from_id()]), width=18)
        mv_move_dist_b.grid(row=1, column=0, columnspan=2)
        
    # control methods
    def click(self, event):
        print(str(self.determine_grid_pos(event.x, event.y)))
        self.map.delete("target")

        if (self.fl_move_ent):
            cur_ent = self.control.entities[self.get_index_from_id()]
            if (self.ent_in_radius(cur_ent, cur_ent.get_move_speed(), [event.x, event.y])):
                new_pos = self.determine_grid_pos(event.x, event.y)
                print("moving ent to " + str(new_pos))
                cur_ent.set_x(new_pos[0])
                cur_ent.set_y(new_pos[1])
                self.fl_move_ent = False
                self.map.delete("movement")
            else:
                print("neg test")
#       while (self.fl_move_ent):
#           cur_ent = self.control.entities[self.get_index_from_id()]
#           if (self.ent_in_radius(cur_ent, cur_ent.get_move_speed(), [event.x, event.y])):
#               new_pos = self.determine_grid_pos(event.x, event.y)
#               print("moving ent to " + str(new_pos))
#               cur_ent.set_x(new_pos[0])
#               cur_ent.set_y(new_pos[1])
#               self.fl_move_ent = False
#               self.map.delete("movement")
#           else:
#               print("neg test")


        elif (self.fl_draw_target):
            print("draw target radius of size " + str(self.mh_radius.get()))
            self.show_target_radius(event.x, event.y, self.mh_radius.get())

        self.update_gamescreen()

#   def draw_circle_on_click(self, event) -> list[int, int]:
#       # placeholders
#       print(str(self.determine_grid_pos(event.x, event.y)))
#       test = self.determine_grid_pos(event.x, event.y)
#       print(str(self.determine_pixel_pos(test[0], test[1])))
#       self.update_players()


    def move_entity(self, cur_ent: dm.controllable_entity, new_pos: list[int,int]):
        cur_ent.set_x(new_pos[0])
        cur_ent.set_y(new_pos[1])
        self.update_players()
        self.show_movement_radius(cur_ent)

#   def ent_mgmt_panel(self):

    # info gathering methods
    def determine_grid_pos(self, x: int, y: int) -> list[int,int]:
        return [int(x / self.square_size), int(y / self.square_size)]

    def determine_pixel_pos(self, x: int, y: int) -> list[int,int]:
        # not thoroughly tested
        return[int((x * self.square_size) + (self.square_size / 2)),int((y * self.square_size) + (self.square_size / 2))]

    def get_screen_size(self):
        return [self.window.winfo_screenwidth(), self.window.winfo_screenheight()]
        
    def set_draw_target_flag(self):
        self.fl_draw_target = True

    def get_index_from_id(self) -> int:
        index = (self.mv_ent_to_move.get())[0:1]
        print("--" + str(index))
        return int(index)
    
    # player interactive methods
    def show_movement_radius(self, cur_ent: dm.controllable_entity):
        self.map.delete("movement")
        l_pos = self.determine_pixel_pos(int(cur_ent.get_grid_x()), int(cur_ent.get_grid_y()))
        self.map.create_oval(l_pos[0] - int(cur_ent.get_move_speed() * self.square_size),
                             l_pos[1] - int(cur_ent.get_move_speed() * self.square_size),
                             l_pos[0] + int(cur_ent.get_move_speed() * self.square_size),
                             l_pos[1] + int(cur_ent.get_move_speed() * self.square_size),
                             width=3,
                             outline="green",
                             fill="#caffcc",
                             tags="movement")
        self.fl_move_ent = True
        self.update_gamescreen()

    def show_target_radius(self, x: int, y: int, radius: int):
        self.map.delete("target")
#       l_pos = self.determine_pixel_pos(int(cur_ent.get_grid_x()), int(cur_ent.get_grid_y()))
        self.map.create_oval(x - int(radius * self.square_size),
                             y - int(radius * self.square_size),
                             x + int(radius * self.square_size),
                             y + int(radius * self.square_size),
                             width=3,
                             outline="orange",
                             fill="#ffe08c",
                             tags="target")
        self.fl_move_ent = True
        self.update_gamescreen()

    def ent_in_radius(self, cur_ent: dm.controllable_entity, radius: int, center: list[int,int]) -> bool:
        ent_pos = self.determine_pixel_pos(cur_ent.get_grid_x(),cur_ent.get_grid_y())
#       print("ent:" + str(ent_pos))
#       self.map.create_oval(ent_pos[0], ent_pos[1], ent_pos[0] + self.square_size, ent_pos[1] + self.square_size, fill="blue")
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

game = dm.control_scheme(ents, 0)


test = DungeonMap(game)
test.update_gamescreen()
test.update_players()
test.init_move_panel()
test.mainloop()
