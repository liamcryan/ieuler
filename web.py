# from flask import Flask, render_template, request, jsonify
#
# app = Flask(__name__)
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/run', methods=['POST'])
# def run():
#     user_code = request.data
#     try:
#         exec(user_code)
#     except Exception as e:
#         return jsonify(exception=str(e))
#     try:
#         return jsonify(submission=eval('submit()'))
#     except NameError:
#         return jsonify(exception='function must be named {submit}')
#     except Exception as e:
#         return jsonify(exception=str(e))
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     elif request.method == 'POST':
#         """ authenticate with PE,
#             if successful, reset 30 minute timeout, save cookies, redirect to /my-project-euler
#             else, warn user/pass incorrect
#         """
#         pass  # authenticate with project euler,
#
#
# @app.route('/captcha')
# def captcha():
#     pass
#
#
# if __name__ == '__main__':
#     app.run(debug=True)


from app import app, db
from app.models import User, Scratchpad, Problem


@app.shell_context_processor
def shell():
    return {'db': db, 'User': User, 'Problem': Problem, 'Scratchpad': Scratchpad}
