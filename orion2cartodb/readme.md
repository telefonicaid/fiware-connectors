Description
-----------

orion2cartodb is Python script to parse NGSI Context Brokers (such as Orion) subscriptions and feed a
CartoDB Map.

You can get Orion at: https://github.com/telefonicaid/fiware-orion

CartoDB is an open source cloud-based solution for showing maps on a website.

You can create an account at: http://cartodb.com/

Deployment, configuration and running
-----

orion2ducksboard must be deployed on a server reacheable by the Context Broker.

orion2ducksboard is based on webapp2, please see https://webapp-improved.appspot.com for full details, so you will need to install the following dependences on your server:

```
    $ pip install WebOb
    $ pip install Paste
    $ pip install webapp2
```

Once webapp2 is installed, you must edit the orion2ducksboard configuration file (orion2ducksboard.yaml): 

-   orion2cartodb_host: your server IP address interface attached IP reacheable by the Context Broker.
-   orion2cartodb_port: your server port. Please remember that must be reacheable from Context Broker.
-   orion2cartodb_apikey: your private CartoDB API key.

Finally orion2ducksboard is ready to be started:

```
    $ python orion2cartodb
```


Usage
-----

### Create a table in CartoDB

Access to CartoDB and create a new table 

```
   https://iotsupport.cartodb.com/login
```

Add colums to the new table with *the same name* of the entity attributes that you would like to shown on the map.


### Create a subscription in ContextBroker

Please, consider using FIGWAY script UpdateEntityAttribute.py.py to update it, you find it at:

https://github.com/telefonicaid/fiware-figway/tree/master/python/ContextBroker

Anyway, you can create it on your own as follows:

```
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
    "reference": "[http://orion2cartodb.appspot.com/notify/your_entity/attribute1-atributte2-...../your_cartodb_table]
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
```


Please note that orion2cartoDB will know the attribute to parse and
the widget to push data based on the notification URL, no other
provision will be required:

```
  http://orion2cartodb.appspot.com/notify/your_entity/your_attribute/your_cartodb_table
```

### Update the ContextBroker entities

Please, consider using FIGWAY script SetSubscription.py to create it, you find it at:

https://github.com/telefonicaid/fiware-figway/tree/master/python/ContextBroker

Anyway, you can update it on your own as follows:

```
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
```

### See the results

If everything went well, you should see the attribute updates at the CartoDB data table.


Limitations
-----------

-   Only supports one CartoDB account that is hardcoded on the code.

-   Location atributtes must be divided in two columns, latitude and longitude, 
    that should be configurated by the creator at the data table


