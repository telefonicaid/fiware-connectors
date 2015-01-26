# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
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


file = open("orion2cartodb.yaml")
properties = yaml.load(file)


class DefaultHandler(webapp2.RequestHandler):

    def send2CartoDB(self, url, attribute_name):
        #Adjusting to CartoDB Throtling
        time.sleep(2)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        response = f.read()
        data = json.loads(response)
        updatedRows = int(data["total_rows"])
        f.close()
        d = datetime.datetime.now()
        ref = uuid.uuid4()
        log = str("time=" + str(d.isoformat("T")) + "|lvl=INFO|corr=" + str(ref) + "|trans=" + str(
            ref) + "|ob=ES|comp=ORION_TO_CARTODB|op=MEASURE_SENT_" + attribute_name.upper())
        print(log)
        return updatedRows

    def composeURL(self,tablename, attribute_name, entity_id, value, action):

        if action== "update":

            if attribute_name == "position":
                latitude, longitude = value.split(',')
                attributes_and_values = "latitude="+latitude+"longitude=" + longitude
            else:
                attributes_and_values = attribute_name + "=" + value

            url = properties["cartodb_base_endpoint"] + "/api/v2/sql?q=UPDATE%20" + tablename + "%20SET%20"+ attributes_and_values +"%20WHERE%20name='" + entity_id + "'&api_key=" + properties["cartodb_apikey"]
            return url

        if action=="create":

            if attribute_name == "position":
                latitude, longitude = value.split(',')
                attributes_and_values = "latitude,longitude)%20VALUES%20('" + entity_id + "','" + latitude + "','" + longitude
            else:
                attributes_and_values = attribute_name + ")%20VALUES%20('" + entity_id + "','" + value

            url = properties["cartodb_base_endpoint"] + "/api/v2/sql?q=INSERT%20INTO%20" + tablename + "%20(name,"+attributes_and_values+"')&api_key=" + properties["cartodb_apikey"]
            return url

    def post(self):
        # get url path
        path = self.request.path
        parameters = path.split('/')

        # get entity
        entity_id = parameters[1]

        # get attributes
        attributes = parameters[2]

        # get tablename
        tablename = parameters[3]

        print("Received: entity id " + entity_id + ", attributes: " + attributes + ", table name: " + tablename)

        attributes_names = attributes.split('-')

        for attribute_name in attributes_names:

            value = ""
            data = json.loads(self.request.body)
            for received_entity in data['contextResponses']:
                if received_entity['contextElement']['id'] == entity_id:
                    for received_attribute in received_entity['contextElement']['attributes']:
                        if received_attribute['name'] == attribute_name:
                            value = received_attribute['value']
                            print (value)

            #Composing Update URL
            url = self.composeURL(tablename, attribute_name, entity_id, value,"update")
            #Try to update the asset information at cartodb table
            updatedRows = self.send2CartoDB(url, attribute_name)

            #if update rows is != 0 means that the asset is not created yet so It creates a new asset
            if updatedRows == 0:
                #Composing Creation URL
                url = self.composeURL(tablename, attribute_name, entity_id, value,"create")
                self.send2CartoDB(url, attribute_name)

def main():
    application = webapp2.WSGIApplication([
                                          (r'/.*', DefaultHandler)
                                      ], debug=True)

    httpserver.serve(application, host=properties["orion2cartodb_host"], port=properties["orion2cartodb_port"])


if __name__ == '__main__':
    main()
