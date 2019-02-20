import base64

from flask import render_template, jsonify, request, flash, redirect, url_for, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm
from app.models import User, Scratchpad, Problem
from ieuler import Client, LoginException


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        c = Client(session.get('euler_cookies'))
        username = form.username.data
        # try:
        #     c.login(username=username, password=form.password.data, captcha=form.captcha.data)
        # except LoginException as e:
        #     flash(f'Login not successful: {e}')
        #     return redirect(url_for('login'))

        user = User.query.filter_by(username=username).first()
        if user is None:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        # session['euler_cookies'] = c.session.cookies.get_dict()

        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('me', username=user.username)
        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/me/<username>')
@login_required
def me(username):
    user = User.query.filter_by(username=username).first_or_404()
    scratchpad = user.scratchpads.first()  # need to sort by timestamp
    if not scratchpad:
        problem = Problem.query.first()
        scratchpad = Scratchpad(language='python', code='', solver=user, problem=problem)
        db.session.add(scratchpad)
        db.session.commit()
    return render_template('me.html', user=user, scratchpad=scratchpad)


@app.route('/logout')
def logout():
    # session.pop('euler_cookies')
    logout_user()
    return redirect(url_for('index'))


@app.route('/captcha')
def captcha() -> bytes:
    """ get a captcha from project euler.

    It is important to save euler cookies to the flask session at this point for when the user enters the captcha code.
    """
    client = Client(cookies=session.get('euler_cookies'))
    # client = Client(cookies=None)
    b_captcha = client.captcha()
    # let's save the cookies to the session
    session['euler_cookies'] = client.session.cookies.get_dict()
    return base64.b64encode(b_captcha)


@app.route('/run', methods=['POST'])
def run():
    user_code = request.data
    try:
        exec(user_code)
    except Exception as e:
        return jsonify(exception=str(e))
    try:
        return jsonify(submission=eval('submit()'))
    except NameError:
        return jsonify(exception='function must be named {submit}')
    except Exception as e:
        return jsonify(exception=str(e))
