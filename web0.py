"""
to do:

1.  get all euler problems from 1 html page, parse and save to sqlite, use flask sqlalchemy to access problems
2.  verify/submit more intuitive...if user/pass required, put that section into focus...then remove from focus
3.  what happens when you submit but are not logged in
4.  list other problem numbers, based on user selection display problem details
5.  need a place for user to write code and run it...when it is finished running, it populates the answer.
6.  make things look nicer
7.  add other languages


"""

import base64
from typing import Dict
from flask import Flask, jsonify, render_template, request, session

from ieuler import Client

app = Flask(__name__)
app.secret_key = b'23asdfcemveovmv m43 n3-0fnpeif'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/problems/<int:number>')
def problem(number) -> Dict:
    """ get a problem from project euler by number """
    client = Client()
    p = client.get(number)
    return jsonify(problemName=p.name, problemContent=p.content, problemNumber=p.number, problemUrl=p.url)


@app.route('/problems/<int:number>', methods=['POST'])
def submit(number) -> Dict:
    """ submit an answer to project euler.

    Check the flask session to see if logged in.  If not, send message to browser.
    Otherwise, let's open the client and submit.

    """
    if not session.get('logged_in'):  # possible to be marked as logged in but really not logged in
        return jsonify(status=False, message='login required')

    client = Client(cookies=session['euler_cookies'], logged_in=True)
    # a this point need to submit and return response
    submission = client.submit(number=number, answer=request.json['answer'], captcha=request.json['captcha'])
    # if user is marked as logged in but really not logged in, it gets the original problem text
    # not sure if you need to save any cookies here
    # if for some reason you are not logged in you will need to set logged_in to false and send above message
    # session['euler_cookies'] = client.session.cookies.get_dict()
    return jsonify(**submission)


@app.route('/captcha')
def captcha() -> bytes:
    """ get a captcha from project euler.

    It is important to save euler cookies to the flask session at this point for when the user enters the captcha code.
    """
    client = Client(cookies=session.get('euler_cookies'))
    b_captcha = client.captcha()
    # let's save the cookies to the session
    session['euler_cookies'] = client.session.cookies.get_dict()
    return base64.b64encode(b_captcha)


@app.route('/login', methods=['POST'])
def login() -> Dict:
    """ login to project euler.

    User provides username, password and captcha.  the mimetype is application/json.
    The captcha is from the captcha function, so need to look up and use cookies from the flask session.

    If the login is successful, then save logged_in = True to the flask session as well as overwrite euler cookies
    """
    user_input = request.json

    client = Client(cookies=session['euler_cookies'])
    login_message = client.login(username=user_input['username'],
                                 password=user_input['password'],
                                 captcha=user_input['captcha'])
    if login_message:  # login_message is None if success, otherwise login_message is some string error message
        return jsonify(logged_in=False, **login_message)

    session['logged_in'] = True
    session['euler_cookies'] = client.session.cookies.get_dict()
    return jsonify(logged_in=True)


if __name__ == '__main__':
    app.run(debug=True)
