Description
-----------
Orion_DataSource is a javascript plugin to feed a Freeboard dashboard with NSGI Context Brokers such as Orion.

You can get Orion at: https://github.com/telefonicaid/fiware-orion

Freeboard is a "Ridiculously simple dashboards for your devices", you can get an account at: 

http://freeboard.io/

This plugin is based on the plugin sample from Freeboard availabe at:

https://github.com/Freeboard/plugins


Install
-----

### Get Freeboard

Get Freeboard code at: 

https://github.com/Freeboard/freeboard

Deploy it on your server or host it directly on your computer.


### Install the plugin

Copy Orion_DataSource.js to freeboard plugins folder:

	***your_freeboard_folder***/plugins/thirdparty


Configuration
-----

### Load javascript at your html freeboard
Edit your freeboard index.html and add the next line before the "Load more plugins here ***" comment:

	"plugins/thirdparty/Orion_DataSource.js",


The result should be something like this:
	<script type="text/javascript">

		head.js("js/freeboard+plugins.min.js",
			"plugins/thirdparty/Orion_Datasource.js",
			// *** Load more plugins here ***
Usage
-----
### Add new datasource
Load on the browser your freeboard index.html and click to add new datasource.

Choose "Orion Data Source" and give it a name.

###Configure Orion Data Source
You will have to indicate the next information:
* **Host**: the Host (IP:PORT) of your Orion service.
* **ThingProxy**: a CORS proxy needed if your Orion server does not have CORS enabled.
* **Fiware-Service**: your fiware-service name.
* **Type**: your entity type.
* **ID**: your entity ID.
* **Advanced**: (only advanced users) You can tick it if you know how is the NGSI JSON document and you want to access to extra information.
* **Refresh every**: It's the polling time.

![General ](https://raw.githubusercontent.com/telefonicaid/fiware-dataviz/develop/FreeBoard-Orion-Plugin/img/Orion_DataSource.png "Orion_DataSource settings example")
