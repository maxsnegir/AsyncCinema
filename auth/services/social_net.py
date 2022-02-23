from db import db_session
from db.db_models import SocialAccount
from .user import UserService


class SocialService:

    @classmethod
    def get_or_create(cls, social_name: str, social_id: str, login: str, email: str):
        soc_account = SocialAccount.query.filter_by(social_name=social_name, social_id=social_id).one_or_none()

        if not soc_account:
            user = UserService.get_or_create(login=login,
                                             email=email,
                                             password=None,
                                             role_name=None)

            with db_session() as session:
                soc_account = SocialAccount(
                    social_name=social_name,
                    social_id=social_id,
                    user_id=user.id
                )
                session.add(soc_account)

        return soc_account
