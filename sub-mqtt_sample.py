#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
import os
import time 
  
def on_connect(client, userdata, flags, rc):  
    print("Connected with result code "+str(rc))
    client.subscribe("genurl", 1)
    
  
def on_message(client, userdata, msg):  
    print(msg.topic + " " + str(msg.payload))       
  
client = mqtt.Client()  
client.on_connect = on_connect  
client.on_message = on_message  
  
client.connect("broker.mqttdashboard.com", 1883) # broker 連線 
client.loop_forever()  
