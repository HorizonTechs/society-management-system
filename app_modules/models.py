from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from .CustomBaseQuery import CustomBaseQuery

db = SQLAlchemy(query_class=CustomBaseQuery)

class Society(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    country_currency_id = db.Column(db.Integer, db.ForeignKey('country_currency.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('name', 'address', 'pin_code'),)

    def __repr__(self):
        return '<Society %r>' % self.id

class CountryCurrency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(50), unique=True)
    currency_name = db.Column(db.String(50))
    currency_code = db.Column(db.String(3))

    def __repr__(self):
        return '<CountryCurrency %r>' % self.id

class PasswordManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)

    def __repr__(self):
        return '<Password %r>' % self.id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable = False, unique=True)
    phone = db.Column(db.String(14), unique=True)
    last_logged_in = db.Column(db.DateTime)

    def __repr__(self):
        return '<User %r>' % self.id

class RoleManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'), default=3)

    __table_args__ = (db.UniqueConstraint('user_id', 'society_id'),)

    def __repr__(self):
        return '<RoleManager %r>' % self.id

class UserQuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('security_question.id'), nullable=False)
    answer = db.Column(db.String(120), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'question_id'),)

    def __repr__(self):
        return '<UserQuestionAnswer %r>' % self.id

class SecurityQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_type_id = db.Column(db.Integer, db.ForeignKey('account_type.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('flat_owner.id'), unique=True)
    due_amount = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<Account %r>' % self.id

class AccountType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<AccountType %r>' % self.id

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'flat_id'),)

    def __repr__(self):
        return '<Member %r>' % self.id

class Flat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'), nullable=False)
    flat_code = db.Column(db.String(10), nullable=False)
    area = db.Column(db.Integer, nullable=False)

    __table_args__ = (db.UniqueConstraint('society_id', 'flat_code'),)

    def __repr__(self):
        return '<Flat %r>' % self.id

class FlatOwner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), unique=True)

    def __repr__(self):
        return '<FlatOwner %r>' % self.id

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    society_id = db.Column(db.Integer, db.ForeignKey('society.id'), nullable = False)
    type_id  = db.Column(db.Integer, db.ForeignKey('collection_type.id'), nullable = False)
    rate = db.Column(db.Integer, nullable = False)
    fixed = db.Column(db.Boolean, nullable = False)
    balance = db.Column(db.Integer, nullable = False)
    collection_start_date = db.Column(db.DateTime, default = datetime.utcnow, nullable=False)

    def __repr__(self):
        return '<Collection %r>' % self.id

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('flat_owner.id'), nullable = False)
    expected_amount = db.Column(db.Integer, nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction_log.id'), unique=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable = False)

    __table_args__ = (db.UniqueConstraint('collection_id', 'owner_id'),)

    def __repr__(self):
        return '<Income %r>' % self.id

class CollectionType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable = False, unique=True)

    def __repr__(self):
        return '<CollectionType %r>' % self.id

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction_log.id'), nullable = False, unique=True)

    def __repr__(self):
        return '<Expense %r>' % self.id

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(20), nullable = False, unique=True)

    def __repr__(self):
        return '<PaymentMethod %r>' % self.id

class TransactionComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(200))
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction_log.id'), nullable=False, unique=True)

class TransactionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(36), unique=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # account_id
    receiver_id = db.Column(db.Integer, db.ForeignKey('account.id'))  # account_id
    amount = db.Column(db.Integer, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), nullable = False)

    def __repr__(self):
        return '<TransactionLog %r>' % self.id

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable = False, unique=True)

    def __repr__(self):
        return '<UserRole %r>' % self.id
