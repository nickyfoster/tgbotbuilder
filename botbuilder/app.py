import flask
from flask import Flask, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf.csrf import CSRFProtect, generate_csrf

from botbuilder.utils import validate_user_data, render_bot, do_deploy_bot, get_variable_from_dot_env, \
    process_login_data

app = Flask(__name__, static_folder="public")
app.config.update(
    DEBUG=True,
    SECRET_KEY=get_variable_from_dot_env("FLASK_APP_SECRET"),
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="None",
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

csrf = CSRFProtect(app)
cors = CORS(
    app,
    resources={r"*": {"origins": "*"}},
    expose_headers=["Content-Type", "X-CSRF-Token"],
    supports_credentials=True,
)

# database
users = [
    {
        "id": 1,
        "username": "test",
        "password": "test",
    }
]


class User(UserMixin):
    ...


def get_user(user_id: int):
    for user in users:
        if int(user["id"]) == int(user_id):
            return user
    return None


@login_manager.user_loader
def user_loader(id: int):
    user = get_user(id)
    if user:
        user_model = User()
        user_model.id = user["id"]
        return user_model
    return None


@app.route("/api/v1/getcsrf", methods=["GET"])
def get_csrf():
    token = generate_csrf()
    response = flask.jsonify({"detail": "CSRF cookie set"})
    response.headers.set("X-CSRF-Token", token)
    return response


@app.route('/api/v1/ping', methods=['GET'])
@login_required
def ping():
    return flask.jsonify({"ping": "pong!"})


@app.route("/api/v1/login", methods=["POST"])
def login():
    print(f"request.data: {request.data}")

    processed_login_data = process_login_data(request.data)
    username = processed_login_data.get("username")
    password = processed_login_data.get("password")

    for user in users:
        if user["username"] == username and user["password"] == password:
            user_model = User()
            user_model.id = user["id"]
            login_user(user_model)
            return flask.jsonify({"login": True})

    return flask.jsonify({"login": False}), 401


@app.route("/api/v1/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return flask.jsonify({"logout": True})


@app.route("/api/v1/getsession", methods=["GET"])
def check_session():
    if current_user.is_authenticated:
        return flask.jsonify({"login": True})

    return flask.jsonify({"login": False})


@app.route('/api/v1/submit-data', methods=['POST'])
@login_required
@csrf.exempt
def submit_data():
    user_data = request.get_json()
    print(f"Request received:\n{user_data}")
    is_valid, error = validate_user_data(user_data)
    if is_valid:
        render_bot(user_data)
        response = flask.jsonify({'success': True, 'botId': None})
    else:
        response = flask.jsonify({'success': False, 'error': error})
        response.status = 500

    print(response.status, response.json)
    return response


@app.route('/api/v1/deploy-bot', methods=['GET'])
@login_required
def deploy_bot():
    is_success, error = do_deploy_bot()
    if is_success:
        response = flask.jsonify({'success': True})
    else:
        response = flask.jsonify({'success': False, 'error': error})
        response.status = 500
    return response


if __name__ == '__main__':
    app.run()
