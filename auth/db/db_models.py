import uuid

from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash

from db import db


class TimeStampModel:
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.current_timestamp())


user_roles = db.Table('user_roles', db.metadata,
                      db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id")),
                      db.Column("role_id", UUID(as_uuid=True), db.ForeignKey("roles.id")))


class User(TimeStampModel, db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return f'<User {self.login}>'

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user_by_login(login: str):
        user = User.query.filter_by(login=login).one_or_none()
        return user


class Role(TimeStampModel, db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Role {self.name}>'
