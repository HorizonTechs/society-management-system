from flask import jsonify, make_response, abort

from ..models import Society, RoleManager


def validate_get_permission(
    user, society_id, msg="You do not have permission to view this society"
):
    role_mgr = get_role_manager(user, society_id)
    if role_mgr and (role_mgr.role_id in [1, 2, 3]):
        return True
    abort(make_response(jsonify(message=msg), 403))


def validate_modify_permission(user, society_id, msg="You do not have permission"):
    role_mgr = get_role_manager(user, society_id)
    if role_mgr and (role_mgr.role_id in [1, 2]):
        return True
    abort(make_response(jsonify(message=msg), 403))

def get_role_manager(user, society_id):
    master_role = RoleManager.query.filter(
        RoleManager.user_id == user.id, RoleManager.role_id == 1
    ).first()
    if master_role:
        return master_role
    role_mgr = RoleManager.query.filter(
        RoleManager.user_id == user.id, RoleManager.society_id == society_id
    ).first()
    if role_mgr:
        return role_mgr


def check_society(society_name, society_address, society_pincode):
    existing_society = Society.query.filter(
        Society.name == society_name,
        Society.address == society_address,
        Society.pin_code == society_pincode,
    ).first()
    return existing_society
