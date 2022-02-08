import click
from flask import Blueprint
from werkzeug.security import generate_password_hash

from db import db
from db.datastore import user_datastore
from sqlalchemy.exc import IntegrityError

cmd = Blueprint('cmd', __name__)

@cmd.cli.command('createsuperuser')
@click.option('--email', help='User email')
@click.option('--login', prompt='enter username', default='admin')
@click.option('--password', prompt='enter password')
def create_superuser(login, email, password):
    password_hash = generate_password_hash(password)
    args = {'login': login, 'email': email}
    args.update({'password': password_hash})
    admin_role = user_datastore.find_or_create_role('admin')
    try:
        user = user_datastore.create_user(**args)
        user_datastore.add_role_to_user(user, admin_role)
        db.session.commit()
        click.echo(f'superuser created: {login}')
    except IntegrityError:
        click.echo(f'User {login} already exists')
