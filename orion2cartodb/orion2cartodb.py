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
import time


#print Logs
def print_log(message,lvl):
    d = datetime.datetime.now()
    ref=uuid.uuid4()
    log=str("time="+str(d.isoformat("T"))+"|lvl="+lvl+"|corr="+str(ref)+"|trans="+str(ref)+"|ob=ES|comp=ORION_TO_CARTODB|op="+message)
    print(log)


# Load properties
print_log("Loading properties from orion2cartodb.yaml","INFO")
file = open("orion2cartodb.yaml")
properties = yaml.load(file)
print_log("Loaded","INFO")

# Class for communications
class DefaultHandler(webapp2.RequestHandler):

    #Send Info to CartoDB
    def send2CartoDB(self, url):
        print_log("Sending '"+str(url)+"' to CartoDB...","INFO")

        # Initializations
        error=False
        total_rows=0

        try:
            # Send data
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
    def Update(self,tablename, entity_name, attributes):

        print_log("Updating attributes '" + str(attributes)+"'","INFO")

        # Get Attributes and concatenate them
        attributes_values=""
        for key in attributes.keys():

            # If it is not a position attribute concatenate it
            if key!="position":
                attributes_values=attributes_values+str(key)+"=%20'"+str(attributes[key])+"',"

            # If it is a position attribute split and concatenate it
            else:
                position=str(attributes[key]).split(',')
                latitude=position[0]
                longitude=position[1]
                attributes_values=attributes_values+"the_geom=ST_SetSRID(ST_Point("+str(longitude)+","+str(latitude)+"),4326)"+","

        # URL for updating attributes
        url=str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q="+"UPDATE%20" + tablename + "%20SET%20"+ attributes_values[:-1] +"%20WHERE%20name='" + entity_name + "'%20&api_key=" + properties["cartodb_apikey"]

        # Update attributes
        error, total_rows=self.send2CartoDB(url)

        if error==False:
            print_log("Updated","INFO")
        else:
            print_log("Attributes could not be updated","WARNING")

        # Return if it was possible to update and the number of ROWs updated
        return error,total_rows


    # Create new table and/or new ROW
    def create_table(self, name, entity_name,attributes, types):

        print_log("Creating table '" + str(name)+"' ...","INFO")

        #Initialization
        error=False
        attributes2create="name%20varchar,"     #String with new attributes and their types
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
                    attributes2create=attributes2create+str(key)+"%20float,"

                    # Concatenate value
                    values=values+attributes[key]+","

                # If attribute type is Boolean indicate it to CartoDB
                elif types[key]=="Boolean":

                    # Concatenate attribute and its type
                    attributes2create=attributes2create+str(key)+"%20boolean,"

                    # Concatenate value
                    values=values+attributes[key]+","

                # If attribute type is not Quantity or Boolean, It is string
                else:

                    # Concatenate attribute and its type
                    attributes2create=attributes2create+str(key)+"%20varchar,"

                    # Concatenate value
                    values=values+"'"+attributes[key]+"'"+","

        # URL to create table
        url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=CREATE%20TABLE%20"+name+"("+attributes2create[:-1]+")"+"%20&api_key=" + properties["cartodb_apikey"]

        # Create table
        error,total_rows=self.send2CartoDB(url)

        # If table is created
        if error==False:

            print_log("Displaying table '" + str(name)+"'","INFO")
            # URL to display it in the interface
            url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=SELECT%20cdb_cartodbfytable('"+name+"')"+"&api_key="+properties["cartodb_apikey"]

            # Send it to CartoDB
            error,total_rows=self.send2CartoDB(url)

            if error==True:
                print_log("Table '" + str(name)+ "' could not be displayed","WARNING")
            else:
                print_log("Table '" + str(name)+ "' displayed","INFO")

        else:
            print_log("Table '" + str(name)+"' could not be created","WARNING")

        print_log("Creating ROW " + str(entity_name)+" ...","INFO")

        # URL to create a new ROW
        url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=INSERT%20INTO%20" + name + "%20("+keys[:-1]+")%20VALUES("+values[:-1]+")%20&api_key=" + properties["cartodb_apikey"]

        # Create new ROW
        error,total_rows=self.send2CartoDB(url)

        if error==False:
            print_log("Created ROW '" + str(entity_name)+"'","INFO")
        else:
            print_log("ROW '" + str(entity_name)+"' could not be created","WARNING")

        # Return if it was possible to create table or ROW
        return error


    # Create new attributes in CartoDB
    def create_attributes(self, tablename, entity_name, attributes, types):
        print_log("Creating attributes '"+str(attributes)+"'","INFO")

        # Initializations
        error=False
        cont=0

        # Loop for attributes
        for key in attributes.keys():

            # Strings with attribute name + attribute type
            attribute2create=""

            # If attribute type is not position (Position has not to be manually created)
            if key!="position":

                # If attribute type is Quantity  indicate it
                if types[key]=="Quantity":
                    attribute2create=str(key)+"%20float"

                # If attribute type is Boolean  indicate it
                elif types[key]=="Boolean":
                    attribute2create=str(key)+"%20boolean"

                # If attribute is not Quantity or Boolean it is string
                else:
                    attribute2create=str(key)+"%20varchar"

            # URL to create new attribute
            url = str(properties["cartodb_base_endpoint"]) + "/api/v2/sql?q=ALTER%20TABLE%20IF%20EXISTS%20"+tablename+"%20ADD%20"+attribute2create+"%20&api_key=" + properties["cartodb_apikey"]

            # Create new attribute
            error,total_rows=self.send2CartoDB(url)

            # If attribute has been created count it
            if error==False:
                print_log("Created attribute '"+str(key)+"'","INFO")
                cont=cont+1
            else:
                print_log("Attribute "+str(key)+"' could not be created","WARNING")

         # Return number of attributes created
        return cont




    def post(self):
        # Get URL path
        path = self.request.path

        #Get JSON Data
        data = json.loads(self.request.body)

        #Get Fiware-Service header = Table name
        tablename=str(self.request.headers.get('Fiware-Service')).lower()

        #Loop for entities
        for entity_id in data["contextResponses"]:

            # Get entity name (replace '.' and ' ' and lower-case)
            entity_name=(((str(entity_id["contextElement"]["id"])).replace('.','_')).replace(' ', '_')).lower()

            # Loop for attributes and their types to append them into a dictionary
            attributes={}       #Initialization
            types={}            #Initialization
            for attritube_id in entity_id['contextElement']['attributes']:

                # Append
                attributes[str(attritube_id["name"])]=str(attritube_id["value"])
                types[str(attritube_id["name"])]=str(attritube_id["type"])

            # Try to update the attributes
            error,total_rows=self.Update(tablename,entity_name,attributes)

            # If there is an error -> Table is not created or ROW is not created or there are new attributes
            if error==True or total_rows==0:

                # Create table and/or ROW
                error=self.create_table(tablename, entity_name,attributes,types)

                # If it's not possible to create table and/or ROW -> Table and ROW are created but there are new attributes
                if error==True:

                    # Create new attributes in CartoDB
                    total_rows=self.create_attributes(tablename, entity_name, attributes, types)


                    print_log("Created "+str(total_rows)+" rows","INFO")

                # Try to Update attributes again
                error,total_rows=self.Update(tablename,entity_name,attributes)

                print_log("Updated "+str(total_rows)+" rows","INFO")
            else:
                print_log("Updated "+str(total_rows)+" rows","INFO")




def main():
    application = webapp2.WSGIApplication([
                                          (r'/.*', DefaultHandler)
                                      ], debug=True)

    httpserver.serve(application, host=properties["orion2cartodb_host"], port=properties["orion2cartodb_port"])


if __name__ == '__main__':
    main()
