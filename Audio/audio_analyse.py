#!/usr/bin/env python
# -*- coding:utf-8 -*-

''' Copyright (C), 2018, TP-LINK Technologies Co., Ltd.

    Filename    : audio_analyse.py
    Version     : 1.0.0
    Description : for Audio Camera
    Author      : lujiannan@tp-link.net
    History:
        2018-09-25 | lujiannan@tp-link.net
            First created.

'''

import os
import logging
import time
import subprocess
import winsound
import wave
import numpy
import math
import matplotlib
matplotlib.use("wxagg")
import matplotlib.pyplot as plt

for i in range(3):
    try:
        import _portaudio
        break
    except:
        time.sleep(.5)

import pyaudio


class AudioAnalyse(object):
    
    def __init__(self,dst_path='D:/result.png'):
        
        self.logger = logging.getLogger("AudioAnalyse")
        self.dst_path=dst_path
        
    def get_audio_volume(self,audio_path):
        """get audio volume.
        
        -Arguments:
            audio_path(string): path of audio need to analyse.
        --Returns:
            volume(float): Average volume over time.
        """
        
        self.logger.debug("get audio volume...")
        audio_sturct=self.open_audio(audio_path)
        volume=self.calc_audio_volume(audio_sturct)
        # self.create_result_picture(raw_arr=volume,
                                    # x_max=audio_sturct['info']['audio_time'],
                                    # y_max=numpy.max(volume)+50,
                                    # diplay_feature='show')
        
        volume_mean=self.calc_volume_mean(volume_array=volume,silent_threshold=0)
        self.logger.info("Audio volume: %s"%volume_mean)
        
        return volume_mean

    def create_result_picture(self, raw_arr,x_max,y_max,diplay_feature):
        """save result.
        
        -Arguments:
            raw_arr(array): input raw data.
            x_max(int): x max value.
            y_max(int):x max value.
            diplay_feature(str):'save','show'.
        --Returns:
            None.
        """
        
        self.logger.debug("create wave picture...") 
        
        if os.path.exists(self.dst_path):
            self.logger.info("Need to delete the  same  name file...")
            os.remove(self.dst_path)
        
        plt.axes(xlim=(0, x_max), ylim=(0, y_max))
        x_step = numpy.arange(0, x_max, x_max/len(raw_arr))
        #plt.plot(x=x_step,y=raw_arr,color="b")
        plt.plot(raw_arr,color="b")
        plt.xlabel("Time(s)")
        plt.ylabel("Volume(dB)")
        if diplay_feature=='save':
            plt.savefig(self.dst_path)
        elif diplay_feature=='show':
            plt.show()
        else:
            pass
        plt.clf()
        
        return
    
    def calc_volume_mean(self,volume_array,silent_threshold=0):
        """calculate volume mean.
        
        -Arguments:
            volume_array(array): volume list data.
            silent_threshold(int): 0 for None; >Max(volume_array) to output 0,others calc >silent_threshold mean.
        --Returns:
            volume_mean(float):volume list mean.
        """
        
        index=[]
        if silent_threshold==0:
            volume_mean=volume_array.mean()
            return volume_mean
        
        elif silent_threshold> numpy.max(volume_array):
            volume_mean=0
            return volume_mean
        
        else:
            for i in range(len(volume_array)):
                if volume_array[i]>silent_threshold:
                    index.append(i)
            volume_array=numpy.take(volume_array,index)
            volume_mean=volume_array.mean()
            return volume_mean
                
    def open_audio(self,audio_path):
        """open audio file.
        
        -Arguments:
            audio_path(string): path of audio need to analyse.
        --Returns:
            _audio(dict): audio including channel, sampwidth, sampling_rate, nframe.
        """
        
        self.logger.debug("open audio file...")
        _audio={}
        
        # audio info
        wave_file = wave.open(audio_path, "rb")
        params = wave_file.getparams()
        nchannels, sampwidth, sampling_rate, nframes = params[:4]
        audio_time = nframes*1.0/sampling_rate
        _audio['info']={'sample_rate':sampling_rate,
                        'frames':nframes,
                        'channels':nchannels,
                        'audio_time':audio_time,
                        'audio_length':0}
        
        #audio data
        data = wave_file.readframes(nframes)
        sound = numpy.fromstring(data, dtype=numpy.int16)
        _audio['info']['audio_length']=len(sound)
        _audio['data']=sound
        
        return _audio        

    def calc_audio_volume(self,audio,frame_size=1024,overlap=512):
        """Time domain analysis,calculate audio volume.
        
        -Arguments:
            audio (dict):  audio dict of data and info.
            frame_size(int): size of frame(window),usually 256,512,1024.
            overlap(int): Overlap part of windows,usually a half of frame_size. 
        --Returns:
            volume(list): the result(dB) array of Time domain analysis.
        """       
        
        self.logger.debug("calc audio volume...")
        step=frame_size-overlap
        framenum=int(math.ceil(audio['info']['audio_length']*1.0/step))
        volume = numpy.zeros((framenum,1))
        for i in range(framenum):
            curframe = audio['data'][numpy.arange(i*step,min(i*step+frame_size,audio['info']['audio_length']))]
            curframe = curframe - numpy.mean(curframe) # zero-justified
            if numpy.sum(curframe*curframe)<1:
                volume[i] = 10*numpy.log10(1)
            else:
                volume[i] = 10*numpy.log10(numpy.sum(curframe*curframe))
        
        return volume

    def record_from_microphone(self, save_path, record_time=10):

        self.logger.debug("start to recording, record time is %s" % record_time)
        record_format = pyaudio.paInt16
        nchannels = 1
        record_rate = 44100
        frames_per_buffer = 1000
        pa = pyaudio.PyAudio()
        record_stream = pa.open(format=record_format, 
                                channels=1,
                                rate=record_rate,
                                input=True,
                                frames_per_buffer=frames_per_buffer)
        data = ""
        for i in range(record_rate * int(record_time) / frames_per_buffer):
            data = b"%s%s" % (data, record_stream.read(frames_per_buffer))

        record_stream.stop_stream()
        record_stream.close()
        pa.terminate()

        wave_file = wave.open(save_path, "wb")
        wave_file.setnchannels(nchannels)
        wave_file.setsampwidth(pa.get_sample_size(record_format))
        wave_file.setframerate(record_rate)
        wave_file.writeframes(data)
        wave_file.close()
        return
    
    @classmethod
    def play_audio_sound(self, audio_path):
    
        winsound.PlaySound(audio_path, winsound.SND_ASYNC | winsound.SND_NOWAIT)
    

if __name__ == "__main__":
    

    test=AudioAnalyse()
    # test.play_audio_sound('C:/Users/tplink/Desktop/Audio_Adjust_Bvt_Test/std_audio_0.wav')
    # print test.get_audio_volume(audio_path="D:/test_0dB.wav")
    #print test.get_audio_volume(audio_path="D:/test_9dB.wav")
    #print test.get_audio_volume(audio_path="D:/test_18dB.wav")
    #print test.get_audio_volume(audio_path="D:/test_18dB.wav")
    #test.get_audio_amplitude("D:/test_9dB.wav")
    #test.get_audio_amplitude("D:/test_18dB.wav")

