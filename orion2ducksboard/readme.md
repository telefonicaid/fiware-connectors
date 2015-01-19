Description
-----------

orion2ducksboard is Python script to parse NGSI Context Brokers (such as Orion) subscriptions and feed a
Ducksboard widget.

You can get Orion at: https://github.com/telefonicaid/fiware-orion

Ducksboard is a web based dashboard creation tool, you can get an account at:

https://ducksboard.com/

Deployment, configuration and running
-----

orion2ducksboard must be deployed on a server with a public URL.

orion2ducksboard is based on webapp2, please see https://webapp-improved.appspot.com for full details, so you will need to install the following dependences on your server:

```
    $ pip install WebOb
    $ pip install Paste
    $ pip install webapp2
```

Once webapp2 is installed, you must edit the orion2ducksboard configuration file (orion2ducksboard.yaml): 

-   orion2ducksboard_host: your server IP address interface attached to the public IP. 
-   orion2ducksboard_port: your server port. Please remember that must be reacheable from Context Broker.
-   orion2ducksboard_apikey: your private Ducksboard API key.

Finally orion2ducksboard is ready to be started:

```
    $ python orion2ducksboard
```

Usage
-----

### Create a dashboard in DucksBoard

Access to Ducksboard, create a new Dashboard and a new widget on it.

```
   https://app.ducksboard.com/accounts/login/
 
```

Access to the widget preferences and in the "Data & API" section and
note down the Widget ID


### Create a subscription in ContextBroker

Start a Context Broker subscription


```
   POST [http://int.dca.tid.es/NGSI10/subscribeContext][]
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
       "**your_attributes**"
   ],
    "reference": "[http://***your_server***/your_entity/***your_connections***][]",
    "duration": "P1M",
    "notifyConditions": [
          {
               "type": "ONCHANGE",
               "condValues": [
               "**your_attributes**"
           ]
       }
   ],
   "throttling": "PT1S"
 }
```

Please note that orion2ducksboard will know the attributes to parse and
the widgets to push data based on the notification URL, no other provision will be required:
The notification URL has got a specific structure in wich you have to declare your entity and
the links separated by "/".
This links start with an attribute, followed by "&" and a widgetId. Then you have to declare the type
of the widget with "-" and the widgetType. Finally if the widget needs parameters you have to declare it with "$" and
the value.
You can link an attribute to one widget or more cloning the structure, and a widget may need various parameters.

```
   Example:

   http://your_server/your_entity/your_attribute&widgetId-widgetType#value#value&widgetId2-widgetType2/your_attribute2&...
```
Table with types of widgets and its values
```
	Widget Type		Parameters (in order)
------------------------------------------------------------------------------------
	value
	delta
	text
	status
	timeline		title(optional)[urlimage(optional)]
	image			caption(optional)
	gauges			min(mandatory),max(mandatory)
	completion		min(mandatory),max(mandatory)
	map			color(optional)[size(optional)[info(optional)]]

```
### Update the ContextBroker entities

Update your CB entity attribute:

```
   POST [***your_Context_Broker][]
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

If everything went well, you should see the attribute updates on the
widget at:

```
   https://app.ducksboard.com
```


Limitations
-----------

-   Only supports one entity.


