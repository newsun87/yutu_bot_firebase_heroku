from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import paho.mqtt.client as mqtt

import os
import json
import random
import time

access_token = "6gOhUQlcO8tQkdUfaw369cspUy378X9lMbJV8nuyGYbcRDYNRJy3N9SvRXjkrbxRBtGCga9hSH6CK+pZtJzam5b4GCExt3QWIbV5MZkgcnTTWa8VemIzchGty8Jhkw2SP8gL6Q7mMD8udCaBJ+icmwdB04t89/1O/w1cDnyilFU="
channel_secret = "8b5c6e8e8df7c5859562f60407602970"

app = Flask(__name__)

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)

@app.route("/")
def home():
    return 'home OK'

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
    global nlu_text       
    musicplay(event.message.text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=nlu_text))

def on_connect(client, userdata, flags, rc):  #偵測MQTT連線成功事件
    if rc == 0:
      if flags["session present"] == 0:
        print("subscribing")                
    else:
        print("connection failed ", rc)
  
def on_message(client, userdata, msg): # 偵測MQTT接收訊息事件
    print(sys.getdefaultencoding()) # 打印出目前系統字符編碼    
    mqttmsg = msg.payload.decode("utf-8") #取得MQTT訊息
    print("收到 MQTT訊息", msg.topic+" "+ mqttmsg)

def random_int_list(num):
  list = range(1, num)
  random_list = [*list]
  random.shuffle(random_list)
  return random_list

def genUrl(songkind, songnum):
    print("generate url running ....")
    time.sleep(3)  	 
    os.system("mpsyt '/%s, x %d, q' > /dev/null"  % (songkind, songnum))                              
    f = os.popen("xclip -selection clipboard -o")   
    video_url = f.readlines()[0] 
    text_message = TextSendMessage(text=video_url)
    user_id = 'Ubf2b9f4188d45848fb4697d41c962591'     
    line_bot_api.push_message(user_id, text_message)                                     
    print("產生 youtube url已結束....") 

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
       client.publish("playsong", mqttmsg, 1, True) #發佈訊息
       print("message published")
       genUrl(songkind, songnum)                          
               
    if action == 'playsinger': #播放指定歌手
        nlu_text = temp['data']['nli'][0]['desc_obj']['result']
        print('nlu', nlu_text) 
        singername = temp['data']['nli'][0]['semantic'][0]['slots'][0]['value']       
        randomList = random_int_list(15)[0:1]
        mqttmsg = singername + '~' + str(randomList[0])                                
        print('singername ', singername)                  
        songnum = randomList[0]
        songkind = singername                                
        client.publish("playsong", mqttmsg, 1, True) #發佈訊息
        print("message published")
        genUrl(songkind, songnum)              

    if action == 'playpause': #播放暫停/繼續
        nlu_text = temp['data']['nli'][0]['desc_obj']['result']
        print('nlu', nlu_text)
        mqttmsg ='playpause'
        client.publish("pause_play", mqttmsg, 1, True) #發佈訊息
        print("message published")      

    if action == 'adjust': #調整音量
         volume = temp['data']['nli'][0] ['semantic'][0]['slots'][0]['value']
         nlu_text = temp['data']['nli'][0]['desc_obj']['result']
         print('nlu', nlu_text)
         if volume == '大聲':
             volume_num = volume_num + 10            
             print("volume_num ", volume_num )
             volume_str = str(volume_num )+'%'
             mqttmsg = volume_str            
             client.publish("volume", mqttmsg, 1, True) #發佈訊息                             
         elif volume == '小聲':
              volume_num = volume_num - 10
              volume_str = str(volume_num)+'%'
              mqttmsg = volume_str             
              client.publish("volume", mqttmsg, 1, True) #發佈訊息              
         elif volume == '最小聲':
              volume_num = 50
              volume_str = str(volume_num)+'%'             
              mqttmsg = volume_str             
              client.publish("volume", mqttmsg, 1, True) #發佈訊息   
         elif volume == '最大聲':
              volume_num = 100
              volume_str = str(volume_num)+'%'
              mqttmsg = volume_str               
              client.publish("volume", mqttmsg, 1, True) #發佈訊息           
         elif volume == '適中' or volume == '剛好':
              volume_num = 70
              volume_str = str(volume_num)+'%'
              mqttmsg = volume_str               
              client.publish("volume", mqttmsg, 1, True) #發佈訊息           
    if action == 'shutdown':            
      nlu_text = temp['data']['nli'][0]['desc_obj']['result']
      os.system("sudo shutdown -h now")
      mqttmsg = "shutdown"               
      client.publish("shutdown", mqttmsg, 1, True) #發佈訊息                
      
    else:
      nlu_text = temp['data']['nli'][0]['desc_obj']['result']

    print("播放NLU結果的語音......"+ nlu_text)
client = mqtt.Client()  
client.on_connect = on_connect  
client.on_message = on_message  
client.connect("broker.mqttdashboard.com", 1883)  
client.loop_start()

if __name__ == "__main__":    
    app.run(debug=True, host='127.0.0.1', port=5000)
    
    