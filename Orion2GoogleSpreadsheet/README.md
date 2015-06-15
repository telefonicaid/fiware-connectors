# Orion2GoogleSpreadsheet

Description
-----------

Orion2GoogleSpreadsheet is Python script to parse NGSI Context Brokers (such as Orion) subscriptions and feed a
Google Spreadsheet. The purpose is to offer the possibility to create a Historic Back-up repository for data coming out Context Broker and automatically store it in a Google Spreadsheet under the user's property.

You can get Orion at: https://github.com/telefonicaid/fiware-orion

Google Spreadsheets is Google cloud-based solution for spreadsheets.

You can create an account at: https://www.google.com/intl/es/sheets/about/

Deployment, configuration and running
-------------------------------------

Orion2GoogleSpreadsheet must be deployed on a server reachable by the Context Broker.

Orion2GoogleSpreadsheet is based on webapp2, please see https://webapp-improved.appspot.com for full details, so you will need to install the following dependences on your server:

```
    $ pip install WebOb
    $ pip install Paste
    $ pip install webapp2
```

Once webapp2 is installed, you must edit the Orion2GoogleSpreadsheet configuration file (credentials.yaml): 

-   orion2gsp_host: your server IP address interface attached IP reachable by the Context Broker.
-   orion2gsp_port: your server port. Please remember that must be reachable from Context Broker.

Finally Orion2GoogleSpreadsheet is ready to be started:

```
    $ python Orion2GoogleSpreadsheet
```


Usage
-----


### Create a subscription in ContextBroker

Please, consider using FIGWAY script UpdateEntityAttribute.py to update it, you find it at:

https://github.com/telefonicaid/fiware-figway/tree/master/python/ContextBroker

Anyway, you can create it on your own as follows:


       POST [[HOST]/v1/subscribeContext][]
       Accept: application/json
       Fiware-Service: **your_service**
       Content-Type: application/json
     
       {
       entities": [
           {
               "type": "device", 
               "isPattern": "false", 
               "id": "**your_entity**"
           }
       ],
       "attributes": [
           "**attribute1**",
           "**attribute2**"
       ],
        "reference": "[your_machine_service]"
        "duration": "P1M",
        "notifyConditions": [
              {
                   "type": "ONCHANGE",
                   "condValues": [
                   "**attribute1**",
                   "**attribute2**"
               ]
           }
       ],
       "throttling": "PT1S"
     }
     
    
Based on the subscription, a table will be generated introducing the attributes and their values as column name and value (for each of the assets) respectively. When a new attribute is added within the subscription, a new column will be appended to the table, and the previous values for the new attribute will be considered null in the previous assets.



### Update the ContextBroker entities

Please, consider using FIGWAY script SetSubscription.py to create it, you find it at:

https://github.com/telefonicaid/fiware-figway/tree/master/python/ContextBroker

Anyway, you can update it on your own as follows:


       POST [[HOST]/v1/updateContext][]
       Accept: application/json
       Fiware-Service: **your_service**
       Content-Type: application/json
     
       {
           "contextElements": [ 
       {
           "type": "**your_type**", 
           "isPattern": "false", 
           "id": "**your_entity**", 
           "attributes": [
              {
                   "name":  "**your_attribute**", 
                   "type":  "**your_id**", 
                   "value": "**your_value**"
               }] }
           ],
           "updateAction": "APPEND" }



### See the results

If everything went well, you should see the attribute updates at the "Orion 2 GSP" GoogleSpreadsheet in your Google Drive account.


Limitations
-----------

-	Your spreadsheet will be named "Orion 2 GSP". Please, do not change manually your spreadsheet name, otherwise another table under the former name could be generated and it will lead to potential loose of data.
-	Avoid changing 1st column cells content. 1st cells in each column contain the headers against which Orion2GoogleSpreadsheet does attribute content matching when feeding the spreadsheet. Changes will cause loose of data.  
-	Avoid changing columns order in the spreadsheet.

Feedback
--------

Please report bugs and suggest features via [GitHub Issues](https://github.com/dfl1/Orion2GoogleSpreadsheet/issues).



