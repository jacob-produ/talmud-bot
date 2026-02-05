import os

from flask import Flask
from school_manager.constants import constants
from school_manager.models.user import User
from flask_login import LoginManager
from school_manager import routes
from school_manager.db import db


class WebServer:
    def __init__(self):
        self.create_app()

    def create_app(self):
        """
            Create and configure the app
        """
        self.app = Flask(__name__, instance_relative_config=True, static_folder=constants.SERVER_UI_DIR, static_url_path='')

        # Init the secret key of the app -it is a must for flask to run
        self.app.config.from_mapping(
            SECRET_KEY='BiliBiliBom116!'
        )

        # Init the app with core routes
        routes.init_app(self.app)

        # Initialize login manager
        login_manager = LoginManager()
        login_manager.init_app(self.app)
        # login_manager.login_view = "/index.html"

        # Define teardown_appcontext event that will be invoked anytime the appcontext is closed
        # After any REST FUL API access, this function will be invoked
        @self.app.teardown_appcontext
        def shutdown_session(exception=None):
            """
            call session.remove() - which will first call Session.close()
            method on the current Session, which releases any existing connection resources still being held;
            Upon next usage within the same scope, the scoped_session will produce a new Session object.
            :param exception:
            :return:
            """
            db.session.remove()

        @login_manager.user_loader
        def user_loader(user_id):
            user_list = User.read(id=user_id, deleted=False)
            db.session.commit()
            return user_list

    def run(self):
        # Threaded True seems to be default only on windows
        # Else for Linux
        if os.name == 'nt':
            self.app.run(host=constants.WEB_SERVER_LISTENING_IP, threaded=True, port=80)
        else:
            self.app.run(ssl_context=('/root/cert.pem', '/root/key.pem'),
                         host=constants.WEB_SERVER_LISTENING_IP, threaded=True, port=443)

    @classmethod
    def start_web_server(cls):
        web_server = WebServer()
        web_server.run()

