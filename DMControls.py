import json, os

class controllable_entity:
    def __init__(self, name = "nul", HP = "-1", location_x = 0, location_y = 0, role = "neutral"):
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
        self.location_x = (location_x - diff_x)
        self.location_y = (location_y - diff_y)

class controls_scheme:
    def __init__(self, entities : list):
        self.entities = entities

    def add_entity(self, entity_to_add: controllable_entity()):
        self.entities += entity_to_add
        
    def remove_entity(self, entity_to_remove: controllable_entity()):
        self.entities -= entity_to_remove

    def upate_view(self):
        for i in self.entities:
            do something
