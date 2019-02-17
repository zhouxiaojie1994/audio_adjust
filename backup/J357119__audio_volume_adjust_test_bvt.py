#!/usr/bin/env python
# -*- coding:utf-8 -*-
###############################################################################
# Copyright (C), 2018, TP-LINK Technologies Co., Ltd.
#
# File Name: J357119__audio_volume_adjust_test_bvt.py
# Version:   1.0.0
# Author:    fanyongpeng
# History:
#   1,2018-09-20, fanyongpeng@tp-link.com.cn, create
###############################################################################

import serial
import os
import pyping
import time
import re
import logging
import shutil
import subprocess
from Audio import ipc_audio
from Audio import audio_analyse

logging.basicConfig(level=logging.DEBUG)

dut_info = raw_input('please input DUT info(example:TL-IPC30_1.0): ')
if dut_info == '':
    dut_info = 'WIPC'
    
COM = 'com1'
BAUDRATE=57600

# FILE_PATH = str(raw_input('please input the path to save capture files: (default is ''D://audio_adjust_bvt_test'')'))
# if FILE_PATH == '':
#     FILE_PATH = 'D://audio_adjust_bvt_test//%s'%dut_info
# # If dir exists, delete it
# if os.path.exists(FILE_PATH):
#     print '*********************************************'
#     print 'Directory exists. Delete it!'
#     print '*********************************************'
#     shutil.rmtree(FILE_PATH)
# # Make dir
# print '*********************************************'
# print 'Make directory for testcase...'
# print '*********************************************'
# os.makedirs(FILE_PATH)


class AudioAdjustTest(object):
    def __init__(self):
        self.dut_serial_port = COM
        self.baudrate = BAUDRATE
        self.filename = "".join(['AudioAdustTest','.txt'])
        self.logname = "".join(['run_log','.txt'])
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.ser = self.pc2.modules.serial.Serial(port=self.dut_serial_port, baudrate=self.baudrate, timeout=10)
            time.sleep(10)
        except Exception,err:
            print 'open serial port fail',err
            
    def audio_adust_bvt_test(self):
        #登录串口
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")

        #开始MIC测试
        self.logger.info("Start MIC test.")
        MIC_value=0
        while MIC_value<=100:
            #设置MIC音量为0
            self.ser.write('''ubus call CET cet_audio_change_capture_volume '{ "volume":%d}\n''') %MIC_value
            time.sleep(1)
            #PC播放测试音频
            audio_analyse.play_audio_sound(self, audio_path)#解决播放完音频后等待时间问题
            audio_analyse.record_from_microphone(self,save_path)
            time.sleep(30)
            #创建音量保存文件
            MIC=os.open("amplitude_test_result.txt","a+")
            #分析录音文件
            MIC_amplitude =audio_analyse.get_audio_amplitude(self,MIC_path)
            #写入结果
            MIC.write("MIC value=%s,amplitude=%s") %MIC_value,MIC_amplitude
            MIC_value=MIC_value+50
        self.logger.info("MIC test finished!\nPlease check the result.")
        time.sleep(5)

        #开始SPEAKER测试
        self.logger.info("Start speaker test.")
        SPEK_value=0
        while SPEK_value<=100:
            #设置SPEK音量为0
            self.ser.write('''ubus call CET set_speaker_volume '{ "volume": %d}\n''') %SPEK_value
            time.sleep(1)
            #PC播放测试音频
            ipc_audio.play_audio(self, audio_path)#解决播放完音频后等待时间问题
            ipc_audio.record_audio(self,save_path)
            time.sleep(30)
            #创建音量保存文件
            SPEK=os.open("amplitude_test_result.txt","a+")
            #分析录音文件
            SPEK_amplitude =audio_analyse.get_audio_amplitude(self,SPEK_path)
            #写入结果
            SPEK.write("SPEK value=%s,amplitude=%s") %SPEK_value,SPEK_amplitude
            SPEK_value=SPEK_value+50
        self.logger.info("Speaker test finished!\nPlease check the result.")

        
if __name__ == '__main__':
    
    test = AudioAdjustTest()
    test.audio_adust_bvt_test()
