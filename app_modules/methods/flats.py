from flask import jsonify, make_response, abort

from ..models import (
    AccountType,
    FlatOwner,
    db,
    User,
    Member,
    Account,
)
from .common import add_entity, db_flush, Map

# Flat views -------------------------------------------------------


def get_flat_owner(flat_id):
    members = Member.query.filter(Member.flat_id == flat_id)
    for member in members:
        flat_owner = FlatOwner.query.filter(FlatOwner.member_id == member.id).first()
        if flat_owner:
            user = User.query.get_or_404(member.user_id)
            user_d = {
                "id": flat_owner.id,
                "name": user.name,
                "email": user.email,
                "due_amount": Account.query.filter(Account.owner_id == flat_owner.id)
                .first()
                .due_amount,
            }
            return Map(user_d)


def add_flat_members(flat_id, owner, members):
    """
    Here `owner` and `members` are emailId of respective users.
    """
    owner_d = get_flat_owner(flat_id)
    # Deleting existing members
    members_db = Member.query.filter(Member.flat_id == flat_id)
    if members_db:
        try:
            for member in members_db:
                db.session.delete(member)
        except:
            return abort(make_response(jsonify(message="Member not deleted."), 500))
        db_flush("Members not deleted")
    # Adding members
    for member in members:
        user = User.query.filter(User.email == member).first()
        new_member = Member(user_id=user.id, flat_id=flat_id)
        add_entity(new_member, f"Problem adding member {member}")
    owner_user = User.query.filter(User.email == owner).first()
    owner_member = Member.query.filter(
        Member.user_id == owner_user.id, Member.flat_id == flat_id
    ).first()
    if owner_d:
        FlatOwner.query.get_or_404(owner_d.id).member_id = owner_member.id
        db_flush("Problem updating owner")
    else:
        new_owner = FlatOwner(member_id=owner_member.id)
        add_entity(new_owner, "Problem adding owner")
        account_type_id = (
            AccountType.query.filter(AccountType.account_type == "Owner").first().id
        )
        owner_account = Account(
            account_type_id=account_type_id, owner_id=new_owner.id, due_amount=0
        )
        add_entity(owner_account, "Problem adding owner account")