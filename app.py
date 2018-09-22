from requests import get
from difflib import unified_diff
from smtplib import SMTP
from os import environ

watched_url = 'http://dsbd.leg.ufpr.br/inscricoes/'

remote_page = get(watched_url)

if not remote_page.status_code == 200:
    print('The page returned  status %s' % remote_page.status_code )
    exit()

remote_content = map(lambda line: line + '\n', remote_page.content.split('\n'))

original_file = open('original.html', 'r')
original_content = original_file.readlines()
original_file.close()

body = ''
diff = list(unified_diff(remote_content, original_content))
if len(diff) == 0:
    body = 'Nothing has changed so far'
else:
    body = 'Something has changed, please look at %s ' % watched_url

sent_from = environ['GMAIL_USER']
to = [environ['GMAIL_USER']]  
subject = 'DSBD enrollment'  

email_text = """\r
From: %s  
To: %s  
Subject: %s

%s
""" % (sent_from, ", ".join(to), subject, body)

server = SMTP('smtp.gmail.com', 587)
server.ehlo()
server.starttls()
server.login(environ['GMAIL_USER'], environ['GMAIL_PASSWORD'])
server.sendmail(sent_from, to, email_text)
server.quit()
server.close()