#!/usr/bin/python3
from requests import get,post
import configparser

config = configparser.ConfigParser()
config.read('cputemp.ini')

middlewareurl = config["API"]["middlewareurl"]

cputemp = -1
with open('/sys/class/thermal/thermal_zone0/subsystem/thermal_zone0/temp') as f:
    cputemp = int(next(f))/1000

posturl = middlewareurl + "/data/" + config['API']["channel"] + ".json" 
print(str(cputemp) + " " + config['API']["channel"] + " " + posturl)
post(posturl, data={"value" : cputemp })