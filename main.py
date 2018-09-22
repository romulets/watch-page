from requests import get
from difflib import unified_diff
from smtplib import SMTP
from os import environ
import logging
from flask import Flask


app = Flask(__name__)

watched_url = 'http://dsbd.leg.ufpr.br/inscricoes/'

@app.route('/')
def verify_page():
    logging.info('Get remote page')
    remote_page = get(watched_url)
    logging.info('Got it')

    body = ''
    if not remote_page.status_code == 200:
        body = 'The page returned  status %s' % remote_page.status_code
    else:
        remote_content = map(lambda line: line + '\n', remote_page.content.split('\n'))

        original_file = open('original.html', 'r')
        original_content = original_file.readlines()
        original_file.close()

        diff = list(unified_diff(remote_content, original_content))
        if len(diff) == 0:
            body = 'Nothing has changed so far'
        else:
            body = 'Something has changed, please look at %s ' % watched_url

    logging.info(body)

    sent_from = environ['GMAIL_USER']
    to = [environ['GMAIL_USER']]  
    subject = 'DSBD enrollment'  

    email_text = """\r
    From: %s  
    To: %s  
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    logging.info('Sending e-mail')

    server = SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(environ['GMAIL_USER'], environ['GMAIL_PASSWORD'])
    server.sendmail(sent_from, to, email_text)
    server.quit()
    server.close()

    logging.info('E-mail sent')

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]