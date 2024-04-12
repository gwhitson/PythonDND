# PythonDND

![alt text](https://github.com/gwhitson/PythonDND/blob/main/res/icons/logo.png?raw=true)

TODO:
UI Formatting/Cleaning

An interactive map for hosting DND sessions.

It will be up to the DM to find/create maps to use within the app, it is currently set to start at your monitors native resolution.

The app has the idea of a campaign which will have a unique (to it) list of entities, attacks, and encounters. Encounters within a given
campaign will have access to all of the same entities. This will allow the DM to add their party members from the entity manager without creating an
encounter specific entitiy.

# Getting Started
![alt text](https://github.com/gwhitson/PythonDND/blob/main/res/readme/splash.png?raw=true)

The main menu screen allows you to create, or load campaigns, alter settings, and quit the game. The settings menu is where you can adjust keybinds. Special keys
may require a specific syntax in order to not break. If a keybind is invalid, it will load the default keybind in its place. Campaigns are stored as sqlite .db files.
They are under the res/saves/ directory and can be accessed directly through sqlite. This can be dangerous and create breaking bugs in your campaign file.
Details on the campaign file and its implementation will be added under devloper notes.

# Encounters and Campaign management
![alt text](https://github.com/gwhitson/PythonDND/blob/main/res/readme/encounter_select.png?raw=true)

After either loading or creating a campaign, you will enter the following screen (a newly created campaign will have no encounterss by default and therefore the top portion will be blank).
If an encounter has already been defined, you can select it from the list and load the encounter. Otherwise you can create an encounter.

# Creating Encounters
![alt text](https://github.com/gwhitson/PythonDND/blob/main/res/readme/encounter_select.png?raw=true)

After selecting the 'New Encounter' option, you will be presented with the menu above.
