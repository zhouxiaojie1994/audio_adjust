#!/usr/bin/env python
# -*- coding:utf-8 -*-

import serial
import os
import PyPing
import time
import re
import rpyc
import logging
import shutil
import subprocess
from RouterCtrl import SohoRouterCtrl as rc
from PyNetConfig import NetConfig as s

logging.basicConfig(level=logging.DEBUG)

dut_info = raw_input('please input DUT info(example:TL-IPC30_1.0): ')
if dut_info == '':
    dut_info = 'WIPC'
    
COM = raw_input('input the serial port(for example: com1, default is com1)')
if COM =='':
    COM = 'com1'

BAUDRATE= raw_input('please input your dut serial baudrate(default is 57600): ')
if BAUDRATE=='':
    BAUDRATE=57600

CHANNEL = raw_input('please input channel to be test(default:1,6,13):')
if CHANNEL == '':
    CHANNEL = '1,6,13'

# BANDWIDTH = raw_input('please input bandwidth to be test(default:WLAN_BANDWIDTH_40M,WLAN_BANDWIDTH_20M):')
# if BANDWIDTH == '':
    # BANDWIDTH = 'WLAN_BANDWIDTH_40M','WLAN_BANDWIDTH_20M'
    

FILE_PATH = str(raw_input('please input the path to save capture files: (default is ''D://iperf_throughput'')'))
if FILE_PATH == '':
    FILE_PATH = 'D://iperf_throughput//%s'%dut_info
# If dir exists, delete it
if os.path.exists(FILE_PATH):
    print '*********************************************'
    print 'Directory exists. Delete it!'
    print '*********************************************'
    shutil.rmtree(FILE_PATH)
# Make dir
print '*********************************************'
print 'Make directory for testcase...'
print '*********************************************'
os.makedirs(FILE_PATH)


class IperfThroughput(object):
    def __init__(self):
        self.dut_serial_port = COM
        self.baudrate = BAUDRATE
        self.filename = "".join(['iperf_throughput','.txt'])
        self.logname = "".join(['run_log','.txt'])
        self.router = rc('192.168.1.1','admin','123456')
        self.bandwidth = [self.router.WLAN_BANDWIDTH_40M,self.router.WLAN_BANDWIDTH_20M]
        self.nic = s('lan')
        self.CHANNEL = CHANNEL.split(',')
        self.pc2 = rpyc.classic.connect('192.168.250.20')
        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            self.ser = self.pc2.modules.serial.Serial(port=self.dut_serial_port, baudrate=self.baudrate, timeout=10)
            time.sleep(10)
        except Exception,err:
            print 'open serial port fail',err
            
    def writeResult(self, loginfo):
        ''' write loginfo into txt file'''
        try:
            result_path = os.path.join(FILE_PATH, self.filename)
            with open(result_path, 'a+') as l:
                l.write('%s\n' % (loginfo))
            return True
        except Exception,err:
            self.logger.debug("save result fail")
            return False

    def writeLog(self, loginfo):
        ''' write loginfo into txt file'''
        try:
            log_path = os.path.join(FILE_PATH, self.logname)
            with open(log_path, 'a+') as l:
                l.write('%s\n' % (loginfo))
            return True
        except Exception, err:
            self.logger.debug("save log fail")
            return False
            
    def iperf_test(self):
        self.ser.write("\n")
        time.sleep(1)
        self.ser.write("root\n")
        time.sleep(1)
        self.ser.write("slprealtek\n")
        time.sleep(1)
        self.logger.debug("serial login success")
        self.ser.write('makeRoomForUpgrade.sh kill\n')
        time.sleep(5)
        #删除已经串口输出的内容#
        #ser.inWaiting()得到当前串口输出的字节数#
        self.ser.flushInput()
        self.logger.debug("flushing input")
        self.ser.write("ifconfig\n")
        time.sleep(2)
        data = self.ser.readall()
        print data
        try:
            if 'br-wan' in data:
                start_index = data.index('br-wan')
                self.logger.debug('start index is %d' % start_index)
                end_index = data.index('Bcast',start_index)
                self.logger.debug('end index is %d' % end_index)
                temp_list = data[start_index:end_index].split(' ')
                temp_index = temp_list.index('inet')
                IPC_IP = temp_list[temp_index + 1].split(':')[1]
                self.logger.debug("IPC IP is %s" % (IPC_IP))
            else:
                start_index = data.index('wlan0')
                self.logger.debug('start index is %d' % start_index)
                end_index = data.index('Bcast',start_index)
                self.logger.debug('end index is %d' % end_index)
                temp_list = data[start_index:end_index].split(' ')
                temp_index = temp_list.index('inet')
                IPC_IP = temp_list[temp_index + 1].split(':')[1]
                self.logger.debug("IPC IP is %s" % (IPC_IP))
        except Exception,e:
            print 'get IPC IP fail,check serial connect',e
            quit()
        
		# data = ser.readall().split(' ')
		
		# mac_index = data.index('HWaddr') + 1
		# IPC_MAC = data[mac_index].replace(':','-')
		# router_client_list = self.router.get_dhcp_client_list()
		# try:
		    # for client in range(len(router_client_list)):
		        # if router_client_list[i]['mac'] == IPC_MAC:
			        # IPC_IP = router_client_list[i]['ip']
			    # else:
				    # raise Exception
        # except Exception,e:
            # print 'get IPC IP fail',e
            # break
    

        # try:
            # self.router.set_wpa2_psk(self.router.WLAN_ENCRYPTION_AES,'12345678')
            # self.router.apply()
        # except Exception, err:
            # print 'cannot set encryption,error occur:',err 
        for bandwidth in self.bandwidth:
            try:
                self.router.set_wlan_mode(self.router.WLAN_MODE_11BGN)
                self.router.set_bandwidth(bandwidth)
                self.router.apply()
            except Exception, err:
                print 'cannot set bandwidth,error occur:',err
            for channel in self.CHANNEL:
                try:
                    self.router.set_channel(int(channel))
                    self.router.apply()
                except Exception, err:
                    print 'cannot set router,error occur:',err

                time.sleep(10)#wait for IPC to connect to router#
                
                #get nic ip#
                self.nic.enable()
                self.nic.enable_dhcp()
                NIC_IP = self.nic.get_ip_list()[0]['ip']
 
                count = 0
                while(count<3):
                    if PyPing.check_ping(IPC_IP,timeout=2,count=4):
                        self.logger.debug("check connect OK!")
                        break
                    else:
                        count += 1
               

                # try:
                    # IPC_IP = self.dut_onboarding_with_ap(ssid=SSID,
                                                # encryption_type='WPA2_PSK_AES',
                                                # encryption_key='12345678')
                    # print 'onboarding succeed'
                # except Exception, err:
                    # print 'onboarding fail:',err
                    
              
                # try:
                    # if not check_ping(IPC_IP,time_out=2,count=4):
                        # raise ConnectError
                # except ConnectError,e:
                    # print 'check connectivity fail',e
                    # break
                    
                

                #run down_stream#
                try:
                    self.ser.write("iperf -s -w 4M\n") #open iperf server#
                    time.sleep(1)
                    down_result_tem = self.run_iperf_from_lan_pc(server_ip=IPC_IP,run_time = 30,pair_number = 5,interval = 10,window = '4M')
                    print 'do run iperf lan PC'
                    down_stream = down_result_tem[-1]['Bandwidth']                                      
                    self.logger.debug("run down stream finish,writing result")
                    self.writeResult('bandwidth %s ch %s down_stream_throughput is %s'% (bandwidth,channel,down_stream))
                except Exception,e:
                    self.logger.debug("run down stream fail")
                #run up_stream#
                try:
                    try:
                        self.ser.write(chr(0x03)) #ctrl+c#
                        time.sleep(1)
                        self.ser.flushInput()
                        time.sleep(1)
                        self.open_iperf_server_at_lan_pc(window='4M')
                        time.sleep(1)
                        up_result_tem = self.run_iperf_from_dut(server_ip = NIC_IP,run_time = 30,pair_number = 1,interval = 5,window = '4M')
                        up_stream = up_result_tem[-1]['Bandwidth']
                        self.logger.debug("run up stream finish,writing result")
                        self.writeResult('bandwidth %s ch %s up_stream_throughput is: %s'% (bandwidth,channel,up_stream))
                    except Exception,e:
                        self.logger.debug("run up stream fail")
                finally:
                    self.close_iperf_server_at_lan_pc()
        
    def open_iperf_server_at_lan_pc(self, host='',window='4M'):
        '''This function will call cmd.exe iperf -s -D -B host.
        The output will be like this:
            ------------------------------------------------------------
            Server listening on TCP port 5001
            TCP window size: 8.00 KByte (default)
            ------------------------------------------------------------
            IPerf Service started.
            
        Arguments:
            host(str): the network interface will be binded. an interface or multicast address.
                       Default is blank that means binding to all interfaces.
            
        Returns:
            None   
        '''
        
        self.logger.debug('Open iperf server with host %s' % host)
        
        cmd = 'iperf -s -D -w %s -B %s' % (window,host)
        output = os.popen(cmd).read()
        if re.search('IPerf Service started', output, re.I) is not None:
            self.logger.debug('Open iperf server successfully.')
        else:
            err_msg = 'Fail to open Iperf server.'
            self.logger.warn(err_msg)
            raise RuntimeError(err_msg)
            
    def close_iperf_server_at_lan_pc(self, host=''):
        '''This function will call cmd.exe iperf -s -B host.
        The output will be like this:
            ------------------------------------------------------------
            Server listening on TCP port 5001
            TCP window size: 8.00 KByte (default)
            ------------------------------------------------------------
            Stopping IPerf Service.
            IPerf Service stopped.
            IPerf Service removed.
            IPerf Service is removed.
            
        Arguments:
            host(str): the network interface will be binded. an interface or multicast address.
                       Default is blank that means binding to all interfaces. 
            
        Returns:
            None     
        '''
        
        self.logger.debug('Close iperf server with host %s' % host)
         
        cmd = 'iperf -s -R -B %s' % host
        output = os.popen(cmd).read()
        if re.search('IPerf Service is removed', output, re.I) is not None:
            self.logger.debug('Close iperf server successfully.')
        else:
            err_msg = 'Fail to close Iperf server.'
            self.logger.warn(err_msg)
            raise RuntimeError(err_msg)
        
    def run_iperf_from_lan_pc(self, server_ip, pair_number=10, run_time=60, window='64k', interval=0, host=''):
        '''This function will call cmd.exe iperf -c -t.
        The output will be like this:
            (multi-pair)
            [1904]  0.0-10.0 sec  11.2 MBytes  9.41 Mbits/sec
            [1840]  0.0-10.0 sec  11.3 MBytes  9.52 Mbits/sec
            [SUM]   0.0-10.0 sec  114 MBytes   95.3 Mbits/sec
            [1888]  0.0-16.4 sec  11.5 MBytes  5.90 Mbits/sec
            [1824]  0.0-16.4 sec  11.4 MBytes  5.84 Mbits/sec
            [1872]  0.0-16.4 sec  11.7 MBytes  5.99 Mbits/sec
            [1856]  0.0-16.4 sec  11.5 MBytes  5.90 Mbits/sec
            [1920]  0.0-16.4 sec  11.3 MBytes  5.77 Mbits/sec
            [1808]  0.0-16.4 sec  11.3 MBytes  5.80 Mbits/sec
            [1776]  0.0-16.4 sec  11.2 MBytes  5.76 Mbits/sec
            [1792]  0.0-16.4 sec  11.4 MBytes  5.82 Mbits/sec
            [1904]  0.0-16.4 sec  11.2 MBytes  5.76 Mbits/sec
            [SUM]   0.0-16.4 sec   114 MBytes  58.3 Mbits/sec
            (single-pair)
            [ ID]    Interval       Transfer     Bandwidth
            [1840]  0.0-16.4 sec  11.4 MBytes  5.82 Mbits/sec         
        
        Arguments:
            server_ip(str)  : Iperf Server IP.
            pair_number(int): Number of parallel client threads to run (default 10).
            run_time(int)   : Time in seconds to transmit for (default 60 secs).
            window(str)     : TCP window size (socket buffer size). Default is '64k'.
            interval(int)   : seconds between periodic bandwidth reports (default is 0).
            host(str)       : the network interface will be binded. an interface or multicast address.
                              Default is blank that means binding to all interfaces.  
            
        Returns(list):
            return a list contain the info of the rule. For example:
            When pair_number > 1:
            [{'Transfer': '57.2MBytes', 'SUM': 0, 'Interval': '0.0- 5.0 sec', 
              'Bandwidth': '95.9Mbits/sec'}, 
             {'Transfer': '56.5MBytes', 'SUM': 1, 'Interval': '5.0-10.0 sec', 
              'Bandwidth': '94.8Mbits/sec'}, 
             {'Transfer': '114MBytes', 'SUM': 2, 'Interval': '0.0-10.6 sec', 
              'Bandwidth': '90.3Mbits/sec'}]           
            When pair_number == 1: 
            [{'Transfer': '114MBytes', 'Interval': '0.0-10.6 sec', 
              'Bandwidth': '90.3Mbits/sec', 'ID':0}] 
        '''
    
        self.logger.debug('Run iperf client to server with ip %s' % server_ip)
        
        # cmd like as 'iperf -c 192.168.2.101 -w 64k -t 10 -i 5'
        run_cmd = 'iperf -f m -c %s -P %s -t %s -w %s -i %s' % \
                        (server_ip, pair_number, run_time, window, interval)
        self.logger.debug('iperf client cmd is: %s' % run_cmd)
        output = os.popen(run_cmd).read()
        
        print output
        if pair_number >= 2:    
            sum_str = ('\[SUM\]\s*([0-9.\-\s*]+)\s*sec\s*([0-9.]+)'
                       '\s*MBytes\s*([0-9.]+)\s*Mbits\/sec')
            my_list = re.findall(sum_str, output, re.I)

            sum_list = []
            for i in range(len(my_list)):
                fmt = {}
                fmt['SUM'] = i
                fmt['Interval'] = '%ssec' % my_list[i][0]
                fmt['Transfer'] = '%sMBytes' % my_list[i][1]
                fmt['Bandwidth'] = '%sMbits/sec' % my_list[i][2]
                
                sum_list.append(fmt.copy())    
        
        else:
            sum_str = ('\[\s*\d+\]\s*([0-9.\-\s*]+)\s*sec\s*([0-9.]+)'
                       '\s*MBytes\s*([0-9.]+)\s*Mbits\/sec')
            my_list = re.findall(sum_str, output, re.I)

            sum_list = []
            for i in range(len(my_list)):
                fmt = {}
                fmt['ID'] = i
                fmt['Interval'] = '%ssec' % my_list[i][0]
                fmt['Transfer'] = '%sMBytes' % my_list[i][1]
                fmt['Bandwidth'] = '%sMbits/sec' % my_list[i][2]
                
                sum_list.append(fmt.copy())
        return sum_list      
    def run_iperf_from_dut(self, server_ip, pair_number=10, run_time=60, window='64k', interval=0, host=''):
        run_serial = 'iperf -f m -c %s -P %s -t %s -w %s -i %s\n' % \
                        (server_ip, pair_number, run_time, window, interval)
        self.ser.write(run_serial)
        self.logger.debug('iperf client serial is: %s' % run_serial)
        ser_data = self.ser.readall()
        print ser_data
        self.writeLog(ser_data)
        if pair_number >= 2:    
            sum_str = ('\[SUM\]\s*([0-9.\-\s*]+)\s*sec\s*([0-9.]+)'
                       '\s*MBytes\s*([0-9.]+)\s*Mbits\/sec')
            my_list = re.findall(sum_str, ser_data, re.I)

            sum_list = []
            for i in range(len(my_list)):
                fmt = {}
                fmt['SUM'] = i
                fmt['Interval'] = '%ssec' % my_list[i][0]
                fmt['Transfer'] = '%sMBytes' % my_list[i][1]
                fmt['Bandwidth'] = '%sMbits/sec' % my_list[i][2]
                
                sum_list.append(fmt.copy())    
        
        else:
            sum_str = ('\[\s*\d+\]\s*([0-9.\-\s*]+)\s*sec\s*([0-9.]+)'
                       '\s*MBytes\s*([0-9.]+)\s*Mbits\/sec')
            my_list = re.findall(sum_str, ser_data, re.I)

            sum_list = []
            for i in range(len(my_list)):
                fmt = {}
                fmt['ID'] = i
                fmt['Interval'] = '%ssec' % my_list[i][0]
                fmt['Transfer'] = '%sMBytes' % my_list[i][1]
                fmt['Bandwidth'] = '%sMbits/sec' % my_list[i][2]
                
                sum_list.append(fmt.copy())
        return sum_list
        
if __name__ == '__main__':

        test = IperfThroughput()
        test.iperf_test()
