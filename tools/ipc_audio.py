#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Copyright (C), 2018, TP-LINK Technologies Co., Ltd.

    Filename    : IPC_Audio.py
    Version     : 1.0.0
    Author      : lujiannan@tp-link.net
    History:
        1, 2018-09-25, lujiannan@tp-link.net, create this file.
'''

import urllib2
import time
import logging
import os
import json
import subprocess
import wave

class DUTCtrl(object):
    
    def __init__(self, ip):
        
        self.logger = logging.getLogger("IPCAudio")
        self.ip=ip
    
    def record_audio(self,dst_audio,audio_time=30):
        
        record_path='E:/Public/fyp/auto_test/audio_adjust/material/tmp.mp4'
        self.record_video(record_path=record_path,record_time=audio_time)
        self.split_audio_from_video(video_path=record_path, dst_audio_path=dst_audio)
        
        return
    
    def play_audio(self, src_audio, audio_time):
        
        '''let dut play audio src_audio using it's speaker.
        Arguments:
            src_audio(str): src_audio to play.
            
        Returns:
            None
                                 
        Examples:
            dutctrl.play_audio("D:/save/audio.wav")
        '''
        addr = (self.ip, 8800)
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(addr)
        header = "\r\n".join(["POST /stream HTTP/1.1", "Host: %s:%d" % (self.ip,8800), "Content-Type: multipart/mixed;boundary=playaudio"])
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
        
    def record_video(self, record_path, record_bytes=None, record_time=None):
        '''record video and save it to dst_path
        Arguments:
            dst_path(str): dst_path to save video recorded.
            
        Returns:
            None
                                 
        Examples:
            record_video("D:/save/video.mp4")
        '''
        if os.path.exists(record_path):
            os.remove(record_path)

        data = {"type":"request", "seq":"1", "params":
                    {
                    "method":"get",
                    "preview":
                        {
                            "channels":[0],
                            "resolutions":["VGA"],
                            "audio":["default"]
                        }
                    }
                }

        data = json.dumps(data)
        data = "\r\n".join(["--record_video", "Content-Type:application/json", "Content-Length:%s" % len(data), "", data])


        handler = urllib2.BaseHandler()
        req = urllib2.Request(url="http://%s:%s/stream" % (self.ip, 8800), data=data)
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
        
        return

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

        exe_file = 'E:/Public/fyp/auto_test/audio_adjust/tools/video_spliter.exe'
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

        if not os.path.exists(init_audio_path):
            raise self.MpTestError(u'split audio fail.')

        origin_file = open(init_audio_path, "rb")
        origin_file.read(44)
        data = origin_file.read()
        origin_file.close()

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
        
        

if __name__ == "__main__":
    pass

