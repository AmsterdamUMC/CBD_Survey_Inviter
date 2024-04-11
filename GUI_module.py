import sys
import time
import warnings
from tkinter import *
from tkinter import ttk
from functools import partial
from tkinter import filedialog
from GUI_helper_functions import *
from PIL import Image, ImageTk  # pip install pillow
from get_API_access_token import verify_api_credentials


# First screen of GUI, used to verify API credentials and getting an API access token:
def start_gui(root_window):
    # store access_token initialization time in environment variable
    now = str(time.time())
    os.environ["TIME_INIT_ACCESS"] = now

    # initialize one more environment variable
    os.environ["NUMBER_OF_CALLS"] = ""

    # temporarily hide the window to avoid the flickering effect when centering the window
    root_window.withdraw()

    # Create an image widget
    image = Image.open(image_path)

    # Set the desired size in pixels
    width, height = 12, 12

    # Resize the image
    image = image.resize((width, height), Image.LANCZOS)

    # Create a PhotoImage object from the resized image
    photo_image = ImageTk.PhotoImage(image)

    # Create a frame to hold both image and text
    frame_label_widget = Frame(root_window)

    # Create a label to display the image
    image_label = Label(frame_label_widget, image=photo_image)
    image_label.grid(row=0, column=1)

    # Create a label to go on frame outline
    label_text = Label(frame_label_widget, text="Castor API credentials")
    label_text.grid(row=0, column=0)

    def show_hover_text(event):
        try:
            # Create a Toplevel window as the message box
            message_box = Toplevel(root_window)
            message_box.wm_attributes("-topmost", 1)  # Set the message box as topmost

            # Set the position of the message box relative to the mouse cursor
            x, y, _, _ = event.widget.bbox("insert")
            x += (
                root_window.winfo_rootx()
            )  # Adjust the x-coordinate to position the message box
            y += (
                root_window.winfo_rooty() + 45
            )  # Adjust the y-coordinate to position the message box
            message_box.geometry(f"+{x}+{y}")

            # Create a Label to display the hover text
            hover_text_label = Label(
                message_box,
                wraplength=300,
                text="To retrieve these credentials, go to 'User settings', then click the 'Castor EDC API' tab and copy your 'Client ID' and 'Client secret'",
            )
            hover_text_label.grid(row=0, column=1, padx=10, pady=5)

            # Bind the Leave event to destroy the message box
            event.widget.bind("<Leave>", lambda ee: message_box.destroy())

        except Exception as err:
            handle_error(err)

    # Bind the hover text to the image using the Enter event
    image_label.bind("<Enter>", show_hover_text)

    # define frame
    castor_db_info_frame = LabelFrame(root_window, labelwidget=frame_label_widget)
    castor_db_info_frame.grid(row=0, column=0, padx=20, pady=20)

    # labels "castor_db_info_frame"
    client_id_label = Label(castor_db_info_frame, text="Client ID*")
    client_secret_label = Label(castor_db_info_frame, text="Client Secret*")

    # entries "castor_db_info_frame"
    entry_width = 40
    client_id_entry = Entry(castor_db_info_frame, width=entry_width)
    client_secret_entry = Entry(castor_db_info_frame, width=entry_width, show="*")

    # placement labels "castor_db_info_frame"
    client_id_label.grid(row=0, column=0, sticky="w")
    client_secret_label.grid(row=1, column=0, sticky="w")

    # placement entries "castor_db_info_frame"
    client_id_entry.grid(row=0, column=1)
    client_secret_entry.grid(row=1, column=1)

    for widget in castor_db_info_frame.winfo_children():
        widget.grid_configure(padx=10, pady=5)

    # button
    button = Button(
        root_window,
        text="Verify API credentials",
        command=lambda: verify_api_credentials(
            client_id_entry.get().strip(),
            client_secret_entry.get().strip(),
            root_window,
        ),
    )
    button.grid(row=1, column=0, sticky="news", padx=20, pady=5)

    # update root to retrieve proper size of the window
    root_window.update()

    # center and resize window
    center_and_resize_window(root_window)

    # show the window again
    root_window.deiconify()

    root_window.mainloop()


# Second screen of GUI, used to select files/folders to use for importing data and to miscellaneous checkbox options
def initialize_file_explorer(root_window, client_id, client_secret):
    try:
        from api_call import perform_api_call
        from get_API_access_token import get_access_token

        root_window.destroy()

        # Create the root window
        window = Tk()
        window.title("File Explorer")

        # temporarily hide the window to avoid the flickering effect when centering the window
        window.withdraw()

        frame = Frame(window)
        frame.pack()

        # retrieve a list of studies the current authenticated user has access to:
        access_token, access_granted = get_access_token(client_id, client_secret)
        study_list = json.loads(
            perform_api_call("", "", access_token, "GET", "NO_PARAMS")
        )
        study_list = study_list["_embedded"]["study"]

        study_list_name = []
        study_list_id = []
        for study in study_list:
            study_list_name.append(study["name"])
            study_list_id.append(study["study_id"])

        # sort the study_lists
        sorted_lists = sorted(zip(study_list_name, study_list_id))
        study_list_name, study_list_id = zip(*sorted_lists)

        # -- "castor_db_info_frame"
        castor_db_info_frame = LabelFrame(frame, text="Castor EDC Study Database")
        castor_db_info_frame.grid(row=0, column=0, padx=20, pady=20, sticky="news")
        study_id_label = Label(castor_db_info_frame, text="Castor Study*")
        study_id_label.grid(row=0, column=0)

        selected_option = StringVar(window)
        selected_option.set(
            "Please Select Castor Study Database"
        )  # set the default selected option
        option_menu = ttk.Combobox(
            castor_db_info_frame, textvariable=selected_option, values=study_list_name
        )
        combobox_width = len(option_menu.get())
        option_menu.configure(width=combobox_width)
        option_menu.grid(row=0, column=1)

        # -- "import_frame"
        import_frame = LabelFrame(frame, text="Import file")
        import_frame.grid(row=1, column=0, padx=20, pady=20, sticky="news")
        label_import_file_explorer = Label(
            import_frame,
            text="Select a CSV file to upload data set/participant list",
            fg="blue",
        )
        label_import_file_explorer.grid(row=0, column=0)
        import_button_explore = Button(
            import_frame,
            text="Browse Files",
            command=lambda: browse_files(label_import_file_explorer),
        )
        import_button_explore.grid(row=2, column=0, sticky="w")

        # -- "survey_frame"
        survey_frame = LabelFrame(frame, text="Survey Parameters")
        survey_frame.grid(row=5, column=0, padx=20, pady=20, sticky="news")

        # -- "survey_sub_select_frame"
        survey_select_frame = Frame(survey_frame)
        survey_select_frame.grid(row=4, column=0, padx=20, pady=20, sticky="news")

        # Create combobox for site list
        label_site_dropdown = Label(survey_frame, text="Site:")
        label_site_dropdown.grid(row=0, column=0, sticky="w")
        site_combobox = ttk.Combobox(survey_frame)
        site_combobox.grid(row=0, column=1)

        # Create combobox for survey list
        label_survey_dropdown = Label(survey_frame, text="Survey:")
        label_survey_dropdown.grid(row=1, column=0, sticky="w")
        survey_combobox = ttk.Combobox(survey_frame)
        survey_combobox.grid(row=1, column=1)

        # Create combobox for survey package list
        label_survey_dropdown = Label(survey_frame, text="Survey Package:")
        label_survey_dropdown.grid(row=2, column=0, sticky="w")
        survey_package_combobox = ttk.Combobox(survey_frame)
        survey_package_combobox.grid(row=2, column=1)

        # Bind on_selection_changed function to option_menu combobox
        option_menu.bind(
            "<<ComboboxSelected>>",
            partial(
                on_selection_changed,
                option_name_list=study_list_name,
                option_id_list=study_list_id,
                dropdown_name="castor database",
                site_combobox=site_combobox,
                survey_combobox=survey_combobox,
            ),
        )

        # Bind on_selection_changed function to site_combobox combobox
        site_combobox.bind(
            "<<ComboboxSelected>>",
            partial(
                on_selection_changed,
                option_name_list=study_list_name,
                option_id_list=study_list_id,
                dropdown_name="site",
                site_combobox=site_combobox,
                survey_combobox=survey_combobox,
                survey_package_menu=survey_package_combobox,
            ),
        )

        # Bind on_selection_changed function to survey_combobox combobox
        survey_combobox.bind(
            "<<ComboboxSelected>>",
            partial(
                on_selection_changed,
                option_name_list=study_list_name,
                option_id_list=study_list_id,
                dropdown_name="survey",
                site_combobox=site_combobox,
                survey_combobox=survey_combobox,
                survey_package_menu=survey_package_combobox,
            ),
        )

        # Bind on_selection_changed function to survey_package_combobox combobox
        survey_package_combobox.bind(
            "<<ComboboxSelected>>",
            partial(
                on_selection_changed,
                option_name_list=study_list_name,
                option_id_list=study_list_id,
                dropdown_name="survey_package",
                site_combobox=site_combobox,
                survey_package_menu=survey_package_combobox,
            ),
        )

        # Initially, the button command is set to None to handle the order issue with the "confirmation warning"
        button_submit = Button(
            frame, text="Submit", command=lambda: handle_submit(window, frame)
        )
        button_submit.grid(row=6, column=0, sticky="news")

        # grid styling
        apply_grid_configure(frame)
        apply_grid_configure(castor_db_info_frame)
        apply_grid_configure(import_frame)
        apply_grid_configure(survey_frame)
        apply_grid_configure(survey_select_frame)

        # update root to retrieve proper size of the window
        window.update()
        center_window(window)

        # show the window again
        window.deiconify()
        window.mainloop()

    except Exception as err:
        handle_error(err)


# Function to browse files in second screen of GUI
def browse_files(label_file_explorer, file_type=""):
    try:
        if "CASTOR_EDC_STUDY_ID" in os.environ:
            if file_type == "validation_result":
                filename_path = filedialog.askdirectory(
                    initialdir="/", title="Select a directory to save files"
                )
                slash_position = filename_path.rfind("/")
                filepath = filename_path + "/"
            else:
                filename_path = filedialog.askopenfilename(
                    initialdir="/",
                    title="Select a File",
                    filetypes=(("CSV files", "*.csv*"),),
                )
                slash_position = filename_path.rfind("/")
                filepath = filename_path[: slash_position + 1]

            filename = filename_path[slash_position + 1 :]
            database_name = os.environ["CASTOR_EDC_STUDY_NAME"]

            # Change label contents
            if file_type == "validation_result":
                if filepath != "/":  # type selected and filepath != empty
                    datetime_now = datetime.now().strftime("%d_%m_%Y_%H%M%S")
                    os.environ["FULL_EXPORT_FILE_PATH"] = (
                        filepath
                        + "validation_export_"
                        + database_name
                        + "_"
                        + datetime_now
                        + ".csv"
                    )
                    os.environ["VALIDATION_RESULT_FILE_PATH"] = (
                        filepath
                        + "validation_results_"
                        + database_name
                        + "_"
                        + datetime_now
                        + ".txt"
                    )
                    os.environ["FULL_VALIDATION_IMPORT_FILE_PATH"] = (
                        filepath
                        + "validation_import_"
                        + database_name
                        + "_"
                        + datetime_now
                        + ".csv"
                    )
                    os.environ["IMPORT_LOG_FILE_PATH"] = (
                        filepath + "import_results_" + datetime_now + ".txt"
                    )
                label_file_explorer.configure(text="Folder selected: " + filename)
            else:
                os.environ["IMPORT_FILE_PATH"] = filepath.replace("/", "\\")
                os.environ["IMPORT_FILE_NAME"] = filename
                label_file_explorer.configure(text="File selected: " + filename)
        else:
            messagebox.showerror(
                title="Castor Study ID missing",
                message="Please select your Castor Study Database first",
            )

    except Exception as err:
        handle_error(err)


# Get the base directory of the executable
base_dir = getattr(sys, "_MEIPATH", os.path.abspath(os.path.dirname(__file__)))

# Construct the path to the image file relative to the base directory
image_path = os.path.join(base_dir, "help_icon.png")

# Enable warning capture
warnings.filterwarnings("always")

# Get the list of captured warnings
with warnings.catch_warnings(record=True) as captured_warnings:
    # start main script
    if __name__ == "__main__":
        try:
            # Global variable to store the initial window size
            initial_window_size = None

            # Call the start_gui function to start the process, only when run from "main" and not when importing
            root = Tk()
            root.title("CastorDataBridge")
            start_gui(root)
        except Exception as e:
            handle_error(e)

# Iterate over the captured warnings and print them
for warning in captured_warnings:
    # Check if the file exists and delete
    full_file_path = os.path.join(os.environ["IMPORT_FILE_PATH"], "warning_log.txt")
    if os.path.isfile(full_file_path):
        os.remove(full_file_path)
    write_warning_to_file(warning, full_file_path)
