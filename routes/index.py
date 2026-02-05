from flask_restful import Resource
from flask import redirect
from school_manager.routes.auth import login_required, role_required


class IndexAPI(Resource):
    def get(self, path=None):
        return redirect('/index.html')

    @classmethod
    def register_error_handlers(cls, app):
        @app.errorhandler(404)
        def redirect_home(path=None, params=None):
            return redirect('/index.html')
