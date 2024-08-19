from flask import request, render_template, redirect, url_for, Blueprint, jsonify,session
from soccer_app.app import db
from soccer_app.comment.models import SubPost, MainPost
from soccer_app.user.utils import login_required, all_admin_required, owner_required
from snowflake import SnowflakeGenerator
from sqlalchemy import update,select,bindparam
from soccer_app.user.models import User
from soccer_app.comment.utils import delete_main_post_auth_required, delete_sub_post_auth_required, is_log_in

gen = SnowflakeGenerator(42)

comment = Blueprint('comment', __name__)

@comment.route("/addNewPost", methods=["POST"])
@login_required
def add_new_post():
    user_id = request.args.get("userId")
    current_user = User.data_parse(session[f"{user_id}"])
    user_name = current_user.username
    description = request.form.get("description")
    new_post = MainPost(
        id=next(gen),
        user_name=user_name,
        user_id=user_id,
        description=description,
        is_delete=0
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"code": "200", "data": "", "message": "successfully add a new post"})

@comment.route("/deleteSubPost", methods=["POST"])
@login_required
@delete_sub_post_auth_required
def delete_sub_post():
    id = request.form.get("id")
    query = update(SubPost).where(SubPost.id == id).values(is_delete=1)
    db.session.execute(query)
    db.session.commit()
    return jsonify({"code": "200", "data": "", "message": "successfully delete a sub post"})

@comment.route("/deletePost", methods=["POST"])
@login_required
@delete_main_post_auth_required
def delete_post():
    id = request.form.get("id")
    query = update(MainPost).where(MainPost.id == id).values(is_delete=1)
    db.session.execute(query)
    query_for_sub = update(SubPost).where(SubPost.post_id == id).values(is_delete=1)
    db.session.execute(query_for_sub)
    db.session.commit()
    return jsonify({"code": "200", "data": "", "message": "successfully delete a post"})

@comment.route("/addNewSubPost", methods=["POST"])
@login_required
def add_new_sub_post():
    user_id = request.args.get("userId")
    current_user = User.data_parse(session[f"{user_id}"])
    user_name = current_user.username
    description = request.form.get("description")
    post_id = request.form.get("postId")
    new_post = SubPost(
        id=next(gen),
        post_id=post_id,
        user_name=user_name,
        user_id=user_id,
        description=description,
        is_delete=0
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"code": "200", "data": "", "message": "successfully add a new comment"})

@comment.route("/queryMainPost", methods=["POST"])
def query_main_post():
    page_num = request.form.get("pageNum")
    page_size = request.form.get("pageSize")

    query = select(MainPost).where(MainPost.is_delete == 0).offset((int(page_num) - 1) * int(page_size)).limit(page_size).order_by(MainPost.create_time)
    main_post_rows = db.session.execute(query).all()
    is_login = is_log_in()
    user_id = request.args.get("userId")
    main_post_list = []
    for main_post in main_post_rows:
        current_main_post = main_post.MainPost
        if is_login == True:
            main_post_detail = {
                "id": current_main_post.id,
                "userName": current_main_post.user_name,
                "can_delete": current_main_post.user_id == int(user_id),
                "description": current_main_post.description
            }
            main_post_list.append(main_post_detail)
        else:
            main_post_detail = {
                "id": current_main_post.id,
                "userName": current_main_post.user_name,
                "can_delete": False,
                "description": current_main_post.description
            }
            main_post_list.append(main_post_detail)
    return jsonify({"code": "200", "data": main_post_list, "message": "successfully query main posts"})

@comment.route("/querySubPost", methods=["POST"])
def query_sub_post():
    page_num = request.form.get("pageNum")
    page_size = request.form.get("pageSize")
    post_id = request.form.get("id")

    query = select(SubPost).where((SubPost.post_id == post_id) & (SubPost.is_delete == 0)).offset((int(page_num) - 1) * int(page_size)).limit(page_size).order_by(SubPost.create_time)
    sub_post_rows = db.session.execute(query).all()
    is_login = is_log_in()
    user_id = request.args.get("userId")
    sub_post_list = []
    for sub_post in sub_post_rows:
        current_sub_post = sub_post.SubPost
        if is_login == True:
            sub_post_detail = {
                "id": current_sub_post.id,
                "userName": current_sub_post.user_name,
                "can_delete": current_sub_post.user_id == int(user_id),
                "description": current_sub_post.description
            }
            sub_post_list.append(sub_post_detail)
        else:
            sub_post_detail = {
                "id": current_sub_post.id,
                "userName": current_sub_post.user_name,
                "can_delete": False,
                "description": current_sub_post.description
            }
            sub_post_list.append(sub_post_detail)
    return jsonify({"code": "200", "data": sub_post_list, "message": "successfully query sub posts"})
