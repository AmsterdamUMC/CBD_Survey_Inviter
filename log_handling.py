import os
import json
import traceback
from datetime import datetime
from tkinter import messagebox


class ErrorClass(Exception):
    # Placeholder exception class to inherit from Exception or BaseException
    pass


def handle_error(error):
    # Get the traceback information as a string
    traceback_info = traceback.format_exc()

    # Check if the file exists and delete
    if "IMPORT_FILE_PATH" in os.environ:
        datetime_now = datetime.now().strftime("%d_%m_%Y_%H%M%S")
        full_error_file_path = os.path.join(
            os.environ["IMPORT_FILE_PATH"], "error_log_", datetime_now, ".txt"
        )
        if os.path.isfile(full_error_file_path):
            os.remove(full_error_file_path)
    else:
        current_dir = os.getcwd()  # Get the current working directory
        datetime_now = datetime.now().strftime("%d_%m_%Y_%H%M%S")
        full_error_file_path = current_dir + "\\error_log_" + datetime_now + ".txt"
        os.environ["ERROR_LOG_FILE_PATH"] = full_error_file_path

    # check if script is run from Pycharm to raise error directly, else write to file
    if "PYCHARM_HOSTED" in os.environ:
        raise ErrorClass(traceback_info)
    else:
        # Write the error and traceback to the file
        with open(full_error_file_path, "w") as file:
            file.write(f"Error: {str(error)}\n")
            file.write("Traceback:\n")
            file.write(traceback_info)
            log_or_show_message(
                f"An error occurred, please report to rdm@amsterdamumc.nl and include details from {os.environ['ERROR_LOG_FILE_PATH']}",
                "GUI",
                "error",
            )
            print(
                f"An error occurred, please report to rdm@amsterdamumc.nl and include details from {os.environ['ERROR_LOG_FILE_PATH']}"
            )


def log_or_show_message(
    message, presentation_type, message_type="", tkinter_frame=None, progress_label=None
):

    # handle GUI/CLI logs
    if presentation_type == "GUI":
        if message_type == "config":
            # Update the tkinter progress bar label
            progress_label.config(text=message)
            tkinter_frame.update()
        elif message_type == "error":
            messagebox.showerror(title="Error", message=message)
        elif message_type == "warning":
            messagebox.showwarning(title="Warning", message=message)
    elif presentation_type == "CLI":
        # Write the message to a file for CLI
        log_path = os.path.join(os.environ["LOGS_PATH"], "cli_log.txt")
        if os.path.isfile(log_path) and os.environ["INITIAL_LOG_WRITE"] == "Yes":

            # Delete the file, reset environ variable
            os.remove(log_path)
            os.environ["INITIAL_LOG_WRITE"] = "No"

        # open file and write/append
        with open(log_path, "a") as log_file:
            log_file.write(message + "\n")
    else:
        # Handle other presentation types or errors
        print("Unsupported presentation type")


def update_progress_bar(tkinter_frame, progress_bar):
    # update tkinter window progress bar
    progress_bar["value"] += 1
    tkinter_frame.update()


def write_warning_to_file(warn, file_path):
    try:
        with open(file_path, "a") as file:
            file.write(
                f"File: {warn.filename}, Line: {warn.lineno}, Warning: {warn.message}"
            )
            file.write("\n")
    except Exception as err:
        print(f"An error occurred while writing to the warning log file: {str(err)}")


def log_import_status(
    data, result, json_result, participant_id_raw, import_log_file_path, field_name=""
):
    if result == "Internal Server Error":
        import_status = "500, " + result
        with open(import_log_file_path, "a") as f:
            f.write(
                f"Participant ID: '{participant_id_raw}' processed with result: '{import_status}'\n"
            )
    elif "errors" in json_result:
        import_status = json_result["status"] + json_result["detail"]
        with open(import_log_file_path, "a") as f:
            f.write(
                f"Participant ID: '{participant_id_raw}' processed with result: '{import_status}'\n"
            )
    elif field_name != "" and "total_failed" in json_result:
        with open(import_log_file_path, "a") as f:
            f.write(
                f"Participant ID: '{participant_id_raw}' could not process field: {field_name}\n"
            )
    elif "total_failed" in json_result and json_result["total_failed"] != 0:
        # get failed data
        failed_data = json_result.get("failed", [])

        # Concatenate the "code" and "message" elements for each failed entry
        field_id_list = [entry["field_id"] for entry in failed_data]
        failed_message = []
        for field in failed_data:
            failed_message.append(field["code"] + ", " + field["message"])

        # Search for matches (between "field_id_list" and "data" (a list containing all field IDs, field names and field types from Castor)
        matches = []
        for field_id in field_id_list:
            for item in data:
                if field_id == item[0]:
                    matches.append('"' + item[1] + '"')
                    break  # Break the inner loop once a match is found

        # Combine the strings from both lists
        combined_strings = [
            f"{field_id}: {message}"
            for field_id, message in zip(matches, failed_message)
        ]
        import_status = "\n".join(combined_strings)

        with open(import_log_file_path, "a") as f:
            f.write(
                f"Participant ID: '{participant_id_raw}' could not process the following field(s):\n"
            )
            f.write(f"{import_status}\n")
    else:  # extract the first element from JSON object
        import_status = next(iter(json.loads(result)))
        if field_name != "":
            if import_status == "participant_id":
                import_status = "Success"
            with open(import_log_file_path, "a") as f:
                f.write(
                    f"Participant ID: '{participant_id_raw}', field: '{field_name}' processed with result: '{import_status}'\n"
                )
        else:
            with open(import_log_file_path, "a") as f:
                f.write(
                    f"Participant ID: '{participant_id_raw}' processed with result: '{import_status}'\n"
                )
