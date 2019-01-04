EPL Player Fantasy Form Tracker
===============================

Overview
--------

Script scrapes through multiples URLs to compile a list of players from the English Premier League along with their fantasy league statistics in order to create an excel sheet ranking the league's top performers in each position.

Dependencies
------------

User needs to install xlsxwriter library. Follow instructions here <https://xlsxwriter.readthedocs.io/getting_started.html>

How Script Works
----------------

1. User is prompted to select one of the following positions:
- Goalkeeper
- Defender
- Midfielder
- Forward

2. Script then gathers a list of players from the English Premier League that play that position

3. Script then extracts all the statistics for each of the players

4. User is then prompted to choose how long the list of top performers should be and how many recent fixtures will be used to determine player form

5. Script then sorts players based on user parameters

6. Script then prints out x amount of top performers' name, team, next opponent, and how many points they've scored in each of the last x amount of fixtures

Need to Work On
---------------

Speeding up step 3 and look to add new features.
