# This file is part of IoT Partner Integration kit software (a set of tools for FIWARE Orion ContextBroker and IDAS2.6).
#
# IoT Partner Integration kit is free software: you can redistribute it and/or modify it under the terms of the GNU
# Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# IoT Partner Integration kit is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with IoT Partner Integration kit.
# If not, see http://www.gnu.org/licenses/
#
# For those usages not covered by the GNU Affero General Public License please contact with iot_support@tid.es
#
# Developed by @IndustrialIoT Team (mail:iot_support@tid.es)

__author__ = 'Daniel Fernandez Lazaro'

import webapp2
from paste import httpserver
import json
import logs
import time
import gdata.spreadsheet.service
import gdata.service
from functions import (post_TEST, get_spreadsheet_key, check_headers, move_column,
                       insert_file, check_file)
from clientcreds import (get_properties, get_client_credentials)
from normalizer import string_normalizer


logs.config_log()


### CLASSES ###

class DefaultHandler(webapp2.RequestHandler):
    """Listen and Catch Context Broker data"""

    # Listen to Context Broker requests
    def post(self):
        """
        Listens to and Catches incoming Context Broker requests.
        Transforms incoming data and stores it to be processed later

        return: entities List of Entity dict objects.
                Each entity contains: Entity Name: Entity name // Attributes: attributes dict
        """
        global data
        try:
            data = json.loads(self.request.body)

        except:
            logs.logger.error("Malformed JSON")
            self.response.status_int = 403
            self.response.write("Malformed JSON")

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
            self.insert_data(entities)
            return entities

        except:
            logs.logger.error("An exception occurred")
            self.response.status_int = 403
            self.response.write("An exception occurred")

    # Insert data in file
    def insert_data(self, entities):
        """
        Inserts data coming from Context Broker into the Spreadsheet previously created

        return:None
        """
        client = get_client_credentials('sheets')
        spreadsheet_key = get_spreadsheet_key()
        worksheet_id = 'od6'  # default

        ### CONTEXT BROKER DATA  ###
        attributes = []
        headers = {}  # Attributes dict
        rows = []  # Data
        try:
            logs.logger.info("Extracting entities")

            for entity in entities:
                # Extract headers for columns in spreadsheet
                for attrib in entity['attributes']:
                    attributes.append(str(attrib))

                # Append rows to insert
                row = {'id': str(entity['entity_name']), 'date': time.strftime('%m/%d/%Y'), 'time': time.strftime('%H:%M:%S')}
                for key, value in entity['attributes'].iteritems():
                    row[str(key)] = "' " + str(value) # ' to avoid formatting errors when inserting data into spreadsheet's columns
                rows.append(row)
                logs.logger.info("Row: " + str(row))

            logs.logger.info("Formatting headers")

            # Format headers
            attributes = dict.fromkeys(attributes).keys()
            attributes.insert(0, 'id')
            attributes.append('date')
            attributes.append('time')
            for i, attrib in enumerate (attributes):
                headers[i+1] = attrib

            # Check headers in file
            current_headers = check_headers()

            # If No headers in file
            if not current_headers:
                logs.logger.info("Inserting headers")
                for i, header in enumerate(headers.values()):
                    entry = client.UpdateCell(row=1, col=i + 1, inputValue=header, key=spreadsheet_key, wksht_id=worksheet_id)
                    if not isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
                        logs.logger.warn("Header insert failed: '{0}'".format(entry))
            else:
                logs.logger.info("Adjusting headers")
                # If New Headers differ from Existing Headers
                if headers != current_headers:
                    # Detect missing headers
                    missing_headers = set(headers.values()) - set(current_headers.values())
                    # Columns to move
                    col_to_move = []
                    # Detect column number for each missing header
                    for h in missing_headers:
                        h = [key for key, value in headers.iteritems() if value == h][0]
                        col_to_move.append(h)
                    col_to_move.sort()

                    if len(col_to_move) == 1:
                        for i in range(col_to_move[0]+1, max(current_headers.keys())+1):
                            col_to_move.append(i)
                        # Higher value (last value) first --> next value...
                        for col in reversed(col_to_move):
                            move_column(col,col+1)
                    else:
                        #Compare col_to_move vs current_headers
                        matching_col = [item for item in current_headers if item in col_to_move]
                        for col in reversed(matching_col):
                            move_column(col,col+len(col_to_move))

                    # Insert headers in file
                    for i, header in enumerate(headers.values()):
                        entry = client.UpdateCell(row=1, col=i + 1, inputValue=header, key=spreadsheet_key, wksht_id=worksheet_id)
                        if not isinstance(entry, gdata.spreadsheet.SpreadsheetsCell):
                            logs.logger.warn("Header insert failed: '{0}'".format(entry))

            # Insert rows in file
            logs.logger.info("Inserting rows")
            for row in rows:
                try: ###-Consider batch request-TO DO###
                    entry = client.InsertRow(row, spreadsheet_key, worksheet_id)
                    if not isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
                        logs.logger.warn("Row insert failed: '{0}'".format(entry))

                except Exception as e:
                    logs.logger.error("An error occurred: " + str(e))

            #logs.logger.info(str(len(rows)) + " rows inserted")

        except Exception as e:
            logs.logger.error("An error occurred while inserting data: " + str(e))


### MAIN ###

# User account Auth for Google Drive + Spreadsheet creation
if check_file() == False:
    insert_file()

# Insert Incoming Data in Google Spreadsheet
handler = DefaultHandler()
handler.insert_data(post_TEST())

# def main():
#     properties = get_properties()
#     application = webapp2.WSGIApplication([(r'/.*', DefaultHandler)], debug=True)
#     httpserver.serve(application, host=properties['orion2gsp_host'], port=properties['orion2gsp_port'])
#
# if __name__ == '__main__':
#     main()
