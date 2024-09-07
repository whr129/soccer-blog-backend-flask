from soccer_app.group.models import Group
from flask import request, render_template, redirect, url_for, Blueprint, jsonify, session
from soccer_app.user.utils import login_required, all_admin_required, owner_required
from soccer_app.app import db
from snowflake import SnowflakeGenerator
from sqlalchemy import update,select,func
from soccer_app.group.utils import add_group_role
from soccer_app.user.models import Role, UserRole, User
gen = SnowflakeGenerator(42)

group = Blueprint('group', __name__)

@group.route("/addGroup", methods=["POST"])
@login_required
@all_admin_required
def add_new_group():
    group_name = request.form.get("name")
    description = request.form.get("description")
    pic_url = request.form.get("picUrl")
    code = request.form.get("code")
    group = Group(
        id=next(gen),
        group_name=group_name,
        description=description,
        pic_url=pic_url,
        code=code,
        is_active=0
    )
    db.session.add(group)
    db.session.commit()
    add_group_role(group.id, code)
    return jsonify({"code": 200, "data": "", "message": "successfully add a new group"})

@group.route("/disableGroup", methods=["POST"])
@login_required
@all_admin_required
def disable_group():
    group_id = request.form.get("id")
    is_active = request.form.get("status")
    query = update(Group).where(Group.id == group_id).values(is_active=is_active)
    query_role = update(Role).where(Group.id == group_id).values(is_active=is_active)
    db.session.execute(query)
    db.session.execute(query_role)
    db.session.commit()
    return jsonify({"code": 200, "data": f"", "message": "successfully change a group status"})

@group.route("/editGroup", methods=["POST"])
@login_required
@all_admin_required
def edit_group():
    group_id = request.form.get("id")
    group_name = request.form.get("name")
    group_description = request.form.get("description")
    # pic_url = request.form.get("picUrl")
    query = update(Group).where(Group.id == group_id).values(group_name=group_name, description=group_description)
    db.session.execute(query)
    db.session.commit()
    return jsonify({"code": 200, "data": f"", "message": "successfully edit a group info"})

@group.route("/updateGroupOwner", methods=["POST"])
@login_required
@all_admin_required
def update_group_owner():
    user_id = request.form.get("userId")
    group_id = request.form.get("groupId")
    group_code = request.form.get("code")
    query_for_role = select(Role).where(Role.code == f"{group_code}-A")
    role_row = db.session.execute(query_for_role).first()
    db.session.commit()
    current_role = role_row.Role
    query_disable = update(UserRole).where(UserRole.role_id == current_role.id).values(is_active=1)
    db.session.execute(query_disable)
    db.session.commit()
    query_exist = select(UserRole).where((UserRole.role_id == current_role.id) & (UserRole.user_id == user_id))
    user_role_row = db.session.execute(query_exist).first()
    if user_role_row == None:
        new_user_role = UserRole(
            user_id=user_id,
            role_id=current_role.id,
            is_active=0
        )
        db.session.add(new_user_role)
        db.session.commit()
    else:
        query_enable = update(UserRole).where((UserRole.role_id == current_role.id) & (UserRole.user_id == user_id)).values(is_active=0)
        db.session.execute(query_enable)
        db.session.commit()
    return jsonify({"code": 200, "data": f"", "message": "successfully update a group owner"})

@group.route("/disableGroupAdmin", methods=["POST"])
@login_required
@owner_required
def disable_group_admin():
    user_id = request.form.get("userId")
    group_id = request.form.get("groupId")
    group_code = request.form.get("code")
    query_for_role = select(Role).where(Role.code == f"{group_code}-B")
    role_row = db.session.execute(query_for_role).first()
    db.session.commit()
    current_role = role_row.Role
    query_disable = update(UserRole).where((UserRole.role_id == current_role.id) & (UserRole.user_id == user_id)).values(is_active=1)
    db.session.execute(query_disable)
    db.session.commit()
    return jsonify({"code": 200, "data": f"", "message": "successfully disable a group admin"})

@group.route("/addGroupAdmin", methods=["POST"])
@login_required
@owner_required
def add_group_admin():
    user_id = request.form.get("userId")
    group_id = request.form.get("groupId")
    group_code = request.form.get("code")
    query_for_role = select(Role).where(Role.code == f"{group_code}-B")
    role_row = db.session.execute(query_for_role).first()
    db.session.commit()
    if role_row == None:
        return jsonify({"code": 500, "data": f"", "message": "role not found"})
    else:
        # update or insert
        current_role = role_row.Role
        query_for_user_role = select(UserRole).where((UserRole.role_id == current_role.id) & (UserRole.user_id == user_id))
        user_role_row = db.session.execute(query_for_user_role).first()
        #insert
        if user_role_row == None:
            user_role = UserRole(
                user_id=user_id,
                role_id=current_role.id,
                is_active=0
            )
            db.session.add(user_role)
            db.session.commit()
        else:
            #update
            query_enable = update(UserRole).where(
                (UserRole.role_id == current_role.id) & (UserRole.user_id == user_id)).values(is_active=0)
            db.session.execute(query_enable)
            db.session.commit()
    return jsonify({"code": 200, "data": f"", "message": "successfully add a group admin"})

@group.route("/queryGroupDetail", methods=["POST"])
def query_group_role():
    group_id = request.form.get("id")
    query = select(Group).where(Group.id == group_id)
    group_row = db.session.execute(query).first()
    current_group = group_row.Group
    owner = []
    admins = []
    for role in current_group.roles:
        if role.role == 0:
            for user in role.active_users:
                owner.append({
                    "userName": user.username,
                    "userId": str(user.id)
                })
        elif role.role == 1:
            for user in role.active_users:
                admins.append({
                    "userName": user.username,
                    "userId": str(user.id)
                })
    return jsonify({"code": 200, "data": {
        "groupName": current_group.group_name,
        "id": str(current_group.id),
        "picUrl": current_group.pic_url,
        "description": current_group.description,
        "code": current_group.code,
        "owner": owner,
        "admin": admins
    }, "message": "successfully query a group role"})

@group.route("/queryGroupList", methods=["POST"])
def query_group_list():
    page_num = request.form.get("pageNum")
    page_size = request.form.get("pageSize")
    query = select(Group).limit(page_size).offset((int(page_num) - 1) * int(page_size)).order_by(Group.create_time)
    group_rows = db.session.execute(query)
    query_count = select(func.count()).select_from(Group);
    group_count = db.session.execute(query_count).first();
    group_list = []
    for group_row in group_rows:
        current_group = group_row.Group
        owner = []
        admins = []
        for role in current_group.roles:
            if role.role == 0:
                for user in role.active_users:
                    owner.append({
                        "userName": user.username,
                        "userId": str(user.id)
                    })
            elif role.role == 1:
                for user in role.active_users:
                    admins.append({
                        "userName": user.username,
                        "userId": str(user.id)
                    })
        group_detail = {
            "id": str(current_group.id),
            "groupName":current_group.group_name,
            "picUrl": current_group.pic_url,
            "description": current_group.description,
            "code": current_group.code,
            "status": current_group.is_active,
            "owner": owner,
            "admin": admins
        }
        group_list.append(group_detail)
    return jsonify({"code": 200, "data": {
        "totalNum": group_count.count,
        "groupList": group_list}, "message": "successfully query group list"})
