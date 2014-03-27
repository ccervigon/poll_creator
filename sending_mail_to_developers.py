#!/usr/bin/python
# -*- coding: utf-8 -*- 

import argparse
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import sqlite3
import csv

# Parse command line options
parser = argparse.ArgumentParser(description="""Scripts to make a survey of specific project""")
parser.add_argument("-email",
                    help="Email",
                    required = True)
parser.add_argument("-email_pw",
                    help="Email password",
                    required = True)
parser.add_argument("-smtp",
                    help="SMTP server",
                    required = True)
parser.add_argument("-smtp_port",
                    help="SMTP port",
                    required = True)
parser.add_argument("-survey_dir",
                    help="Survey directory",
                    required = True)
parser.add_argument("-url",
                    help="URL where the survey is hosted",
                    required = True)

args = parser.parse_args()

con = sqlite3.connect(args.survey_dir + '/survey/db.sqlite3')
con.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cursor = con.cursor()

#Email authentication
mailServer = smtplib.SMTP(args.smtp,args.smtp_port)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(args.email,args.email_pw)

#INFO: 1º NAME, 2º PROJECT, 3º URL, 4º EMAIL_HASH, 5º URL
template_content = u'''Dear %s,<br><br>

I am a researcher at a Spanish University and together with another university in the UK we are working on a model for estimating effort in Open Source Software.<br><br>

To validate our findings we need your input. Therefore we have built a small survey -it is composed of 6 questions and should take you less than 3 minutes to respond- about your effort and time spent on the %s project.<br><br>

The survey can be accessed at %s/%s<br><br>

For more information about ourselves, our research, and the possibility to give more feedback, please visit %s/contact or find us on the IRC (#libresoft on Freenode).<br><br>

We have already studied OpenStack with our methodology. Have a look at the <a href="%s/result">preliminary results</a>.

Thank you in advance.<br><br>

Carlos Cervigón<br>
Researcher at Universidad Rey Juan Carlos<br>
GSyC/LibreSoft Libre Software Engineering Research Lab<br>
http://www.libresoft.es<br>
'''

list_email_errors = []

query = ('SELECT name,email,author_hash,project FROM surveyApp_author GROUP BY email')

for developer in cursor.execute(query):
    project = developer[3][:developer[3].rfind('_')]
    try:
        print 'Sending email to ' + developer[1] + '...',
        #Message
        msg = MIMEMultipart()
        msg['From'] = args.email
        msg['To'] = developer[1]
        msg['Subject'] = 'Short survey to tune up Effort Estimation Model for Open Source Software'
        #INFO: 1º NAME, 2º PROJECT, 3º URL, 4º EMAIL_HASH, 5º URL 6º URL
        email_content = template_content % (developer[0].split()[0], project, args.url, developer[2], args.url, args.url)
        msgText = MIMEText('<p>%s</p>'.encode('utf-8') % email_content, 'html', 'utf-8')
        msg.attach(msgText)
        mailServer.sendmail(args.email, developer[1], msg.as_string())
        print 'OK'
    except:
        print 'Problem'
        list_email_errors.append(developer)

mailServer.close()
cursor.close()
con.close()

with open("~/list_email_errors.csv", "wb") as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'email', 'author_hash', 'project'])
    writer.writerows(list_email_errors)

print 'Finish'
