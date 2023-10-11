import tkinter as tk


class attack:
    def __init__(self, name="", att_range=5, damage="", aoe=5, active_ent=None):
        self.parent_window = None
        self.name = name
        self.att_range = att_range
        self.aoe = aoe
        self.damage = damage
        self.active_ent = active_ent

    # setter funcs
    def set_att_name(self, new_name=""):
        self.name = new_name

    def set_att_range(self, new_range=5):
        self.att_range = new_range

    def set_att_damage(self, new_damage=""):
        self.damage = new_damage

    def set_att_aoe(self, new_aoe=""):
        self.aoe = new_aoe

    def set_active_ent(self, new_ent):
        self.active_ent = new_ent

    def set_current_attack(self):
        self.active_ent.set_current_attack(self)
        self.active_ent.raise_chose_action_flag()
        self.parent_window.destroy()
    
    def set_parent_window(self, window: tk.Tk):
        self.parent_window = window

    # getter funcs
    def get_att_name(self):
        return self.name

    def get_att_range(self):
        return self.att_range

    def get_att_damage(self):
        return self.damage

    def get_att_aoe(self):
        return self.aoe

    def get_tk_button(self, frame: tk.Frame, button_command: str):
        return (tk.Button(frame, command=button_command, text=self.get_att_name()))

    def get_self(self):
        return self



class controllable_entity:
    def __init__(self, name="", HP=0, AC=0, grid_x=0, grid_y=0, role="player", index=-1, targetted=False):
        self.name = name
        self.HP = HP
        self.AC = AC
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.role = role
        self.index = index
        self.targetted = targetted
        self.id = ""
        self.move_speed = -1
        self.attacks = []
        self.current_attack = None
        self.fl_has_chosen_action = False

    # setter funcs
    def add_health(self, change):
        self.HP = self.HP + change

    def rem_health(self, change):
        self.HP = self.HP - change

    def set_name(self, new_name):
        self.name = new_name

    def set_x(self, new_x):
        self.grid_x = new_x

    def set_y(self, new_y):
        self.grid_y = new_y

    def set_index(self,  new_index):
        self.index = new_index

    def set_HP(self, new_hp):
        self.HP = new_hp

    def set_AC(self, new_ac):
        self.AC = new_ac

    def set_role(self, new_role):
        self.role = new_role

    def set_id(self):
        self.id = str(self.get_index()) + ":" + str(self.get_name())

    def set_move_speed(self, new_speed: int):
        self.move_speed = new_speed

    def set_current_attack(self, attack: attack):
        self.current_attack = attack

    def add_attack(self, new_attack: attack):
        self.attacks.append(new_attack)

    def raise_chose_action_flag(self):
        self.fl_has_chosen_action = True

    def lower_chose_action_flag(self):
        self.fl_has_chosen_action = False

    def raise_targetted_flag(self):
        self.targetted = True

    def lower_targetted_flag(self):
        self.targetted = False

    # getter funcs
    def get_name(self):
        return self.name

    def get_HP(self):
        return self.HP

    def get_AC(self):
        return self.AC

    def get_grid_x(self):
        return self.grid_x

    def get_grid_y(self):
        return self.grid_y

    def get_role(self):
        return self.role

    def get_index(self):
        return self.index

    def get_targetted(self):
        return self.targetted

    def get_id(self):
        return self.id

    def get_move_speed(self):
        return self.move_speed

    def get_attacks(self):
        return self.attacks

    def get_attack_by_name(self, name: str):
        for i in self.get_attacks():
            if name == i.get_att_name():
                return i
            else:
                return None

    def get_curr_atk(self):
        return self.current_attack

    def get_chose_action_flag(self):
        return self.fl_has_chosen_action


class control_scheme:
    def __init__(self, entities: list, map_size: int):
        self.entities = entities
        self.map_size = map_size
        self.update_ents()

    def update_ents(self):
        for i in range(len(self.entities)):
            self.entities[i].set_index(i)
            self.entities[i].set_id()

    def add_entity(self, entity_to_add: controllable_entity()):
        self.entities.append(entity_to_add)

    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove

    def ent_list(self):
        local_list = []
        for i in self.entities:
            local_list.append(i.get_id())

        return local_list

    def get_ent_by_name(self, name: str):
        for i in self.entities:
            if name == i.get_name():
                return i
        return None
