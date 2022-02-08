from flask import Flask

from api import init_api
from db import init_db, db
from db.redis import init_redis
from db.datastore import init_datastore
from jwt_manager import init_jwt
from api.commands import cmd


app = Flask(__name__)
app.config["SECRET_KEY"] = 'SECRET_KEY'
app.config["FLASK_APP"] = "main:app"

app.register_blueprint(cmd)

init_db(app)
init_redis(app)
init_datastore(app)
init_api(app)
init_jwt(app)

app.app_context().push()
db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
