#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
import os
import time
import sys 
import pyperclip
  
def on_connect(client, userdata, flags, rc):  
    print("Connected with result code " + str(rc))
    if rc == 0:
      if flags["session present"] == 0:
        print("subscribing") 
        client.subscribe("playsong")  
        client.subscribe("volume")
        client.subscribe("pause_play")
        client.subscribe("shutdown")        
                                 
    else:
        print("connection failed ", rc)    
   
  
def on_message(client, userdata, msg):
    global music_source    
    print(sys.getdefaultencoding()) # 打印出目前系統字符編碼    
    mqttmsg = msg.payload.decode("utf-8") #取得MQTT訊息
    print("收到 MQTT訊息", msg.topic+" "+ mqttmsg)
    
    if msg.topic == 'playsong':
      os.system("ps aux | grep mpsyt | awk '{print $2}' | xargs kill -9") 		      
      songkind = msg.payload.decode("utf-8").split("~", 1)[0] #取得目前播歌的資訊 
      songnum = int(msg.payload.decode("utf-8").split("~", 1)[1]) #取得目前播歌的資訊
      print("songkind...", songkind)
      print("songnum....", songnum)           
      playmusic(songkind, songnum)
      genurl(songkind, songnum)   
        
    elif msg.topic == 'volume':
      volume_str = msg.payload.decode("utf-8")
      print("volume....", volume_str)      		
      os.system("sudo amixer -M set PCM %s > /dev/null &" % volume_str) #預設音量為80%
    elif msg.topic == 'pause_play': 
      os.system("ps aux | grep mpsyt | awk '{print $2}' | xargs kill -9")
    elif msg.topic == 'shutdown': 
      os.system("shutdown -h now")	      		     		                   
           
def playmusic(songkind, songnum):
    global genUrl_state          
    os.system("mpsyt '/%s, %d, q' > /dev/null&" % (songkind, songnum)) 

def genurl(songkind, songnum):
    print("generate url running ....")
    time.sleep(3)
    os.system("mpsyt '/%s, x %d, q' > /dev/null"  % (songkind, songnum))       
    video_url = pyperclip.paste()                                        
    print("youtube URL..", video_url)
    mqttmsg = video_url
    client.publish("genurl", mqttmsg, 0, True) #發佈訊息     
      
client = mqtt.Client()  
client.on_connect = on_connect  
client.on_message = on_message 
client.connect("broker.mqttdashboard.com", 1883) # broker 連線 
client.loop_forever()  
