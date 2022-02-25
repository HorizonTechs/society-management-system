from flask import request, make_response, jsonify

from datetime import datetime

from ..models import (
    PaymentMethod,
    TransactionLog,
    db,
)
from ..methods.auth import login_required
from ..methods.transactions import *
from ..methods.societies import validate_get_permission, validate_modify_permission
from ..methods.flats import get_flat_owner
from ..methods.common import db_commit
from . import view


@view.route("/getTransactions/<society_id_str>")
@login_required
def get_transactions(current_user, society_id_str):
    society_id = int(society_id_str.split("-")[-1])
    validate_get_permission(current_user, society_id)
    transactions = TransactionLog.query.order_by(TransactionLog.date.desc()).limit(100)
    transactions_list = []
    for transaction in transactions:
        if transaction.sender_id==1 or check_account_in_society(
            transaction.sender_id, society_id
        ) or check_account_in_society(transaction.receiver_id, society_id):
            transactions_list.append(
                {
                    "public_id": transaction.public_id,
                    "sender": get_account_details(transaction.sender_id),
                    "receiver": get_account_details(transaction.receiver_id),
                    "amount": transaction.amount,
                    "date": datetime.strftime(transaction.date, "%Y-%m-%d"),
                    "paymentMethod": PaymentMethod.query.get_or_404(
                        transaction.method_id
                    ).method,
                    "transactionComment": get_transaction_comment(transaction.id),
                }
            )
    return jsonify(transactions_list)


@view.route("/addPaymentMethod", methods=["POST"])
@login_required
def add_payment_method():
    method = request.json["method"]
    new_method = PaymentMethod(method=method)
    try:
        db.session.add(new_method)
        db.session.commit()
    except:
        return make_response(jsonify(message="Method not added"), 500)
    return "Method added successfully"


@view.route("/getPaymentMethods")
@login_required
def get_payment_methods_response(current_user):
    return jsonify(to_dictionary_list(PaymentMethod.query.filter(PaymentMethod.id > 1)))


@view.route("/transferDueAmount", methods=["POST"])
@login_required
def transfer_due_amount(current_user):
    sender_flat_id = request.json["senderFlatId"]
    receiver_flat_id = request.json["receiverFlatId"]
    amount = request.json["amount"]
    comment = request.json["comment"]
    society_id = Flat.query.get_or_404(sender_flat_id).society_id
    if society_id!=Flat.query.get_or_404(receiver_flat_id).society_id:
        return make_response(jsonify(message="Sender and receiver should be from same society"), 403)
    validate_modify_permission(current_user, society_id)
    add_transaction(
        sender_id=Account.query.filter(
            Account.owner_id == get_flat_owner(sender_flat_id).id
        ).first().id,
        receiver_id=Account.query.filter(
            Account.owner_id == get_flat_owner(receiver_flat_id).id
        ).first().id,
        amount=amount,
        comment=comment,
    )
    db_commit()
    return jsonify(message="Amount transferred successfully")