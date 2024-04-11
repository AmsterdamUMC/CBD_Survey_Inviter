import re
import requests as req
from log_handling import *
from tkinter import messagebox


# Function to submit entries from second screen of GUI - MAIN PROCESS START
def submit_file_explorer_entries():

    try:
        # check if all required input fields are filled in
        env_vars = [
            "SELECTED_SURVEY",
            "SELECTED_SURVEY_NAME",
            "SELECTED_SURVEY_PACKAGE",
            "SELECTED_SITE_ID",
            "SELECTED_SITE_NAME",
        ]

        if all(variable in os.environ for variable in env_vars):
            messagebox.showerror(
                title="Let's go",
                message="Do something",
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
    except Exception as err:
        handle_error(err)


# configure button to execute "submit_file_explorer_entries", based on user action
def handle_submit(_window, _frame):
    confirmation_text = "Are you sure you want to submit?"
    result = messagebox.askyesno("Confirmation", confirmation_text)
    if result:
        submit_file_explorer_entries()


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
            site_name_list, site_id_list, site_date_format_list = get_site_lists()
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
            site_name_list, site_id_list, _ = get_site_lists()
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


def get_site_lists():
    from api_call import perform_api_call

    # open session
    session = req.Session()

    # Create and configure the dropdown menu
    site_name_list = []
    site_id_list = []
    site_date_format_list = []
    if "CASTOR_EDC_STUDY_ID" in os.environ:
        castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
        access_token = os.environ["ACCESS_TOKEN"]

        # get page count for sites
        sites_list = json.loads(
            perform_api_call("site", castor_study_id, access_token, "GET")
        )
        page_count = sites_list["page_count"]

        # Loop over the pages and retrieve participant data
        paged_sites_list = []
        for i in range(1, page_count + 1):
            api_endpoint = f"site?page={i}"
            paged_field_request = json.loads(
                perform_api_call(
                    api_endpoint, castor_study_id, access_token, "GET", session=session
                )
            )
            paged_sites_list.extend(paged_field_request["_embedded"]["sites"])

        # retrieve lists of id's and names
        for site in paged_sites_list:
            if site["deleted"] is not True:
                site_name_list.append(site["name"])
                site_id_list.append(site["id"])
                site_date_format_list.append(site["date_format"])

        # sort the lists
        sorted_lists = sorted(zip(site_name_list, site_id_list, site_date_format_list))
        site_name_list, site_id_list, site_date_format_list = zip(*sorted_lists)

    return site_name_list, site_id_list, site_date_format_list


def get_survey_lists():
    from api_call import perform_api_call

    # open session
    session = req.Session()

    # Create and configure the dropdown menu
    survey_name_list = []
    survey_id_list = []
    if "CASTOR_EDC_STUDY_ID" in os.environ:
        castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
        access_token = os.environ["ACCESS_TOKEN"]

        # get page count for surveys
        survey_list = json.loads(
            perform_api_call("survey", castor_study_id, access_token, "GET")
        )
        page_count = survey_list["page_count"]

        # Loop over the pages and retrieve participant data
        paged_surveys_list = []
        for i in range(1, page_count + 1):
            api_endpoint = f"survey?page={i}"
            paged_field_request = json.loads(
                perform_api_call(
                    api_endpoint, castor_study_id, access_token, "GET", session=session
                )
            )
            paged_surveys_list.extend(paged_field_request["_embedded"]["surveys"])

        # retrieve lists of id's and names
        for survey in paged_surveys_list:
            survey_name_list.append(survey["name"])
            survey_id_list.append(survey["id"])

        # sort the lists
        sorted_lists = sorted(zip(survey_name_list, survey_id_list))
        survey_name_list, survey_id_list = zip(*sorted_lists)

    return survey_name_list, survey_id_list


def get_survey_package_list(selected_survey_id):
    from api_call import perform_api_call

    if "CASTOR_EDC_STUDY_ID" in os.environ:
        castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
        access_token = os.environ["ACCESS_TOKEN"]

        existing_survey_packages = json.loads(
            perform_api_call("survey-package", castor_study_id, access_token, "GET")
        )
        page_count = existing_survey_packages["page_count"]

        # Loop over the pages and retrieve existing repeating data instances
        paged_existing_package_request = []
        for i in range(1, page_count + 1):
            category = f"survey-package?page={i}"
            paged_survey_package_request = json.loads(
                perform_api_call(category, castor_study_id, access_token, "GET")
            )
            paged_existing_package_request.extend(
                paged_survey_package_request["_embedded"]["survey_packages"]
            )

        # Extract matching survey_packages from the JSON response
        matching_package_ids = []
        matching_package_names = []
        for package in paged_existing_package_request:
            package_id = package["survey_package_id"]
            package_name = package["name"]
            embedded = package["_embedded"]["surveys"]
            for survey in embedded:
                survey_id = survey["survey_id"]
                if survey_id == selected_survey_id:
                    matching_package_ids.append(package_id)
                    matching_package_names.append(package_name)

        if matching_package_names and matching_package_ids:
            # sort the lists
            sorted_lists = sorted(zip(matching_package_names, matching_package_ids))
            matching_package_names, matching_package_ids = zip(*sorted_lists)

        return matching_package_ids, matching_package_names
