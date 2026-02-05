from school_manager.models.user import User
from werkzeug.security import generate_password_hash
from school_manager.db import db
from school_manager.db import initialize_db

initialize_db.init_db()


def create():
    user = User()
    user.username = "admin"
    user.password = generate_password_hash("password")
    user.first_name = 'Yosi2'
    user.last_name = 'Tal2'
    user.role = 'admin'
    user.deleted = False
    db.session.add(user)
    db.session.commit()
    print("Test user was successfully done")

    external_api_user = User()
    external_api_user.username = "external_api_user"
    external_api_user.password = generate_password_hash("t43GSF0At@T9lRnd*ZWXtS%iU%77Maa4Ic5mEhl")
    external_api_user.first_name = 'external'
    external_api_user.last_name = 'api user'
    external_api_user.role = 'publisher'
    external_api_user.deleted = False
    db.session.add(external_api_user)
    db.session.commit()
    print("Test external api user was successfully done")


def update():
    User.update({'password': generate_password_hash("Sch00lManager@dm!n53c")}, username="admin")


if __name__ == "__main__":
    # create()
    update()
