import os
import random
from flask import jsonify, make_response, abort

from datetime import datetime

from ..models import db

def to_dictionary_list(objects):
    output = []
    for obj in objects:
        objd = vars(obj)
        objd.pop("_sa_instance_state", None)
        output.append(objd)
    return output

def to_json_response(db_objs):
    output = []
    for obj in db_objs:
        objd = vars(obj)
        objd.pop("_sa_instance_state", None)
        output.append(objd)
    return jsonify(output)

def add_entity(entity, error="Entity not added", status=500):
    try:
        db.session.add(entity)
        db.session.flush()
    except:
        abort(make_response(jsonify(message=error), status))

def delete_entity(entity, error="Entity not deleted", status=500):
    try:
        db.session.delete(entity)
        db.session.flush()
    except:
        abort(make_response(jsonify(message=error), status))

def db_flush(error="Problem updating data", status=500):
    try:
        db.session.flush()
    except:
        abort(make_response(jsonify(message=error), status))

def db_commit(error="Something went wrong", status=500):
    try:
        db.session.commit()
    except:
        abort(make_response(jsonify(message=error), status))

class Map(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def log_error(error):
    file = open(os.path.join(os.getcwd(), "app_modules",
             "logs",f"{datetime.now().strftime('%Y%m%d')}.log"), "a")
    file.write(f'{datetime.now()} '
            f'---------------------------------------------------------------------\n{str(error)}\n')
    file.close()

def generate_invitation_code():
    random_number = random.randint(100000, 999999)
    file = open(os.path.join(os.getcwd(), "app_modules", "security", "inivitation_code.key"), "w")
    file.write(str(random_number))
    file.close()

def get_invitation_code():
    file = open(os.path.join(os.getcwd(), "app_modules", "security", "inivitation_code.key"), "r")
    return file.read()