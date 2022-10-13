import pyaudio
 
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()
VOWELS = ('a', 'e', 'i', 'o', 'u',)
 
# starts recording
stream = p.open(
   format=FORMAT,
   channels=CHANNELS,
   rate=RATE,
   input=True,
   frames_per_buffer=FRAMES_PER_BUFFER
)

import websockets
import asyncio
import base64
import json
import re
# from configure import auth_key
 
# the AssemblyAI endpoint we're going to hit
URL = "wss://api.assemblyai.com/v2/realtime/ws?sample_rate=16000"
auth_key = ""
async def send_receive():
   print(f'Connecting websocket to url ${URL}')
   async with websockets.connect(
       URL,
       extra_headers=(("Authorization", auth_key),),
       ping_interval=5,
       ping_timeout=20
   ) as _ws:
       await asyncio.sleep(0.1)
       print("Receiving SessionBegins ...")
       session_begins = await _ws.recv()
       print(session_begins)
       print("Sending messages ...")
       async def send():
           while True:
               try:
                   data = stream.read(FRAMES_PER_BUFFER)
                   data = base64.b64encode(data).decode("utf-8")
                   json_data = json.dumps({"audio_data":str(data)})
                   await _ws.send(json_data)
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
               await asyncio.sleep(0.01)
          
           return True
      
       async def receive():
           while True:
               try:
                   result_str = await _ws.recv()
                   # if(json.loads(result_str)['text'])
                   text = json.loads(result_str)['text']
                   if(len(text) > 0): 
                     print(text.split(" "))
                     new_text = ' '.join([w+"-v" if re.sub(r'[^\w\s]','',w.lower())[-1] in VOWELS else w+"-c" for w in text.split(" ")])
                     print(new_text)
                   else:
                     print(text)
               except websockets.exceptions.ConnectionClosedError as e:
                   print(e)
                   assert e.code == 4008
                   break
               except Exception as e:
                   assert False, "Not a websocket 4008 error"
      
       send_result, receive_result = await asyncio.gather(send(), receive())

asyncio.run(send_receive())