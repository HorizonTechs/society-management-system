from flask import request, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash

from ..models import (
    PasswordManager,
    RoleManager,
    SecurityQuestion,
    Society,
    UserQuestionAnswer,
    db,
    User,
    Member,
    Flat,
)
from ..methods.auth import login_required
from ..methods.societies import validate_get_permission, validate_modify_permission
from ..methods.common import add_entity, db_commit, delete_entity, to_json_response
from . import view


@view.route("/getUserName")
@login_required
def get_user_name(current_user):
    return jsonify(user_full_name=current_user.name)


@view.route("/getUserDetails")
@login_required
def get_user_details(current_user):
    return jsonify(
        {
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
        }
    )


@view.route("/updateUserDetails", methods=["PUT"])
@login_required
def update_user(current_user):
    email = current_user.email
    name = request.json["name"]
    phone = request.json["phone"]
    user = User.query.filter(User.email == email).first()
    user.name = name
    user.phone = phone
    db_commit()
    return jsonify(message="Details updated successfully")


@view.route("/changePassword", methods=["PUT"])
@login_required
def change_password(current_user):
    current_password = request.json["currPassword"]
    new_password = request.json["newPassword"]
    pd_mgr = PasswordManager.query.filter(
        PasswordManager.user_id == current_user.id
    ).first()
    if not check_password_hash(pd_mgr.password, current_password):
        return make_response(jsonify(message="Current password do not match"), 403)
    pd_mgr.password = generate_password_hash(new_password, method="sha256")
    db_commit()
    return jsonify(message="Password updated successfully")


@view.route("/deleteUser")
@login_required
def delete_user(id):
    user_to_delete = User.query.get_or_404(id)
    memberships = Member.query.filter(Member.user_id == id)
    if memberships:
        flats = []
        for membership in memberships:
            flat = Flat.query.filter(Flat.id == membership.flat_id).first()
            society = Society.query.get_or_404(flat.society_id)
            flats.append({society.name: flat.flat_code})
        return make_response(
            jsonify(message=f"User is present as member in below flats: {flats}"), 409
        )
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return "User deleted successfully."
    except:
        return make_response(jsonify(message="User not deleted."), 500)


@view.route("/getUsers")
@login_required
def get_users(current_user):
    master_users = RoleManager.query.filter(RoleManager.role_id == 1)
    users = User.query.all()
    master_user_ids = [master_user.user_id for master_user in master_users]
    return jsonify(
        [
            {"name": user.name, "email": user.email}
            for user in users
            if user.id not in master_user_ids
        ]
    )


@view.route("/getSocietyUsers/<society_id_str>")
@login_required
def get_society_users(current_user, society_id_str):
    society_id = society_id_str.split("-")[-1]
    validate_get_permission(current_user, society_id)
    role_mgrs = RoleManager.query.filter(RoleManager.society_id == society_id)
    society_users = []
    for role_mgr in role_mgrs:
        society_user = User.query.get_or_404(role_mgr.user_id)
        society_users.append(
            {
                "id": role_mgr.id,
                "name": society_user.name,
                "email": society_user.email,
                "isAdmin": True if role_mgr.role_id == 2 else False,
            }
        )
    return jsonify(society_users)


@view.route("/addSocietyUser", methods=["POST"])
@login_required
def add_society_user(current_user):
    society_id = request.json["societyId"].split("-")[-1]
    validate_modify_permission(current_user, society_id)
    user_email = request.json["email"]
    is_admin = request.json["isAdmin"]
    user = User.query.filter(User.email == user_email).first()
    add_entity(
        RoleManager(
            user_id=user.id, society_id=society_id, role_id=(2 if is_admin else 3)
        )
    )
    db_commit()
    return jsonify(message="User added successfully")


@view.route("/updateSocietyUser", methods=["PUT"])
@login_required
def update_society_user(current_user):
    role_mgr_id = request.json["id"]
    role_mgr = RoleManager.query.get_or_404(role_mgr_id)
    validate_modify_permission(current_user, role_mgr.society_id)
    user_email = request.json["email"]
    is_admin = request.json["isAdmin"]
    user = User.query.filter(User.email == user_email).first()
    role_mgr.user_id = user.id
    role_mgr.role_id = 2 if is_admin else 3
    db_commit()
    return jsonify(message="User updated successfully")


@view.route("/deleteSocietyUser/<int:id>", methods=["DELETE"])
@login_required
def delete_society_user(current_user, id):
    role_mgr = RoleManager.query.get_or_404(id)
    validate_modify_permission(current_user, role_mgr.society_id)
    delete_entity(role_mgr)
    db_commit()
    return jsonify(message="User deleted successfully")


@view.route("/getSecurityQuestions")
@login_required
def get_security_questions(current_user):
    return to_json_response(SecurityQuestion.query.all())


@view.route("/setSecurityQuestions", methods=["POST"])
@login_required
def set_security_questions(current_user):
    current_password = request.json["currentPassword"]
    pd_mgr = PasswordManager.query.filter(
        PasswordManager.user_id == current_user.id
    ).first()
    if not check_password_hash(pd_mgr.password, current_password):
        return make_response(jsonify(message="Current password do not match"), 403)
    questions = request.json["questions"]
    existing_questions = UserQuestionAnswer.query.filter(
        UserQuestionAnswer.user_id == current_user.id
    )
    for existing_question in existing_questions:
        delete_entity(existing_question)
    for question in questions:
        print(question)
        add_entity(
            UserQuestionAnswer(
                user_id=current_user.id,
                question_id=question["id"],
                answer=question["answer"],
            )
        )
    db_commit()
    return jsonify(message="Questions set successfully")


