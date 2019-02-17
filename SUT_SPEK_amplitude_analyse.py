#!/usr/bin/env python
# -*- coding:utf-8 -*-
###############################################################################
# Copyright (C), 2019, TP-LINK Technologies Co., Ltd.
#
# File Name: SUT_SPEK_amplitude_analyse.py
# Version:   1.0.0
# Author:    fanyongpeng
# History:
#   1,2019-01-15, fanyongpeng@tp-link.com.cn, create
###############################################################################
import os
import time
import logging

from tools import IPCAudio_interface
from tools import ipc_audio
from tools import audio_analyse

#保存为表格
import xlrd,xlutils
from xlutils.copy import copy

#复制表格
SUT_SPEK_Test_Result_Sheet=xlrd.open_workbook('E:/Public/fyp/auto_test/audio_adjust/material/Audio_Adjust_Test_Result.xls')
excel=copy(SUT_SPEK_Test_Result_Sheet)
table=excel.get_sheet(0)
#统计文件
Value_list=[]
file_path=r'E:/Public/fyp/auto_test/audio_adjust/sut_test/SPEK'
for parent,dirnames,filenames in os.walk(file_path):
    for file in filenames:
        if os.path.splitext(file)[1]=='.wav':
            filename=os.path.splitext(file)[0]
            Value_list.append(int(filename))
# print Value_list_tmp
Value_list.sort()
# print Value_list_tmp

#计算音量
# Value_list=range(101)[::5]
sut_SPEK_volume=[]#用list存储MIC音量
PC_Ctrl=audio_analyse.AudioAnalyse()
i=2
for SPEK_value in Value_list:
    logging.info('Analysing record wave amplitude which audio value is %s...'%SPEK_value)
    SPEK_amplitude =PC_Ctrl.get_audio_volume('E:/Public/fyp/auto_test/audio_adjust/sut_test/SPEK/%s.wav' %SPEK_value)
    SPEK_amplitude_result='%.2f'%SPEK_amplitude
    #写入结果
    sut_SPEK_volume.append(SPEK_amplitude_result) 
    #写入Excel
    table.write(i,0,SPEK_value)
    table.write(i,2,SPEK_amplitude_result)
    i+=1
excel.save('E:/Public/fyp/auto_test/audio_adjust/sut_test/SPEK_Test_Result.xls')