from web import manager, web_session
from flask_login import UserMixin
from database import funcs


class User(UserMixin):
    def __init__(self, username, first_name, last_name, aid):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.aid = aid

    def get_id(self):
        return self.username


@manager.user_loader
def load_user(username):
    account = funcs.get_account(username, session=web_session)
    return User(username=account.username, first_name=account.first_name,
                last_name=account.last_name, aid=account.account_id) if account else None
