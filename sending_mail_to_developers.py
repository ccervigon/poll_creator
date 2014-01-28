#!/usr/bin/python
# -*- coding: utf-8 -*- 

import argparse
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import sqlite3

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
parser.add_argument("-project",
                    help="Project name",
                    required = True)
parser.add_argument("-url",
                    help="URL where the survey is hosted",
                    required = True)

args = parser.parse_args()

print 'Project: ' + args.project
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
template_content = '''Hello %s,<br><br>

We are researchers from a Spanish and a British university working on a model for estimating effort in Open Source Software.<br><br>

To validate our findings we have built a small survey -it is composed of 6 questions and should take you less than 3 minutes to respond- about your effort and time spent on the %s project.<br><br>

The survey can be accessed at %s/%s<br><br>

For more information about ourselves, our research, and the possibility to give more feedback, please visit %s<br><br>

Thank you very much,<br><br>

Carlos'''

#Header image
img_file = open("logo-libresoft.png", "rb")
attach_image = MIMEImage(img_file.read())
attach_image.add_header('Content-ID', '<logo-libresoft.png>')
img_file.close()

query = ('SELECT name,email,email_hash FROM surveyApp_author')
for developer in cursor.execute(query):
    print 'Sending email to ' + developer[1] + '...',
    #Message
    msg = MIMEMultipart()
    msg['From'] = args.email
    msg['To'] = developer[1]
    msg['Subject'] = 'Subject'
    #INFO: 1º NAME, 2º PROJECT, 3º URL, 4º EMAIL_HASH, 5º URL
    email_content = template_content % (developer[0], args.project, args.url, developer[2], args.url)
    msgText = MIMEText('<p>%s</p><br><img src="cid:logo-libresoft.png" width="400" style="display: block;margin: auto;"><br>' % email_content, 'html')
    msg.attach(msgText)
    msg.attach(attach_image)
    mailServer.sendmail(args.email, developer[1], msg.as_string())
    print 'OK'

mailServer.close()
cursor.close()
con.close()
print 'Finish'
