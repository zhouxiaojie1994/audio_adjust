#!/usr/bin/env python
# -*- coding:utf-8 -*-
###############################################################################
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
#
# File Name: J383926__audio_volume_MIC_adjust_changing_curve_in_talk_mode_check.py
# Version:   1.0.0
# Author:    fanyongpeng
# History:
#   1,2019-01-15, fanyongpeng@tp-link.com.cn, create
###############################################################################

import serial
import os,shutil
import time
import logging
import PyPing
# import threading
from tools import IPCAudio_interface_half
from tools import ipc_audio
from tools import audio_analyse
#画图
import numpy as np
import matplotlib.pyplot as plt
from pylab import *#支持中文
save_path='E:/Public/fyp/auto_test/audio_adjust'
#保存为表格
import xlrd,xlwt
from xlutils.copy import copy

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

    def dut_mic_test(self):
        #登录串口
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")
        #增加登陆成功的检测
        i=2
        for MIC_value in Value_list:
            #串口设置MIC音量
            self.logger.info("Setting MIC value for %s" %MIC_value)
            self.ser.write("ubus call CET cet_audio_change_capture_volume \'{ \"volume\":%s }\'\n" %MIC_value)
            time.sleep(3)
            #增加音量设置成功的检测
            #PC播放测试音频
            PC_Ctrl.play_audio_sound('E:/Public/fyp/auto_test/audio_adjust/material/std_audio.wav')#解决播放完音频后等待时间问题
            DUT_Ctrl.record_audio('E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/DUT_MIC/'+'MIC_DUT_Test_Value_%d_Record.wav' %MIC_value,audio_time=5)
            self.logger.info("Recording MIC sound,please wait a moment...")
            #time.sleep(10)
            #分析录音文件
            MIC_amplitude =PC_Ctrl.get_audio_volume('E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/DUT_MIC/MIC_DUT_Test_Value_%s_Record.wav' %MIC_value)
            MIC_amplitude_result='%.2f'%MIC_amplitude
            #写入结果
            dut_MIC_volume.append(MIC_amplitude_result) 
            #保存为Excel
            table.write(i,0,MIC_value)
            table.write(i,1,MIC_amplitude_result)
            i+=1
        # 测试完毕后将样机恢复出厂
        # time.sleep(3)
        # self.logger.info("Restore DUT,test finished")
        # self.ser.write("slprestore -r\n")
        self.logger.info('DUT test finished.please change to SUT.') 
    def sut_mic_test(self):
        #登录串口
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")
        #增加登陆成功的检测
        i=2
        for MIC_value in Value_list:
            #串口设置MIC音量
            self.logger.info("Setting MIC value for %s" %MIC_value)
            self.ser.write("ubus call CET cet_audio_change_capture_volume \'{ \"volume\":%s }\'\n" %MIC_value)
            time.sleep(3)
            #增加音量设置成功的检测
            #PC播放测试音频
            PC_Ctrl.play_audio_sound('E:/Public/fyp/auto_test/audio_adjust/material/std_audio.wav')#解决播放完音频后等待时间问题
            DUT_Ctrl.record_audio('E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/SUT_MIC/'+'MIC_SUT_Test_Value_%d_Record.wav' %MIC_value,audio_time=5)
            self.logger.info("Recording MIC sound,please wait a moment...")
            #time.sleep(10)
            #分析录音文件
            MIC_amplitude =PC_Ctrl.get_audio_volume('E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/SUT_MIC/MIC_SUT_Test_Value_%s_Record.wav' %MIC_value)
            MIC_amplitude_result='%.2f'%MIC_amplitude
            #写入结果
            sut_MIC_volume.append(MIC_amplitude_result) 
            #保存为Excel 
            table.write(i,2,MIC_amplitude_result)
            i+=1
        # 测试完毕后将样机恢复出厂
        # time.sleep(3)
        # self.logger.info("Restore SUT,test finished")
        # self.ser.write("slprestore -r\n")
        self.logger.info('SUT test finished.')   
       #以下代码画图
    def chart_draw(self,dut_MIC_volume,sut_MIC_volume):
        plt.plot(Value_list, dut_MIC_volume,label=u'DUT')
        # plt.plot(Value_list, sut_SPEK_volume, marker='*', ms=10,label=u'SUT')
        plt.plot(Value_list, sut_MIC_volume,label=u'SUT')
        plt.legend()  # 让图例生效
        plt.xticks(Value_list,rotation=45)
        plt.margins(0)
        plt.subplots_adjust(bottom=0.15)
        plt.xlabel(u"volume_setting_values") #X轴标签
        plt.ylabel(u"volume_testing_values") #Y轴标签
        plt.title(u"MIC_Test_Result_Chart") #标题
        plt.show()
        plt.savefig(file_path)
        self.logger.info("MIC test finished!Please check the result.")
        time.sleep(5)
        self.logger.info("Test finished!\nFile save in %s,Please check the result." %file_path)
        
        # # 测试完毕后将样机恢复出厂
        # time.sleep(3)
        # self.logger.info("Restore DUT,test finished")
        # self.ser.write("slprestore -r\n")
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
    MIC_Test_Result_Sheet=xlrd.open_workbook('E:/Public/fyp/auto_test/audio_adjust/material/Audio_Adjust_Test_Result.xls')
    excel=copy(MIC_Test_Result_Sheet)
    table=excel.get_sheet(1)

    # MIC_Test_Result_Sheet=xlwt.Workbook(encoding='utf-8')
    # MIC_Sheet=MIC_Test_Result_Sheet.add_sheet(MIC_Test_Result)


    logging.basicConfig(level=logging.DEBUG)
    dut_ip = raw_input('please input DUT IP(default IP is 192.168.1.60): ')
    if dut_ip == '':
        dut_ip = '192.168.1.60'

    COM = 'com1'
    BAUDRATE=57600
    logging.info("Logining serial port,please wait a moment...")
    PC_Ctrl=audio_analyse.AudioAnalyse()
    DUT_Ctrl=ipc_audio.DUTCtrl(ip=dut_ip)
    
    #以日期创建文件夹
    # if not os.path.exists('D:/audio_adjust_test/'):
        # os.makedirs('D:/audio_adjust_test',0777)
    # L=time.localtime()[:6]
    file_path='E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record'
    # test_result_path=os.makedirs(file_path)

    Value_list=range(101)[::5]#设置音量大小
    dut_MIC_volume=[]#用list存储MIC音量
    sut_MIC_volume=[]
    test = AudioAdjustTest()
        # test.del_file(file_path)
        # test.writeLog(file_path)
    test.ping_dut(dut_ip)
    logging.info("Reload file_path.")
    DUT_MIC_Record_path=r'E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/DUT_MIC'
    test.reload_file_path(DUT_MIC_Record_path)
    test.dut_mic_test()
    print dut_MIC_volume 
    #输入SUT IP
    sut_test=raw_input("Please check if your SUT type is TP IPC(Y/N):")
    if sut_test=='Y':
        sut_ip = raw_input('please input SUT IP(default IP is 192.168.1.60): ')
        if sut_ip == '':
            sut_ip = '192.168.1.60'
        else:
            pass
        test.ping_dut(sut_ip)
        logging.info("Reload file_path.")
        SUT_MIC_Record_path=r'E:/Public/fyp/auto_test/audio_adjust/record/half_mode/MIC_Record/SUT_MIC'
        test.reload_file_path(SUT_MIC_Record_path)
        DUT_Ctrl=ipc_audio.DUTCtrl(ip=sut_ip)
        test.sut_mic_test()
        excel.save('%s/MIC_Test_Result.xls'%file_path)
        test.chart_draw(dut_MIC_volume,sut_MIC_volume)
    else:
        sut_MIC_volume=['50']*21
        excel.save('%s/MIC_Test_Result.xls'%file_path)
        test.chart_draw(dut_MIC_volume,sut_MIC_volume)
    


