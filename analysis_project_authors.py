#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import os
from dateutil.relativedelta import relativedelta

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

cursor.execute('SELECT MIN(date) FROM scmlog')
date_min = cursor.fetchall()[0][0]
date_min = date_min.year
cursor.execute('SELECT MAX(date) FROM scmlog')
date_max = cursor.fetchall()[0][0]
date_max = date_max.year

period = range(date_min,date_max)
period.append(date_max)

query = ('SELECT id from upeople')
cursor.execute(query)
upeople = cursor.fetchall()

authors_commits = []
authors_ids = []
for aut in upeople:
    query = ('SELECT people_id FROM people_upeople WHERE upeople_id=%s')
    cursor.execute(query, aut[0])
    people_ids = cursor.fetchall()
    if people_ids:
        list_commits = ()
        for pid in people_ids:
            query = ('SELECT committer_id, author_id, ' + date + ' FROM scmlog '
                     'WHERE author_id = %s')
            cursor.execute(query, pid[0])
            list_commits += cursor.fetchall()
        authors_commits.append(tuple(sorted(list_commits, key=lambda item: item[2])))
        ids = (aut,) + people_ids
        authors_ids.append(ids)

tot_authors = len(authors_commits)

work_authors_month = []

for author in authors_commits:
    M_month = []
    for year in period:
        for month in range(1, 13):
            aut = calendar_commit_month_author(year, month, author)
            work_days = 0
            for i in range(len(aut)):
                if aut[i] != 0:
                    work_days += 1
            M_month.append(work_days)   #CONTAMOS EN ESTE CASO LOS DIAS TRABAJADOS AL MES Y NO LOS COMMITS AL MES
            
    work_authors_month.append(M_month)

startdate = datetime.date(date_min, 1, 1)
enddate = datetime.date(date_max, 12, 1)
delta = relativedelta(months=+1)
list_date = []
d = startdate
while d <= enddate:
    list_date.append(d)
    d += delta
months = mdates.MonthLocator(range(1,13), bymonthday=1, interval=2)
monthsFmt = mdates.DateFormatter("%b '%y")
width_bar = [(np.array(list_date)[j+1]-np.array(list_date)[j]).days \
             for j in range(len(np.array(list_date))-1)] + [30]

for aut in range(tot_authors):
    query = ('SELECT identifier FROM upeople WHERE id=' + str(authors_ids[aut][0][0]))
    cursor.execute(query)
    name_author = cursor.fetchall()[0][0]
    
    ax = plt.subplot(111)
    ax.bar(np.array(list_date), work_authors_month[aut],
           width=width_bar, align="center")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(8)  
    plt.xticks(rotation=90)
    plt.axhline(10, color = 'g')
    plt.axhline(12, color = 'b')
    plt.axhline(15, color = 'r')
    ax.set_xlim(left=startdate, right=enddate)
    ax.set_ylim(bottom=0, top=30)
    plt.ylabel('Days')
    plt.title(unicode('Temporal figure of work done by author ' + name_author, 'iso-8859-1'))
    plt.savefig('author_' + str(authors_ids[aut][0][0]) + '.png', dpi = 200)
    plt.close()

cursor.close()
con.close()
