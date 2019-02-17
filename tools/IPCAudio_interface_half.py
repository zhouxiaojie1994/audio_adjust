#!/usr/bin/env python
# -*- coding:utf-8 -*-

''' module for control pc interface of audio(like microphone).

:Copyright: (c) 2018 by lujiannan.
:Name: PCAudio_interface.py

'''

import re
import os
import time
import json
import socket
import hashlib
import urllib2
import logging
import subprocess
import requests
import wave
from Crypto.Cipher import AES

logging.basicConfig(level=logging.DEBUG)

class IPCCtrl(object):
    
    def __init__(self,ip='192.168.1.60',port=80,username='admin',password='TPL075526460603'):
        self.ip=ip
        self.port=port
        self.username=username
        self.password=password
        
        self.vhttpd_port=8800
        self.stok=''

        self.logger = logging.getLogger("IPCAudio_interface")
        self.set_vhttpd_port()
        
    def _login(self):
        
        param={"method":"do",
                "login":{"username":"admin",
                          "password":'tyWcQbhc9TefbwK'
                         }
                }
        try:
            get_response=requests.post(url='http://%s/'%self.ip,json=param)
            get_response=get_response.json()
            self.stok=get_response['stok']
            print self.stok
        except Exception,errmsg :
            self.logger.error('Fail to login in:%s.'%errmsg)
            
        return
    
    def record_audio(self,record_audio_path,time=10): 
        
        tmpfile_path='E:/Public/fyp/auto_test/audio_adjust/material/tmp.mp4'
        bool_support_media_encrypt=self.get_module_spec()['media_encrypt_status']
        if bool_support_media_encrypt:
            self.record_encrypt_video(record_path=tmpfile_path,record_time=time)
        else:
            self.record_video(record_path=tmpfile_path,record_time=time)
        
        self.split_audio_from_video(video_path=tmpfile_path,dst_audio_path=record_audio_path)
        
        return
             
    def set_vhttpd_port(self):
        
        if  self.stok=='':
            self._login()
        
        param={"cet":{"name":["rtsp","vhttpd"]},
               "uhttpd":{"name":["main"]},
               "method":"get"
              }
        try:
            get_response=requests.post(url='http://%s/stok=%s/ds'%(self.ip,self.stok),json=param)
            get_response=get_response.json()
            self.vhttpd_port=int(get_response['cet']['vhttpd']['port'])
        except Exception,errmsg :
            self.logger.error('Fail to set vhttpd port:%s.'%errmsg)
        
        return
    
    def get_media_encrypt_status(self):
        
        if  self.stok=='':
            self._login()
            
        param={"method":"get",
                "cet":{"name":["media_encrypt"]}
              }
        try:
            get_response=requests.post(url='http://%s/stok=%s/ds'%(self.ip,self.stok),json=param)
            get_response=get_response.json()
            media_encrypt_status=get_response['cet']['media_encrypt']['enabled']
        except Exception,errmsg :
            self.logger.error('Fail to get vhttpd media encrypt status:%s.'%errmsg)
        
        return media_encrypt_status

    def get_module_spec(self):
        
        if self.stok=='':
            self._login()
        
        param={"method":"get",
               "function":{"name":["module_spec"]}
               }
        module_spec={'media_encrypt_status':0}
       
        try:
            get_response=requests.post(url='http://%s/stok=%s/ds'%(self.ip,self.stok),json=param)
            get_response=get_response.json()
            module_spec['media_encrypt_status']=int(get_response['function']['module_spec']['media_encrypt'])
        except Exception,errmsg :
            self.logger.error('Fail to get vhttpd media encrypt status:%s.'%errmsg)
        
        return module_spec
    
    def record_encrypt_video(self,record_path,record_time=10):
       
        if os.path.exists(record_path):
            os.remove(record_path)
        
        self.aes_info={'cipher':'',
                        'username':'',
                        'padding':'',
                        'algorithm':'',
                        'nonce':''}
        
        addr = (self.ip, self.vhttpd_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        header = "\r\n".join(["POST /stream HTTP/1.1", 
                                "Host: %s:%d" % (self.ip,self.vhttpd_port), 
                                "Content-Type: multipart/mixed;boundary=--client-stream-boundary--",
                                "Content-Length:-1"])
        
        data = "%s\r\n\r\n" % (header)
        sock.send(data)
        recv_data = sock.recv(1024)

        self.aes_info['cipher']=re.findall('cipher=(.*?)username',recv_data)[0][1:-2]
        self.aes_info['username']=re.findall('username=(.*?)padding',recv_data)[0][1:-2]
        self.aes_info['padding']=re.findall('padding=(.*?)algorithm',recv_data)[0][1:-2]
        self.aes_info['algorithm']=re.findall('algorithm=(.*?)nonce',recv_data)[0][1:-2]
        self.aes_info['nonce']=re.findall('nonce=(.*?)\r\nConnection',recv_data)[0][1:-1]

        data = {"type":"request", "seq":"0", "params":
                    {
                    "method":"get",
                    "preview":
                        {
                            "channels":[0],
                            "resolutions":["VGA"]
                        }
                    }
                }
        data = json.dumps(data)
        data = "\r\n".join(["----client-stream-boundary--", "Content-Type:application/json", "Content-Length:%s" % len(data), "", data])
        sock.send(data)
        if record_time is None:
            record_time = 10
        start_time = time.time()
        get_data = ""
        while time.time()-start_time < record_time:
            rd_data = sock.recv(32)
            if rd_data:
                get_data = "%s%s" % (get_data, rd_data)
            else:
                break
        
        record_file = open("%s.tmp" % record_path, "wb")
        record_file.write(get_data)
        record_file.close()

        data = self.__get_record_file_from_multipart_encryptresp("%s.tmp" % record_path)
        record_file = open(record_path, "wb")
        record_file.write(data)
        record_file.close()
        
        self.logger.debug("nonce: %s" % self.aes_info['nonce'])
        
        return
    
    def __get_record_file_from_multipart_encryptresp(self, response):

        response = open(response, "rb")
        video_data = ""
        boundary = ""
        while not boundary.startswith("--"):
            boundary = response.readline()

        if not boundary.startswith("--"):
            raise RuntimeError("no boundary in response when get record video.")

        data = ""
        while True:
            data = response.readline()
            if data=="":
                break
            # video data
            if data.startswith("Content-Type: video/mp2t"):
                data_length = 0
                for i in range(5):
                    data = response.readline()
                    if data.startswith("Content-Length"):
                        data_length = int(data.split(":")[-1])
                        break
                if data_length == 0:
                    break
                    #raise RuntimeError("get video from multipart fail due to data_length is zero.")
                else:
                    for i in range(5):
                        data = response.readline()
                        if data.startswith("X-Session-Id"):
                            break
                    else:
                        #raise RuntimeError("get video from multipart fail due to X-Session-Id is missing after content-length.")
                        break

                    for i in range(5):
                        data = response.readline() 
                        if data.startswith("X-If-Encrypt"):
                            break
                    else:
                        #raise RuntimeError("get video from multipart fail due to no Encrypt line after session.")
                        break
                    
                    for i in range(5):
                        data = response.readline() 
                        if data == "\r\n":
                            break
                    else:
                        #raise RuntimeError("get video from multipart fail due to no blank line after encrption.")
                        break
                    tmp_data=self.decription_data(nonce=self.aes_info['nonce'],
                                        username=self.aes_info['username'],
                                        password='TPL075526460603',
                                        data=response.read(data_length))
                    # print len(tmp_data)
                    video_data = "%s%s" % (video_data,tmp_data )
                    continue

        response.close()
        return video_data
    
    def record_video(self, record_path, record_time=10):

        if os.path.exists(record_path):
            os.remove(record_path)

        data = {"type":"request", "seq":"1", "params":
        {
                "method":"get",
                "preview":
                {
                    #"channels":[1,2,3],
                    #"resolutions":["VGA","HD","HD"],
                    #"audio":["enable","disable","default"]
                    "channels":[0],
                    "resolutions":["VGA"],
                    "audio":["default"]
                }
            }
            }

        data = json.dumps(data)
        data = "\r\n".join(["--record_video", "Content-Type:application/json", "Content-Length:%s" % len(data), "", data])


        handler = urllib2.BaseHandler()
        req = urllib2.Request(url="http://%s:%s/stream" % (self.ip, self.vhttpd_port), data=data)
        req.add_header("Content-Type", "multipart/mixed;boundary=record_video")
        req.add_header("Connection", "keep-alive")
        opener = urllib2.build_opener(handler)
        f = opener.open(req, timeout=10)
        
        if record_time is None:
            record_time = 10
        start_time = time.time()
        data = ""
        while time.time()-start_time < record_time:
            rd_data = f.read(40240)
            if rd_data:
                data = "%s%s" % (data, rd_data)
            else:
                break
        record_file = open("%s.tmp" % record_path, "wb")
        record_file.write(data)
        record_file.close()

        data = self.__get_record_file_from_multipart_resp("%s.tmp" % record_path)
        record_file = open(record_path, "wb")
        record_file.write(data)
        record_file.close()

    def __get_record_file_from_multipart_resp(self, response):

        response = open(response, "rb")

        video_data = ""
        boundary = ""
        while not boundary.startswith("--"):
            boundary = response.readline()

        if not boundary.startswith("--"):
            raise RuntimeError("no boundary in response when get record video.")

        data = ""
        while True:
            data = response.readline()
            if data=="":
                break

            # video data
            if data.startswith("Content-Type: video/mp2t"):
                data_length = 0
                for i in range(5):
                    data = response.readline()
                    if data.startswith("Content-Length"):
                        data_length = int(data.split(":")[-1])
                        break
                if data_length == 0:
                    break
                    #raise RuntimeError("get video from multipart fail due to data_length is zero.")
                else:
                    for i in range(5):
                        data = response.readline()
                        if data.startswith("X-Session-Id"):
                            break
                    else:
                        #raise RuntimeError("get video from multipart fail due to X-Session-Id is missing after content-length.")
                        break

                    for i in range(5):
                        data = response.readline() 
                        if data == "\r\n":
                            break
                    else:
                        #raise RuntimeError("get video from multipart fail due to no blank line after X-Session-Id.")
                        break
                    video_data = "%s%s" % (video_data, response.read(data_length))
                    continue
        response.close()
        return video_data
    
    def encrption_data(self,nonce,username,password,data):
        
        md5_key=hashlib.md5()
        md5_key.update(nonce+':'+password)
        aes_key=md5_key.digest()
        
        md5_iv=hashlib.md5()
        md5_iv.update(username+':'+nonce)
        iv=md5_iv.digest()
        
        encrption_cryptor=AES.new(aes_key,AES.MODE_CBC,iv)
        ecydata=encrption_cryptor.encrypt(self.pcks7_padding(data))
 
        return ecydata
    
    def decription_data(self,nonce,username,password,data):
        
        md5_key=hashlib.md5()
        md5_key.update(nonce+':'+password)
        aes_key=md5_key.digest()
        
        md5_iv=hashlib.md5()
        md5_iv.update(username+':'+nonce)
        iv=md5_iv.digest()
        
        cryptor=AES.new(aes_key,AES.MODE_CBC,iv)
        try:
            dcydata=cryptor.decrypt(data)
            dcydata=self.pcks7_unpadding(dcydata)
        except:
            dcydata=data

        return dcydata
    
    def pcks7_padding(self,data,byte_alignlen=16):
        
        padding_byte=len(data)%byte_alignlen
        if padding_byte==0:
            return data+byte_alignlen*chr(byte_alignlen)
        else:
            #print 'padding'
            return data+(byte_alignlen-padding_byte)*chr(byte_alignlen-padding_byte)
    
    def pcks7_unpadding(self,data,byte_alignlen=16):
        
        pad=ord(data[-1])
        return data[:-pad]

    def subprocess_call(self,*args, **kwargs):
        # also works for Popen. It creates a new *hidden* window,
        # so it will work in frozen apps (.exe).
    
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        kwargs['startupinfo'] = startupinfo
        retcode = subprocess.call(*args, **kwargs)
        
        return retcode   
    
    def split_audio_from_video(self, video_path, dst_audio_path):

        exe_file =  "E:/Public/fyp/auto_test/audio_adjust/tools/video_spliter.exe"
        init_audio_path = os.path.join(os.getcwd(), "aout0.wav")

        if os.path.exists(init_audio_path):
            os.remove(init_audio_path)
        
        args = [exe_file, video_path]
        
        try:
            proc = self.subprocess_call(args,shell=True)

            start_time = time.time()
            while time.time() - start_time < 3:
                if not proc:
                    break
            else:
                raise RuntimeError("split_audio_from_video timeout.")
        except Exception, err:
            
            raise RuntimeError("split_audio_from_video: %s" % str(err))

        # 研发给的分离工具有问题，生成的wave文件头有问题，需要自己改写分离后的文件；若工具改进后可以省略
        if not os.path.exists(init_audio_path):
            raise self.MpTestError(u'split audio fail.')

        origin_file = open(init_audio_path, "rb")
        origin_file.read(44)
        data = origin_file.read()
        origin_file.close()

        #dst_audio_path = os.path.join(data_dir, "aout1.wav")
        if os.path.exists(dst_audio_path):
            os.remove(dst_audio_path)

        new_file = wave.open(dst_audio_path, "wb")
        new_file.setnchannels(1)
        new_file.setsampwidth(2)
        new_file.setframerate(8000)
        new_file.writeframes(data)
        new_file.close()

        # wave 文件处理结束

        return dst_audio_path

    def play_audio(self, src_audio, audio_time):

        bool_support_media_encrypt=self.get_module_spec()['media_encrypt_status']
        print bool_support_media_encrypt
        if bool_support_media_encrypt:
            self.play_encrypt_audio(src_audio=src_audio,audio_time=audio_time)
            return
            
        addr = (self.ip, self.vhttpd_port)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        header = "\r\n".join(["POST /stream HTTP/1.1", "Host: %s:%d" % (self.ip,self.vhttpd_port), "Content-Type: multipart/mixed;boundary=playaudio"])
        header = header

        data = {"type":"request", "seq":"1", "params":{
                    "method":"get",
                    "talk":
                    {
                        "mode":"half_duplex"
                    }
                }
                }

        data = json.dumps(data)
        data = "\r\n".join(["--playaudio", "Content-Type:application/json", "Content-Length:%s" % len(data), "", data])

        data = "%s\r\n\r\n%s\r\n\r\n" % (header, data)

        sock.send(data)
        recv_data = sock.recv(1024)
        recv_data = sock.recv(1024)
        
        recv_data = recv_data.split("\r\n")[-2]
        self.logger.debug("response: %s" % recv_data)
        recv_data = json.loads(recv_data)
        sid = recv_data["params"]["session_id"]

        self.logger.debug("audio stream session: %s" % str(sid))

        f = open(src_audio, "rb")
        # f = open(r"E:\Public\gh\MPT_Perf_IPC22v1_add_audio\data\speaker_std.pcm", "rb")
        file_length = os.path.getsize(src_audio)
        buf = 594
        time_interval = audio_time*buf/file_length

        data = f.read(buf)
        while data:
            data = "\r\n".join(["--playaudio", "Content-Type:audio/mp2t", "Content-Length:%s" % len(data), "X-Session-Id:%s" % str(sid), "", data, ""])
            data = "%s\r\n" % data
            start_time = time.clock()
            while time.clock()-start_time < time_interval:
                pass
            sock.send(data)
            data = f.read(buf)
        f.close()
        sock.close()

    def play_encrypt_audio(self, src_audio, audio_time):
        '''let dut play audio src_audio using it's speaker.
        Arguments:
            src_audio(str): src_audio to play.
            
        Returns:
            None
                                 
        Examples:
            dutctrl.play_audio("D:/save/audio.wav")
        '''
        self.aes_info={'cipher':'',
                        'username':'',
                        'padding':'',
                        'algorithm':'',
                        'nonce':''}
        addr = (self.ip, self.vhttpd_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        header = "\r\n".join(["POST /stream HTTP/1.1", 
                                "Host: %s:%d" % (self.ip,self.vhttpd_port), 
                                "Content-Type: multipart/mixed;boundary=--client-stream-boundary--",
                                "Content-Length:-1"])
        
        header = header
        data = "%s\r\n\r\n" % (header)
        sock.send(data)
        recv_data = sock.recv(1024)
        
        self.aes_info['cipher']=re.findall('cipher=(.*?)username',recv_data)[0][1:-2]
        self.aes_info['username']=re.findall('username=(.*?)padding',recv_data)[0][1:-2]
        self.aes_info['padding']=re.findall('padding=(.*?)algorithm',recv_data)[0][1:-2]
        self.aes_info['algorithm']=re.findall('algorithm=(.*?)nonce',recv_data)[0][1:-2]
        self.aes_info['nonce']=re.findall('nonce=(.*?)\r\nConnection',recv_data)[0][1:-1]

        data = {"type":"request", "seq":"0", "params":{
                    "method":"get",
                    "talk":
                    {
                        "mode":"half_duplex"
                    }
                }
                }

        data = json.dumps(data)
        data = "\r\n".join(["----client-stream-boundary--",
                            "Content-Type:application/json",
                            "Content-Length:%s" % len(data), 
                            "", 
                            data])
        data = "\r\n\r\n%s" % (data)
        sock.send(data)
        recv_data = sock.recv(1024)

        recv_data = recv_data.split("\r\n")[-2]
        self.logger.debug("response: %s" % recv_data)
        recv_data = json.loads(recv_data)
        sid = recv_data["params"]["session_id"]

        self.logger.debug("audio stream session: %s" % str(sid))

        f = open(src_audio, "rb")
        # f = open(r"E:\Public\gh\MPT_Perf_IPC22v1_add_audio\data\speaker_std.pcm", "rb")
        file_length = os.path.getsize(src_audio)
        print file_length
        buf = 594
        time_interval = audio_time*buf/file_length

        data = f.read(buf)
        while data:
            encrption_data=self.encrption_data(nonce=self.aes_info['nonce'],
                                                username=self.aes_info['username'],
                                                password='TPL075526460603',
                                                data=data)
            data = "\r\n".join(["----client-stream-boundary--",
                                "Content-Type:audio/mp2t",
                                "Content-Length:%s" % len(encrption_data), 
                                "X-Session-Id:%s" % str(sid),
                                "X-If-Encrypt: 1",
                                "", encrption_data, ""])
            data = "%s\r\n" % data
            start_time = time.clock()
            while time.clock()-start_time < time_interval:
                pass
            sock.send(data)
            data = f.read(buf)
        f.close()
        sock.close()
        return 
    
        
if __name__ == "__main__":
    
    test=IPCCtrl(ip='192.168.1.60')
    
    #test _login
    #test._login()
    #print test.stok
    
    # test set_vhttpd_port
    #test.set_vhttpd_port()
    #print test.vhttpd_port
    
    # test get_media_encrypt_status
    #print test.get_media_encrypt_status()
    
    # test get_module_spec
    #print test.get_module_spec()['media_encrypt_status']
    
    # test record audio
    #test.record_audio(record_audio_path='D:/123.wav',time=10)
    
    # test play audio
    test.play_audio(src_audio='std_speaker.ts', audio_time=7.0)
    

    