from flask import request, render_template, redirect, url_for, Blueprint, jsonify, session, json
from functools import wraps
from soccer_app.app import db
import jwt
from sqlalchemy import select
from soccer_app.user.models import User, UserRole
from soccer_app.comment.models import MainPost, SubPost
from soccer_app.user.utils import owner_required, group_admin_required

def delete_main_post_auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get("userId")
        main_post_id = request.form.get("id")
        query = select(MainPost).where(MainPost.id == main_post_id)
        post_row = db.session.execute(query).first()
        if post_row == None :
            return jsonify({"code": "500", "data": "", "message": "post not found"})
        current_post = post_row.MainPost
        if current_post.user_id == user_id:
            return func(*args, **kwargs)
        else:
            return group_admin_required(func(*args, **kwargs))
    return wrapper

def delete_sub_post_auth_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.args.get("userId")
        sub_post_id = request.form.get("id")
        query = select(SubPost).where(SubPost.id == sub_post_id)
        post_row = db.session.execute(query).first()
        if post_row == None:
            return jsonify({"code": "500", "data": "", "message": "sub post not found"})
        current_post = post_row.SubPost
        if current_post.user_id == user_id:
            return func(*args, **kwargs)
        else:
            return group_admin_required(func(*args, **kwargs))

    return wrapper

def is_log_in():
    token = request.headers.get("Authorization")
    if token == None:
        return False
    id_obj = jwt.decode(token, "secret", algorithms=["HS256"])
    user_id = id_obj["id"]
    if session.get(f"{user_id}") != None:
        request.args = request.args.copy()
        request.args["userId"] = user_id
        return True
    else:
        return False