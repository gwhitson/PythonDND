import json
import os

class controllable_entity:
    def __init__(self, name="nul", HP=-1, location_x=0, location_y=0, role="neutral"):
        self.name = name
        self.HP = HP
        self.location_x = location_x
        self.location_y = location_y
        self.role = role

    def add_health(self, health_gain):
        self.HP = (self.HP + health_gain)

    def rem_health(self, damage):
        self.HP = (self.HP - damage)

    def move_entity(self, diff_x, diff_y):
        self.location_x = (self.location_x - diff_x)
        self.location_y = (self.location_y - diff_y)

    def print(self):
        print("name: " + self.name)
        print("HP:   " + str(self.HP))
        print("role: " + self.role)
        print("xloc: " + str(self.location_x))
        print("yloc: " + str(self.location_y))


class control_scheme:
    def __init__(self, entities: list, map_size=1):
        self.entities = entities
        self.map_size = map_size

    def add_entity(self, entity_to_add: controllable_entity()):
        self.entities += entity_to_add

    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove

    def print(self):
        print(self.map_size)
        for i in self.entities:
            print("----")
            i.print()

   # def update_view(self):
   #     for i in self.entities:
   #         do something

