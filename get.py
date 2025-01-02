#!/usr/bin/env python3
"""
pip3 install garth requests readchar

export EMAIL=<your garmin email>
export PASSWORD=<your garmin password>

"""
import datetime
#from datetime import timezone
import json
import logging
import os
from getpass import getpass

import requests
from garth.exc import GarthHTTPError

from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

def get_credentials():
    """Get user credentials."""

    email = input("Login e-mail: ")
    password = getpass("Enter password: ")

    return email, password
    
def init_api(email, password):
    """Initialize Garmin API with your credentials."""

    try:
        # Using Oauth1 and OAuth2 token files from directory
        print(
            f"Trying to login to Garmin Connect using token data from directory '{tokenstore}'...\n"
        )

        # Using Oauth1 and Oauth2 tokens from base64 encoded string
        # print(
        #     f"Trying to login to Garmin Connect using token data from file '{tokenstore_base64}'...\n"
        # )
        # dir_path = os.path.expanduser(tokenstore_base64)
        # with open(dir_path, "r") as token_file:
        #     tokenstore = token_file.read()

        garmin = Garmin()
        garmin.login(tokenstore)

    except (FileNotFoundError, GarthHTTPError, GarminConnectAuthenticationError):
        # Session is expired. You'll need to log in again
        print(
            "Login tokens not present, login with your Garmin Connect credentials to generate them.\n"
            f"They will be stored in '{tokenstore}' for future use.\n"
        )
        try:
            # Ask for credentials if not set as environment variables
            if not email or not password:
                email, password = get_credentials()

            garmin = Garmin(
                email=email, password=password, is_cn=False, prompt_mfa=get_mfa
            )
            garmin.login()
            # Save Oauth1 and Oauth2 token files to directory for next login
            garmin.garth.dump(tokenstore)
            print(
                f"Oauth tokens stored in '{tokenstore}' directory for future use. (first method)\n"
            )
            # Encode Oauth1 and Oauth2 tokens to base64 string and safe to file for next login (alternative way)
            token_base64 = garmin.garth.dumps()
            dir_path = os.path.expanduser(tokenstore_base64)
            with open(dir_path, "w") as token_file:
                token_file.write(token_base64)
            print(
                f"Oauth tokens encoded as base64 string and saved to '{dir_path}' file for future use. (second method)\n"
            )
        except (
            FileNotFoundError,
            GarthHTTPError,
            GarminConnectAuthenticationError,
            requests.exceptions.HTTPError,
        ) as err:
            logger.error(err)
            return None

    return garmin

def get_mfa():
    """Get MFA."""

    return input("MFA one-time code: ")
# Configure debug logging
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables if defined
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
tokenstore_base64 = os.getenv("GARMINTOKENS_BASE64") or "~/.garminconnect_base64"
api = None

# Let's say we want to scrape all activities using switch menu_option "p". We change the values of the below variables, IE startdate days, limit,...
today = datetime.date.today()
startdate = today - datetime.timedelta(days=7)  # Select past week
start = 0
limit = 100
start_badge = 1  # Badge related calls calls start counting at 1
activitytype = "cycling"  # Possible values are: cycling, running, swimming, multi_sport, fitness_equipment, hiking, walking, other
activityfile = "MY_ACTIVITY.fit"  # Supported file types are: .fit .gpx .tcx
weight = 89.6
weightunit = "kg"

api = init_api(email, password)
activities = api.get_activities_by_date(startdate.isoformat(), today.isoformat(), activitytype)
#print(activities)


for activity in activities:
    print(activity["activityType"])
    print(activity["activityName"])
    activity_id = activity["activityId"]
    activity_name = activity["activityName"]
    activity_name = activity_name.replace("/", "-")
    activity_name = activity_name.replace(" ", "_")
    activity_start_time = activity["startTimeLocal"]
    zip_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
    output_file = f"./{str(activity_name)}_{str(activity_start_time)}_{str(activity_id)}.zip"
    with open(output_file, "wb") as fb:
        fb.write(zip_data)
        print(f"Activity data downloaded to file {output_file}")
