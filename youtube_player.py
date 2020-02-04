#!/usr/bin/python
# -*- coding: UTF-8 -*-

import paho.mqtt.client as mqtt
import os
import time
import sys 
import pyperclip
import requests

youtubeurl_line_token = 'dw8xZ8HE5RK9PqG7g7X1ClBhKELzb0lyFirvM5syijw'
volume_str = 80
os.system("sudo amixer -M set PCM %s > /dev/null &" % volume_str) #預設音量為80%

def lineNotifyMessage(line_token, msg):
      headers = {
          "Authorization": "Bearer " + line_token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}
      r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
      return r.status_code
  
def on_connect(client, userdata, flags, rc):  
    print("Connected with result code " + str(rc))
    if rc == 0:
      if flags["session present"] == 0:
        print("subscribing", 0) 
        client.subscribe("playsong", 0)  
        client.subscribe("volume", 0)
        client.subscribe("pause_play",0)
        #client.subscribe("shutdown", 0)        
                                 
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
    time.sleep(1)
    lineNotifyMessage(youtubeurl_line_token, video_url)         
      
os.system("ps aux | grep mpsyt | awk '{print $2}' | xargs kill -9") 
lineNotifyMessage(youtubeurl_line_token, "youtube播放器已啟動")
client = mqtt.Client()  
client.on_connect = on_connect  
client.on_message = on_message 
client.connect("broker.mqttdashboard.com", 1883) # broker 連線 
client.loop_forever()  
