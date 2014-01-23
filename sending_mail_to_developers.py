#!/usr/bin/python
# -*- coding: utf-8 -*- 

import argparse
import MySQLdb
import smtplib
from email.mime.text import MIMEText

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

args = parser.parse_args()

print 'Project: ' + args.dbname
con = MySQLdb.connect(host=args.dbhostname, user=args.dbuser, \
                      passwd=args.dbpass, db=args.dbname)
con.set_character_set('utf8')
cursor = con.cursor()

query = ('SELECT email FROM people WHERE id = ANY (SELECT DISTINCT author_id from scmlog)')
cursor.execute(query)
emails = cursor.fetchall()

#Message
msg = MIMEText("Content")
msg['Subject'] = 'Subject'
msg['From'] = args.email

#Authentication
mailServer = smtplib.SMTP(args.smtp,args.smtp_port)
mailServer.ehlo()
mailServer.starttls()
mailServer.ehlo()
mailServer.login(args.email,args.email_pw)

for email in emails:
    print 'Sending email to ' + email[0] + '...',
    msg['To'] = email[0]
    mailServer.sendmail(args.email, email[0], msg.as_string())
    print 'OK'

mailServer.close()
print 'Finish'
