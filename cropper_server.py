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
# 
app = Flask(__name__)
socketio = SocketIO(app)



global save_list_name
save_list_name='img_crop_data.txt'

subprocess.call("mkdir /root/host_workspace/cropper_dev/crop_data",shell=True)
subprocess.call("chmod 777 /root/host_workspace/cropper_dev/crop_data",shell=True)
subprocess.call("mkdir /root/host_workspace/cropper_dev/process_idx",shell=True)
subprocess.call("chmod 777 /root/host_workspace/cropper_dev/process_idx",shell=True)

detect_img_path='/root/host_workspace/cropper_dev/static/images'

detect_data_path='/root/host_workspace/cropper_dev/crop_data/'

def find_img_list():
  img_list=[]
  for file in os.listdir(detect_img_path):
    if file.endswith('.png') or file.endswith('.jpg'):
      img_list.append(file)
  print "img list here"
  print img_list
  return img_list

def find_data_list():
  data_list=[]
  for file in os.listdir(detect_data_path):
    if file.endswith('.txt'):
      data_list.append(file)
  print "crop data list here"
  print data_list
  return data_list


@app.route('/', methods = ['GET','POST']) # 
def crop():
  if not os.path.exists(detect_img_path):
    return "img path not exists"

  open('/root/host_workspace/cropper_dev/crop_data/'+save_list_name,'w+').close()
  os.chmod('/root/host_workspace/cropper_dev/crop_data/'+save_list_name, 0o777)
  img_list=find_img_list()
  return render_template('index.html',img_list=img_list)

@socketio.on('crop_data_submit')
def save_crop_data(message):
    print message
    with open('/root/host_workspace/cropper_dev/crop_data/'+save_list_name,'a+') as cropfile:
      cropfile.write(json.dumps(message)+'\n')
    process_name=save_list_name[:save_list_name.find('.txt')]
    with open('/root/host_workspace/cropper_dev/process_idx/'+process_name+'_last_idx.txt','w+') as idxfile:
      idxfile.write(str(message['last_idx']))
    emit('success_save', 'crop data saved to server')

@socketio.on('new_process')
def create_new_process(message):
  print "receive process new"
  print message
  print message['new_process_name']
  data_list_array=find_data_list()
  process_file_name=message['new_process_name']+'.txt'
  if(process_file_name in data_list_array):
    emit('new_process_fail', 'process name already exists')
    return
  global save_list_name
  save_list_name=process_file_name
  open('/root/host_workspace/cropper_dev/crop_data/'+save_list_name,'a+').close()
  open('/root/host_workspace/cropper_dev/process_idx/'+message['new_process_name']+'_last_idx.txt','w+').close()
  os.chmod('/root/host_workspace/cropper_dev/crop_data/'+save_list_name, 0o777)
  emit('new_process_success', {'process_file_name':process_file_name})

@socketio.on('continue_process')
def continue_process(message):
  print "receive continue process"
  print message
  print message['continue_process_name']
  data_list_array=find_data_list()
  process_file_name=message['continue_process_name']+'.txt'
  if(not process_file_name in data_list_array):
    emit('continue_process_fail', 'cannot find given process')
    return
  global save_list_name
  save_list_name=process_file_name
  with open('/root/host_workspace/cropper_dev/process_idx/'+message['continue_process_name']+'_last_idx.txt','r') as idxfile:
    last_idx=idxfile.read()
  emit('continue_process_success', {'last_idx':last_idx,'process_file_name':process_file_name})

    


if __name__ == '__main__':
    socketio.run(app,threaded=True)