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

import webapp2
import json
import urllib2
import yaml
from paste import httpserver
import uuid
import datetime
import unicodedata
import string


#EPSG is the identifier of WGS84
EPSG = "4326"
Non_encode_symbols = "&:/=(),'?!"


# Print Logs
def print_log(message,lvl):
    d = datetime.datetime.now()
    ref=uuid.uuid4()
    log=str("time="+str(d.isoformat("T"))+"|lvl="+lvl+"|corr="+str(ref)+"|trans="+str(ref)+"|ob=ES|comp=ORION_TO_CARTODB|op="+message)
    print(log)


#Normalize strings
def string_normalizer(message):
    try:
        # Convert to unicode format
        message = message.decode()

        # Lower-case
        message=message.lower()

        # Replace some characters
        message=message.replace('.','_')
        message=message.replace(' ','_')

        # Get NFKD unicode format
        message=unicodedata.normalize('NFKD', message)

        # Delete not ascii_letters
        message=''.join(x for x in message if x in string.ascii_letters or x=="_" or x.isdigit())
    except:
        print_log("An error occurred while trying to normalize string","WARNING")
        return ""

    # Return normalized string
    return message


# Load properties
print_log("Loading properties from orion2cartodb.yaml","INFO")
file = open("orion2cartodb.yaml")
properties = yaml.load(file)
print_log("Loaded","INFO")

# Class for communications
class DefaultHandler(webapp2.RequestHandler):

    #Send Info to CartoDB
    def send_cartodb(self, url):
        try:
            print_log("Sending '"+str(url)+"' to CartoDB...","INFO")

            # Initializations
            error=False
            total_rows=0

            # Send data
            url= urllib2.quote(url,Non_encode_symbols)
            req = urllib2.Request(url)
            f = urllib2.urlopen(req)

            # Get response
            response=f.read()
            resp=json.loads(str(response))

            print_log("Response: '"+str(resp)+ "'","INFO")

            # If there is an error -> Error Control
            if "error" in resp:
                error=True

            # Get rows updated
            if "total_rows" in resp:
                total_rows=int(resp["total_rows"])
            f.close()

            print_log("Sent to CartoDB","INFO")

        # If it is not possible to send the data -> Error Control
        except:
            print_log("An error occurred while trying to send info to CartoDB","WARNING")
            error=True

        # Return number of ROWs updated and if there was an error
        return error, total_rows


    # Update ROW
    def update(self,tablename, entity_name, attributes):
        try:
            print_log("Updating attributes '" + str(attributes)+"'","INFO")

            # Get Attributes and concatenate them
            attributes_values=""
            for key in attributes.keys():

                # If it is not a position attribute concatenate it
                if key!="position":
                    attributes_values=attributes_values+str(key)+"= '"+str(attributes[key])+"',"

                # If it is a position attribute split and concatenate it
                else:
                    position=str(attributes[key]).split(',')
                    latitude=position[0]
                    longitude=position[1]
                    attributes_values=attributes_values+"the_geom=ST_SetSRID(ST_Point("+str(longitude)+","+str(latitude)+"),"+EPSG+")"+","

            # URL for updating attributes
            url=str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q="+"UPDATE " + tablename + " SET "+ attributes_values[:-1] +" WHERE name='" + entity_name + "' &api_key=" + properties["cartodb_apikey"]

            # Update attributes
            error, total_rows=self.send_cartodb(url)

            if error==False:
                print_log("Updated","INFO")
            else:
                print_log("Attributes could not be updated","WARNING")

        except:
            print_log("An error occurred while trying to Update","WARNING")
            error=True

        # Return if it was possible to update and the number of ROWs updated
        return error,total_rows


    # Create new table and/or new ROW and/or new attributes
    def create_table_and_attributes(self, name, entity_name, attributes, types):
        try:
            print_log("Creating table '" + str(name)+"' ...","INFO")

            #Initialization
            error=False
            cont=0
            attributes2create="name varchar,"     #String with new attributes and their types
            keys="name,"                            #String with new attributes
            values="'"+entity_name+"',"             #String with the values

            # Loop for attributes
            for key in types.keys():

                # If attribute type is not position (Position is automatically created)
                if key!="position":

                    # Concatenate attribute names
                    keys=keys+str(key)+","

                    # If attribute type is Quantity indicate it to CartoDB
                    if types[key]=="Quantity":

                        # Concatenate attribute and its type
                        attributes2create=attributes2create+str(key)+" float,"

                        # Concatenate value
                        values=values+attributes[key]+","

                    # If attribute type is Boolean indicate it to CartoDB
                    elif types[key]=="Boolean":

                        # Concatenate attribute and its type
                        attributes2create=attributes2create+str(key)+" boolean,"

                        # Concatenate value
                        values=values+attributes[key]+","

                    # If attribute type is not Quantity or Boolean, It is string
                    else:

                        # Concatenate attribute and its type
                        attributes2create=attributes2create+str(key)+" varchar,"

                        # Concatenate value
                        values=values+"'"+attributes[key]+"'"+","

            # URL to create table
            url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=CREATE TABLE "+name+"("+attributes2create[:-1]+")"+" &api_key=" + properties["cartodb_apikey"]

            # Create table
            error,total_rows=self.send_cartodb(url)

            # If table is created
            if error==False:
                print_log("Displaying table '" + str(name)+"'","INFO")

                # URL to display it in the interface
                url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=SELECT cdb_cartodbfytable('"+name+"')"+"&api_key="+properties["cartodb_apikey"]

                # Send it to CartoDB
                error,total_rows=self.send_cartodb(url)

                if error==True:
                    print_log("Table '" + str(name)+ "' could not be displayed","WARNING")
                    return error
                else:
                    print_log("Table '" + str(name)+ "' displayed","INFO")

            else:
                print_log("Table '" + str(name)+"' could not be created","WARNING")

            print_log("Creating ROW " + str(entity_name)+" ...","INFO")

            # URL to create a new ROW
            url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=INSERT INTO " + name + " ("+keys[:-1]+") VALUES("+values[:-1]+") &api_key=" + properties["cartodb_apikey"]

            # Create new ROW
            error,total_rows=self.send_cartodb(url)

            if error==False:
                print_log("Created ROW '" + str(entity_name)+"'","INFO")

            # If it's not possible to create table and/or ROW -> Table and ROW are created but there are new attributes
            else:
                print_log("ROW '" + str(entity_name)+"' could not be created","WARNING")

                # Create new attributes in CartoDB
                try:
                    print_log("Creating attributes '"+str(attributes)+"'","INFO")

                    # Loop for attributes
                    for key in attributes.keys():

                        # Strings with attribute name + attribute type
                        attribute2create=""

                        # If attribute type is not position (Position has not to be manually created)
                        if key!="position":

                            # If attribute type is Quantity  indicate it
                            if types[key]=="Quantity":
                                attribute2create=str(key)+" float"

                            # If attribute type is Boolean  indicate it
                            elif types[key]=="Boolean":
                                attribute2create=str(key)+" boolean"

                            # If attribute is not Quantity or Boolean it is string
                            else:
                                attribute2create=str(key)+" varchar"

                        # URL to create new attribute
                        url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=ALTER TABLE IF EXISTS "+name+" ADD "+attribute2create+" &api_key=" + properties["cartodb_apikey"]

                        # Create new attribute
                        error,total_rows=self.send_cartodb(url)

                        # If attribute has been created count it
                        if error==False:
                            print_log("Created attribute '"+str(key)+"'","INFO")
                            cont=cont+1
                        else:
                            print_log("Attribute "+str(key)+"' could not be created","WARNING")

                except:
                    print_log("An error occurred while trying to create attributes","WARNING")
                    error=True

        except:
            print_log("An error occurred while trying to create table","WARNING")
            error=True

        # Return if it was possible to create table, ROW or attributes
        return error,cont

    def post(self):

        # Initialization
        rows_updated=0
        try:
            #Get JSON Data
            data = json.loads(self.request.body)
        except:
            print_log("Malformed JSON","ERROR")
            self.response.status_int = 403
            self.response.write("Malformed JSON")
            return

        try:
            #Get Fiware-Service header = Table name
            tablename=string_normalizer(str(self.request.headers.get('Fiware-Service')))

            # Control table name
            if tablename=='none':

                print_log("Wrong table name. Fiware-Service request header was expected","ERROR")
                self.response.status_int = 403
                self.response.write("Wrong table name. Fiware-Service request header was expected")
                return

            #Loop for entities
            for entity_id in data["contextResponses"]:

                # Get entity name (replace '.' and ' ' and lower-case)
                entity_name=string_normalizer(entity_id["contextElement"]["id"])

                # Loop for attributes and their types to append them into a dictionary
                attributes={}       #Initialization
                types={}            #Initialization
                for attritube_id in entity_id['contextElement']['attributes']:

                    # Append
                    attributes[str(attritube_id["name"])]=str(attritube_id["value"])
                    types[str(attritube_id["name"])]=string_normalizer(str(attritube_id["type"]))

                # Try to update the attributes
                error,total_rows=self.update(tablename,entity_name,attributes)
                rows_updated=rows_updated+total_rows

                # If there is an error -> Table is not created or ROW is not created or there are new attributes
                if error==True or total_rows==0:

                    # Create table and/or ROW and/or attributes
                    error,total_rows=self.create_table_and_attributes(tablename, entity_name,attributes,types)

                    if error==False:
                        print_log("Created "+str(total_rows)+" rows in table "+tablename,"INFO")

                    # Try to Update attributes again
                    error,total_rows=self.update(tablename,entity_name,attributes)
                    rows_updated=rows_updated+total_rows

            print_log("Updated "+str(rows_updated)+" rows","INFO")
            self.response.status_int = 200
            self.response.write("Updated "+str(rows_updated)+" rows")

        except:
            print_log("An exception occurred","ERROR")
            self.response.status_int = 403
            self.response.write("An exception occurred")



def main():
    application = webapp2.WSGIApplication([
                                          (r'/.*', DefaultHandler)
                                      ], debug=True)

    httpserver.serve(application, host=properties["orion2cartodb_host"], port=properties["orion2cartodb_port"])


if __name__ == '__main__':
    main()
