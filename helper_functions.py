import re
import os
import json
from api_call import perform_api_call


def search_participant_column_index(csv_header):

    # check for the column containing the participant ID
    participant_list_request_id_keys = {
        "PARTICIPANT_ID",
        "PARTICIPANT ID",
        '"PARTICIPANT ID"',
        '"PARTICIPANT_ID"',
        "CASTOR PARTICIPANT ID",
        "CASTOR_PARTICIPANT_ID",
        '"CASTOR PARTICIPANT ID"',
        '"CASTOR_PARTICIPANT_ID"',
    }
    matched_participant_id_key = next(
        (
            i
            for i, x in enumerate(csv_header)
            if x.upper() in participant_list_request_id_keys
        ),
        False,
    )

    return matched_participant_id_key


def create_participant_id(
    participant_id_raw, site_id, import_log_file_path, session
):

    # default params
    castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
    access_token = os.environ["ACCESS_TOKEN"]

    # create new participant ID
    post_fields = {"participant_id": str(participant_id_raw), "site_id": str(site_id)}

    # create new participant ID
    created_participant_id = json.loads(
        perform_api_call(
            "participant",
            castor_study_id,
            access_token,
            "POST",
            post_fields,
            session=session,
        )
    )

    # error handling participant ID creation
    if created_participant_id["status"] in [402, 404, 422]:
        with open(import_log_file_path, "a") as f:
            f.write(
                f"Creation of participant ID: '{participant_id_raw}' failed: {created_participant_id['detail']}\n"
            )
        return None
    else:
        participant_id = created_participant_id["participant_id"]
        with open(import_log_file_path, "a") as f:
            f.write(f"Created participant ID: '{participant_id}'\n")

    return participant_id


def get_or_create_participant(
    row, matched_participant_id_key, site_id="", session=None
):

    # default parameters
    import_log_file_path = os.environ["IMPORT_LOG_FILE_PATH"]

    # store participant ID in variables
    participant_id = row.iloc[matched_participant_id_key]

    castor_study_id = os.environ["CASTOR_EDC_STUDY_ID"]
    access_token = os.environ["ACCESS_TOKEN"]

    participant_id_call = json.loads(
        perform_api_call(
            f"participant/{participant_id}",
            castor_study_id,
            access_token,
            "GET",
            "",
            session=session,
        )
    )

    if str(participant_id_call["status"]) == "404":
        participant_id_exists = False
    else:
        participant_id_exists = True

    # create new participant ID
    if not participant_id_exists:
        participant_id = create_participant_id(
            participant_id,
            site_id,
            import_log_file_path,
            session,
        )

    return participant_id


# Define a function to replace placeholders with values
def replace_placeholders(row, body, df):

    # Ensure body is a single string
    if not isinstance(body, str):
        body = str(body[0])

    # Search for placeholders in the body text using regular expression
    placeholders = re.findall(r"{(.*?)}", body)

    for placeholder in placeholders:
        placeholder_clean = placeholder.lower().replace(" ", "_")

        # Check if the placeholder exists in the first CSV file
        if placeholder_clean in df.columns:
            value = row[placeholder_clean]
            body = body.replace(f"{{{placeholder}}}", str(value))

    return body


def remove_special_characters(csv_header):
    special_chars = '\\/+,.-";:()[]{}!@$%^&*|?<>ï»¿'
    for i in range(len(csv_header)):

        new_column_name = (csv_header[i].encode("ascii", "ignore")).decode("utf-8")
        new_column_name = re.sub(
            r"[{}]+".format(re.escape(special_chars)), "", new_column_name
        )
        new_column_name = new_column_name.replace(" ", "_")
        if new_column_name == "Participant_Id":
            new_column_name = "Participant_ID"
        csv_header[i] = new_column_name

    return csv_header
