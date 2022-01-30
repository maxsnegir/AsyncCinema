from flask import Flask

from db.datastore import init_datastore
from db import init_db
from api import init_api
from jwt_helper import init_jwt

app = Flask(__name__)
app.config["SECRET_KEY"] = 'SECRET_KEY'
app.config["FLASK_APP"] = "main:app"

init_db(app)
init_datastore(app)
init_api(app)
init_jwt(app)

app.app_context().push()

if __name__ == '__main__':
    app.run(debug=True)
