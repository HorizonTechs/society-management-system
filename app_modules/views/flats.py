from flask import jsonify, make_response, abort, request

from ..models import (
    FlatOwner,
    TransactionLog,
    db,
    Flat,
    User,
    Member,
    Account,
)
from ..methods.auth import login_required
from ..methods.flats import *
from ..methods.societies import validate_get_permission, validate_modify_permission
from ..methods.common import db_commit, delete_entity
from . import view

# Flat views -------------------------------------------------------

@view.route("/addFlat", methods=["POST"])
@login_required
def add_flat(current_user):
    flat_code = request.json["code"]
    area = request.json["area"]
    society_id = request.json["societyId"].split("-")[-1]
    members = request.json["members"]
    owner = request.json["owner"]

    validate_modify_permission(current_user, society_id)

    if owner:
        if not (owner in members):
            return make_response(jsonify(message="Invalid input"), 400)
    else:
        if len(members) > 0:
            return make_response(jsonify(message="Invalid input"), 400)
    flat = Flat.query.filter(
        Flat.society_id == society_id, Flat.flat_code == flat_code
    ).first()
    if flat:
        return make_response(
            jsonify(message="Flat with same flat code already exist in this society"),
            409,
        )
    new_flat = Flat(flat_code=flat_code, area=area, society_id=society_id)
    add_entity(new_flat, "Flat not added")
    if owner:
        add_flat_members(new_flat.id, owner, members)
    db_commit("Flat not added")
    return jsonify(message="Flat added successfully")


@view.route("/updateFlat", methods=["PUT"])
@login_required
def update_flat(current_user):
    flat_id = request.json["id"]
    flat_code = request.json["code"]
    area = request.json["area"]
    members = request.json["members"]
    owner = request.json["owner"]
    is_change = False

    # Updating data in Flat table
    flat = Flat.query.get_or_404(flat_id)
    
    validate_modify_permission(current_user, flat.society_id)

    flat.flat_code = flat_code
    flat.area = area
    if owner:
        if not (owner in members):
            return make_response(jsonify(message="Invalid input"), 400)
        if not is_change:
            db_members = Member.query.filter(Member.flat_id == flat.id).all()
            if len(members) != len(db_members):
                is_change = True
            else:
                for i in range(len(members)):
                    if db_members[i] != members[i]:
                        is_change = True
                        break
    if is_change:
        # Adding new members
        if owner:
            add_flat_members(flat_id, owner, members)
    db_commit("Flat not updated")
    return jsonify(message="Flat updated successfully")


@view.route("/deleteFlat/<int:id>", methods=["DELETE"])
@login_required
def delete_flat(current_user, id):
    # Put comment in front-end "All the members of flat will be deleted"
    flat_to_delete = Flat.query.get_or_404(id)

    validate_modify_permission(current_user, flat_to_delete.society_id)
    
    owner = get_flat_owner(id)
    if owner:
        owner_account = Account.query.filter(Account.owner_id == owner.id).first()
        if owner_account:
            as_sender = TransactionLog.query.filter(
                TransactionLog.sender_id == owner_account.id
            ).first()
            as_receiver = TransactionLog.query.filter(
                TransactionLog.receiver_id == owner_account.id
            ).first()
            if as_sender or as_receiver:
                return make_response(
                    jsonify(
                        message="Owner is present in transaction, cannot be deleted"
                    ),
                    403,
                )
        members_db = Member.query.filter(Member.flat_id == id)
        if members_db:
            try:
                for member in members_db:
                    db.session.delete(member)
            except:
                return make_response(jsonify(message="Member not deleted."), 500)
            db_flush("Members not deleted")
        delete_entity(FlatOwner.query.get_or_404(owner.id))
        delete_entity(Account.query.filter(Account.owner_id == owner.id).first())
    delete_entity(flat_to_delete, "Flat not deleted")
    db_commit()
    return jsonify(message="Flat deleted successfully")


# Member views -------------------------------------------------------
@view.route("/getFlatMembers/<int:flat_id>")
@login_required
def get_flat_members(current_user, flat_id):
    validate_get_permission(current_user, Flat.query.get_or_404(flat_id).society_id)
    members = Member.query.filter(Member.flat_id == flat_id)
    owner = get_flat_owner(flat_id)
    if owner:
        members_list = []
        for member in members:
            user = User.query.get_or_404(member.user_id)
            members_list.append({"name": user.name, "email": user.email})
        return jsonify(
            {
                "owner": {"name": owner.name, "email": owner.email},
                "members": members_list,
            }
        )
    else:
        return jsonify({"owner": None, "members": None})