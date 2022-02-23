from flask import ( Blueprint, redirect, render_template,
                    url_for, request, session, g, Response)
from sqlalchemy.sql.base import Executable
from werkzeug.wrappers import response
from .models import *
from .encrypter import decrypt_data, decrypt, load_key
import json

view = Blueprint('view', __name__)
key = load_key()

def to_dictionary_list(objects):
    output = []
    for obj in objects:
        objd = vars(obj)
        objd.pop("_sa_instance_state", None)
        output.append(objd)
    return output

def to_json_response(objects):
    output = []
    for obj in objects:
        objd = vars(obj)
        objd.pop("_sa_instance_state", None)
        output.append(objd)
    return make_response(jsonify(message=json.dumps(output),  mimetype='application/json')

def add_to_db(obj, sucess_msg = "Added successfully.", failure_msg= "Not added"):
    try:
        db.session.add(obj)
        db.session.commit()
        return make_response(jsonify(message=sucess_msg)
    except:
        return make_response(jsonify(message=failure_msg, status = 500)

def update_db(sucess_msg = "Updated successfully.", failure_msg= "Not Updated"):
    try:
        db.session.commit()
        return make_response(jsonify(message=sucess_msg)
    except:
        return make_response(jsonify(message=failure_msg, status = 500)

# @view.before_request
# def before_request():
#     if 'user_id' in session:
#         user = User.query.get_or_404(session['user_id'])
#         g.user = user
def check_society(society_name, society_address, society_pincode):
    existing_society = Society.query.filter(
                        Society.name == society_name, 
                        Society.address == society_address, 
                        Society.pin_code == society_pincode).first()
    return existing_society

@view.route("/")
def index():
    if "user_id" in session:
        return redirect("/home")
    return redirect("/login")
    

@view.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        
        username = request.json['username']
        password = request.json['password']

        user = User.query.filter(User.email == username).first()

        if user and decrypt_data(user.password, key) == decrypt(password):
            session['user_id'] = user.id
            # g.user = user
            return redirect("/home")

        return make_response(jsonify(message="Username or Password is incorrect", status=404)
    return render_template('login.html')

@view.route('/home')
def home():
    if not ("user_id" in session):
        return redirect("/login")
    return render_template('index.html')

# Society List Component --------------------------------------------------------------------
@view.route('/societies')
def get_societies():
    # if not ("user_id" in session):
    #     return redirect("/login")
    societies = Society.query.all()
    return to_json_response(societies)

@view.route('/addSociety', methods=['POST'])
def add_society():
    society_name = request.json['name']
    society_address = request.json['address']
    society_pincode = request.json['pin_code']
    existing_society = check_society(society_name, society_address, society_pincode)
    if existing_society:
        return make_response(jsonify(message="Society with same name and address already exist", status=409)
    new_society = Society(name = society_name, address = society_address, pin_code = society_pincode)
    return add_to_db(new_society, "Society added successfully", "Society not added")

@view.route("/updateSociety", methods=['PUT'])
def update_society():
    society_name = request.json['name']
    society_address = request.json['address']
    society_pincode = request.json['pin_code']
    society = Society.query.get_or_404(request.json['id'])
    existing_society = check_society(society_name, society_address, society_pincode)
    if existing_society:
        return make_response(jsonify(message="Society with same name and address already exist", status=409)
    society.name = society_name
    society.address = society_address
    society.pin_code = society_pincode
    return update_db("Society updated successfully", "Society not updated")

@view.route("/deleteSociety/<int:id>", methods=['DELETE'])
def delete_society(id):
    society_to_delete = Society.query.get_or_404(id)
    try:
        db.session.delete(society_to_delete)
        db.session.commit()
        return "Society deleted successfully."
    except:
        return make_response(jsonify(message="Society not deleted.", status = 500)

# Flat List Component --------------------------------------------------------------------    
@view.route('/societies/<int:society_id>')
def get_society_flats(society_id):
    # if not ("user_id" in session):
    #     return redirect("/login")
    flats = Flat.query.filter(Flat.society_id == society_id)
    society_members = []
    for flat in flats:
        owner = User.query.get_or_404(Member.query.get_or_404(flat.owner_id).user_id)
        # members = Member.query.filter(Member.flat_id == flat.id)
        # users = []
        # for member in members:
        #     user = User.query.get_or_404(member.user_id)
        #     users.append({
        #         "name": user.name,
        #         "email": user.email,
        #         "phone": user.phone
        #     })
        society_members.append({
            "flat_id": flat.id,
            "flat_code": flat.flat_code,
            "balance": flat.balance,
            "owner": owner.name
        })
    return make_response(jsonify(message=json.dumps(society_members),  mimetype='application/json')

@view.route('/addFlat', methods=['POST'])
def add_flat():
    flat_code = request.json['flat_code']
    society_id = request.json['society_id']
    balance = request.json['balance']
    owner = request.json['owner']
    new_flat = Flat(flat_code = flat_code, society_id = society_id, balance = balance)
    response = add_to_db(new_flat, failure_msg="Flat not added")
    if response.status == 500:
        return response

    new_user = User(name = owner['name'], email = owner['email'], phone = owner['phone'])
    response = add_to_db(new_user, failure_msg="User not added")
    if response.status == 500:
        return response

    new_member = Member(user_id = new_user.id, flat_id = new_flat.id)
    response = add_to_db(new_member, failure_msg="Member not added")
    if response.status == 500:
        return response

    new_flat.owner_id = new_member.id
    return update_db(sucess_msg="Flat added successfully", failure_msg="Owner not added")

@view.route('/changeFlatOwner', methods=['PUT'])
def update_flat():
    flat_id = request.json['flat_id']
    owner_id = request.json['owner_id']
    flat = Flat.query.get_or_404(flat_id)
    flat.owner_id = owner_id 
    try:
        db.session.commit()
        return "Owner updated successfully"
    except:
        return make_response(jsonify(message="Owner not updated", status = 500)

@view.route('/renameFlat', methods=['PUT'])
def rename_flat():
    flat_id = request.json['flat_id']
    flat_code = request.json['flat_code']
    flat = Flat.query.get_or_404(flat_id)
    flat.flat_code = flat_code
    try:
        db.session.commit()
        return "Flat code updated successfully"
    except:
        return make_response(jsonify(message="Flat code not updated", status = 500)

@view.route('/addMember', methods=['POST'])
def add_member():
    flat_id = request.json['flat_id']
    name = request.json['name']
    email = request.json['email']
    phone = request.json['phone']
    new_user = User(name = name, email = email, phone = phone)
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return make_response(jsonify(message="User not added", status = 500)
    new_member = Member(user_id = new_user.id, flat_id = flat_id)
    try:
        db.session.add(new_member)
        db.session.commit()
        return "Member added successfully"
    except:
        return make_response(jsonify(message="Member not added", status = 500)
    # email = request.json['email']
    # phone = request.json['phone']
    # society_id = request.json['flat_id']
    # new_society = Society(name = society_name, address = society_address, pin_code = society_pincode)
    # try:
    #     db.session.add(new_society)
    #     db.session.commit()
    #     return "Society added successfully."
    # except:
    #     return make_response(jsonify(message="Society not added.", status = 500)

@view.route("/updateMember", methods=['PUT'])
def update_member():
    society_name = request.json['name']
    society_address = request.json['address']
    society_pincode = request.json['pin_code']
    society = Society.query.get_or_404(request.json['id'])
    existing_society = check_society(society_name, society_address, society_pincode)
    if existing_society:
        return make_response(jsonify(message="Society with same name and address already exist", status=409)
    society.name = society_name
    society.address = society_address
    society.pin_code = society_pincode
    try:
        db.session.commit()
        return "Society updated successfully."
    except:
        return make_response(jsonify(message="Society not updated.", status = 500)

@view.route("/deleteMember/<int:id>", methods=['DELETE'])
def delete_member(id):
    society_to_delete = Society.query.get_or_404(id)
    try:
        db.session.delete(society_to_delete)
        db.session.commit()
        return "Society deleted successfully."
    except:
        return make_response(jsonify(message="Society not deleted.", status = 500)

