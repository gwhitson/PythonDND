import DMControls as dm

player1 = dm.controllable_entity("player1", 5, 3,3, "player")
player2 = dm.controllable_entity("player2", 5, 3,3, "player")
player3 = dm.controllable_entity("player3", 5, 3,3, "player")
player4 = dm.controllable_entity("player4", 5, 3,3, "player")
player5 = dm.controllable_entity("player5", 5, 3,3, "player")

ents = [player1,player2,player3,player4,player5]

game = dm.control_scheme(ents, 15)

game.print()
