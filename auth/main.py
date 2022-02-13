import os

from dotenv import load_dotenv
from flask import Flask

from api import init_api
from db import init_db
from db.datastore import init_datastore
from db.redis import init_redis
from jwt_manager import init_jwt

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["FLASK_APP"] = os.getenv("FLASK_APP")

init_db(app)
init_redis(app)
init_datastore(app)
init_api(app)
init_jwt(app)

app.app_context().push()

if __name__ == '__main__':
    app.run(debug=True)
