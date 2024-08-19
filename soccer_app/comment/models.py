from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import BIGINT, String, INTEGER, Column, String, DateTime,Text, ForeignKey
from soccer_app.app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class MainPost(db.Model):
    __tablename__ = 'main_post'

    id = db.Column(BIGINT, primary_key=True, nullable=False, comment='main post Id')
    user_name = db.Column(String(255), nullable=False)
    user_id = db.Column(BIGINT, nullable=False)
    create_time = db.Column(DateTime, default=datetime.now(), nullable=False)
    description = db.Column(Text, nullable=False)
    #0 not delete 1 is deleted
    is_delete = db.Column(INTEGER)
    sub_posts = relationship("SubPost")

class SubPost(db.Model):
    __tablename__ = 'sub_post'

    id = db.Column(BIGINT, primary_key=True, nullable=False, comment='main post Id')
    user_name = db.Column(String(255), nullable=False)
    user_id = db.Column(BIGINT, nullable=False)
    #main post id
    post_id = db.Column(BIGINT, db.ForeignKey("main_post.id"), nullable=False, )
    create_time = db.Column(DateTime, default=datetime.now(), nullable=False)
    description = db.Column(Text, nullable=False)
    # 0 not delete 1 is deleted
    is_delete = db.Column(INTEGER)
