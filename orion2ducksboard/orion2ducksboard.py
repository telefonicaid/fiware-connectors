# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of IoT Partner Integration kit  software (a set of tools for FIWARE Orion ContextBroker and IDAS2.6).
#
# IoT Partner Integration kit  is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# IoT Partner Integration kit  is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with FIGWARE.
# If not, see http://www.gnu.org/licenses/
#
# For those usages not covered by the GNU Affero General Public License please contact with iot_support@tid.es 
# 
# Developed by @IndustrialIoT Team (iot_support@tid.es) 

import webapp2
import json
import urllib2
import yaml
import base64
import datetime
import uuid
from paste import httpserver

#Class for errors
class MiError(Exception):
    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        if self.valor==100:
            return "POST: Error " + str(self.valor)+" Malformed path"
        elif self.valor==101:
            return "POST: Error " + str(self.valor)+" Not found entity"
        elif self.valor==102:
            return "POST: Error " + str(self.valor)+" Not found attributes"
        elif self.valor==103:
            return "POST: Error " + str(self.valor)+" Not found widgets_ids"
        elif self.valor==104:
            return "POST: Error " + str(self.valor)+" Not found types"
        elif self.valor==105:
            return "POST: Error " + str(self.valor)+" Size vector error"
        elif self.valor==106:
            return "POST: Error " + str(self.valor)+" Invalid Api Key"
        elif self.valor==107:
            return "POST: Error " + str(self.valor)+" Data could not be sent"
        elif self.valor==108:
            return "CONFIGURATION: Error " + str(self.valor)+" Invalid HOST"


#print Logs
def print_log(message,lvl):
    d = datetime.datetime.now()
    ref=uuid.uuid4()
    log=str("time="+str(d.isoformat("T"))+"|lvl="+lvl+"|corr="+str(ref)+"|trans="+str(ref)+"|ob=ES|comp=ORION_TO_DUCKSBOARD|op="+message)
    print(log)

class DefaultHandler(webapp2.RequestHandler):

    #get API_KEY in MD5 format
    def get_api_key(self):
        try:
            api_key=0
            file=open("orion2ducksboard.yaml")

            #check ir file exists
            if file.closed:
                print_log("GET_API_KEY: File does not exist","WARNING")
                return 1

            #Load content file
            file_content=yaml.load(file)

            #Geet Api Key
            api_key=base64.encodestring('%s:%s' % (file_content["orion2ducksboard_apikey"], "unused"))[:-1]
        except:
            return 1,api_key

        #return Api_key
        return 0,api_key

    #Parse input data
    def parse(self, path):
        try:
            #Split path in parameters
            parameters = path.split('/')

            # get entity
            entity_id = parameters[1]

            #Initialization
            attributes_names = []
            widgets_ids = []
            types = []
            values = []

            #Check parameters size
            if len(parameters)<=2:
                print_log("parameters length<=2","WARNING")
                return 1, entity_id, attributes_names, widgets_ids, types, values
            # get each link of attributes with widgets
            for param in range(2, len(parameters)):

                # get all attributes
                params = parameters[param].split('&')
                attributes_names.append(params[0])

                # get each widget with its parameters
                widgets_attrib = []
                types_attrib = []
                values_attrib = []

                #Check params size
                if len(params)<=1:
                    print_log("params length<=1","WARNING")
                    return 1, entity_id, attributes_names, widgets_ids, types, values

                for widg_param in range(1, len(params)):
                    widg = params[widg_param].split('-')

                    #get each widget
                    widgets_attrib.append(widg[0])
                    type_values = widg[1].split('$')

                    #get each type
                    types_attrib.append(type_values[0])

                    #get values
                    values_attrib_widg = []

                    for value in range(1, len(type_values)):
                        values_attrib_widg.append(type_values[value])
                    values_attrib.append(values_attrib_widg)

                #get all widgets
                widgets_ids.append(widgets_attrib)

                #get all types
                types.append(types_attrib)

                #get all values
                values.append(values_attrib)
        except:
            return 1, entity_id, attributes_names, widgets_ids, types, values

        #return values
        return 0, entity_id, attributes_names, widgets_ids, types, values

    #Generate data to send
    def create_data(self, type, values, data, timestamp):
        try:
            #initialize ducksboard_data
            ducksboard_data =""

            # type value
            if type == "value":
                ducksboard_data = {"value": data,"timestamp": timestamp}

            # type delta
            elif type == "delta":
                ducksboard_data = {"delta": data,"timestamp": timestamp}

            # type text
            elif type == "text":
                ducksboard_data = {"value": {"content": data},"timestamp":timestamp}

            # type status
            elif type == "status":
                if data == "true":
                    ducksboard_data = {"value": 0,"timestamp":timestamp}
                elif data == "false":
                    ducksboard_data = {"value": 3,"timestamp":timestamp}
                else:
                    print_log("CREATE_DATA: Status not defined","WARNING")
                    return 1, ducksboard_data

            # type timeline #Values=title,image
            elif type == "timeline":
                if len(values) == 2:
                    ducksboard_data = {"value": {
                        "title": values[0],
                        "image": values[1],
                        "content": data},"timestamp":timestamp}
                elif len(values) == 1:
                    ducksboard_data = {"value": {
                        "title": values[0],
                        "image": "",
                        "content": data},"timestamp":timestamp}
                elif len(values) == 0:
                    ducksboard_data = {"value": {
                        "title": "",
                        "image": "",
                        "content": data},"timestamp":timestamp}
                else:
                    print_log("CREATE_DATA: Too values in timeline","WARNING")
                    return 1, ducksboard_data

            # type image #Values=caption
            elif type == "image":
                if len(values) == 1:
                    ducksboard_data = {"value": {
                        "source": data,
                        "caption": values[0]},"timestamp":timestamp}
                elif len(values) == 0:
                    ducksboard_data = {"value": {
                        "source": data,
                        "caption": ""},"timestamp":timestamp}
                else:
                    print_log("CREATE_DATA: Too values in image","WARNING")
                    return 1, ducksboard_data

            # type gauges #Values=min,max
            elif type == "gauges":
                if len(values) != 2:
                    print_log("CREATE_DATA: Parameter error in gauges type","WARNING")
                    return 1, ducksboard_data
                else:
                    min = float(values[0])
                    max = float(values[1])
                    val = ((float(data)) - min) / (max - min)
                    ducksboard_data = {"value": val,"timestamp":timestamp}

            # type completion #Values=min,max
            elif type == "completion":
                if len(values) == 2:
                    print_log("CREATE_DATA: Parameter error in completion type","WARNING")
                    return 1, ducksboard_data
                else:
                    ducksboard_data = {"value": {
                        "current": data,
                        "min": values[0],
                        "max": values[1]},"timestamp":timestamp}

            # type map #Values=color,size,info
            elif type == "map":
                latitude, longitude = data.split(',')
                if len(values) == 3:
                    ducksboard_data = {"value": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "color": '#'+values[0],
                        "size": values[1],
                        "info": values[2]},"timestamp":timestamp}

                elif len(values) == 2:
                    ducksboard_data = {"value": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "color": '#'+values[0],
                        "size": values[1]},"timestamp":timestamp}

                elif len(values) == 1:
                    ducksboard_data = {"value": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "color": '#'+values[0]},"timestamp":timestamp}

                elif len(values) == 0:
                    ducksboard_data = {"value": {
                        "latitude": latitude,
                        "longitude": longitude},"timestamp":timestamp}
                else:
                    print_log("CREATE_DATA: Too values in map","WARNING")
                    return 1, ducksboard_data
            else:
                print_log("CREATE_DATA: Wrong widget type","WARNING")
                return 1, ducksboard_data

        except:
            return 1, ducksboard_data

        #return data
        return 0, ducksboard_data

    # Transform date to timestamp
    def get_timestamp(self,date):
        try:
            epoch=datetime.datetime(1970,1,1)
            dt = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            td = dt - epoch
            timestamp=(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6
        except:
            return 1,0
        return 0, str(timestamp).split('.')[0]

    #Send to Ducksboard
    def send2Ducksboard(self,ducksboard_data, wideget_id, headers):

        #Send request
        print_log("SENDING TO DUCKSBOARD: "+"WidgetID:"+str(wideget_id)+" Data:"+str(ducksboard_data),"DEBUG")

        try:
            opener = urllib2.build_opener
            data_post = json.dumps(ducksboard_data)
            url = 'https://push.ducksboard.com/v/' + wideget_id
            req = urllib2.Request(url, data_post, headers)
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
            message="SENT TO DUCKSBOARD: "+"WidgetID:"+str(wideget_id)+" Data:"+str(ducksboard_data)
            print_log(message,"DEBUG")
        except:
            return 1
        return 0

    #Send request
    def send(self, api_key, entity_id, attributes_names, widgets_ids, types, values):
        try:
            # headers
            headers = {"Authorization": "Basic " + api_key}

            # Get JSON
            data = json.loads(self.request.body)

            # Look for the entity
            for received_entity in data['contextResponses']:
                if received_entity['contextElement']['id'] == entity_id:

                    # Loop of attributes
                    for attribute_pos in range(0, len(attributes_names)):
                        for received_attribute in received_entity['contextElement']['attributes']:
                            if received_attribute['name'] == attributes_names[attribute_pos]:

                                # Get value
                                value = str(received_attribute['value'])

                                # Get time and parse to timestamp
                                timestamp=""
                                for metadata in received_attribute['metadatas']:
                                    if metadata['name']=="TimeInstant":
                                        time=metadata['value']
                                        status_error,timestamp=self.get_timestamp(time)
                                        if status_error==1:
                                            print_log("SEND: Error in get_timestamp","WARNING")
                                            return 1

                                # Loop for widgets
                                for widget_pos in range(0, len(widgets_ids[attribute_pos])):
                                    status_error,ducksboard_data=self.create_data(types[attribute_pos][widget_pos], values[attribute_pos][widget_pos], value, timestamp)
                                    if status_error==1:
                                        print_log("SEND: Error in create_data","WARNING")
                                        return 1

                                    #Send request
                                    wideget_id=widgets_ids[attribute_pos][widget_pos]
                                    status_error=self.send2Ducksboard(ducksboard_data,wideget_id,headers)
                                    if status_error==1:
                                        print_log("SEND: Error in send2ducksboard","WARNING")
                                        return 1

        except:
            return 1
        return 0

    # Get request and send the information to ducksboard
    def post(self):
        # Initialize status_error
        status_error = 0

        #Print path received
        message="PATH RECEIVED: "+self.request.path
        print_log(message,"DEBUG")

        try:
            # get url path
            path = self.request.path

            # Parse urls
            status_error, entity_id, attributes_names, widgets_ids, types, values = self.parse(path)

            #If error in parse
            if status_error == 1:
                self.response.status_int = 403
                self.response.write("Malformed path")
                raise MiError(100)

            # Error control of needed information
            elif entity_id == "":
                self.response.status_int = 403
                self.response.write("Not found entity")
                raise MiError(101)

            elif len(attributes_names) == 0 or attributes_names[0]== "":
                self.response.status_int = 403
                self.response.write("Not found attributes")
                raise MiError(102)

            elif len(widgets_ids) == 0:
                self.response.status_int = 403
                self.response.write("Not found widgets_ids")
                raise MiError(103)

            elif len(types) == 0:
                self.response.status_int = 403
                self.response.write("Not found types")
                raise MiError(104)

            elif (len(attributes_names)!=len(widgets_ids)) or (len(attributes_names)!=len(types)) or (len(widgets_ids)!=len(types)):
                self.response.status_int = 403
                self.response.write("Size vector error")
                raise MiError(105)


        except MiError, e:
            print_log(str(e),"ERROR")

        else:
            try:
                #get API_KEY
                status_error, api_key = self.get_api_key()

                if status_error == 1:
                    self.response.status_int = 403
                    self.response.write("Invalid Api Key")
                    raise MiError(106)

            except MiError, e:
                print_log(str(e),"ERROR")

            else:
                try:
                    #Send data
                    status_error = self.send(api_key, entity_id, attributes_names, widgets_ids, types, values)

                    if status_error == 1:
                        self.response.status_int = 403
                        self.response.write("Data could not be sent")
                        raise MiError(107)

                except MiError, e:
                    print_log(str(e),"ERROR")

                else:
                    #reply
                    if status_error==0:
                        self.response.write("OK")
                        print_log("POST: OK","INFO")
                    else:
                        self.response.write("Error")
                        print_log("POST: Error","ERROR")


#Get ip and port from configuration file
def get_Ip_Port():
    try:
        file=open("orion2ducksboard.yaml")
        if file.closed:
            print_log("GET_IP_PORT: File orion2ducksboard.yaml does not exists","WARNING")
            return 1
        file_content=yaml.load(file)
        ip=file_content["orion2ducksboard_host"]
        port=file_content["orion2ducksboard_port"]
    except:
        return 1

    #return IP and PORT
    return 0,ip,port

#main
def main():
    application = webapp2.WSGIApplication([(r'/.*', DefaultHandler)], debug=True)
    status_error,IP,PORT=get_Ip_Port()
    if status_error==0:
        httpserver.serve(application, host=IP, port=PORT)
    else:
        raise MiError(108)
        print_log(str(e),"ERROR")

if __name__ == '__main__':
    main()

