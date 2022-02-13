from time import sleep

from gevent import monkey

monkey.patch_all()

import typer
from werkzeug.security import generate_password_hash
from gevent.pywsgi import WSGIServer
from db import db
from db.db_models import DefaultRoles, Role
from db.datastore import user_datastore
from sqlalchemy.exc import IntegrityError
from main import app

typer_manager = typer.Typer()


def create_user(login: str, email: str, password: str, role: str):
    try:
        user = user_datastore.create_user(login=login, email=email, password=generate_password_hash(password))
        admin_role = user_datastore.find_or_create_role(role)
        user_datastore.add_role_to_user(user, admin_role)
        db.session.commit()
        typer.echo(f'superuser created: {login}')
    except IntegrityError:
        typer.echo(f'Login or email already exists')


@typer_manager.command()
def create_superuser(login: str, email: str, password: str) -> None:
    create_superuser(login, email, password, DefaultRoles.SUPER_USER)


@typer_manager.command()
def create_base_roles():
    for role in Role.Meta.BASE_ROLES:
        user_datastore.find_or_create_role(role)
        sleep(0.1)
        typer.echo(f'Role {role} created')

    db.session.commit()


@typer_manager.command()
def runserver():
    http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()


if __name__ == "__main__":
    typer_manager()
