import flask
from flask import Flask, request
from flask_cors import CORS

from botbuilder.utils import validate_user_data, render_bot

app = Flask(__name__)
CORS(app)


@app.route('/submit-data', methods=['POST'])
def submit_data():
    user_data = request.get_json()
    print(f"Request received!")

    if validate_user_data(user_data)[0]:
        render_bot(user_data)
        response = flask.jsonify({'success': True})
    else:
        response = flask.jsonify({'success': False})
        response.status = 500
    return response


if __name__ == '__main__':
    app.run()
