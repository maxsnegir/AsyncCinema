import uuid

from flask import Request
from flask_security import UserMixin, RoleMixin
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from user_agents import parse
from werkzeug.security import check_password_hash

from db import db


class DefaultRoles:
    ADMIN = 'admin'
    SUPER_USER = 'super user'
    USER = 'user'


class AuthDevices:
    PC = "web"
    MOBILE = "mobile"
    TABLET = "tablet"


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


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_tablet" PARTITION OF "auth_history" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "auth_history" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "auth_history" FOR VALUES IN ('web')"""
    )


class AuthHistory(db.Model):
    __tablename__ = 'auth_history'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column("user_id", UUID(as_uuid=True), db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, server_default=db.func.now())
    user_agent = db.Column(db.Text, nullable=False)
    user_ip = db.Column(db.String)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'<AuthHistory {self.user_id}:{self.logined_by}>'

    @staticmethod
    def create_history_record(user: User, request: Request):
        user_agent = parse(request.user_agent.string)
        if user_agent.is_mobile:
            user_device_type = AuthDevices.MOBILE
        elif user_agent.is_tablet:
            user_device_type = AuthDevices.TABLET
        else:
            user_device_type = AuthDevices.PC

        history_record = AuthHistory(user_id=user.id,
                                     user_agent=request.user_agent.string,
                                     user_ip=request.remote_addr,
                                     user_device_type=user_device_type)
        db.session.add(history_record)
        db.session.commit()


class SocialAccount(db.Model):
    __tablename__ = 'social_account'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name', name='social_pk'),)

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
