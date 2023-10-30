# PythonDND

--WORK IN PROGRESS--
An interactive map for hosting DND sessions.

It will be up to the DM to find/create maps to use within the app,
it is currently set to start at your monitors native resolution.

This has and likely will continue to go through a large amount of changes in
my  control scheme and overall app flow. The current idea seems to be the best.

I decided (and this seems simple in hindsight) that setting up a turn 
based combat system that cycles through the entities given in the move order
and allows you to act from there. Not having to select your entities manually
makes a significant difference in use and it seems much better, at least at the moment.

I will have to build the system for setting up the move order. Until I do that,
it uses the list of entities given to build the map.

I am thinking about building systems for tracking actions, however the amount of
variance that can be makes it seem like a pretty difficult task to get right.
Bonus actions and boss entities with multiple actions per turn means it needs to be
something that can be set easily with the base configuration. Most likely would be a
part of the entity class.

Another addition to the entity class would be weapons/attacks that are able to have a range
set on them and can prompt players to roll damage rolls and track status effects.
That is yet more work...


To-dos:
- refactor code to work with self.ent_to_act      [x]
        fleshed out turn based combat system a little,
        start combat button now goes away to symbolize combat has started,
        I may end up replacing it with an end combat button later
        a selector circle also shows which character is up to act

- clean any unnecesary functions left behind
  from the original selection system              [x] clean??

- built systems to select attack, may need to be cleaned up some [x]
        easily the hardest thing to build so far, needed to make a million helper 
        functions to make everything happen in the proper sequence. My initial ideas
        on how to do  this were way far off but this was a good learning experience

- build targetting systems, highlight target-
  ted entities                                    [x] 
        targetting system is working, built in aoe with it to adjust for how it
        was selecting entities. If the aoe is 0, the target will be whatever entity
        is in the square clicked on. This does mean that you only technically need enough
        range on an attack to reach the very corner of the square to make the attack, 
        however that seems reasonable enough to me.

- fix/test click function thoroughly, i 
  believe there were issues with it keeping
  flags set when they were not supposed to be     [x]
        this issue has been taken care of. Flags were indeed staying when they should
        not have been but I built a separate function for setting everything back to 
        clear. This just makes sure that at every stage we have all the right flags set

- also need to make aoe to work on top of range   [x]
    I think i want this to be a circle that moves 
    with the mouse and shows what the aoe would be
    where you click
        this should not have been a separate item on the list. Built in with targetting
        logic

- adding and removing entities                    [x]

    - I realized before the next option I have to decide how to 
      run the attack and modifyy entity hp

- tracking damage and removing entities when hp=0 [ ]

- adding backgrounds and scaling it to screen     [ ]

- build intiative ordering                        [ ]

- create enemy symbols and assign them to ents    [ ]

- allow player ents to be assigned letters        [ ]
    this will be quite a bit easier with the turn
    based combat setup than the selection one, tbc
    works with the entities themselves and does not 
    need to print unique identifies for player interaction

- add movement tracking system                    [ ]
    ideally, this will allow ents to make multi-part movements
    it largely just adds more flexibility

- make non-combat mode leverage movement tracking
  system to allow entities to be placed anywhere
  on the map before combat starts                 [ ]
    this will most likely use the click-to-select system
    that i just made and am mostly moving away from already
    taking out the need to attack in that mode too makes it 
    easier to track everything

- may need to rework the click function to be
  better suited to the turn based combat system   [ ]

- will likely need quite large scale refactoring
  and cleaning here                               [ ]

- action tracking?                                [ ]

- add attacks to class                            [x]
    attacks have been added, they now exist on the 'control_scheme' object from the 
    DMControls.py file. On turns, the attacks have their 'active_entity' property set to
    the entity from the 'control_scheme' that is chosen to modify or is acting to be used.
    This cuts down on memory as previously each object had attack objects creatd as well

- more.....
