from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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



if __name__ == '__main__':
    app.run(debug=True)
