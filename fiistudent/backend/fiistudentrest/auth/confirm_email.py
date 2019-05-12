from flask import Flask, redirect
from itsdangerous import URLSafeSerializer, SignatureExpired
from fiistudentrest.models import Student
import fiistudentrest.mail as Mail


# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Dragomir Cristian\\Documents\\fii-student-5c3ee6b54bbd.json"


# app = Flask(__name__)

def send_confirm_email(to_email):
    link = "nujcum.ro/validate/"
    token = generate_token(to_email)
    link_token = link + token

    subject = "Confirm your email"
    content = "<h4>Hi there,</h4>"
    content += "\n<p>This message is to confirm that the account created lately belongs to you. " \
               "Verifying your email address helps you secure your account. " \
               "If you forgot your password, you will now be able to reset it by email.</p>"
    content += '\n<div style="display:flex; flex-direction: column; align-items: center">'
    content += '\n<p>To confirm that this is your account press on the button below.</p>'
    content += '\n<form action="' + link_token + '">' \
               '\n<input style="border: none;cursor: pointer;padding: 10px 20px;border-radius: 5px;font-size: 15px;' \
               'background-color: #21d146;font-weight: bold" type="submit"/></form></div>'

    Mail.send_mail(Mail.DEFAULT_MAIL, to_email, subject, content)



def generate_token(email, salt='email-confirmation'):
    serializer = URLSafeSerializer("Thisisasecret!!!")
    return serializer.dumps(email, salt)


def confirm_token(token):
    serializer = URLSafeSerializer("Thisisasecret!!!")
    try:
        email = serializer.loads(token, salt='email-confirmation')
    except SignatureExpired:
        return False
    return email


# @app.route('/')
def index():
    email = 'dragomircristian323@yahoo.com'
    serializer = URLSafeSerializer('Thisisasecret!!!')
    token = serializer.dumps(email, salt='email-confirmation')
    return '<h1>token: {}'.format(token)


# @app.route('/confirm-email/<token>')
def confirm_email(token):
    email = None
    try:
        email = confirm_token(token)
    except:
        print("The confirmation link is invalid or has expired!")
    query = Student.query()
    query.add_filter('email', '=', email)
    query_it = query.fetch()
    for ent in query_it:
        if ent.confirmed == True:
            print('Account already confirmed.')
        else:
            ent.confirmed = True
            Student.put(ent)
            print('You have confirmed your account.')
        return redirect('/')

# if __name__ == '__main__':
#     app.run(debug=True)
