# -*- coding: UTF-8 -*-

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

from flask import render_template
import paho.mqtt.client as mqtt

import os
import json
import random
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import configparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import random

config = configparser.ConfigParser()
config.read('youtu_music.conf')

#取得通行憑證
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://line-bot-test-77a80.firebaseio.com/'
})

#取得 linebot 通行憑證
access_token = config.get('linebot', 'access_token')
channel_secret = config.get('linebot', 'channel_secret')
volume = config.get('setup', 'volume')
mqttmsg = volume +'%'

base_users_userId  = 'smarthome-bot/'
ref = db.reference('/') # 參考路徑 

app = Flask(__name__)

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.route('/')
def showPage():
 return render_template('index.html')

@app.route('/getdata', methods=['GET', 'POST']) 
def getData():
  with open('record.txt','r', encoding = "utf-8") as fileobj:
    word = fileobj.read().strip('\n')
    print(word)  
  return word

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  global userId, nlu_text 
  ref = db.reference('/') # 參考路徑 
  userId = event.source.user_id   
  users_userId_ref = ref.child('youtube_music/'+ userId)  
  # -----雲端音樂 quickreply 的指令操作-------------- 
  if event.message.text.startswith('【youtube url】'):
      new_message = event.message.text.lstrip('【youtube url】')
      ref.child(base_users_userId + userId + '/youtube_music/').update({"videourl":videourl})
      print("歌曲 {videourl} 更新成功...".format(videourl=new_message))
      line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text="馬上播放 " + new_message))
      client.publish("music/youtubeurl", userId+'~'+ new_message, 2, retain=True) #發佈訊息
      time.sleep(1)
      client.publish("music/youtubeurl", '', 2, retain=True) #發佈訊息           
      
  elif event.message.text.startswith('https://youtube.com/watch?') or event.message.text.startswith('https://youtu.be/'):      
      line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text="馬上播放 " + event.message.text))
      ref.child(base_users_userId + userId + '/youtube_music/').update({"videourl":event.message.text})
      print("歌曲 {videourl} 更新成功...".format(videourl=event.message.text))      
      client.publish("music/youtubeurl", userId +'~'+ event.message.text, 2, retain=True) #發佈訊息 
      time.sleep(1)
      client.publish("music/youtubeurl", '', 2, retain=True) #發佈訊息     
      
  elif event.message.text.startswith('https://www.youtube.com/watch?'):      
      line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text="馬上播放 " + event.message.text))
      ref.child(base_users_userId + userId + '/youtube_music/').update({"videourl":event.message.text})
      print("歌曲 {videourl} 更新成功...".format(videourl=event.message.text))          
      client.publish("music/youtubeurl", userId +'~'+ event.message.text, 2, retain=True) #發佈訊息
      time.sleep(1)
      client.publish("music/youtubeurl", '', 2, retain=True) #發佈訊息       
# -----------------------------------------------------------------------
  elif event.message.text == 'menu':
      QuickReply_text_message = TextSendMessage(
       text="點選你想要的功能",
       quick_reply = QuickReply(
        items = [
          QuickReplyButton(
            action = MessageAction(label = "求助", text = "help"),
            image_url = 'https://i.imgur.com/iIZYTVw.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "停止播放", text = "停止播放"),
            image_url = 'https://i.imgur.com/PEHPvG8.png'
          ),
           QuickReplyButton(
            action = MessageAction(label = "音樂播放", text = "music_play"),
            image_url = 'https://i.imgur.com/W1jVNlS.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "音量大聲", text = "音量大聲一點"),
            image_url = 'https://i.imgur.com/jPHUkGZ.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "音量小聲", text = "音量小聲一點"),
            image_url = 'https://i.imgur.com/fmArX5z.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "音量最小聲", text = "音量最小聲"),
            image_url = 'https://i.imgur.com/sC1Xf98.png'
          )
          
        ]
       )
      )
      line_bot_api.reply_message(event.reply_token, QuickReply_text_message) 
  elif event.message.text == 'favor':
      QuickReply_text_message = TextSendMessage(
       text="點選你喜歡的歌手",
       quick_reply = QuickReply(
        items = [
          QuickReplyButton(
            action = MessageAction(label = "張惠妹", text = "我要聽歌手張惠妹的歌"),
            image_url = 'https://i.imgur.com/0yjTHss.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "張信哲", text = "我要聽歌手張信哲的歌"),
            image_url = 'https://i.imgur.com/Q3lUQJa.png'
          ),
           QuickReplyButton(
            action = MessageAction(label = "田馥甄", text = "我要聽歌手田馥甄的歌"),
            image_url = 'https://i.imgur.com/0yjTHss.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "鄧紫棋", text = "我要聽歌手鄧紫棋的歌"),
            image_url = 'https://i.imgur.com/0yjTHss.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "藍又時", text = "我要聽歌手藍又時的歌"),
            image_url = 'https://i.imgur.com/0yjTHss.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "李玖哲", text = "我要聽歌手李玖哲的歌"),
            image_url = 'https://i.imgur.com/Q3lUQJa.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "李玖哲", text = "我要聽歌手李玖哲的歌"),
            image_url = 'https://i.imgur.com/sC1Xf98.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "伍佰", text = "我要聽歌手伍佰的歌"),
            image_url = 'https://i.imgur.com/sC1Xf98.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "陳奕迅", text = "我要聽歌手陳奕迅的歌"),
            image_url = 'https://i.imgur.com/sC1Xf98.png'
          ),
          QuickReplyButton(
            action = MessageAction(label = "郁可唯", text = "我要聽歌手郁可唯的歌"),
            image_url = 'https://i.imgur.com/0yjTHss.png'
          )          
        ]
       )
      )
      line_bot_api.reply_message(event.reply_token, QuickReply_text_message)     
  elif event.message.text == 'help':
      with open('help.txt', mode='r', encoding = "utf-8") as f:
        content = f.read()
        print(content)      
        line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage(text=content))     
  else:             
      musicplay(event.message.text)
      line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=nlu_text))           
            
def random_int_list(num):
  list = range(1, num)
  random_list = [*list]
  random.shuffle(random_list)
  return random_list

def musicplay(text):
  global nlu_text, songnum, songkind, client, genUrl_state, volume_num	
  cmd = './olami-nlu-api-test.sh https://tw.olami.ai/cloudservice/api 8bd057135ec8432bb7bd2b2caa510aca 3fd33f86b57642c08fbea22f8eb9132d %s'     
  output = os.popen(cmd % text) #點歌語意      
  fp = open("output.txt", "w")  
  fp.write(output.read()) # 文字語意理解過程結果寫入檔案      
  fp.close()  
  os.system('cat output.txt | grep nli | grep status > nlu_output.txt') # 文字語意理解結果輸出
  f = open('nlu_output.txt', 'r')
  temp = json.load(f) # json格式讀取文字語意理解結果
  print(temp)    
  f.close()
  type =  temp['data']['nli'][0]['type']        
  status = temp['data']['nli'][0]['desc_obj']['status']      
  print('status', status)
  print('type', type)         
        
  if status == 0 and type == 'smarthome':     
    action = temp['data']['nli'][0] ['semantic'][0]['modifier'][0]
    if action == 'playsong': #播放指定歌曲
       nlu_text = temp['data']['nli'][0]['desc_obj']['result']
       print('nlu', nlu_text) 
       songname = temp['data']['nli'][0] ['semantic'][0]['slots'][0]['value'] 
       randomList = random_int_list(15)[0:1]       
       mqttmsg = songname + '~' + str(randomList[0])           
       print('songname ', songname)       
       songnum = randomList[0]
       songkind = songname
       with open('record.txt','w', encoding = "utf-8") as fileobj:
         word = fileobj.write(songname)                    
       client.publish("music/playsong", userId+'~'+ mqttmsg, 2, retain=True) #發佈訊息
       time.sleep(1)
       client.publish("music/playsong", ' ', 2, retain=True) #發佈訊息 
       #playsong      
       print("message published")
       message = TextSendMessage(text = nlu_text)       
       return message                                                  
               
    if action == 'playsinger': #播放指定歌手
        nlu_text = temp['data']['nli'][0]['desc_obj']['result']
        print('nlu', nlu_text) 
        singername = temp['data']['nli'][0]['semantic'][0]['slots'][0]['value']       
        video_url = yt_search(singername)        
        ref.child(base_users_userId + userId + '/youtube_music/').update({"videourl":video_url})
        print("歌曲 {videourl} 更新成功...".format(videourl=video_url))      
        client.publish("music/youtubeurl", userId +'~'+ video_url, 2, retain=True) #發佈訊息 
        print("message published")
        time.sleep(1)
        client.publish("music/youtubeurl", '', 2, retain=True) #發佈訊息         
        #message = TextSendMessage(text = nlu_text + '\n' + video_url)  
        message = TextSendMessage(text = video_url)       
        return message                             

    if action == 'playpause': #播放暫停/繼續
        nlu_text = temp['data']['nli'][0]['desc_obj']['result']
        print('nlu', nlu_text)
        mqttmsg ='playpause'
        client.publish("music/pause_play", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息              
        print("message published")
        message = TextSendMessage(text = nlu_text)
        return message         

    if action == 'adjust': #調整音量
         #userId = 'Ubf2b9f4188d45848fb4697d41c962591'
         users_userId_ref = ref.child(base_users_userId + userId + '/youtube_music/volume')
         volume_str = users_userId_ref.get()         
         volume = temp['data']['nli'][0] ['semantic'][0]['slots'][0]['value']         
         nlu_text = temp['data']['nli'][0]['desc_obj']['result']
         print('nlu', nlu_text)
         if volume == '大聲':
             print("volume....",volume_str)
             volume_num = int(volume_str) + 10            
             print("volume_num ", volume_num )             
             mqttmsg = str(volume_num )           
             client.publish("music/volume", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息                             
         elif volume == '小聲':
              volume_num = int(volume_str) - 10             
              mqttmsg = str(volume_num )           
              client.publish("music/volume", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息              
         elif volume == '最小聲':
              volume_num = 50                          
              mqttmsg = str(volume_num )           
              client.publish("music/volume", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息   
         elif volume == '最大聲':
              volume_num = 100
              mqttmsg = str(volume_num )               
              client.publish("music/volume", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息           
         elif volume == '適中' or volume == '剛好':
              volume_num = 70              
              mqttmsg = str(volume_num)               
              client.publish("music/volume", userId+'~'+ mqttmsg, 0, retain=False) #發佈訊息
         print('volume....', volume_num)      
         #ref.child(base_users_userId + userId + '/youtube_music').update({
         #      'volume':volume_num}                
         #)         
         message = TextSendMessage(text = nlu_text)
         return message                 
           
    if action == 'shutdown':            
      nlu_text = temp['data']['nli'][0]['desc_obj']['result']      
      mqttmsg = "shutdown"               
      client.publish("shutdown", mqttmsg, 0, retain=False) #發佈訊息                
      
  else:
      nlu_text = temp['data']['nli'][0]['desc_obj']['result']

  print("播放NLU結果的語音......"+ nlu_text)

# Setup YouTube API
KEY = 'AIzaSyCXdlB7xy9F2YJn7sYsNkmA4dE3PvbHVhw'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'  
def yt_search(video_keywords):
    youtube = build('youtube', 'v3', developerKey=KEY)

    # Get YouTube API results
    search_response = youtube.search().list(
        q=video_keywords, # 查詢文字
        type='video',
        part='id,snippet', # 把需要的資訊列出來
        maxResults=10 # 預設為五筆資料，可以設定1~50
    ).execute()
    items = search_response['items']
    #print(items)
    if not items:
      return 'Error: No YouTube results'
    else:
      videos = list(map(video_filter, items))     
      num = random.randint(0,len(videos))
      print(num)
      videoid = videos[num]['影片網址']
      youtube_url = f'{videoid}'
      print(youtube_url)    
      return youtube_url

# Sent an HTML page with the top ten videos
def video_filter(api_video):
  title = api_video['snippet']['title']         
  kind = api_video['id']['kind']
  videoid = api_video['id']['videoId']
  url = f'https://youtu.be/{videoid}'
  thumbnails = api_video['snippet']['thumbnails']['medium']['url']
  return {
            '影片名稱': title,
            '影片種類': kind,
            '影片網址': url,
            '封面照片':thumbnails
  }
  

def on_connect(client, userdata, flags, rc):  
    print("Connected with result code "+str(rc))
    client.subscribe("genurl", 0)    
  
def on_message(client, userdata, msg):      
    print(msg.topic + " " + str(msg.payload))         

client = mqtt.Client()  
client.on_connect = on_connect  
client.on_message = on_message  
client.connect("broker.mqttdashboard.com", 1883) 
client.publish("volume", mqttmsg, 0, retain=False) #發佈訊息 
client.loop_start()

if __name__ == "__main__":           
    app.run(debug=True, host='0.0.0.0', port=5000)    

    
    
