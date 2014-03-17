#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
import sqlite3
import argparse
from subprocess import call
import sys
import os
import hashlib

# Parse command line options
parser = argparse.ArgumentParser(description="""Scripts to make a survey of specific project""")
parser.add_argument("-dbhostname",
                    help = "MySQL hostname",
                    default = 'localhost')
parser.add_argument("-dbuser",
                    help = "MySQL user name",
                    required = True)
parser.add_argument("-dbpass",
                    help = "MySQL password",
                    required = True)
parser.add_argument("-dbname",
                    help = "Name of the database with project cvsanaly information",
                    required = True)
parser.add_argument("-survey_dir",
                    help="Survey directory",
                    default = '/tmp/survey')
parser.add_argument("-delete",
                    help="Delete automatically the directory if exist",
                    action='store_true',
                    default = False)
parser.add_argument("-update_survey",
                    help="Only update survey App",
                    action='store_true',
                    default = False)
parser.add_argument("-add_project",
                    help="Add project to the survey",
                    action='store_true',
                    default = False)


args = parser.parse_args()
if args.survey_dir[-1] != '/':
    survey_project = args.survey_dir + '/'
else:
    survey_project = args.survey_dir

print 'Running script'

#Creating directory where we will store and copy the survey and web
#survey_project += 'survey_' + args.dbname + '/'

if not args.update_survey and not args.add_project:
    if os.path.isdir(survey_project):
        print 'The directory "' + survey_project + '" exists.'
        if not args.delete:
            print 'IMPORTANT!!! Remember create a backup of the DB before continue if you want conserve the results.'
            print 'Do you want delete it? [yes/no] (Default: NO):'
            if raw_input().lower() != 'yes':
                print 'Script Aborted'
                sys.exit(1)
        call(['rm', '-r', survey_project])
        print 'Directory deleted'
    
    print 'Copying files...',
    call(['mkdir', survey_project])
if not args.add_project:
    call(['cp', '-r', 'survey', survey_project])
    print 'Done'

if not args.update_survey or args.add_project:
    #Analysis of project and obtaining graphs of authors
    print 'Analyzing project and making images...'
    fig_dir = survey_project + 'survey/static/img/'
    call(['python', 'analysis_project_authors.py', args.dbname, args.dbhostname,
          args.dbuser, args.dbpass, fig_dir])

#Copy of authors to survey's DB
print 'Updating DB...'
con = MySQLdb.connect(host=args.dbhostname, user=args.dbuser, \
                      passwd=args.dbpass, db=args.dbname)
con.set_character_set('utf8')
cursor = con.cursor()

con2 = sqlite3.connect(survey_project + '/survey/db.sqlite3')
con2.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cursor2 = con2.cursor()

query = ('SELECT COUNT(*) from surveyApp_author')
tot_aut = cursor2.execute(query).fetchall()[0][0]


query = ('SELECT * FROM people WHERE id = ANY (SELECT DISTINCT author_id FROM scmlog) AND NOT id = ANY (SELECT id FROM people WHERE name LIKE "%bot" OR name LIKE "%jenkins%" OR name LIKE "%gerrit%")')
cursor.execute(query)
people = cursor.fetchall()

for author in people:
    query = ('SELECT upeople_id FROM people_upeople WHERE people_id=%s')
    cursor.execute(query, author[0])
    upeople_id = cursor.fetchall()[0][0]
    sha = hashlib.sha1()
    sha.update((args.dbname + author[2]))
    query = ('INSERT INTO surveyApp_author VALUES(?,?,?,?,?,?,?)')
    cursor2.execute(query, (str(tot_aut + 1), author[1], author[2], sha.hexdigest(), str(upeople_id), args.dbname, (args.dbname+'_author_'+str(upeople_id))))
    tot_aut += 1

#Saving changes into DB
con2.commit()
print 'Done'

#Disconnect of BBDD
cursor.close()
con.close()
cursor2.close()
con2.close()

print 'Script finished'
