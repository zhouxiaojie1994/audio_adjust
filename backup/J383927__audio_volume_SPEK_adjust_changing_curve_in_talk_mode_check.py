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
import os,shutil
import time
import logging
import threading
import PyPing
from Audio import IPCAudio_interface
from Audio import ipc_audio
from Audio import audio_analyse
#画图
import numpy as np
import matplotlib.pyplot as plt
from pylab import *#支持中文
save_path='E:/Public/fyp/auto_test/audio_adjust'
#保存为表格
import xlrd,xlutils
from xlutils.copy import copy

class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        threading.Thread.__init__(self)
        self.func=func
        self.args=args

    def run(self):
        return self.func(*self.args)

class AudioAdjustTest(object):
    def __init__(self):
        self.dut_serial_port = COM
        self.baudrate = BAUDRATE
        self.ip = dut_ip
        self.filename = "".join(['AudioAdustTest','.txt'])
        self.logname = "".join(['run_log','.txt'])
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.ser = serial.Serial(port=self.dut_serial_port, baudrate=self.baudrate, timeout=10)
            time.sleep(5)
        except Exception,err:
            print 'open serial port fail',err

    def reload_file_path(self,file_path):
        if os.path.exists(file_path):
            shutil.rmtree(file_path)
            time.sleep(2)
        else:
            pass
        os.makedirs(file_path)  

    def dut_SPEK_test(self):
        #登录串口
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")
        #增加登陆成功的检测

        #开始SPEAKER测试
        self.logger.info("Start speaker test.")
        i=2
        for SPEK_value in Value_list:
            #设置SPEK音量
            self.logger.info("Setting speaker value for %s" %SPEK_value)
            self.ser.write("ubus call CET set_speaker_volume \'{ \"volume\":%s }\'\n" %SPEK_value)
            time.sleep(1)
            #DUT播放测试音频
            audio_save_path='E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/DUT_SPEK/SPEK_Test_Value_%s_Record.wav' %SPEK_value
            play_audio_path='E:/Public/fyp/auto_test/audio_adjust/audio_test.ts'
            #多线程控制音频播放
            test_thread = []
            test_thread.append(MyThread(func=PC_Ctrl.record_from_microphone, args=(audio_save_path,6)))
            test_thread.append(MyThread(func=DUT_Ctrl.play_audio, args=(play_audio_path,5.0)))
            for each in test_thread:
                each.start()
            for each in test_thread:
                each.join()

            self.logger.info("Recording Speaker sound,please wait a moment...")
            SPEK_amplitude =PC_Ctrl.get_audio_volume('E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/DUT_SPEK/SPEK_Test_Value_%s_Record.wav' %SPEK_value)
            SPEK_amplitude_result='%.2f'%SPEK_amplitude
            #写入结果
            dut_SPEK_volume.append(SPEK_amplitude_result) 
            #保存为Excel
            table.write(i,0,SPEK_value)
            table.write(i,1,SPEK_amplitude_result)
            i+=1
        # excel.save('D:/MIC_Test_Result.xls')
        self.logger.info('DUT test finished.please change to SUT.')
    def sut_SPEK_test(self):
        
        #登录串口
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")
        #增加登陆成功的检测

        #开始SPEAKER测试
        self.logger.info("Start speaker test.")
        i=2
        for SPEK_value in Value_list:
            #设置SPEK音量
            self.logger.info("Setting speaker value for %s" %SPEK_value)
            self.ser.write("ubus call CET set_speaker_volume \'{ \"volume\":%s }\'\n" %SPEK_value)
            time.sleep(1)
            #DUT播放测试音频
            audio_save_path='E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/SUT_SPEK/SPEK_Test_Value_%s_Record.wav' %SPEK_value
            play_audio_path='E:/Public/fyp/auto_test/audio_adjust/audio_test.ts'
            #多线程控制音频播放
            test_thread = []
            test_thread.append(MyThread(func=PC_Ctrl.record_from_microphone, args=(audio_save_path,6)))
            test_thread.append(MyThread(func=DUT_Ctrl.play_audio, args=(play_audio_path,5.0)))
            for each in test_thread:
                each.start()
            for each in test_thread:
                each.join()
            time.sleep(3)
            self.logger.info("Recording Speaker sound,please wait a moment...")
            SPEK_amplitude =PC_Ctrl.get_audio_volume('E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/SUT_SPEK/SPEK_Test_Value_%s_Record.wav' %SPEK_value)
            SPEK_amplitude_result='%.2f'%SPEK_amplitude
            #写入结果
            sut_SPEK_volume.append(SPEK_amplitude_result) 
            #保存为Excel
            # table.write(i,0,SPEK_value)
            table.write(i,2,SPEK_amplitude_result)
            i+=1
        self.logger.info('SUT test finished.')
       #以下代码画图
    def chart_draw(self):
        # plt.plot(Value_list, dut_SPEK_volume, marker='o', mec='r', mfc='w',label=u'DUT')
        plt.plot(Value_list, dut_SPEK_volume,label=u'DUT')
        # plt.plot(Value_list, sut_SPEK_volume, marker='*', ms=10,label=u'SUT')
        plt.plot(Value_list, sut_SPEK_volume,label=u'SUT')
        plt.legend()  # 让图例生效
        plt.xticks(Value_list,rotation=45)
        plt.margins(0)
        plt.subplots_adjust(bottom=0.15)
        plt.xlabel(u"volume_setting_values") #X轴标签
        plt.ylabel(u"volume_testing_values") #Y轴标签
        plt.title(u"SPEK_Test_Result_Chart") #标题
        plt.show()
        plt.savefig(file_path)
        self.logger.info("MIC test finished!Please check the result.")
        time.sleep(5)
        self.logger.info("Test finished!\nFile save in %s,Please check the result." %file_path)
    #以下代码检查样机连接状态
    def ping_dut(self,ip):
        dut_ip=self.ip
        count = 0
        while(count<3):
            if PyPing.check_ping(dut_ip,timeout=2,count=4):
                self.logger.debug("check connect OK!")
                break
            else:
                count += 1   
if __name__ == '__main__':
    # try:
    SPEK_Test_Result_Sheet=xlrd.open_workbook('E:/Public/fyp/auto_test/audio_adjust/Audio_Adjust_Test_Result.xls')
    excel=copy(SPEK_Test_Result_Sheet)
    table=excel.get_sheet(0)

    #输入DUT IP
    dut_ip = raw_input('please input DUT IP(default IP is 192.168.1.60): ')
    if dut_ip == '':
        dut_ip = '192.168.1.60'
    logging.basicConfig(level=logging.DEBUG)
    COM = 'com1'
    BAUDRATE=57600
    logging.info("Logining serial port,please wait a moment...")
    PC_Ctrl=audio_analyse.AudioAnalyse()
    DUT_Ctrl=ipc_audio.DUTCtrl(ip=dut_ip)

    #以日期创建文件夹
    # if not os.path.exists('D:/audio_adjust_test/'):
        # os.makedirs('D:/audio_adjust_test',0777)
    # L=time.localtime()[:6]
    file_path='E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record'
    # test_result_path=os.makedirs(file_path)

    Value_list=range(101)[::50]#设置音量大小
    dut_SPEK_volume=[]#用list存储MIC音量
    sut_SPEK_volume=[]
    test = AudioAdjustTest()
        # test.del_file(file_path)
        # test.writeLog(file_path)
    test.ping_dut(dut_ip)
    logging.info('Reload file path')
    DUT_SPEK_Record_path=r'E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/DUT_SPEK'
    test.reload_file_path(DUT_SPEK_Record_path)
    test.dut_SPEK_test()
        #输入SUT IP
    sut_ip = raw_input('please input SUT IP(default IP is 192.168.1.60): ')
    if sut_ip == '':
        sut_ip = '192.168.1.60'
    test.ping_dut(sut_ip)
    logging.info('Reload file path')
    SUT_SPEK_Record_path=r'E:/Public/fyp/auto_test/audio_adjust/Record/SPEK_Record/SUT_SPEK'
    test.reload_file_path(SUT_SPEK_Record_path)
    test.sut_SPEK_test()
    excel.save('%s/SPEK_Test_Result.xls'%file_path)
    test.chart_draw()
    # except Exception,err:
        # print 'Please build and install the PortAudio Python bindings first.',err