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

    # setter funcs

    def add_health(self, change):
        self.HP = self.HP + change

    def rem_health(self, change):
        self.HP = self.HP - change

    def set_x(self, new_x):
        self.grid_x = new_x

    def set_y(self, new_y):
        self.grid_y = new_y

    def set_index(self,  new_index):
        self.index = new_index

    def set_ac(self, new_ac):
        self.AC = new_ac

    def set_id(self):
        self.id = str(self.get_index()) + ":" + str(self.get_name())

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
        self.entities += entity_to_add

    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove
    
    def ent_list(self):
        local_list = []
        for i in self.entities:
            local_list.append(i.get_id())

        return local_list
