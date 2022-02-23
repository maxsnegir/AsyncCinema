from http import HTTPStatus

from flask import url_for, make_response, jsonify, abort, redirect, session
from flask_restplus import Resource

from api.admin import admin_namespace as namespace
from oauth import oauth
from services.social_net import SocialService
from services.token import TokenService


@namespace.route("/login/<string:social_name>")
class OAuthLogin(Resource):

    def get(self, social_name):
        client = oauth.create_client(social_name)
        if not client:
            abort(HTTPStatus.NOT_FOUND)

        auth_redirect = url_for("Api v1_o_auth_authorization", social_name=social_name, _external=True)
        return client.authorize_redirect(auth_redirect)


@namespace.route("/auth/<string:social_name>")
class OAuthAuthorization(Resource):

    def get(self, social_name):

        client = oauth.create_client(social_name)
        if not client:
            abort(HTTPStatus.NOT_FOUND)

        if not session.get(f'_{social_name}_authlib_state_'):
            return redirect(url_for("Api v1_o_auth_login", social_name=social_name, _external=True))

        client.authorize_access_token()
        user_info = client.userinfo()
        social_id = user_info["sub"]
        login = user_info["login"]
        email = user_info["email"]

        soc_acc = SocialService.get_or_create(social_name, social_id, login, email)
        access_token, refresh_token = TokenService(soc_acc.user).get_jwt_tokens()
        return make_response(jsonify(access_token=access_token, refresh_token=refresh_token), HTTPStatus.OK)
