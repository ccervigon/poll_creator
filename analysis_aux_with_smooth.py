#!/usr/bin/python

import MySQLdb
from datetime import *
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

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
        raise ValueError, "Input vector needs to be bigger than window size."

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

project = sys.argv[1]
#os.system('mkdir /home/tthebosss/Dropbox/PFC/scripts/figuras/smoothing/' + project)
print 'Project: ' + project
con = MySQLdb.connect(host='localhost', user='tthebosss', passwd='1234', \
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

windows=['hanning']
len_windows = [1, 7]

smooth_work_days_authors_win1 = []
smooth_work_days_authors_win2 = []
for aut in work_authors_month:
    smooth_work_days_authors_win1.append(smooth(np.array(aut), len_windows[0], windows[0]))
    smooth_work_days_authors_win2.append(smooth(np.array(aut), len_windows[1], windows[0]))

for aut in range(0, tot_authors):
    i = 0
    for len_window in len_windows:
        i += 1
        #REPRESENTACION GRAFICA
        ax = plt.subplot(len(len_windows),1,i)
        if len_window == 1:
            ax.bar(np.arange(len(smooth_work_days_authors_win1[aut])), smooth_work_days_authors_win1[aut])
        if len_window == 7:
            ax.bar(np.arange(len(smooth_work_days_authors_win2[aut])), smooth_work_days_authors_win2[aut])
        plt.axhline(10, color = 'g')
        plt.axhline(12, color = 'b')
        plt.axhline(15, color = 'r')
        ax.set_xlim(left=0, right=len(smooth_work_days_authors_win2[aut]))
        ax.set_ylim(bottom=0, top=30)
        textstr = 'Ancho de ventana: ' + str(len_window)
        props = dict(boxstyle = 'round', facecolor = 'red', alpha = 0.15)
        ax.text(0.02, 0.86, textstr, transform = ax.transAxes, fontsize = 10, verticalalignment = 'top', horizontalalignment = 'left', bbox = props)

    #REPRESNTACION GRAFICA
    plt.subplot(len(len_windows),1,1)
    plt.title(windows[0])
    plt.savefig('/home/tthebosss/Dropbox/PFC/scripts/figuras/smoothing/' + project + '/author_' + str(aut) + '_' + windows[0] + '_month.png', dpi = 200)
    plt.close()

cursor.close()
con.close()
