#!/usr/bin/python
# -*- coding: utf-8 -*- 

import MySQLdb
import datetime
import numpy as np
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
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

def smooth(x, window_len=10, window='hanning'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    import numpy as np
    t = np.linspace(-2,2,0.1)
    x = np.sin(t)+np.random.randn(len(t))*0.1
    y = smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        #raise ValueError, "Input vector needs to be bigger than window size."
        return x

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"

    s=np.r_[2*x[0]-x[window_len:1:-1], x, 2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = getattr(np, window)(window_len)
    y = np.convolve(w/w.sum(), s, mode='same')
    return y[window_len-1:-window_len+1]

def fix_smooth(f_original, len_window, window):
    f_smooth = np.array([], dtype=np.int)
    flag = False
    position = 0
    for i in range(0, len(f_original)):
        if f_original[i] != 0:
            if i+1 == len(f_original):
                if flag:
                    if len(f_original[position:]) == 7:
                        smooth_aux = smooth(np.array(f_original[position-1:]), len_window, window)
                        smooth_aux = smooth_aux[1:]
                    else:
                        smooth_aux = smooth(np.array(f_original[position:]), len_window, window)
                    f_smooth = np.append(f_smooth, smooth_aux)
                else:
                    f_smooth = np.append(f_smooth, f_original[i])
            elif not flag:
                position = i
                flag = True
        elif f_original[i] == 0 and flag:
            if i+1 == len(f_original):
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
            elif f_original[i+1] == 0:
                if len(f_original[position:i]) == 7:
                    smooth_aux = smooth(np.array(f_original[position-1:i]), len_window, window)
                    smooth_aux = smooth_aux[1:]
                else:
                    smooth_aux = smooth(np.array(f_original[position:i]), len_window, window)
                f_smooth = np.append(f_smooth, smooth_aux)
                f_smooth = np.append(f_smooth, 0)
                flag = False
        else:
            f_smooth = np.append(f_smooth, 0)
    return f_smooth

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
cursor.execute('SELECT MAX(date) FROM scmlog')
date_max = cursor.fetchall()[0][0]

period = range(date_min.year,date_max.year)
period.append(date_max.year)

#Upeople
date_limit = datetime.datetime(date_max.year-1, date_max.month, 1)
query = ('SELECT upeople_id FROM people_upeople WHERE people_id = ANY (SELECT DISTINCT author_id FROM scmlog WHERE date >= %s)')
cursor.execute(query, date_limit)
upeople = cursor.fetchall()

#Bots
query = ('SELECT upeople_id FROM people_upeople WHERE people_id = ANY (SELECT id FROM people WHERE name LIKE "%bot" OR name LIKE "%jenkins%" OR name LIKE "%gerrit%")')
cursor.execute(query)
bots = cursor.fetchall()

print 'Getting activity'
authors_commits = []
authors_ids = []
aut_num = 0
len_aut = len(upeople)
for aut in upeople:
    print aut_num, len_aut
    if not aut in bots:
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
    aut_num+=1

tot_authors = len(authors_commits)

work_authors_month = []

print 'Getting activity'
count_aut = 0
for author in authors_commits:
    print count_aut, tot_authors
    M_month = []
    for year in period:
        first_month = 1
        last_month = 12
        if year == date_min.year:
            first_month = date_min.month
            last_month = 12
        elif year == date_max.year:
            first_month = 1
            last_month = date_max.month
        for month in range(first_month, last_month+1):
            aut = calendar_commit_month_author(year, month, author)
            work_days = 0
            for i in range(len(aut)):
                if aut[i] != 0:
                    work_days += 1
            M_month.append(work_days)
    work_authors_month.append(M_month)
    count_aut+=1
    
    windows=['hanning']
    len_windows = [7]
    
    smooth_work_days_authors = []
    for aut in work_authors_month:
        smooth_work_days_authors.append(fix_smooth(aut, len_windows[0], windows[0]))

startdate = datetime.date(date_min.year, date_min.month, 1)
enddate = datetime.date(date_max.year, date_max.month, 1)
delta = relativedelta(months=+1)
list_date = []
d = startdate
while d <= enddate:
    list_date.append(d)
    d += delta
interval = 1 + (len(list_date) / 45)
months = mdates.MonthLocator(range(1,13), bymonthday=1, interval=interval)
monthsFmt = mdates.DateFormatter("%b '%y")
width_bar = [(np.array(list_date)[j+1]-np.array(list_date)[j]).days \
             for j in range(len(np.array(list_date))-1)] + [30]

print 'Making graph'
aut_num = 0
for aut in range(tot_authors):
    print aut_num, tot_authors
    query = ('SELECT identifier FROM upeople WHERE id=' + str(authors_ids[aut][0][0]))
    cursor.execute(query)
    name_author = cursor.fetchall()[0][0]
    
    ax = plt.subplot(111)
    ax.bar(np.array(list_date), smooth_work_days_authors[aut],
           width=width_bar, align="center")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    for label in ax.xaxis.get_majorticklabels():
        label.set_fontsize(8)  
    plt.xticks(rotation=90)
    plt.axhline(9, color='g', linewidth=2)
    ax.set_xlim(left=startdate, right=enddate)
    ax.set_ylim(bottom=0, top=30)
    textstr = 'Above Green Line (> 9): Full Time Developer'
    props = dict(boxstyle = 'round', facecolor = 'g', alpha = 0.3)
    ax.text(0.97, 0.96, textstr, transform = ax.transAxes, fontsize = 10, verticalalignment = 'top', horizontalalignment = 'right', bbox = props)
    plt.ylabel('Days worked')
    plt.title(unicode('Temporal figure of work done by author ' + name_author, 'iso-8859-1'))
    plt.savefig(project + '_author_' + str(authors_ids[aut][0][0]) + '.png', dpi = 200)
    plt.close()
    aut_num+=1

cursor.close()
con.close()
