from datetime import datetime
import uuid
from ..models import (
    AccountType,
    FlatOwner,
    Member,
    PaymentMethod,
    TransactionLog,
    db,
    Flat,
    User,
    Account,
    TransactionComment,
)
from .common import add_entity, db_flush, to_dictionary_list


def get_account_details(account_id):
    account = Account.query.get_or_404(account_id)
    name = ""
    flat_code = ""
    if account.owner_id:
        member = Member.query.get_or_404(
            FlatOwner.query.get_or_404(account.owner_id).member_id
        )
        flat_code = Flat.query.get_or_404(member.flat_id).flat_code
        user = User.query.get_or_404(member.user_id)
        name = user.name
    else:
        name = AccountType.query.get_or_404(account.account_type_id).account_type
    return {"name": name, "flatCode": flat_code}


def check_account_in_society(account_id, society_id):
    account = Account.query.get_or_404(account_id)
    if account.owner_id:
        member = Member.query.get_or_404(
            FlatOwner.query.get_or_404(account.owner_id).member_id
        )
        if society_id == Flat.query.get_or_404(member.flat_id).society_id:
            return True
    return False


def add_transaction(
    sender_id="",
    receiver_id="",
    amount="",
    date=datetime.now(),
    method_id=1,
    comment="",
):
    amount = int(amount)
    if not date.__class__ == datetime:
        date = datetime.strptime(date, "%Y-%m-%d")
    public_id=""
    for i in range(3):
        public_id = str(uuid.uuid4()).split("-")[0]
        if not TransactionLog.query.filter(TransactionLog.public_id==public_id):
            break
    new_transaction = TransactionLog(
        public_id=public_id,
        sender_id=sender_id,
        receiver_id=receiver_id,
        amount=amount,
        date=date,
        method_id=method_id,
    )
    add_entity(new_transaction, "Transaction not added")
    if comment:
        new_transaction_comment = TransactionComment(
            comment=comment, transaction_id=new_transaction.id
        )

        add_entity(new_transaction_comment, "Transaction comment not added")

    Account.query.get_or_404(sender_id).due_amount -= amount
    Account.query.get_or_404(receiver_id).due_amount += amount

    db_flush("Sender and receiver due amounts not updated")
    return new_transaction.id


def revert_transaction(transaction_id):
    transaction = TransactionLog.query.get_or_404(transaction_id)
    transaction_id = add_transaction(
        sender_id=transaction.receiver_id,
        receiver_id=transaction.sender_id,
        amount=transaction.amount,
        method_id=transaction.method_id,
        comment="Reverted transaction %s" % (
            TransactionLog.query.get_or_404(transaction_id).public_id),
    )

    db_flush("Transaction not reverted")
    return transaction_id


def get_payment_methods():
    return to_dictionary_list(PaymentMethod.query.filter(PaymentMethod.id > 1))


def get_transaction_comment(transaction_id):
    transaction_comment = TransactionComment.query.filter(
        TransactionComment.transaction_id == transaction_id
    ).first()
    if transaction_comment:
        return transaction_comment.comment
