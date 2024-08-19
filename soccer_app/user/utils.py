from flask import request, render_template, redirect, url_for, Blueprint, jsonify, session, json
from functools import wraps
import jwt
from sqlalchemy import select
from soccer_app.user.models import User, UserRole
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token == None:
            return jsonify({"code": 500, "data": "", "message": "log in required"})
        id_obj = jwt.decode(token, "secret", algorithms=["HS256"])
        user_id = id_obj["id"]

        if session.get(f"{user_id}") != None:
            request.args = request.args.copy()
            request.args["userId"] = user_id
            return func(*args, **kwargs)
        else:
            return jsonify({"code": 500, "data": "", "message": "log in required"})
    return wrapper

def all_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get("userId")
        current_user_role_list = User.get_role_list_parse(session[f"{user_id}"])
        if "ALL-ADMIN" in current_user_role_list:
            return func(*args, **kwargs)
        else:
            return jsonify({"code": 500, "data": "", "message": "unauthorized"})
    return wrapper

def owner_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get("userId")
        group_code = request.args.get("code")
        current_user_role_list = User.get_role_list_parse(session[f"{user_id}"])
        if "ALL-ADMIN" or f"{group_code}-A" in current_user_role_list:
            return func(*args, **kwargs)
        else:
            return jsonify({"code": 500, "data": "", "message": "unauthorized"})
    return wrapper

def group_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get("userId")
        group_code = request.args.get("code")
        current_user_role_list = User.get_role_list_parse(session[f"{user_id}"])
        if "ALL-ADMIN" or f"{group_code}-A" or f"{group_code}-B" in current_user_role_list:
            return func(*args, **kwargs)
        else:
            return jsonify({"code": 500, "data": "", "message": "unauthorized"})

    return wrapper

def role_id_to_list(role_id_list, is_active):
    role_list = []
    for role_id in role_id_list:
        role_obj = {
            "role_set_id": role_id,
            "is_active": is_active
        }
        role_list.append(role_obj)
    return role_list

def add_role_to_list(role_id_list, user_id):
    role_list = []
    for role_id in role_id_list:
        user_role_obj = {
            "user_id": user_id,
            "role_id": role_id,
            "is_active": 0
        }
        role_list.append(user_role_obj)
    return role_list