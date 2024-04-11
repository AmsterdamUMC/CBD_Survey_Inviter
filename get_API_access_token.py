# basic API call authentication
# needs the following packages:
# - requests: pip install requests (using: requests 2.28.1)

import os
import re
import time
import json  # needed to convert API call to JSON
import requests as req
from tkinter import messagebox
from log_handling import handle_error


def get_access_token(client_id, client_secret):

    try:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        token_url = "https://data.castoredc.com/oauth/token"
        response = req.post(token_url, data)
        json_response = json.loads(response.text)
        access_granted = False
        if response.status_code == 200:
            access_token = json_response["access_token"]
            os.environ["ACCESS_TOKEN"] = str(access_token)
            access_granted = True

            # store first access time to check for validity of token (5 hours)
            if "FIRST_ACCESS_TIME" not in os.environ:
                time_now = str(time.time())
                os.environ["FIRST_ACCESS_TIME"] = time_now
        else:
            access_token = "Invalid Credentials"

        return access_token, access_granted

    except Exception as e:
        handle_error(e)


# Verification of API credentials from first GUI window:
def verify_api_credentials(client_id, client_secret, root_window=None):
    try:

        from GUI_module import initialize_file_explorer

        is_sanitized = False
        pattern_to_match = r"^[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}$"

        if len(client_secret) == 32 and re.match(pattern_to_match, client_id):
            is_sanitized = True

        if client_id and client_secret and is_sanitized:
            access_token, access_granted = get_access_token(client_id, client_secret)
            if access_granted:
                os.environ["ACCESS_TOKEN"] = str(access_token)
                initialize_file_explorer(root_window, client_id, client_secret)
            else:
                messagebox.showerror(title="Error", message=access_token)
        else:
            messagebox.showwarning(
                title="Warning", message="API credentials are incorrect"
            )

    except Exception as err:
        handle_error(err)


def check_access_token_expiry(access_token):
    time_now = str(time.time())
    elapsed_time = float(time_now) - float(os.environ["TIME_INIT_ACCESS"])

    if elapsed_time >= 15000:
        client_id = os.environ["CLIENT_ID"]
        client_secret = os.environ["CLIENT_SECRET"]

        # get new access token
        access_token = get_access_token(client_id, client_secret)

        # store global
        time_now = str(time.time())
        os.environ["TIME_INIT_ACCESS"] = time_now

    return access_token
