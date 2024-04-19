import os
import json
import requests as req


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
