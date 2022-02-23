from flask import request, make_response, jsonify, current_app, render_template
import uuid
import random
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

from ..models import User, PasswordManager, SecurityQuestion, UserQuestionAnswer
from ..methods.auth import validate_captcha
from ..methods.common import db_commit, add_entity

from . import view

@view.route("/loginUser", methods=['POST'])
def login():
    auth = request.authorization
    if not (auth and auth.username and auth.password):
        return make_response(jsonify(
            message = "Could not verify"),
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    user = User.query.filter_by(email=auth.username.lower()).first()
    if not user:
        return make_response(jsonify(
            message = "Invalid username or password"),
            401,
            {"WWW-Authenticate": 'Basic realm="Username or Password is incorrect"'},
        )

    pwd = PasswordManager.query.filter_by(user_id=user.id).first()
    if check_password_hash(pwd.password, auth.password):
        user.last_logged_in = datetime.datetime.utcnow()
        db_commit("Something went wrong, try again after sometime.")
        if request.headers['Remember-Me']=="true":
            token = jwt.encode(
                {
                    "uuid": user.uuid,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
                },
                current_app.config["SECRET_KEY"]
            )
        else:
            token = jwt.encode(
                {
                    "uuid": user.uuid,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                current_app.config["SECRET_KEY"]
            )
        return jsonify({"token": token.decode("UTF-8")})

    return make_response(jsonify(
        message="Invalid username or password"),
        401,
        {"WWW-Authenticate": 'Basic realm="Username or Password is incorrect"'},
    )

@view.route('/', defaults={'path': ''})
@view.route('/<path:path>')
def home(path):
    return render_template("index.html")


@view.route("/signupUser", methods=["POST"])
def signup():
    if not validate_captcha(request.json['captchaToken']):
        return make_response(jsonify(message="Captcha not verified"), 400)
    email = request.json["email"].lower()
    name = request.json["name"]
    phone = request.json["phone"]
    password = request.json["password"]

    if email =="" or name == "" or password=="":
        return make_response(
            jsonify(message="Required fields cannot be blank"), 400
        )

    user = User.query.filter(User.email == email).first()
    if user:
        return make_response(
            jsonify(message="This email id is already registered."), 409
        )
    if phone:
        phone_obj = User.query.filter(User.phone == phone).first()
        if phone_obj:
            return make_response(
                jsonify(
                    message="Somebody else has registered using this phone number.<br>Please contact system administrator."
                ),
                409,
            )
    else:
        phone=None
    new_user = User(uuid=str(uuid.uuid4()), email=email, name=name, phone=phone)

    add_entity(new_user, "There was a problem registering the user")

    pwd = PasswordManager(
        password=generate_password_hash(password, method="sha256"),
        user_id=new_user.id,
    )

    add_entity(pwd, "There was a problem setting the password")
    db_commit()
    return jsonify(message="Registration successfull!!!")

@view.route("/getUserQuestions", methods=["POST"])
def get_user_questions():
    email_id = request.json["email"]
    user = User.query.filter(User.email == email_id.lower()).first()
    if not user:
        return make_response(jsonify(message="User does not exist"), 404)
    user_questions = UserQuestionAnswer.query.filter(
        UserQuestionAnswer.user_id == user.id
    )
    random_questions = []
    for i in range(2):
        rand_idx = random.randrange(len(list(user_questions)))
        random_questions.append(user_questions[rand_idx])
    security_questions = [
        SecurityQuestion.query.get_or_404(user_question.question_id)
        for user_question in random_questions
    ]
    return jsonify(
        [
            {"id": security_question.id, "question": security_question.question}
            for security_question in security_questions
        ]
    )

@view.route("/verifySecurityQuestions", methods=["POST"])
def verify_security_questions():
    email = request.json["email"]
    questions = request.json["questions"]
    user = User.query.filter(User.email == email.lower()).first()
    if not user:
        return make_response(jsonify(message="Invalid user"), 400)
    for question in questions:
        user_ans = UserQuestionAnswer.query.filter(
            UserQuestionAnswer.user_id == user.id,
            UserQuestionAnswer.question_id == question["id"],
        ).first()
        if not user_ans:
            return make_response(jsonify(message="Invalid input"), 400)
        if user_ans.answer.lower()!=question['answer'].lower():
            return make_response(jsonify(message="Incorrect answers"), 400)
    token = jwt.encode(
                {
                    "uuid": user.uuid,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
                },
                current_app.config["PASSWORD_RESET_KEY"]
            )
    return jsonify({"token": token.decode("UTF-8")})

@view.route("/resetPassword", methods=["POST"])
def reset_password():
    if "Authorization" in request.headers:
        token = request.headers["Authorization"]

    if not token:
        return make_response(jsonify(message="Invalid input"), 401)

    try:
        data = jwt.decode(token.split("Bearer ")[1], current_app.config["PASSWORD_RESET_KEY"])
        user = User.query.filter_by(uuid = data["uuid"]).first()
        if not user: raise
    except:
        return make_response(jsonify(message="Invalid user"), 401)
    password = request.json['password']
    pd_mgr = PasswordManager.query.filter(PasswordManager.user_id==user.id).first()
    if not pd_mgr:
        return make_response(jsonify(message="Invalid user"), 401)
    pd_mgr.password = generate_password_hash(password, method="sha256")
    db_commit()
    return jsonify(message="Password reset has been done successfully!")