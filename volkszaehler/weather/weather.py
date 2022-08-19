#!/usr/bin/python3
from requests import get,post
import configparser

config = configparser.ConfigParser()
config.read('weather.ini')

# try:
lat = config["API"]["lat"]
lon = config["API"]["lon"]
apikey = config["API"]["apikey"]
middlewareurl = config["API"]["middlewareurl"]
#pushserverurl = config.get("API","pushserverurl",fallback="")

url = "https://api.openweathermap.org/data/3.0/onecall?lat=" + lat + "&lon=" + lon + "&exclude=minutely%2Chourly%2Cdaily&units=metric&appid=" + apikey

print(url)
resp = get(url)
data = resp.json()
print(data)
 
#temp = float(data["main"]["temp"])
#pres = float(data["main"]["pressure"])
#humi = float(data["main"]["humidity"])
 
for key in config['channels']:
    posturl = middlewareurl + "/data/" + config['channels'][key] + ".json" 
    print(key + ": " + str(data["current"][key]) + " " + config['channels'][key] + " " + posturl)
    post(posturl, data={"value" : data["current"][key] })

    # if (pushserverurl):
    #     post(pushserverurl, data={})

#post("http://localhost/middleware/data/70919b00-c5f8-11ea-8152-ed29ae9e5e38.json", data={"value" : temp })
#post("http://localhost/middleware/data/<CHANNEL-UUID>.json", data={"value" : pres })
#post("http://localhost/middleware/data/<CHANNEL-UUID>.json", data={"value" : humi })

#{ "data": [ { "uuid": "448ef440-e380-11ec-954a-af2e0666b22c", "tuples": [ [ 1654368477168, 2603507.5 ] ] } ] }