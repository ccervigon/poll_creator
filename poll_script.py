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
parser = argparse.ArgumentParser(description="""Scripts to make a poll of specific project""")
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
parser.add_argument("-poll_dir",
                    help="Poll directory",
                    default = '/tmp')
parser.add_argument("-delete",
                    help="Delete automatically the directory if exist",
                    action='store_true',
                    default = False)


args = parser.parse_args()
if args.poll_dir[-1] != '/':
    poll_project = args.poll_dir + '/'
else:
    poll_project = args.poll_dir

print 'Running script'

#Creating directory where we will store and copy the poll and web
poll_project += 'poll_' + args.dbname + '/'

if os.path.isdir(poll_project):
    print 'The directory "' + poll_project + '" exists.'
    if not args.delete:
        print 'IMPORTANT!!! Remember create a backup of the DB before continue if you want conserve the results.'
        print 'Do you want delete it? [yes/no] (Default: NO):'
        if raw_input().lower() != 'yes':
            print 'Script Aborted'
            sys.exit(1)
    call(['rm', '-r', poll_project])
    print 'Directory deleted'

print 'Copying files...',
call(['mkdir', poll_project])
call(['cp', '-r', 'poll', poll_project])
print 'Done'

#Analysis of project and obtaining graphs of authors
print 'Analyzing project and making DB...'
fig_dir = poll_project + 'poll/static/img/'
call(['python', 'analysis_project_authors.py', args.dbname, args.dbhostname,
      args.dbuser, args.dbpass, fig_dir])

#Copy of authors to poll's DB
con = MySQLdb.connect(host=args.dbhostname, user=args.dbuser, \
                      passwd=args.dbpass, db=args.dbname)
con.set_character_set('utf8')
cursor = con.cursor()

con2 = sqlite3.connect(poll_project + '/poll/db.sqlite3')
con2.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cursor2 = con2.cursor()

query = ('SELECT * FROM people')
cursor.execute(query)
people = cursor.fetchall()

for author in people:
    query = ('SELECT upeople_id FROM people_upeople WHERE people_id=%s')
    cursor.execute(query, author[0])
    upeople_id = cursor.fetchall()[0][0]
    sha = hashlib.sha1()
    sha.update(author[2])
    query = ('INSERT INTO pollApp_author VALUES(?,?,?,?,?)')
    cursor2.execute(query, (str(author[0]), author[1], author[2], sha.hexdigest(), str(upeople_id)))

#Saving changes into DB
con2.commit()
print 'Done'

#Disconnect of BBDD
cursor.close()
con.close()
cursor2.close()
con2.close()

print 'Script finished'
