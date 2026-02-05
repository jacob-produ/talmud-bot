import os, pandas as pd
from io import StringIO
from flask import Response
from school_manager.constants.constants import UT8_WITH_BOM_ENCODING
from school_manager.constants.constants_lists import EXCEL_EXTENSIONS

CURRENT_DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SCHOOL_MANAGER_DIR_PATH = os.path.dirname(os.path.dirname(CURRENT_DIR_PATH))
CSV_TEMPLATES_PATH = os.path.join(SCHOOL_MANAGER_DIR_PATH,'assets/files_upload_templates')
EXCEL_CONVERSION_PATH = os.path.join(SCHOOL_MANAGER_DIR_PATH,'assets/excel_conversions')

class File:

    class Read:
        @staticmethod
        def get_csv_template_by_name(csv_parameter):
            files = [os.path.join(CSV_TEMPLATES_PATH,file_name) for file_name in os.listdir(CSV_TEMPLATES_PATH) if file_name.startswith(csv_parameter)]
            if not files:
                raise FileNotFoundError
            file_path = files[0]
            file_type = file_path.split(".")[1]
            with open(file_path, 'rb') as f:
                file_data = f.readlines()
            if file_type == 'xlsx':
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            elif file_type == ".zip":
                content_type = 'application/zip'
            else:
                content_type = 'application/'
            return Response(file_data, headers={
                'Content-Type': content_type,
                'Content-Disposition': f'attachment; filename={os.path.basename(file_path)};'
            })

        @staticmethod
        def convert_excel_to_csv(file_stream,file_name):
            file_name_no_extension = file_name.split(".")[0].lower()
            csv_file_path = os.path.join(EXCEL_CONVERSION_PATH,file_name_no_extension)
            read_file = pd.read_excel(file_stream)
            read_file.to_csv(csv_file_path, index=None, header=True)
            with open(csv_file_path, 'rb') as f:
                csv_data = f.read()
            return csv_data


        @staticmethod
        def read_file(file_stream, file_name, encoding=UT8_WITH_BOM_ENCODING, without_stringio=False):
            file_extension = file_name.split(".")[1].lower()
            if file_extension in EXCEL_EXTENSIONS:
                file_decode = File.Read.convert_excel_to_csv(file_stream, file_name).decode(encoding)
            else:
                file_decode = file_stream.decode(encoding)
            if without_stringio:
                return file_decode
            return StringIO(file_decode)
