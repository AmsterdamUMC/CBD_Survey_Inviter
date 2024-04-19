import os
import json


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
