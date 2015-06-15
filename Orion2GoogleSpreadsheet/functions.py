"""
This module is part of Orion2GoogleSpreadsheet project.

Contains utility functions used by Orion2GoogleSpreadsheet
"""

import gdata.spreadsheet.service
from apiclient import errors
from clientcreds import get_client_credentials
import json
import logs
import yaml

################################# IGNORE THE CODE BELOW #################################
#########################################################################################

from normalizer import string_normalizer

# IGNORE. Load TEST json data. TO BE DELETED IN FINAL RELEASE.
# Emulates DefaultHandler.post() catching data function
d = open("json_test_data.txt").read()
data = json.loads(d)

# IGNORE. Listen to Context Broker requests TEST. TO BE DELETED IN FINAL RELEASE

def post_TEST():
    global data
    try:
        # Loop for entities and store data
        entities = []
        for entity_id in data["contextResponses"]:
            # Get entity name (replace '.' and ' ' and lower-case)
            entity_name = string_normalizer(entity_id["contextElement"]["id"])

            # Loop for attributes and their types to append them into a dictionary
            attributes = {}  # Initialization
            for attribute in entity_id['contextElement']['attributes']:
                # Append {attr name:attr value, attr name:attr value...}
                attributes[string_normalizer(str(attribute["name"]))] = str(attribute["value"])
                # Create the data and launch insert_data()
            entity = {'entity_name': entity_name, 'attributes': attributes}
            entities.append(entity)
        return entities

    except:
        print "An exception occurred"


#########################################################################################
################################# IGNORE THE CODE ABOVE #################################


# Check file
def check_file():
    """
    Checks if a spreadsheet used by the app already exists
    in the user's Google Drive account/ Spreadsheets

    :return: True / False
    """
    logs.logger.info("Checking file status")
    if retrieve_spreadsheet_key() == get_spreadsheet_key():
        logs.logger.info("File already exists in user's Drive account. Stored file Key matches Drive's file key")
        return True
    else:
        return False


# Insert new file
def insert_file():
    """
    Inserts a new empty Spreadsheet file in the user's Google Drive account/ Spreadsheets

    :return: None
    """
    drive_service = get_client_credentials('drive')
    body = {'title': 'Orion 2 GSP',
            'mimeType': 'application/vnd.google-apps.spreadsheet'}

    logs.logger.info("Inserting new Spreadsheet file")

    try:
        file = drive_service.files().insert(body=body).execute()
        store_spreadsheet_key(file)
        logs.logger.info("File Created")

    except errors.HttpError, error:
        logs.logger.warn("An error occurred: " + str(error))


# Store Spreadsheet Key
def store_spreadsheet_key(file):
    with open('spreadsheet_key.yaml', 'w') as f:
        yaml.safe_dump(file['id'], f, default_flow_style=False)
    logs.logger.info("Spreadsheet Key stored")


# Get Spreadsheet Key from file
def get_spreadsheet_key():
    """
    Gets the spreadsheet key from yaml file

    :return: Spreadsheet Key string
    """
    if 'spreadsheet_key.yaml':
        logs.logger.info("Checking Spreadsheet Key in yaml file")
        try:
            with open('spreadsheet_key.yaml') as f:
                return yaml.load(f)

        except:
            logs.logger.info("No Key in file")
    else:
        logs.logger.info("No 'spreadsheet_key.yaml' file exists")
        return ""


# Retrieve Spreadsheet Key from Google account
def retrieve_spreadsheet_key():
    """
    Retrieves the spreadsheet key from user's Google account

    :return: Spreadsheet Key string
    """
    logs.logger.info("Retrieving Spreadsheet Key from users account")
    drive_service = get_client_credentials('drive')
    result = []
    try:
        fields = 'items(id)'
        q = "title = 'Orion 2 GSP' and trashed = false"
        files = drive_service.files().list(fields=fields, q=q).execute()
        result.extend(files['items'])
        for item in result:
            return item['id']

    except errors.HttpError, error:
        logs.logger.warn("An error occurred: " + str(error))


# Check Headers
def check_headers():
    """
    Check column headers in the previously created spreadsheet

    return: headers dictionary. Key = Column number (starting from 1):Value = Column name
    """
    logs.logger.info("Checking headers")
    client = get_client_credentials('sheets')
    spreadsheet_key = get_spreadsheet_key()
    worksheet_id = 'od6'  # default
    headers = {}

    try:
        query = gdata.spreadsheet.service.CellQuery()
        query.max_row = '1'
        cells = client.GetCellsFeed(spreadsheet_key, wksht_id=worksheet_id, query=query)
        for i, entry in enumerate(cells.entry):
            headers[i + 1] = entry.cell.text

        return headers

    except:
        logs.logger.warn("An error occurred while checking headers")


# Move columns in Spreadsheet
def move_column(origin, destination):
    """
    Moves the required columns in the Spreadsheet to handle new incoming attributes
    Columns are moved as many spaces right as new attributes coming in

    param origin: origin column number (int)
    param destination: destination column number (int)

    return: None
    """
    logs.logger.info("Adjusting columns")

    from collections import OrderedDict

    client = get_client_credentials('sheets')
    spreadsheet_key = get_spreadsheet_key()
    worksheet_id = 'od6'  # default
    col_values = OrderedDict()  # Ordered Dict

    try:

        try:
            # Origin Column
            logs.logger.info("Generating origin column")
            query_orig = make_cell_query(origin, origin)
            cells_orig = client.GetCellsFeed(spreadsheet_key, wksht_id=worksheet_id, query=query_orig)

            # Request Origin Column
            batch_request_orig = gdata.spreadsheet.SpreadsheetsCellsFeed()

            for i, entry_orig in enumerate(cells_orig.entry):
                col_values[i] = entry_orig.cell.text
                if entry_orig.cell.text != None:  # Avoid inserting new rows at the end due to the initial query
                    entry_orig.cell.inputValue = ''
                    batch_request_orig.AddUpdate(cells_orig.entry[i])

            # Execute origin column request
            client.ExecuteBatch(batch_request_orig, cells_orig.GetBatchLink().href)

        except:
            logs.logger.warn("An error occurred while generating origin column")

        # Handle empty cells before doing destination query
        col_values_clean = {}
        handle_empty_cells(col_values,col_values_clean)

        try:
            # Destination Column
            logs.logger.info("Generating destination column")
            query_dest = make_cell_query(destination, destination, len(col_values_clean))
            cells_dest = client.GetCellsFeed(spreadsheet_key, wksht_id=worksheet_id, query=query_dest)

            # Request Destination Column
            batch_request_dest = gdata.spreadsheet.SpreadsheetsCellsFeed()

            for i, entry_dest in enumerate(cells_dest.entry):
                entry_dest.cell.inputValue = col_values[i]
                batch_request_dest.AddUpdate(cells_dest.entry[col_values.keys().index(i)])

            # Execute destination column request
            client.ExecuteBatch(batch_request_dest, cells_dest.GetBatchLink().href)

        except:
            logs.logger.warn("An error occurred while generating destination column")

    except:
        logs.logger.warn("An error occurred while moving columns")


# Make cells query
def make_cell_query(min_col, max_col, max_row = None):
    logs.logger.info("Making cell query")
    try:
        query = gdata.spreadsheet.service.CellQuery()
        query.return_empty = "true"
        query.min_col = str(min_col)
        query.max_col = str(max_col)
        if max_row:
            query.max_row = str(max_row)
        return query
    except:
        logs.logger.error("Error making cell query")


# Handle empty cells
def handle_empty_cells(col_values, col_values_clean):
    logs.logger.info("Handing empty cells")
    try:
        for i in enumerate(col_values.items()):
            if i[1][1] is not None:
                col_values_clean[i[0]] = i[1][1]

        for x in range(0, max(col_values_clean.keys()) + 1):
            if x not in col_values_clean.iterkeys():
                col_values_clean[x] = '-'

        return col_values_clean

    except:
        logs.logger.warn("An error occurred while handing empty cells in column")