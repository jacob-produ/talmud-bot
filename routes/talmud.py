import io
import pandas as pd
from datetime import datetime
from flask_restful import Resource
import school_manager.constants.talmud as tc
from school_manager.routes.auth import login_required
from school_manager.modules.talmud.talmud import Talmud
from flask import send_from_directory, request, send_file, jsonify, Response
from school_manager.modules.talmud.utils.extract_data_from_file import extract_credentials
from school_manager.constants.constants import STR_ERROR, STR_MESSAGE, STR_DATA, STR_FILE_DATA
from school_manager.modules.talmud.utils.progress import ProgressManager
from flask_login import current_user

class TalmudAPI(Resource):
    @login_required()
    def get(self):
        html_directory = '../assets/talmud/html'
        return send_from_directory(html_directory, 'talmud_index.html')

    @login_required()
    def post(self):
        request_form_dict = request.form.to_dict()
        selected_action = request_form_dict.pop('action')
        file = request.files['file']
        input_method = request_form_dict.get('inputMethod') if 'inputMethod' in request_form_dict else None

        # Initialize progress for this user and action
        task_key = f"talmud:{current_user[0]['id']}:{selected_action}"
        ProgressManager.start(task_key, {"action": selected_action})

        if selected_action == tc.TASK_ADD_STUDENTS and input_method == "file":
            if file.filename == '' or file.filename == '':
                ProgressManager.error(task_key, tc.NO_FILE_SELECTED)
                return jsonify({STR_ERROR: True, STR_MESSAGE: tc.NO_FILE_SELECTED})
            if not file.filename.endswith(".xlsx") and not file.filename.endswith(".xls"):
                ProgressManager.error(task_key, tc.FILE_TYPE_NOT_SUPPORTED)
                return jsonify({STR_ERROR: True, STR_MESSAGE: tc.FILE_TYPE_NOT_SUPPORTED})

        if selected_action == tc.TASK_ADD_STUDENTS and input_method == "manual":
            username = request_form_dict.pop('manualUsername')
            password = request_form_dict.pop('manualPassword')
            branch = request_form_dict.pop('branchNum')
        else:
            username = request_form_dict.get('username')
            password = request_form_dict.get('password')
            branch = request_form_dict.get('branch')

        if not username and not password:
            if not selected_action == tc.TASK_ADD_STUDENTS:
                username, password = extract_credentials(file)
            if (not username and not password) or (username == "<USERNAME>" and password=="<PASSWORD>"):
                # Don't set error status for credentials_missing as it's handled by popup
                return jsonify({STR_ERROR: True, STR_MESSAGE: tc.CREDENTIALS_MISSING})

        try:
            # Determine the file type based on the extension
            id_number_dtype = {"StudentIdentity": str}
            # Skip 3 empty rows that exist in the input file.
            skips = 3 if not selected_action == tc.TASK_ADD_STUDENTS else 0

            df = None

            # Read the Excel file directly using pandas without saving it
            if file.filename.lower().endswith('.csv'):
                # Read a CSV file
                df = pd.read_csv(file, skiprows=skips, dtype=id_number_dtype)
            elif file.filename.lower().endswith(('.xlsx', '.xls')):
                # Read an Excel file
                df = pd.read_excel(file, skiprows=skips, dtype=id_number_dtype)

            if username and password:
                if not selected_action == tc.TASK_ADD_STUDENTS or input_method == "file":
                    if df.empty:
                        ProgressManager.error(task_key, tc.NO_DATA_TO_PROCESS)
                        return jsonify({STR_ERROR: True, STR_MESSAGE: tc.NO_DATA_TO_PROCESS})
                if selected_action == tc.TASK_ADD_STUDENTS:
                    if input_method == "manual":
                        result = Talmud(request_form_dict, username, password, f"{int(branch):02}", task_key=task_key).perform(selected_action)
                    else:
                        data = {"data_df": df, "inputMethod": "file", "skipExistingStudents": request_form_dict["skipExistingStudents"]}
                        result = Talmud(data, username, password, f"{int(branch):02}", task_key=task_key).perform(selected_action)
                else:
                    result = Talmud(df, username, password, task_key=task_key).perform(selected_action)

                # Check if result has error first
                if result and result.get(STR_ERROR, False):
                    ProgressManager.error(task_key, result.get(STR_MESSAGE, "Unknown error"))
                    return jsonify(result)

                if result and STR_FILE_DATA in result.keys():
                    if selected_action == tc.TASK_APPROVE_STUDENTS:
                        # Create a string representation of the list
                        file_content = ",".join(result[STR_FILE_DATA])

                        # Return the file as a response
                        return Response(
                            file_content,
                            mimetype="text/plain",
                            headers={
                                "Content-Disposition": "attachment;filename=no_action_performed.txt"
                            }
                        )
                    if selected_action == tc.TASK_ADD_STUDENTS:
                        headers = ["מזהה תלמיד", "הצלחה", "הודעה"]
                        df = pd.DataFrame(result[STR_FILE_DATA], columns=headers)
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Sheet1')
                        output.seek(0)
                        timestamp = datetime.now().strftime("%d-%m-%Y-%M-%H")
                        filename = f"data_{timestamp}.xlsx"

                        # Return the file as a response
                        return Response(
                            output,
                            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                            headers={"Content-Disposition": "attachment;filename={filename}"
                                     }
                        )
                    return jsonify({STR_ERROR: False, STR_MESSAGE: tc.TRANSFER_SUCCESS})

                ProgressManager.finish(task_key)
                return jsonify(result if result else {STR_ERROR: True, STR_MESSAGE: "No result returned"})
            return jsonify({STR_ERROR: True, STR_MESSAGE: "משהו השתבש נסה שוב..."})
            # return send_file(OUTPUT_PAYMENT_FILE_PATH, as_attachment=True, download_name="payment_checks.pdf", mimetype='application/pdf')
        except Exception as e:
            ProgressManager.error(task_key, str(e))
            return jsonify({STR_ERROR: True, STR_MESSAGE: str(e)})

class TalmudProgressAPI(Resource):
    @login_required()
    def get(self):
        request_args = request.args.to_dict()
        selected_action = request_args.get('action')
        if not selected_action:
            return jsonify({STR_ERROR: True, STR_MESSAGE: 'Missing action parameter'})
        task_key = f"talmud:{current_user[0]['id']}:{selected_action}"
        state = ProgressManager.get(task_key)
        return jsonify({"error": False, "data": state})

class TalmudDownloadAPI(Resource):
    @login_required()
    def get(self):
        """Download a file from the results folder by file path"""
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({STR_ERROR: True, STR_MESSAGE: 'Missing path parameter'}), 400
        
        import os
        import school_manager.constants.talmud as tc
        
        # Security check: ensure file is in the results folder
        results_folder = os.path.abspath(tc.RESULTS_FOLDER_NAME)
        requested_path = os.path.abspath(file_path)
        
        if not requested_path.startswith(results_folder):
            return jsonify({STR_ERROR: True, STR_MESSAGE: 'Invalid file path'}), 403
        
        if not os.path.exists(requested_path):
            return jsonify({STR_ERROR: True, STR_MESSAGE: 'File not found'}), 404
        
        # Extract filename from path for download
        filename = os.path.basename(requested_path)
        
        return send_file(
            requested_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


