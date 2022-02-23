from authlib.integrations.flask_client import OAuth
from flask import Flask

from settings import OAuthSettings

oauth = OAuth()
oauth_settings = OAuthSettings()


def yandex_compliance_fix(client, user_data):
    return {
        "sub": user_data["id"],
        "login": user_data["login"],
        "name": user_data["display_name"],
        "email": user_data["default_email"],
    }


def mail_compliance_fix(client, user_data):
    return {"sub": user_data["id"],
            "login": user_data["nickname"],
            "name": user_data["first_name"],
            "email": user_data["email"],
            }


oauth.register(
    "yandex",
    access_token_url=oauth_settings.YANDEX_ACCESS_TOKEN_URL,
    userinfo_endpoint=oauth_settings.YANDEX_USERINFO_ENDPOINT,
    authorize_params={
        "response_type": "code",
    },
    token_placement="header",
    userinfo_compliance_fix=yandex_compliance_fix,

)

oauth.register(
    "mail",
    access_token_url=oauth_settings.MAIL_ACCESS_TOKEN_URL,
    userinfo_endpoint=oauth_settings.MAIL_USERINFO_ENDPOINT,
    authorize_params={
        "response_type": "code",
    },
    token_placement="url",
    userinfo_compliance_fix=mail_compliance_fix

)


def init_oauth(app: Flask):
    app.config["YANDEX_CLIENT_ID"] = oauth_settings.YANDEX_CLIENT_ID
    app.config["YANDEX_CLIENT_SECRET"] = oauth_settings.YANDEX_CLIENT_SECRET
    app.config["YANDEX_AUTHORIZE_URL"] = oauth_settings.YANDEX_AUTHORIZE_URL

    app.config["MAIL_CLIENT_ID"] = oauth_settings.MAIL_CLIENT_ID
    app.config["MAIL_CLIENT_SECRET"] = oauth_settings.MAIL_CLIENT_SECRET
    app.config["MAIL_AUTHORIZE_URL"] = oauth_settings.MAIL_AUTHORIZE_URL
    oauth.init_app(app)
