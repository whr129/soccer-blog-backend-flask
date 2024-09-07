from flask import request, render_template, redirect, url_for, Blueprint, jsonify, session, json
from soccer_app.app import db
from soccer_app.user.models import User, Role, UserRole
# from flask_login import current_user, login_required, login_user, logout_user
from flask_bcrypt import Bcrypt
from sqlalchemy import select, update, bindparam, insert, func
from snowflake import SnowflakeGenerator
import jwt
from soccer_app.user.utils import login_required, all_admin_required, role_id_to_list, add_role_to_list
from soccer_app.comment.models import MainPost, SubPost
from soccer_app.comment.utils import owner_required

gen = SnowflakeGenerator(42)

bcrypt = Bcrypt()

user = Blueprint('user', __name__)

@user.route('/')
def index():
    return "Hello World!"

@user.route('/register', methods=["POST"])
def register():
    #register new user
    user_name = request.form.get("userName")
    password_origin = request.form.get("password")
    password_hashed = bcrypt.generate_password_hash(password_origin).decode('utf-8')
    email = request.form.get("email")
    user = User(
        id=next(gen),
        username=user_name,
        email=email,
        is_active=0,
        password=password_hashed
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"code": 200, "data": "", "message": "successfully register"})

@user.route("/login", methods=["POST"])
def log_in():
    user_name = request.form.get("userName")
    user_password = request.form.get("password")
    query = select(User).where(User.username == user_name)
    row = db.session.execute(query).first()

    if row == None :
        return jsonify({"code": 500, "data": "", "message": "user not found"})

    current_user = row.User
    if bcrypt.check_password_hash(current_user.password, user_password) == False :
        return jsonify({"code": 500, "data": "", "message": "password incorrect"})

    encoded_jwt = jwt.encode({"id": f"{current_user.id}"}, "secret", algorithm="HS256")
    session[f"{current_user.id}"] = User.to_dict(current_user)

    return jsonify({"code": 200, "data": f"{encoded_jwt}", "message": "successfully log in"})

@user.route("/logout", methods=["POST"])
@login_required
def log_out():
    user_id = request.args.get("userId")
    session.pop(f"{user_id}", default=None)
    return jsonify({"code": 200, "data": "", "message": "successfully log out"})

@user.route("/addRoleToUser", methods=["POST"])
@login_required
@all_admin_required
def add_role_to_user():
    role_id = request.form.get("roleId")
    user_id = request.form.get("userId")

    new_user_role = UserRole(
        user_id = user_id,
        role_id = role_id,
        is_active = 0
    )

    db.session.add(new_user_role)
    db.session.commit()

    if (session.get(f"{user_id}")):
        query = select(User).where(User.id == user_id)
        row = db.session.execute(query).first()
        current_user = row.User
        session[f"{user_id}"] = User.to_dict(current_user)

    return jsonify({"code": 200, "data": "", "message": "successfully add new role to user"})

@user.route("/changeUserStatus", methods=["POST"])
@login_required
@all_admin_required
def change_user_status():
    user_id = request.form.get("userId")
    is_active = request.form.get("status")
    query = update(User).where(User.id == user_id).values(is_active=is_active)
    db.session.execute(query)
    db.session.commit()
    return jsonify({"code": 200, "data": "", "message": "successfully change the status of a user"})

@user.route("/editUserInfo", methods=["POST"])
@login_required
@all_admin_required
def edit_user_info():
    user_id = request.form.get("userId")
    user_name = request.form.get("userName")
    email = request.form.get("email")
    password_orgin = request.form.get("password")
    password_hashed = bcrypt.generate_password_hash(password_orgin).decode('utf-8')

    query = update(User).where(User.id == user_id).values(username=user_name, password=password_hashed, email=email)
    db.session.execute(query)
    db.session.commit()

    #update session
    query = select(User).where(User.id == user_id)
    row = db.session.execute(query).first()
    current_user = row.User
    session[f"{user_id}"] = User.to_dict(current_user)

    #update comments user name
    query_for_main_post = update(MainPost).where(MainPost.user_id == user_id).values(user_name=user_name)
    query_for_sub_post = update(SubPost).where(SubPost.user_id == user_id).values(user_name=user_name)
    db.session.execute(query_for_main_post)
    db.session.execute(query_for_sub_post)
    db.session.commit()
    return jsonify({"code": 200, "data": "", "message": "successfully edit the user baseinfo"})

@user.route("/editUserRoles", methods=["POST"])
@login_required
@all_admin_required
def edit_user_roles():
    user_id = request.form.get("userId")
    new_role_list = []
    i = 0
    while True:
        role = request.form.get(f'roles[{i}]')
        if role is None:
            break
        new_role_list.append(role)
        i += 1
    get_query = select(User).where(User.id == user_id)
    user_row = db.session.execute(get_query).first()
    current_user = user_row.User
    disable_role_list = []
    enable_role_list = []
    add_role_list = []
    #query existing user_role to update
    for role in current_user.roles:
        if f"{role.id}" in new_role_list:
            enable_role_list.append(role.id)
        else:
            disable_role_list.append(role.id)
    #query new user_role to insert
    for role_id in new_role_list:
        if int(role_id) not in enable_role_list:
            add_role_list.append(role_id)
    enable_role_list_for_query = role_id_to_list(enable_role_list, 0)
    disable_role_list_for_query = role_id_to_list(disable_role_list, 1)
    #update existing roles
    if len(enable_role_list_for_query) + len(disable_role_list_for_query) != 0:
        db.session.connection().execute(
            update(UserRole).where((UserRole.role_id == bindparam("role_set_id")) & (UserRole.user_id == user_id)),
            [*enable_role_list_for_query, *disable_role_list_for_query],
        )
    add_role_list_for_insert = add_role_to_list(add_role_list, user_id)
    #insert new roles
    if len(add_role_list_for_insert) != 0:
        db.session.connection().execute(
            insert(UserRole),
            [*add_role_list_for_insert]
        )
    db.session.commit()
    return jsonify({"code": 200, "data": new_role_list, "message": "successfully edit the user roles"})

@user.route("/queryUserInfo", methods=["POST"])
@login_required
def query_user_info():
    user_id = request.args.get("userId")
    current_user = User.data_parse(session[f"{user_id}"])
    return jsonify({"code": 200, "data": {
        "username" : current_user.username,
        "email": current_user.email,
        "roles": User.get_role_list_parse(session[f"{user_id}"])
    }, "message": "successfully query user info"})

@user.route("/getUserList", methods=["POST"])
@login_required
@owner_required
def get_user_list():
    page_num = request.form.get("pageNum")
    page_size = request.form.get("pageSize")
    query_count = select(func.count()).select_from(User);
    user_count = db.session.execute(query_count).first();
    if page_num == None and page_size == None:
        query = select(User).order_by(User.create_time)
    else:
        query = select(User).offset((int(page_num) - 1) * int(page_size)).limit(page_size).order_by(User.create_time)
    user_rows = db.session.execute(query).all()
    user_list = []
    for user_row in user_rows:
        current_user = user_row.User
        user_detail = {
            "id": str(current_user.id),
            "email": current_user.email,
            "userName": current_user.username,
            "status": current_user.is_active,
            "roles": current_user.get_active_roles()
        }
        user_list.append(user_detail)
    return jsonify({"code": 200, "data": {"totalNum": user_count.count, "userList": user_list}, "message": "successfully get the user list"})

@user.route("/queryRoleList", methods=["POST"])
@login_required
@all_admin_required
def query_role_list():
    query = select(Role)
    role_list_rows = db.session.execute(query).all()
    role_list = []
    for role_row in role_list_rows:
        role = role_row.Role
        new_role = {
            "id": str(role.id),
            "code": role.code,
            "label": role.code,
            "value": str(role.id)
        }
        role_list.append(new_role)
    return jsonify({"code": 200, "data": role_list, "message": "successfully get the user list"})