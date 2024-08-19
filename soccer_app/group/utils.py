from soccer_app.group.models import Group
from flask import request, render_template, redirect, url_for, Blueprint, jsonify
from soccer_app.user.utils import login_required, all_admin_required
from soccer_app.app import db
from snowflake import SnowflakeGenerator
from sqlalchemy import update
from soccer_app.user.models import Role

gen = SnowflakeGenerator(42)

def add_group_role(group_id, group_code):
    #group owner
    group_owner = Role(
        id=next(gen),
        code=f"{group_code}-A",
        role=0,
        group_id=group_id,
        is_active=0
    )
    #group admin
    group_admin = Role(
        id=next(gen),
        code=f"{group_code}-B",
        role=1,
        group_id=group_id,
        is_active=0
    )
    db.session.add(group_owner)
    db.session.add(group_admin)
    db.session.commit()
    return "success"