from flask import jsonify, request, make_response

from ..models import (
    CountryCurrency,
    Society,
    Expense,
    FlatOwner,
    db,
    TransactionLog,
    Collection,
    CollectionType,
    Income,
    Flat,
    Account,
    Member,
    User,
)
from ..methods.auth import login_required
from ..methods.transactions import revert_transaction
from ..methods.societies import validate_get_permission, validate_modify_permission
from ..methods.common import log_if_error, to_json_response, add_entity, delete_entity, db_commit
from ..methods.collections import *
from . import view
    
@view.route("/getCollectionTypes")
@login_required
def get_collection_types(current_user):
    collection_types = CollectionType.query.all()
    return to_json_response(collection_types)


# Fix this
@view.route("/addCollectionType", methods=["POST"])
@login_required
def add_collection_type():
    new_type = CollectionType(type=request.json["type"])
    try:
        db.session.add(new_type)
        db.session.commit()
        return "Collection Type added successfully"
    except:
        return make_response(jsonify(message="Collection Type not added."), 500)


@view.route("/updateCollectionType", methods=["PUT"])
@login_required
def update_collection_type():
    collection_type = CollectionType.query.get_or_404(request.json["id"])
    collection_type.type = request.json["type"]
    try:
        db.session.commit()
        return "Collection Type updated successfully"
    except:
        return make_response(jsonify(message="Collection Type not updated."), 500)


@view.route("/deleteCollectionType/<int:id>", methods=["DELETE"])
@login_required
def delete_collection_type(id):
    collection_type_to_delete = CollectionType.query.get_or_404(id)
    collection = Collection.query.filter(Collection.type_id == id).first()
    if collection:
        return make_response(jsonify(message="This collection type is in use, cannot be deleted"), 403)
    try:
        db.session.delete(collection_type_to_delete)
        db.session.commit()
        return "Collection Type deleted successfully."
    except:
        return make_response(jsonify(message="Collection Type not deleted."), 500)


@view.route("/getCollections/<society_id_str>")
@login_required
@log_if_error
def get_collections(current_user, society_id_str):
    society_id = society_id_str.split("-")[-1]
    validate_get_permission(current_user, society_id)
    society = Society.query.get_or_404(society_id)
    currency = CountryCurrency.query.get_or_404(
        society.country_currency_id
    ).currency_code
    collections = Collection.query.filter(Collection.society_id == society_id)
    collections_list = []
    for collection in collections:
        collections_list.append(
            {
                "id": collection.id,
                "name": collection.name,
                "typeId": collection.type_id,
                "rate": collection.rate,
                "fixed": collection.fixed,
                "collectionStartDate": datetime.strftime(
                    collection.collection_start_date, "%Y-%m-%d"
                ),
            }
        )
    return jsonify(currency=currency, collections=collections_list)

@view.route("/addCollection", methods=["POST"])
@login_required
def add_collection(current_user):
    name = request.json["name"]
    type_id = request.json["typeId"]
    rate = int(request.json["rate"])
    fixed = bool(request.json["fixed"])
    society_id = request.json["societyId"].split("-")[-1]
    collection_start_date_str = request.json["collectionStartDate"]
    collection_start_date = datetime.strptime(collection_start_date_str, "%Y-%m-%d")

    validate_modify_permission(current_user, society_id)

    flats = Flat.query.filter(Flat.society_id==society_id)
    if len(list(flats)) == 0:
        return make_response(jsonify(message="Please add flats and members before adding collection"), 403)
    owner = None
    for flat in flats:
        owner = get_flat_owner(flat.id)
        if owner:
            break
    if not owner:
        return make_response(jsonify(message="Please add members to flats before adding collection"), 403)    

    new_collection = Collection(
        name=name,
        society_id=society_id,
        type_id=type_id,
        rate=rate,
        fixed=fixed,
        balance=0,
        collection_start_date=collection_start_date,
    )
    add_entity(new_collection, "Collection not added.")
    make_collection_deductions(new_collection.id)
    db_commit()
    return jsonify(message="Collection added successfully")


@view.route("/updateCollection", methods=["PUT"])
@login_required
def update_collection(current_user):
    collection_id = request.json["id"]

    collection = Collection.query.get_or_404(collection_id)
    validate_modify_permission(current_user, collection.society_id)
    # Reverting previous deduction
    revert_collection_deductions(collection_id)
    make_collection_deductions(collection_id)
    # Updating new changes
    collection.name = request.json["name"]
    collection.type_id = request.json["typeId"]
    collection.rate = int(request.json["rate"])
    collection.fixed = bool(request.json["fixed"])
    collection_start_date_str = request.json["collectionStartDate"]
    collection.collection_start_date = datetime.strptime(
        collection_start_date_str, "%Y-%m-%d"
    )
    db_commit("Collection details not updated")
    return jsonify(message="Collection updated successfully")

@view.route("/deleteCollection/<int:id>", methods=["DELETE"])
@login_required
def delete_collection(current_user, id):
    collection = Collection.query.get_or_404(id)
    validate_modify_permission(current_user, collection.society_id)
    flats = Flat.query.filter(Flat.society_id == collection.society_id)
    # Reverting previous deduction
    revert_collection_deductions(id)

    incomes = Income.query.filter(Income.collection_id == id)
    for income in incomes:
        delete_entity(income, "Unable to delete collection")

    expenses = Expense.query.filter(Expense.collection_id == id)
    for expense in expenses:
        delete_entity(expense, "Unable to delete collection")

    delete_entity(collection, "Unable to delete collection")
    db_commit("Unable to delete collection")
    return jsonify(message="Collection deleted successfully")


@view.route("/getCollectionSummary/<collection_id>")
@login_required
def get_collection_summary(current_user, collection_id):
    id = collection_id.split("-")[-1]
    collection = Collection.query.get_or_404(id)
    validate_get_permission(current_user, collection.society_id)
    # Fetching income summary
    incomes = Income.query.filter(Income.collection_id == id)
    total_expected = 0
    total_received = 0
    for income in incomes:
        total_expected += income.expected_amount
        transaction = TransactionLog.query.get(income.transaction_id)
        if transaction:
            total_received += TransactionLog.query.get_or_404(
                income.transaction_id
            ).amount
    # Fetching expense summary
    expenses = Expense.query.filter(Expense.collection_id == id)
    total_expenditure = 0
    for expense in expenses:
        total_expenditure += TransactionLog.query.get_or_404(
            expense.transaction_id
        ).amount
    previous_balance = 0
    previous_collection = Collection.query.get(int(id) - 1)
    if previous_collection:
        previous_balance = previous_collection.balance
    # Fetching currency
    currency = CountryCurrency.query.get_or_404(
        Society.query.get_or_404(collection.society_id).country_currency_id
    ).currency_code
    return jsonify(
        {
            "currency": currency,
            "collectionName": collection.name,
            "incomeSummary": {
                "totalExpected": total_expected,
                "totalReceived": total_received,
                "remaining": total_expected - total_received,
            },
            "expenseSummary": {
                "totalExpenditure": total_expenditure,
                "previousBalance": previous_balance,
                "balance": collection.balance,
            },
        }
    )


@view.route("/getIncomes/<collection_id>")
@login_required
def get_incomes(current_user, collection_id):
    id = collection_id.split("-")[-1]
    collection = Collection.query.get_or_404(id)
    validate_get_permission(current_user, collection.society_id)
    incomes = Income.query.filter(Income.collection_id == id)
    income_list = []
    total_expected = 0
    total_received = 0
    for income in incomes:
        total_expected += income.expected_amount
        owner = FlatOwner.query.get_or_404(income.owner_id)
        owner_member = Member.query.get_or_404(owner.member_id)
        flat = Flat.query.get_or_404(owner_member.flat_id)
        owner_user = User.query.get_or_404(owner_member.user_id)
        paid_amount = 0
        if income.transaction_id:
            transaction = TransactionLog.query.get_or_404(income.transaction_id)
            paid_amount = transaction.amount
            total_received += paid_amount
        status = True if (income.expected_amount - paid_amount) <= 0 else False
        income_list.append(
            {
                "id": income.id,
                "flatCode": flat.flat_code,
                "owner": owner_user.name,
                "expectedAmount": income.expected_amount,
                "isPaid": status,
            }
        )
    currency = CountryCurrency.query.get_or_404(
        Society.query.get_or_404(collection.society_id).country_currency_id
    ).currency_code
    return jsonify(
        {
            "currency": currency,
            "totalExpected": total_expected,
            "totalReceived": total_received,
            "incomes": income_list,
        }
    )


@view.route("/getExpenses/<collection_id>")
@login_required
def get_expenses(current_user, collection_id):
    id = collection_id.split("-")[-1]
    collection = Collection.query.get_or_404(id)
    validate_get_permission(current_user, collection.society_id)
    expenses = Expense.query.filter(Expense.collection_id == id)
    expense_list = []
    total_expense = 0
    for expense in expenses:
        transaction = TransactionLog.query.get_or_404(expense.transaction_id)
        total_expense += transaction.amount
        expense_list.append(
            {
                "id": expense.id,
                "expenseEntity": get_account_holder(transaction.receiver_id),
                "expenseAmount": transaction.amount,
            }
        )
    currency = CountryCurrency.query.get_or_404(
        Society.query.get_or_404(collection.society_id).country_currency_id
    ).currency_code
    return jsonify(
        {
            "currency": currency,
            "totalExpenditure": total_expense,
            "expenses": expense_list,
        }
    )


@view.route("/getDetailsForIncomeTransaction/<int:income_id>")
@login_required
def get_details_for_income_transaction(current_user, income_id):
    income = Income.query.get_or_404(income_id)
    collection = Collection.query.get_or_404(income.collection_id)
    validate_get_permission(current_user, collection.society_id)
    receiver_accounts = []
    flats = Flat.query.filter(Flat.society_id == collection.society_id)
    for flat in flats:
        owner_d = get_flat_owner(flat.id)
        if owner_d:
            receiver_account = Account.query.filter(
                Account.owner_id == owner_d.id
            ).first()
            receiver_accounts.append(
                {
                    "id": receiver_account.id,
                    "name": owner_d.name,
                    "email": owner_d.email,
                }
            )

    return jsonify(
        {
            "newOptions": {
                "receiverAccounts": receiver_accounts,
                "paymentMethods": get_payment_methods(),
            },
            "currentDetails": get_income_details(income_id),
        }
    )

@view.route("/updateIncome", methods=["PUT"])
@login_required
def update_income(current_user):
    income = Income.query.get_or_404(request.json["id"])
    collection = Collection.query.get_or_404(income.collection_id)
    validate_modify_permission(current_user, collection.society_id)
    amount = request.json["amount"]
    sender_id = request.json["senderId"]
    receiver_id = request.json["receiverId"]
    method_id = request.json["methodId"]
    date = request.json["date"]
    comment = request.json["transactionComment"]
    if income.transaction_id:
        revert_transaction(income.transaction_id)
    income.transaction_id = add_transaction(
        sender_id, receiver_id, amount, date, method_id, comment
    )
    update_collection_balance(income.collection_id)
    db_commit("Transaction not added")
    return jsonify(message="Income updated successfully!")


@view.route("/addExpense", methods=["POST"])
@login_required
def add_expense(current_user):
    collection_id = request.json["collectionId"].split("-")[-1]
    validate_modify_permission(current_user, Collection.query.get_or_404(collection_id).society_id)
    amount = request.json["amount"]
    sender_id = request.json["senderId"]
    receiver_id = request.json["receiverId"]
    date = request.json["date"]
    method_id = request.json["methodId"]
    comment = request.json["transactionComment"]
    transaction_id = add_transaction(
        amount=amount,
        sender_id=sender_id,
        receiver_id=receiver_id,
        date=date,
        method_id=method_id,
        comment=comment,
    )

    new_expense = Expense(collection_id=collection_id, transaction_id=transaction_id)
    add_entity(new_expense, "Expense not added")
    update_collection_balance(collection_id)
    db_commit("Collection balance not updated")
    return jsonify(message="Expense added successfully")


@view.route("/updateExpense", methods=["PUT"])
@login_required
def update_expense(current_user):
    expense_id = request.json["id"]
    amount = request.json["amount"]
    sender_id = request.json["senderId"]
    receiver_id = request.json["receiverId"]
    date = request.json["date"]
    method_id = request.json["methodId"]
    comment = request.json["transactionComment"]

    expense = Expense.query.get_or_404(expense_id)

    validate_modify_permission(current_user, Collection.query.get_or_404(expense.collection_id).society_id)    

    if expense:
        revert_transaction(expense.transaction_id)
        expense.transaction_id = add_transaction(
            amount=amount,
            sender_id=sender_id,
            receiver_id=receiver_id,
            date=date,
            method_id=method_id,
            comment=comment,
        )
    db_commit()
    return jsonify(message="Expense updated successfully")

@view.route("/getDetailsForExpenseTransaction/<int:expense_id>")
@login_required
def get_details_for_expense_transaction(current_user, expense_id):
    expense = Expense.query.get_or_404(expense_id)
    validate_modify_permission(current_user, Collection.query.get_or_404(expense.collection_id).society_id)
    return jsonify(
        {
            "newOptions": get_options_for_expense_transactions(expense.collection_id),
            "currentDetails": get_expense_details(expense_id),
        }
    )


@view.route("/getDetailsForAddExpenseTransaction/<collection_id>")
@login_required
def get_details_for_add_expense_transaction(current_user, collection_id):
    collection_id = collection_id.split("-")[-1]
    validate_modify_permission(current_user, Collection.query.get_or_404(collection_id).society_id)
    return jsonify({"newOptions": get_options_for_expense_transactions(collection_id)})


@view.route("/deleteExpense/<int:id>", methods=["DELETE"])
@login_required
def delete_expense(current_user, id):
    expense = Expense.query.get_or_404(id)
    validate_modify_permission(current_user, Collection.query.get_or_404(expense.collection_id).society_id)
    revert_transaction(expense.transaction_id)
    delete_entity(expense)
    db_commit()
    return jsonify(message="Expense deleted successfully")


@view.route("/transferMoney", methods=["POST", "PUT"])
@login_required
def transfer_money():
    amt = request.json["amount"]
    from_flat_id = request.json["from_flat_id"]
    to_flat_id = request.json["to_flat_id"]
    method_id = request.json["method_id"]
    comment = request.json["comment"]

    transaction_id = add_transaction(
        amount=amt,
        sender_id=from_flat_id,
        receiver_id=to_flat_id,
        method_id=method_id,
        comment=comment,
    )
    if transaction_id:
        from_flat = Flat.query.get_or_404(from_flat_id)
        from_flat.due_amount -= amt
        to_flat = Flat.query.get_or_404(to_flat_id)
        to_flat.due_amount += amt
        try:
            db.session.commit()
            return "Amount transferred successfully"
        except:
            return make_response(jsonify(message="Balance not updated"), 500)