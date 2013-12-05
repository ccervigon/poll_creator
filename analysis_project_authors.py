#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import sys
import os

def calendar_commit_month_author(year, month, author):
    M = np.zeros(31, dtype=np.int)
    for aux in author:
        if (int(aux[2].month) == month) & (int(aux[2].year) == year):
            M[int(aux[2].day-1)] += 1
    return M

project = sys.argv[1]
os.chdir(sys.argv[5])

print 'Project: ' + project
con = MySQLdb.connect(host=sys.argv[2], user=sys.argv[3], passwd=sys.argv[4], \
                      db=project)
cursor = con.cursor()

query = ('SELECT column_name FROM information_schema.columns WHERE '
         'table_schema=DATABASE() AND table_name="scmlog" AND '
         'column_name="author_date"')
cursor.execute(query)
if len(cursor.fetchall()) != 0:
    date = 'author_date'
else:
    date = 'date'

cursor.execute('SELECT COUNT(*) FROM people')
tot_authors = int(cursor.fetchall()[0][0])

cursor.execute('SELECT MIN(' + date + ') FROM scmlog')
date_min = cursor.fetchall()[0][0]
date_min = date_min.year
cursor.execute('SELECT MAX(' + date + ') FROM scmlog')
date_max = cursor.fetchall()[0][0]
date_max = date_max.year

period = range(date_min,date_max)
period.append(date_max)

authors = []
for i in range(1,tot_authors+1):
    query = ('SELECT committer_id, author_id, ' + date + ' FROM scmlog '
              'WHERE author_id = %s ORDER BY ' + date)
    cursor.execute(query, i)
    authors.append(cursor.fetchall())

work_authors_month = []
for author in authors:
    M_month = []
    for year in period:
        for month in range(1, 13):
            aut = calendar_commit_month_author(year, month, author)
            work_days = 0
            for i in range(0, len(aut)):
                if aut[i] != 0:
                    work_days += 1
            M_month.append(work_days)
    work_authors_month.append(M_month)

for aut in range(0, tot_authors):
    query = ('SELECT name FROM people WHERE id=' + str(aut+1))
    cursor.execute(query)
    name_author = cursor.fetchall()[0][0]
    
    ax = plt.subplot(111)
    ax.bar(np.arange(len(work_authors_month[aut])), work_authors_month[aut])
    plt.axhline(10, color = 'g')
    plt.axhline(12, color = 'b')
    plt.axhline(15, color = 'r')
    ax.set_xlim(left=0, right=len(work_authors_month[aut]))
    ax.set_ylim(bottom=0, top=30)
    loc = plticker.MultipleLocator(base=2.0)
    ax.xaxis.set_major_locator(loc)
    plt.xlabel('Month')
    plt.ylabel('Days')
    plt.title(unicode('Temporal figure of work done by author ' + name_author, 'iso-8859-1'))
    plt.savefig('author_' + str(aut+1) + '.png', dpi = 200)
    plt.close()

cursor.close()
con.close()
