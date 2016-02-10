(function () {
	var CBDatasource = function(settings, updateCallback)
	{
		var self = this;
		var updateTimer = null;
		var currentSettings = settings;

		function updateRefresh(refreshTime)
		{
			if(updateTimer)
			{
				clearInterval(updateTimer);
			}

			updateTimer = setInterval(function()
			{
				self.updateNow();
			}, refreshTime);
		}

		updateRefresh(currentSettings.refresh * 1000);

		this.updateNow = function()
		{
		    url = currentSettings.cbhost+"/NGSI10/queryContext";
		
		    if(currentSettings.use_https) {
		        url = "https://"+url;
		    } else {
		        url = "http://"+url;
		    }
			
			if(currentSettings.use_thingproxy) {
				url =  "https://thingproxy.freeboard.io/fetch/" + url;
			}	
			$.ajax({
				url       : url,
				dataType  : "JSON",
				type: "POST",
				data: '{"entities":[{"type": "'+currentSettings.type+'","isPattern": false, "id" :"'+currentSettings.id+'"}]}',
				beforeSend: function(xhr)
				{
					xhr.setRequestHeader("Content-Type", "application/json");
					xhr.setRequestHeader("Accept", "application/json");
					xhr.setRequestHeader("Fiware-Service", currentSettings.service);
					xhr.setRequestHeader("Fiware-ServicePath", currentSettings.servicepath);
					xhr.setRequestHeader("X-Auth-Token", currentSettings.xauthtoken);
				},
				success   : function(data)
				{
					//Initialize mydata 
					mydata={};
					
					//if advanced setting is true do not modify received JSON 
					if(currentSettings.advanced){
						mydata=data;
					}
					
					//if advanced setting is false reduce received JSON nesting
					else{
						
						//Get attributes 
						attributes=data["contextResponses"][0]["contextElement"]["attributes"];
						
						//Get each attribute and append it to mydata
						for (i = 0; i < attributes.length; i++) {
							
							//If attribute selected is position split it in latitude and longitude
							if(attributes[i]["name"]=="position"){
								
								//Get position attribute
								position=attributes[i]["value"];
								
								//Split position
								pos_split=position.split(",");
								
								//Append latitude and longitude
								mydata["latitude"]=pos_split[0];
								mydata["longitude"]=pos_split[1];
							}
							else{
								
								// If attribute is not a number
								if(isNaN(attributes[i]["value"])){
									
									// If attribute is a boolean and false append 0
									if(attributes[i]["value"]=="false"){
										mydata[attributes[i]["name"]]=0;
									}
									
									// If attribute is a boolean and true append 1
									else if(attributes[i]["value"]=="true"){
										mydata[attributes[i]["name"]]=1;
									}
									
									// If attribute is not a boolean or a position or a number append it
									else{
										mydata[attributes[i]["name"]]=attributes[i]["value"];
									}
								}
								
								//If attribute is a number round and append it
								else{
									mydata[attributes[i]["name"]]=((parseFloat(attributes[i]["value"])).toFixed(1)).toString();
								}
							}
						}
					}
					updateCallback(mydata);
				},
				error     : function(xhr, status, error)
				{
				}
			});
		}

		this.onDispose = function()
		{
			clearInterval(updateTimer);
			updateTimer = null;
		}

		this.onSettingsChanged = function(newSettings)
		{
			currentSettings = newSettings;
			updateRefresh(currentSettings.refresh * 1000);
		}
	};

	freeboard.loadDatasourcePlugin({
		type_name  : "FIWARE Orion",
		settings   : [
			{
				name: "use_https",
				display_name: "HTTPS",
				type: "boolean",
				default_value: false
			},
			{
				name        : "cbhost",
				display_name: "Host:port",
				type        : "text"
			},
			{
				name: "use_thingproxy",
				display_name: "Thingproxy",
				description: 'A CORS Proxy (JSONP connection) will be used',
				type: "boolean",
				default_value: true
			},
			{
				name        : "service",
				display_name: "Fiware-Service",
				type        : "text"
			},
			{
				name        : "servicepath",
				display_name: "Fiware-ServicePath",
				type        : "text"
			},
			{
				name        : "xauthtoken",
				display_name: "X-Auth-Token",
				type        : "text"
			},
			{
				name        : "type",
				display_name: "Type",
				type        : "text"
			},			
			{
				name        : "id",
				display_name: "Id",
				type        : "text"
			},
			{
				name        : "advanced",
				display_name: "Advanced",
				description: 'Advanced mode permits access to all JSON request',
				type        : "boolean"
			},			
			{
				name         : "refresh",
				display_name : "Refresh Every",
				type         : "number",
				suffix       : "seconds",
				default_value: 5
			}
		],
		newInstance: function(settings, newInstanceCallback, updateCallback)
		{
			newInstanceCallback( new CBDatasource(settings, updateCallback));
		}
	});
}());
