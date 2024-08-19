from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import BIGINT, String, INTEGER, Column, String, DateTime,Text
from soccer_app.app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class Group(db.Model):
    __tablename__ = 'group'

    id = db.Column(BIGINT, primary_key=True, nullable=False, comment='role Id')
    group_name = db.Column(String(255), nullable=False)
    description = db.Column(Text, nullable=False)
    pic_url = db.Column(Text)
    code = db.Column(String(50))
    #0 is active 1 is deleted
    is_active = db.Column(INTEGER)
    create_time = db.Column(DateTime, default=datetime.now())
    roles = relationship("Role", back_populates="group")