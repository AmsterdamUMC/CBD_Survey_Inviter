import os
import json
import requests as req


def get_site_lists():
    from api_call import perform_api_call

    # open session
    session = req.Session()

    # Create and configure the dropdown menu
    site_name_list = []
    site_id_list = []
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

        # sort the lists
        sorted_lists = sorted(zip(site_name_list, site_id_list))
        site_name_list, site_id_list = zip(*sorted_lists)

    return site_name_list, site_id_list
