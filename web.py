import json

from flask import Flask, redirect, render_template, request, session, url_for

from ieuler import Euler

app = Flask(__name__)
app.secret_key = b'23asdfcemveovmv m43 n3-0fnpeif'


# www.interactive-euler.com/


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/problem/<int:number>')
def problem(number):
    e = Euler(number)
    e.get()
    return json.dumps(
        {'problemName': e.name, 'problemContent': e.content, 'problemNumber': number, 'problemUrl': e.url})


if __name__ == '__main__':
    app.run(debug=True)
