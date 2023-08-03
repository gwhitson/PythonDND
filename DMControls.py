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

    # setter funcs

    def add_health(self, change):
        self.HP = self.HP + change

    def rem_health(self, change):
        self.HP = self.HP - change

    def change_x(self, change):
        self.grid_x += change

    def change_y(self, change):
        self.grid_y += change

    def set_index(self,  new_index):
        self.index = new_index

    def set_ac(self, new_ac):
        self.AC = new_ac

    # getter funcs

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


class control_scheme:
    def __init__(self, entities: list, square_size: int):
        self.entities = entities
        self.square_size = square_size

    def add_entity(self, entity_to_add: controllable_entity()):
        self.entities += entity_to_add

    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove
