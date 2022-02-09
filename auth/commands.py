from gevent import monkey

monkey.patch_all()

import typer
from werkzeug.security import generate_password_hash
from gevent.pywsgi import WSGIServer
from db import db
from db.db_models import DefaultRoles
from db.datastore import user_datastore
from sqlalchemy.exc import IntegrityError
from main import app

typer_manager = typer.Typer()


@typer_manager.command()
def create_superuser(
        login: str,
        email: str,
        password: str) -> None:
    password_hash = generate_password_hash(password)
    args = {'login': login, 'email': email, 'password': password_hash}
    try:
        user = user_datastore.create_user(**args)
        admin_role = user_datastore.find_or_create_role(DefaultRoles.SUPER_USER)
        user_datastore.add_role_to_user(user, admin_role)
        db.session.commit()
        typer.echo(f'superuser created: {login}')
    except IntegrityError:
        typer.echo(f'Login or email already exists')


@typer_manager.command()
def runserver():
    http_server = WSGIServer(('', 5001), app)
    http_server.serve_forever()


if __name__ == "__main__":
    typer_manager()
