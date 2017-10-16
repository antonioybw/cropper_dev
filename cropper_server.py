from flask import Flask,render_template
from flask import request
import json
import os
import time
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
import subprocess
import time

app = Flask(__name__)
socketio = SocketIO(app)


detect_img_path='/Users/Antonio/workspace/cropper_dev/static/images'

def find_img_list():
  img_list=[]
  for file in os.listdir(detect_img_path):
    if file.endswith('.png') or file.endswith('.jpg'):
      img_list.append(file)
  print "process dir here"
  print img_list
  return img_list


@app.route('/', methods = ['GET','POST']) # 
def crop():
  if not os.path.exists(detect_img_path):
    return "img path not exists"
  # subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/*",shell=True)
  img_list=find_img_list()
  return render_template('index.html',img_list=img_list)

@socketio.on('crop_data_submit')
def save_crop_data(message):
    print message


if __name__ == '__main__':
    socketio.run(app,threaded=True)