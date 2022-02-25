from flask import jsonify, request, make_response

from ..models import Society, Flat, CountryCurrency
from ..methods.auth import login_required
from ..methods.flats import get_flat_owner
from ..methods.common import add_entity, delete_entity, db_commit, log_if_error
from ..methods.societies import *

from . import view

@view.route("/getSocieties")
@login_required
@log_if_error
def get_societies(current_user):
    abort(make_response(jsonify(message="this is some error"), 500))
    user_roles = RoleManager.query.filter(RoleManager.user_id==current_user.id)
    if user_roles.first() and user_roles.first().role_id==1:
        societies = Society.query.all()
    else:
        societies = [Society.query.get_or_404(user_role.society_id) for user_role in user_roles]
    society_list = []
    for society in societies:
        society_list.append(
            {
                "id": society.id,
                "name": society.name,
                "address": society.address,
                "pin_code": society.pin_code,
                "countryId": society.country_currency_id,
            }
        )
    return jsonify(society_list)


@view.route("/getSocietyFlats/<name_id>")
@login_required
def get_society_flats(current_user, name_id):
    society_id = name_id.split("-")[-1]
    validate_get_permission(current_user, society_id)
    flats = Flat.query.filter(Flat.society_id == society_id)
    society_flats = []
    currency = CountryCurrency.query.get_or_404(
        Society.query.get_or_404(society_id).country_currency_id
    ).currency_code
    for flat in flats:
        owner_name = None
        due_amount = None
        owner_user = get_flat_owner(flat.id)
        if owner_user:
            owner_name = owner_user.name
            due_amount = owner_user.due_amount
        society_flats.append(
            {
                "id": flat.id,
                "code": flat.flat_code,
                "area": flat.area,
                "owner": owner_name,
                "dueAmount": due_amount,
            }
        )
    return jsonify(currency=currency, flats=society_flats)


@view.route("/getCountries")
@login_required
def get_coutries(current_user):
    countries = CountryCurrency.query.all()
    country_list = []
    for country in countries:
        country_list.append({"id": country.id, "name": country.country_name})
    return jsonify(country_list)


@view.route("/addSociety", methods=["POST"])
@login_required
def add_society(current_user):
    society_name = request.json["name"]
    society_address = request.json["address"]
    society_pincode = request.json["pin_code"]
    country_id = request.json["countryId"]
    existing_society = check_society(society_name, society_address, society_pincode)
    if existing_society:
        return make_response("Society with same name and address already exist", 409)
    new_society = Society(
        name=society_name,
        address=society_address,
        pin_code=society_pincode,
        country_currency_id=country_id,
    )
    add_entity(new_society, "Society not added")
    add_entity(RoleManager(user_id = current_user.id, society_id=new_society.id, role_id=2))
    db_commit()
    return jsonify(message="Society added successfully.")


@view.route("/updateSociety", methods=["PUT"])
@login_required
def update_society(current_user):
    society_id = request.json["id"]
    society_name = request.json["name"]
    society_address = request.json["address"]
    society_pincode = request.json["pin_code"]
    country_id = request.json["countryId"]

    validate_modify_permission(current_user, society_id)

    society = Society.query.get_or_404(society_id)
    existing_society = check_society(society_name, society_address, society_pincode)
    if existing_society and existing_society.id != society_id:
        return make_response(
            jsonify(message="Society with same name and address already exist"), 409
        )
    society.name = society_name
    society.address = society_address
    society.pin_code = society_pincode
    society.country_currency_id = country_id
    db_commit("Society not udpated")
    return jsonify(message="Society updated successfully.")


@view.route("/deleteSociety/<int:id>", methods=["DELETE"])
@login_required
def delete_society(current_user, id):
    validate_modify_permission(current_user, id)
    society_to_delete = Society.query.get_or_404(id)
    flat = Flat.query.filter(Flat.society_id == id).first()
    if flat:
        return make_response(
            jsonify(
                message="Some flats are present inside the society, cannot be deleted"
            ),
            403,
        )
    role_mgrs = RoleManager.query.filter(RoleManager.society_id==id)
    for role_mgr in role_mgrs:
        delete_entity(role_mgr)
    delete_entity(society_to_delete, "Soceity not deleted")
    db_commit()
    return jsonify(message="Society deleted successfully.")