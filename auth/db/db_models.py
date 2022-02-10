import uuid

from flask import Request
from flask_security import UserMixin, RoleMixin
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash

from db import db


class DefaultRoles:
    ADMIN = 'admin'
    SUPER_USER = 'super user'
    USER = 'user'


class TimeStampModel:
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.now())
    updated_at = db.Column(
        db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.current_timestamp()
    )


user_roles = db.Table(
    "user_roles",
    db.metadata,
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id")),
    db.Column("role_id", UUID(as_uuid=True), db.ForeignKey("roles.id")),
)


class User(TimeStampModel, db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean())
    roles = db.relationship(
        "Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic")
    )

    def __repr__(self):
        return f"<User {self.login}>"

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def get_user_by_login(login: str):
        user = User.query.filter_by(login=login).one_or_none()
        return user

    @property
    def is_admin(self):
        return self.has_role(DefaultRoles.ADMIN) or self.has_role(DefaultRoles.SUPER_USER)


class Role(db.Model, RoleMixin, TimeStampModel):
    __tablename__ = "roles"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)

    class Meta:
        BASE_ROLES = (
            DefaultRoles.ADMIN,
            DefaultRoles.SUPER_USER,
            DefaultRoles.USER
        )

    def __repr__(self):
        return f"<Role {self.name}>"

    @staticmethod
    def get_all_roles():
        roles = Role.query.all()
        return roles


class AuthHistory(TimeStampModel, db.Model):
    __tablename__ = "auth_history"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False, )
    user_id = db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, server_default=db.func.now())
    user_agent = db.Column(db.Text, nullable=False)
    user_ip = db.Column(db.String)

    @staticmethod
    def create_history_record(user: User, request: Request):
        user_agent = request.user_agent.string
        ip_address = request.remote_addr

        history_record = AuthHistory(user_id=user.id,
                                     user_agent=user_agent,
                                     user_ip=ip_address)
        db.session.add(history_record)
        db.session.commit()
