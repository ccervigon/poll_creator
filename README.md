# poll_creator

UNDER CONSTRUCTION!!!!!

Program that generates a poll in Django with information of work temporal structure done by developers of a project. 

Its purpose is to obtain accurate information from the developers of the time spent to their work along the project to contrast it with that you can get of the git repository of the project.

Method of use
-------------

### Dependencies

* MySQL database with information obtained of the project. You must use the VizGrimoireR tools to obtain the information (https://github.com/VizGrimoire/VizGrimoireR).

* Python 2.7

* Django 1.6

### Usage:

$ python poll_script.py -dbuser ccervigon -dbpass 1234 -dbname XXX -poll_dir /tmp

This will generate a copy of the Django project in the folder specified by the parameter -poll_dir, also get a list of project developers which it is copied to sqlite database of the poll and it generates a graph with the temporal distribution of work produced per month for each developer.

After only is necessary to run the Django server to can see the poll.
