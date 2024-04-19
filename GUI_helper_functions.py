import csv
import threading
from tkinter import *
from tkinter import ttk
from send_survey_invite import *
from get_site_list import get_site_lists
from get_survey_list import get_survey_lists
from get_survey_package_list import get_survey_package_list


# Function to submit entries from second screen of GUI - MAIN PROCESS START
def submit_file_explorer_entries(root_window, frame):

    try:
        # check if all required input fields are filled in
        env_vars = [
            "SELECTED_SURVEY",
            "SELECTED_SURVEY_NAME",
            "SELECTED_SURVEY_PACKAGE",
            "SELECTED_SITE_ID",
            "SELECTED_SITE_NAME",
            "IMPORT_FILE_PATH",
            "IMPORT_HEADER_FILE_PATH",
        ]

        import_header_path = os.environ["IMPORT_HEADER_FILE_PATH"]
        import_header_name = os.environ["IMPORT_HEADER_FILE_NAME"]
        encodings_to_try = ["UTF-8", "ISO-8859-1"]
        df = pd.DataFrame()
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(
                    import_header_path + import_header_name,
                    delimiter=";",
                    encoding=encoding,
                )
                break  # If successful, exit the loop
            except UnicodeDecodeError:
                print(
                    f" Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
                )

        # get package invitation info
        package_invitation_subject = None
        if "Subject" in df.columns:
            package_invitation_subject = df["Subject"][0]

        # read survey info csv
        import_file_path = os.environ["IMPORT_FILE_PATH"]
        import_file_name = os.environ["IMPORT_FILE_NAME"]
        df = pd.DataFrame()
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(
                    import_file_path + import_file_name,
                    delimiter=";",
                    encoding=encoding,
                )
                break  # If successful, exit the loop
            except UnicodeDecodeError:
                print(
                    f" Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
                )

        if (
            all(variable in os.environ for variable in env_vars)
            and any(
                col.lower() in df.columns.str.lower()
                for col in ["email_address", "email address"]
            )
            and any(
                col.lower() in df.columns.str.lower()
                for col in ["participant_id", "participant id"]
            )
            and package_invitation_subject is not None
        ):
            # change title
            root_window.title("Sending out Surveys")

            # empty the frame and create a blank one
            frame.destroy()
            new_frame = Frame(root_window, width=200, height=200)
            new_frame.pack()

            progress_label = Label(new_frame, text="Processing surveys...")
            progress_label.grid(row=0, column=0, padx=10, pady=10)

            progress_bar = ttk.Progressbar(
                new_frame, orient="horizontal", length=300, mode="determinate"
            )
            progress_bar.grid(row=1, column=0, padx=10, pady=10)

            # update root/frame to retrieve proper size of the window
            root_window.update()
            new_frame.update_idletasks()

            # get screen width and height
            screen_width = root_window.winfo_screenwidth()
            screen_height = root_window.winfo_screenheight()

            # calculate window position
            window_width = new_frame.winfo_width()
            window_height = new_frame.winfo_height()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            # adjust "root" window placement
            root_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # # update root to retrieve proper size of the window
            root_window.update()
            frame.update_idletasks()

            # get some specifics about (to be) imported data set
            import_file_path = os.environ["IMPORT_FILE_PATH"]
            import_file_name = os.environ["IMPORT_FILE_NAME"]

            encodings_to_try = ["UTF-8", "ISO-8859-1"]
            df_survey_file = pd.DataFrame()
            for encoding in encodings_to_try:
                try:
                    df_survey_file = pd.read_csv(
                        import_file_path + import_file_name,
                        delimiter=";",
                        encoding=encoding,
                    )
                    break  # If successful, exit the loop
                except UnicodeDecodeError:
                    print(
                        f" Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
                    )

            total_participants = len(df_survey_file.index)
            progress_bar["maximum"] = total_participants * 2  # each row has two events

            # start asynchronize import while progress bar is shown
            t = threading.Thread(
                target=send_survey_invite(
                    root_window, new_frame, progress_bar, progress_label
                )
            )
            t.start()
        elif "IMPORT_HEADER_FILE_PATH" not in os.environ:
            messagebox.showerror(
                title="Survey Header Info Missing",
                message="Please select a CSV file with survey header info",
            )
        elif "IMPORT_FILE_PATH" not in os.environ:
            messagebox.showerror(
                title="Survey Data Missing",
                message="Please select a CSV file for your survey data",
            )
        elif "CASTOR_EDC_STUDY_ID" not in os.environ:
            messagebox.showerror(
                title="Castor Study ID Missing",
                message="Please provide a Castor EDC Study ID",
            )
        elif (
            "SELECTED_SURVEY_PACKAGE" not in os.environ
            or "SELECTED_SURVEY" not in os.environ
        ):
            messagebox.showerror(
                title="Castor Survey Data Missing",
                message="Please fill in all required fields for Surveys",
            )
        elif (
            "SELECTED_SITE_ID" not in os.environ
            or "SELECTED_SITE_NAME" not in os.environ
        ):
            messagebox.showerror(
                title="Castor Site Info Missing",
                message="Please select a Site",
            )
        elif all(
            col.lower() not in df.columns.str.lower()
            for col in ["email_address", "email address"]
        ):
            messagebox.showerror(
                title="Email Missing",
                message="Please provide a 'Email Address' column in your survey CSV",
            )

        elif all(
            col.lower() not in df.columns.str.lower()
            for col in ["participant_id", "participant id"]
        ):
            messagebox.showerror(
                title="Participant Info Missing",
                message="Please provide a 'Participant ID' column in your survey CSV",
            )
        elif package_invitation_subject is None:
            messagebox.showerror(
                title="Package Invitation Subject missing",
                message="Please provide a 'Subject' column in your header CSV",
            )

    except Exception as err:
        handle_error(err)


# configure button to execute "submit_file_explorer_entries", based on user action
def handle_submit(_window, _frame):
    confirmation_text = "Are you sure you want to submit?"
    result = messagebox.askyesno("Confirmation", confirmation_text)
    if result:
        submit_file_explorer_entries(_window, _frame)


# Function to apply grid configuration (padding) to all widgets in a frame
def apply_grid_configure(_frame, padding_x=10, padding_y=5):
    for _widget in _frame.winfo_children():
        if _widget.widgetName != "radiobutton":
            _widget.grid_configure(padx=padding_x, pady=padding_y)
        elif _widget.widgetName == "radiobutton":
            _widget.grid_configure(padx=padding_x)


def center_and_resize_window(window):
    try:

        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate the window position
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    except Exception as err:
        handle_error(err)


def center_window(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - window.winfo_reqwidth()) // 2
    y = (screen_height - window.winfo_reqheight()) // 2
    window.geometry(f"+{x}+{y}")


def on_selection_changed(
    event,
    option_name_list,
    option_id_list,
    dropdown_name,
    survey_package_menu=None,
    site_combobox=None,
    survey_combobox=None,
):

    try:
        selected_option_text = event.widget.get()

        if dropdown_name == "castor database":

            # Update the database combobox based on the selected Castor database
            selected_option_index = option_name_list.index(selected_option_text)
            selected_id = option_id_list[selected_option_index]
            os.environ["CASTOR_EDC_STUDY_ID"] = selected_id

            # Update the site combobox based on the selected Castor database
            site_name_list, site_id_list = get_site_lists()
            site_combobox["values"] = site_name_list

            # Update the survey combobox based on the selected Castor database
            (
                survey_name_list,
                survey_id_list,
            ) = get_survey_lists()
            survey_combobox["values"] = survey_name_list

            # remove all special characters before storing selected study name
            # this name will be used as a part of the generated validation files
            special_chars = '\\/+,.";:()[]{}!@$%^&*|?<>ï»¿'
            new_selected_option_text = (
                selected_option_text.encode("ascii", "ignore")
            ).decode("utf-8")
            new_selected_option_text = re.sub(
                r"[{}]+".format(re.escape(special_chars)), "", new_selected_option_text
            )
            new_selected_option_text = new_selected_option_text.replace(" ", "_")
            os.environ["CASTOR_EDC_STUDY_NAME"] = new_selected_option_text
        elif dropdown_name == "site":
            site_name_list, site_id_list = get_site_lists()
            selected_option_index = site_name_list.index(selected_option_text)
            selected_id = site_id_list[selected_option_index]
            selected_name = site_name_list[selected_option_index]

            # store selected site
            os.environ["SELECTED_SITE_ID"] = selected_id
            os.environ["SELECTED_SITE_NAME"] = selected_name

        elif dropdown_name == "survey":
            (
                survey_name_list,
                survey_id_list,
            ) = get_survey_lists()
            selected_option_index = survey_name_list.index(selected_option_text)
            selected_id = survey_id_list[selected_option_index]
            selected_name = survey_name_list[selected_option_index]

            # store selected report to be used
            os.environ["SELECTED_SURVEY"] = selected_id
            os.environ["SELECTED_SURVEY_NAME"] = selected_name

            # Show the second dropdown if radio_value is 3 and a survey is selected
            survey_package_ids, survey_package_names = get_survey_package_list(
                selected_id
            )

            if survey_package_names:
                survey_package_menu["values"] = survey_package_names
            else:
                survey_package_menu["values"] = []

        elif dropdown_name == "survey_package":
            survey_package_ids, survey_package_names = get_survey_package_list(
                os.environ["SELECTED_SURVEY"]
            )
            selected_option_index = survey_package_names.index(selected_option_text)
            selected_id = survey_package_ids[selected_option_index]

            # set environment variable
            os.environ["SELECTED_SURVEY_PACKAGE"] = selected_id

    except Exception as exception:
        handle_error(exception)


def get_csv_rows_headers(input_file_path, input_file):

    # List of encodings to try
    encodings_to_try = ["UTF-8", "ISO-8859-1"]
    for encoding in encodings_to_try:
        try:
            with open(
                input_file_path + input_file, "r", encoding=encoding, newline=""
            ) as csv_file:
                csv_dict_reader = csv.DictReader(csv_file, delimiter=";")
                csv_header = csv_dict_reader.fieldnames
                csv_rows = [list(row.values()) for row in csv_dict_reader]
            break  # If successful, exit the loop
        except UnicodeDecodeError:
            print(
                f"Warning: Failed to decode with encoding {encoding}. Trying the next encoding."
            )

    return csv_header, csv_rows
