import sys
import os
from flask_restful import Resource, reqparse, request


class FormAttributesResource(Resource):
    def __init__(self):
        self.load_form_props()

    def load_form_props(self):
        form_props_dir = os.environ.get('form_props_dir')

        sys.path.append(form_props_dir)
        import FormProperties as FORM_PROPERTIES_DICT
        self.form_props = FORM_PROPERTIES_DICT.FORM_PROPERTIES

    def get(self):
        form_id = request.args['form_id']

        # parser = reqparse.RequestParser()
        # parser.add_argument('form_id', type=str)
        # args = parser.parse_args()
        #
        # form_id = args['form_id']

        return self.form_props.get(form_id), 201

