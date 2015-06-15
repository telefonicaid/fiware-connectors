"""
This module is part of Orion2GoogleSpreadsheet project.

Contains functionality used by Orion2GoogleSpreadsheet to Obtain credentials
and Authenticate clients for communication with Google Data API.
"""

import yaml
import logs
import httplib2
import gdata.spreadsheet.service
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client import tools


# Load Credentials and Properties #
def get_properties():
    logs.logger.info("Loading properties")
    try:
        file = open("credentials.yaml")
        properties = yaml.load(file)
        logs.logger.info("Properties loaded")
        return properties
    except:
        logs.logger.error("Error loading properties")


# Clients Auth and Credentials
def get_client_credentials(client):
    """
    Makes Google Oauth flow and store credentials in file.
    Creates an authenticated Drive client/ Spreadsheets client
    depending on the client param introduced.

    param client: "drive" for Drive client / "sheets" for Spreadsheets client
    type client: string

    return: Authenticated Drive/Spreadsheet client Object
    """
    try:
        logs.logger.info("Creating storage for credentials")
        storage = Storage("creds.dat")
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            logs.logger.info("Obtaining credentials")
            flags = tools.argparser.parse_args(args=[])
            properties = get_properties()
            flow = OAuth2WebServerFlow(properties['CLIENT_ID'], properties['CLIENT_SECRET'],
                                       properties['OAUTH_SCOPE'], properties['REDIRECT_URI'])
            credentials = tools.run_flow(flow, storage, flags)

        if credentials.access_token_expired:
            credentials.refresh(httplib2.Http())

        if client == "drive":
            try:
                logs.logger.info("Creating Drive client")
                http = credentials.authorize(httplib2.Http())
                dr_client = build('drive', 'v2', http=http)
                return dr_client
            except:
                logs.logger.warn("An error occurred while creating Drive client")

        elif client == "sheets":
            try:
                logs.logger.info("Creating Spreadsheets client")
                sp_client = gdata.spreadsheet.service.SpreadsheetsService(
                additional_headers={'Authorization': 'Bearer %s' % credentials.access_token})
                return sp_client
            except:
                logs.logger.warn("An error occurred while creating Spreadsheets client")
    except:
        logs.logger.warn("An error occurred while obtaining credentials")