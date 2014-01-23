#!/usr/bin/python
# -*- coding: utf-8 -*- 

import argparse
import smtplib
from email.mime.text import MIMEText
import sqlite3

# Parse command line options
parser = argparse.ArgumentParser(description="""Scripts to make a poll of specific project""")
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
parser.add_argument("-poll_dir",
                    help="Poll directory",
                    required = True)
parser.add_argument("-project",
                    help="Project name",
                    required = True)
parser.add_argument("-url",
                    help="URL where the poll is hosted",
                    required = True)

args = parser.parse_args()

print 'Project: ' + args.project
con = sqlite3.connect(args.poll_dir + '/poll/db.sqlite3')
con.text_factory = lambda x: unicode(x, "utf-8", "ignore")
cursor = con.cursor()

#Email authentication
mailServer = smtplib.SMTP(args.smtp,args.smtp_port)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(args.email,args.email_pw)

email_content = 'Example to %s with hash %s/%s' #CHANGE CONTENT

query = ('SELECT name,email,email_hash FROM pollApp_author')
for developer in cursor.execute(query):
    print 'Sending email to ' + developer[1] + '...',
    #Message
    msg = MIMEText(email_content % (developer[0], args.url, developer[2]))
    msg['Subject'] = 'Subject'
    msg['From'] = args.email
    msg['To'] = developer[1]
    mailServer.sendmail(args.email, developer[1], msg.as_string())
    print 'OK'

mailServer.close()
cursor.close()
con.close()
print 'Finish'
