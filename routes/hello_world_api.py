from flask_restful import Resource


class HelloWorldApiTest(Resource):
    def post(self):
        print("Hello World")
        return "Hello world"
