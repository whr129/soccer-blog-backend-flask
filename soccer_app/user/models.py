# from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import BIGINT, String, INTEGER, Column, String, DateTime, ForeignKey, Table, select, and_
from soccer_app.app import db
from sqlalchemy.orm import Mapped, mapped_column, relationship, registry
from datetime import datetime

mapper_registry = registry()

association_user_role = Table(
    'user_role', db.Model.metadata,
    Column('user_id', BIGINT, ForeignKey('user.id'), primary_key=True, nullable=False, comment="user Id"),
    Column('role_id', BIGINT, ForeignKey('role.id'), primary_key=True, nullable=False, comment="role Id"),
    Column('is_active', BIGINT, nullable=True, comment="0 True 1 False")
)
class UserRole(object):
    pass

mapper_registry.map_imperatively(UserRole, association_user_role)

class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(BIGINT, primary_key=True, nullable=False, comment='role Id')
    code = db.Column(String(50), nullable=False)
    #0: owner 1: admin 2: all-admin
    role = db.Column(INTEGER)
    group_id = db.Column(BIGINT, db.ForeignKey('group.id') ,nullable=False, comment="group Id")
    # 0 True 1 False
    is_active = db.Column(INTEGER)
    group = relationship("Group", back_populates="roles")
    users = relationship('User', secondary=association_user_role, back_populates='roles')
    active_users = relationship('User', secondary=association_user_role,primaryjoin=and_(
            UserRole.role_id == id,
            UserRole.is_active == 0
        ),viewonly=True, back_populates='roles')

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(BIGINT, primary_key=True, nullable=False, comment="user Id")
    email = db.Column(String(50), nullable=False)
    password = db.Column(String(255), nullable=False)
    username = db.Column(String(255), nullable=False)
    # 0 True 1 False
    is_active = db.Column(INTEGER)
    create_time = db.Column(DateTime, default=datetime.now(), nullable=False)
    roles = relationship('Role', secondary=association_user_role, back_populates='users')
    active_roles = relationship('Role', secondary=association_user_role, primaryjoin=and_(
            UserRole.user_id == id,
            UserRole.is_active == 0
        ),
        secondaryjoin=Role.id == UserRole.role_id,viewonly=True, back_populates='users')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "is_active": self.is_active,
            "create_time": self.create_time,
            "roles": self.get_roles_code()
        }

    def get_roles_code(self):
        roles = []
        for role in self.active_roles:
            roles.append(role.code)
        return roles

    def get_active_roles(self):
        roles = []
        for role in self.active_roles:
            roles.append(role.code)
        return roles

    @staticmethod
    def data_parse(data):
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            password=data["password"],
            is_active=data["is_active"],
            create_time=data["create_time"],
        )
    @staticmethod
    def get_role_list_parse(data):
        return data["roles"]

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, password={self.password}, is_active={self.is_active}, create_time={self.create_time},roles={self.roles})>"




