import pandas as pd
import tkinter as tk
import requests as req
from log_handling import *
from helper_functions import *
from api_call import perform_api_call


def send_survey_invite(
    tkinter_window=None, tkinter_frame=None, progress_bar=None, progress_label=None
):

    from GUI_helper_functions import apply_grid_configure

    # get log file path and write
    import_log_file_path = os.environ["IMPORT_LOG_FILE_PATH"]
    with open(import_log_file_path, "w") as file:
        file.write("---- STARTING SURVEY INVITATION SET ----\n")

    # open session
    session = req.Session()

    # update GUI
    log_or_show_message(
        "Start sending out surveys", "GUI", "config", tkinter_frame, progress_label
    )

    # get API specific parameters
    castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
    access_token = os.environ["ACCESS_TOKEN"]

    # read import file from csv
    import_file_path = os.environ["IMPORT_FILE_PATH"]
    import_file_name = os.environ["IMPORT_FILE_NAME"]
    encodings_to_try = ["UTF-8", "ISO-8859-1"]
    df = pd.DataFrame()
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(
                import_file_path + import_file_name, delimiter=";", encoding=encoding
            )

            # Clean column names
            special_chars = '\\/+,.-";:()[]{}!@$%^&*|?<>ï»¿'
            csv_header = list(df.columns)
            for i in range(len(csv_header)):
                new_column_name = (csv_header[i].encode("ascii", "ignore")).decode(
                    "utf-8"
                )
                new_column_name = re.sub(
                    r"[{}]+".format(re.escape(special_chars)), "", new_column_name
                )
                new_column_name = new_column_name.replace(" ", "_").lower()
                csv_header[i] = new_column_name

            df.columns = csv_header

            break  # If successful, exit the loop
        except UnicodeDecodeError:
            print(
                f" Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
            )

    # read header info from csv
    import_header_path = os.environ["IMPORT_HEADER_FILE_PATH"]
    import_header_name = os.environ["IMPORT_HEADER_FILE_NAME"]
    df_header = pd.DataFrame()
    for encoding in encodings_to_try:
        try:
            df_header = pd.read_csv(
                import_header_path + import_header_name,
                delimiter=";",
                encoding=encoding,
            )

            # Replace escaped newline characters '\\n' with '\n'
            df_header = df_header.replace(r"\\n", "\n", regex=True)

            break  # If successful, exit the loop
        except UnicodeDecodeError:
            print(
                f" Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
            )

    # get package invitation info
    package_invitation_subject = None
    if "Subject" in df_header.columns:
        package_invitation_subject = df_header["Subject"][0]

    # get participant ID column index
    matched_participant_id_key = search_participant_column_index(df.columns)

    # create timestamp for this set of surveys
    now = datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    for index, row in df.iterrows():
        email = row["email_address"]
        survey_package_id = os.environ["SELECTED_SURVEY_PACKAGE"]

        # change the body content {tags} values with values from the current row
        df_package_invitation = df_header.apply(
            lambda r: replace_placeholders(row, df_header["Body"], df), axis=1
        )
        package_invitation = df_package_invitation[0]

        # update GUI
        log_or_show_message(
            "Getting or Creating Participant ID",
            "GUI",
            "config",
            tkinter_frame,
            progress_label,
        )
        # update progress bar
        update_progress_bar(tkinter_frame, progress_bar)

        participant_id = get_or_create_participant(
            row,
            matched_participant_id_key,
            os.environ["SELECTED_SITE_ID"],
            session,
        )

        # create survey package instance
        post_data = {
            "survey_package_id": survey_package_id,
            "participant_id": participant_id,
            "email_address": email,
            "package_invitation_subject": package_invitation_subject,
            "package_invitation": package_invitation,
            "auto_send": True,
            "auto_lock_on_finish": True,
        }

        # update GUI
        log_or_show_message(
            f"Sending out Survey Package to Participant ID: {participant_id}",
            "GUI",
            "config",
            tkinter_frame,
            progress_label,
        )

        # perform api call to create survey package instance and send out
        category = "survey-package-instance"
        result = perform_api_call(
            category,
            castor_study_id,
            access_token,
            "POST",
            post_data,
            "survey_invite",
            session=session,
        )
        json_result = json.loads(result)
        filename = ""
        if "survey_package_instance_id" in json_result:
            # Save the updated DataFrame to a new CSV file or append to existing (for all subsequent rows)
            filename = f"survey_package_invitations_{now}.csv"
            output_path = os.environ["OUTPUT_PATH"] + "\\" + filename

            # Create a new DataFrame to store the index and text separately
            df_to_save = pd.DataFrame(
                {
                    "Index": df_package_invitation.index,
                    "Participant_ID": participant_id,
                    "Email Body": df_package_invitation[0],
                }
            )

            # Set the index of df_to_save to match the index of df_package_invitation
            df_to_save.set_index("Index", inplace=True)

            # Check if the file exists
            if not os.path.isfile(output_path):
                df_to_save.to_csv(output_path, index=False)
            else:
                df_to_save.to_csv(output_path, mode="a", header=False, index=False)

        else:
            with open(import_log_file_path, "a") as f:
                f.write(f"Couldn't create Survey Package Instance: '{json_result}'\n")

        # update progress bar
        update_progress_bar(tkinter_frame, progress_bar)

    # create "Done" screen
    root = tk.Tk()
    root.title("Done")

    # Create a label widget
    label = tk.Label(
        root,
        text=f"Done sending out surveys! \n "
        f"Please check 'output/{filename}' for an overview of sent survey packages \n"
        f"and 'output/{os.environ['IMPORT_LOG_FILE_NAME']}' for any possible errors.",
    )
    label.grid(row=0, column=0)

    # Create a "Done" button
    def close_app():
        root.destroy()

    done_button = tk.Button(root, text="Done", width=10, command=close_app)
    done_button.grid(row=1, column=0)

    apply_grid_configure(root)

    # Call the restart_new_session function to prompt user for another session
    from GUI_helper_functions import restart_new_session

    restart_new_session(tkinter_window, import_log_file_path)

    # close session
    session.close()
