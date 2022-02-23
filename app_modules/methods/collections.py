from datetime import datetime

from ..models import (
    Expense,
    FlatOwner,
    TransactionComment,
    TransactionLog,
    Collection,
    Income,
    Flat,
    Account,
    AccountType,
    Member,
    User,
)
from .common import (
    add_entity,
    db_flush,
)
from .transactions import add_transaction, get_payment_methods
from .flats import get_flat_owner
    
def revert_collection_deductions(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    flats = Flat.query.filter(Flat.society_id == collection.society_id)
    total_expected = 0
    for flat in flats:
        if collection.fixed:
            due_amount = collection.rate
        else:
            due_amount = flat.area * collection.rate
        owner = get_flat_owner(flat.id)
        if owner:
            owner_db = FlatOwner.query.get_or_404(owner.id)
            Account.query.filter(
                Account.owner_id == owner_db.id
            ).first().due_amount -= due_amount
            total_expected += due_amount
    add_transaction(
        sender_id=3,
        receiver_id=2,
        amount=total_expected,
        method_id=1,
        comment="Due amount reverted in all flat owners by system for collection '%s'"
        % collection.name,
    )

def make_collection_deductions(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    flats = Flat.query.filter(Flat.society_id == collection.society_id)
    total_expected = 0
    for flat in flats:
        if collection.fixed:
            expected_amount = collection.rate
        else:
            expected_amount = flat.area * collection.rate
        owner = get_flat_owner(flat.id)
        if owner:
            new_income = Income(
                owner_id=owner.id,
                expected_amount=expected_amount,
                collection_id=collection_id,
            )
            add_entity(new_income, "Collection not added")
            owner_db = FlatOwner.query.get_or_404(owner.id)
            Account.query.filter(
                Account.owner_id == owner_db.id
            ).first().due_amount += expected_amount
            total_expected += expected_amount
    add_transaction(
        sender_id=1,
        receiver_id=2,
        amount=total_expected,
        method_id=1,
        comment="Due amount updated in all flat owners by system for collection '%s'"
        % collection.name,
    )

def get_account_holder(account_id):
    account = Account.query.get_or_404(account_id)
    account_holder = ""
    if account.owner_id:
        user = User.query.get_or_404(
            Member.query.get_or_404(
                FlatOwner.query.get_or_404(account.owner_id).member_id
            ).user_id
        )
        account_holder = f"{user.name}({user.email})"
    else:
        account_holder = AccountType.query.get_or_404(
            account.account_type_id
        ).account_type
    return account_holder


def update_collection_balance(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    incomes = Income.query.filter(Income.collection_id == collection_id)
    total_received = 0
    for income in incomes:
        transaction = TransactionLog.query.get(income.transaction_id)
        if transaction:
            total_received += TransactionLog.query.get_or_404(
                income.transaction_id
            ).amount
    expenses = Expense.query.filter(Expense.collection_id == collection_id)
    total_expenditure = 0
    for expense in expenses:
        total_expenditure += TransactionLog.query.get_or_404(
            expense.transaction_id
        ).amount
    previous_balance = 0
    previous_collection = Collection.query.get(int(collection_id) - 1)
    if previous_collection:
        previous_balance = previous_collection.balance
    collection.balance = previous_balance + total_received - total_expenditure
    db_flush("Unable to update collection balance")


def get_expense_details(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    transaction = TransactionLog.query.get_or_404(expense.transaction_id)
    transaction_comment_db = TransactionComment.query.filter(
        TransactionComment.transaction_id == transaction.id
    ).first()
    transaction_comment = ""
    if transaction_comment_db:
        transaction_comment = transaction_comment_db.comment
    return {
        "amount": transaction.amount,
        "receiverId": transaction.receiver_id,
        "senderId": transaction.sender_id,
        "date": datetime.strftime(transaction.date, "%Y-%m-%d"),
        "methodId": transaction.method_id,
        "transactionComment": transaction_comment,
    }


def get_options_for_expense_transactions(collection_id):
    account_types = AccountType.query.filter(AccountType.id > 3)
    receiver_accounts = []
    for account_type in account_types:
        expense_account = Account.query.filter(
            Account.account_type_id == account_type.id
        ).first()
        receiver_accounts.append(
            {"id": expense_account.id, "name": account_type.account_type}
        )
    flats = Flat.query.filter(
        Flat.society_id == Collection.query.get_or_404(collection_id).society_id
    )
    sender_accounts = []
    for flat in flats:
        owner_d = get_flat_owner(flat.id)
        if owner_d:
            sender_accounts.append(
                {
                    "id": Account.query.filter(Account.owner_id == owner_d.id)
                    .first()
                    .id,
                    "name": owner_d.name,
                    "email": owner_d.email,
                }
            )
    return {
        "senderAccounts": sender_accounts,
        "receiverAccounts": receiver_accounts,
        "paymentMethods": get_payment_methods(),
    }


def get_income_details(income_id):
    income = Income.query.get_or_404(income_id)
    amount = 0
    transaction_comment = ""
    receiver_account_id = ""
    date = ""
    method_id = ""
    sender_account_id = (
        Account.query.filter(Account.owner_id == income.owner_id).first().id
    )
    if income.transaction_id:
        transaction = TransactionLog.query.get_or_404(income.transaction_id)
        receiver_account_id = transaction.receiver_id
        date = datetime.strftime(transaction.date, "%Y-%m-%d")
        method_id = transaction.method_id
        amount = transaction.amount
        transaction_comment_db = TransactionComment.query.filter(
            TransactionComment.transaction_id == income.transaction_id
        ).first()
        if transaction_comment_db:
            transaction_comment = transaction_comment_db.comment
    return {
        "senderId": sender_account_id,
        "amount": amount,
        "receiverId": receiver_account_id,
        "date": date,
        "methodId": method_id,
        "transactionComment": transaction_comment,
    }