Description
==================

Set of Python scripts for integrating visualization tools with NSGI Context Brokers such as Orion.

You can get Orion at: https://github.com/telefonicaid/fiware-orion

These scripts connect Orion Context Broker with different dashboarding tools to simplify creating a visualization layer for your Orion Context Broker based application.

On this repository you can find the following scripts:

* **[orion2cartodb](/orion2cartodb)**: parse Orion Context Broker subscription notifications and feed a CartoDb Map.  Use this if you have many entities with a location that you want to show on a map.
* **[orion2ducksboard](/orion2ducksboard)**: parse Orion Context Broker subscription notifications and feed a Ducksboard dashboard. Use this if you have a limited set of entities and want to show widgets with their historic evolution.

Please, take into account that you will be required to host these scripts into a server reacheable by the Orion Context Broker your are using.

