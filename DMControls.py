import json
import os

class controllable_entity:
    def __init__(self, name="nul", HP=-1, location_x=0, location_y=0, role="neutral"):
        self.name = name
        self.HP = HP
        self.location_x = location_x
        self.location_y = location_y
        self.role = role
        self.targetted = False
        self.index = 0

    def add_health(self, health_gain):
        self.HP = (self.HP + health_gain)

    def rem_health(self, damage):
        self.HP = (self.HP - damage)

    def move_entity(self, diff_x, diff_y):
        self.location_x = (self.location_x - diff_x)
        self.location_y = (self.location_y - diff_y)

    def get_name(self):
        return self.name

    def set_index(self, id: int):
        self.index = id

    def get_index(self):
        return self.index

    def print(self):
        print("name: " + self.name)
        print("HP:   " + str(self.HP))
        print("role: " + self.role)
        print("xloc: " + str(self.location_x))
        print("yloc: " + str(self.location_y))
        print("targ: " + str(self.targetted))


class control_scheme:
    def __init__(self, entities: list, map_size=1):
        self.entities = entities
        self.map_size = map_size

    def add_entity(self, entity_to_add: controllable_entity()):
        self.entities += entity_to_add

    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove

    def get_name_list(self) -> list:
        lits = []
        for i in self.entities:
            lits.append(i.get_name())
        return lits

    def print(self):
        print(self.map_size)
        for i in self.entities:
            print("----")
            i.print()

   # def update_view(self):
   #     for i in self.entities:
   #         do something

