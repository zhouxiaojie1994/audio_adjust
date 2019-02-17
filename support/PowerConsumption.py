#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import time
import xlrd
import xlwt
import threading

from PyQt4 import QtCore, QtGui
from ui_code import Ui_Dialog

import powermeter_ctrl

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s
		
#constant

class MyThread(threading.Thread):
	def __init__(self, func, args=()):
		threading.Thread.__init__(self)
		self.func=func
		self.args=args
		
	def getResult(self):
		return self.res
		
	def run(self):
		self.res = self.func(*self.args)


class POWER_COMSUMPTION_DUT_TEST(object):
	
	'''
		Description: For a complete test, you may use the class in powermeter.
	'''
	
	def __init__(self,com=None):
		
		self.COM=com

	def powermeter_control(self):
		
		'''
			dut+power:	com3.
			dut:		com1.
			if changing,please add something here.
		'''
		Test = powermeter_ctrl.get(self.COM)
		return Test

	def set_powermeter_mode(self,tmp_mode):
		
		'''
			0: max hold off.
			1: max hold on.
		'''
		PowerConsumption_Test=self.powermeter_control()
		PowerConsumption_Test.set_mode(tmp_mode)

	def set_powermeter_sample_rate(self,tmp_rate):
		
		'''
			The legal input: 0.1,0.25,0.5,1,2,5.
		'''
		PowerConsumption_Test=self.powermeter_control()
		PowerConsumption_Test.set_sample_rate(tmp_rate)
		if PowerConsumption_Test.get_sample_rate()==tmp_rate :
			return True
		else:
			return False

	def	get_powermeter_data(self,tmp_number):
		
		'''
			description:	tmp_number-the number of test data that you want to get. 
			return:			data[voltage,current,power].
		'''
		voltage_list		=	[]
		current_list		=	[]
		power_list			=	[]
		PowerConsumption_Test=self.powermeter_control()
		for i in range(tmp_number):
			tmp_data=PowerConsumption_Test.get_data()
			voltage_list.append(float(tmp_data[0]))
			current_list.append(float(tmp_data[1]))
			power_list.append(float(tmp_data[2]))
		return voltage_list,current_list,power_list	

# instantiation
SINGLE_TEST			=	POWER_COMSUMPTION_DUT_TEST('com1')
ALL_TEST			=	POWER_COMSUMPTION_DUT_TEST('com3')


class Dialog(QtGui.QDialog):
	
	def __init__(self, parent=None):
		
		super(Dialog, self).__init__(parent)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		
		# slot 
		self.ui.pushButton_2.clicked.connect(self.testmodel_set_factory)
		self.ui.pushButton_5.clicked.connect(self.testmodel_make_sure)
		self.ui.pushButton_4.clicked.connect(self.savesetup_set_factory)
		self.ui.toolButton.clicked.connect(self.savesetup_file_path)
		self.ui.pushButton_3.clicked.connect(self.savesetup_mske_sure)
		self.ui.pushButton.clicked.connect(self.powerconsumption_test)
		
	def testmodel_set_factory(self):
		
		self.ui.comboBox.setCurrentIndex(0)
		self.ui.comboBox_2.setCurrentIndex(0)
		self.ui.comboBox_3.setCurrentIndex(0)
		self.ui.spinBox_2.setProperty("value", 30)
		self.ui.spinBox_6.setProperty("value", 30)
		self.ui.spinBox_9.setProperty("value", 30)
		self.ui.spinBox_3.setProperty("value", 0)
		self.ui.spinBox_5.setProperty("value", 0)
		self.ui.spinBox_8.setProperty("value", 0)
		self.ui.checkBox.setChecked(True)
		self.ui.checkBox_4.setChecked(True)
		self.ui.checkBox_6.setChecked(True)
		self.ui.checkBox_2.setChecked(True)
		self.ui.checkBox_3.setChecked(True)
		self.ui.checkBox_5.setChecked(True)
	
	def testmodel_make_sure(self):
		
		# empty the list in case of wrong operation.
		SAMPLE_TIME_LIST	=	[]
		TEST_INTERVEL_LIST	=	[]
		TEST_TIMES_LIST		=	[]
		PEAK_POWER_LIST		=	[]
		AVERAGE_POWER_LIST	=	[]
		
		#get the value of element.
		SAMPLE_TIME_LIST.append(float(self.ui.comboBox.currentText()))
		SAMPLE_TIME_LIST.append(float(self.ui.comboBox_2.currentText()))
		SAMPLE_TIME_LIST.append(float(self.ui.comboBox_3.currentText()))
		TEST_INTERVEL_LIST.append(int(self.ui.spinBox_2.value()))
		TEST_INTERVEL_LIST.append(int(self.ui.spinBox_6.value()))
		TEST_INTERVEL_LIST.append(int(self.ui.spinBox_9.value()))
		TEST_TIMES_LIST.append(int(self.ui.spinBox_3.value()))
		TEST_TIMES_LIST.append(int(self.ui.spinBox_5.value()))
		TEST_TIMES_LIST.append(int(self.ui.spinBox_8.value()))	
		if self.ui.checkBox.isChecked():
			PEAK_POWER_LIST.append(1)
		else:
			PEAK_POWER_LIST.append(0)
		if self.ui.checkBox_4.isChecked():
			PEAK_POWER_LIST.append(1)
		else:
			PEAK_POWER_LIST.append(0)
		if self.ui.checkBox_6.isChecked():
			PEAK_POWER_LIST.append(1)
		else:
			PEAK_POWER_LIST.append(0)	
		if self.ui.checkBox_2.isChecked():
			AVERAGE_POWER_LIST.append(1)
		else:
			AVERAGE_POWER_LIST.append(0)
		if self.ui.checkBox_3.isChecked():
			AVERAGE_POWER_LIST.append(1)
		else:
			AVERAGE_POWER_LIST.append(0)
		if self.ui.checkBox_5.isChecked():
			AVERAGE_POWER_LIST.append(1)
		else:
			AVERAGE_POWER_LIST.append(0)
		
		return SAMPLE_TIME_LIST,TEST_INTERVEL_LIST,TEST_TIMES_LIST,PEAK_POWER_LIST,AVERAGE_POWER_LIST

	def savesetup_file_path(self):
		filename = QtGui.QFileDialog.getExistingDirectory(self,_fromUtf8('打开'),'E:/data')
		self.ui.lineEdit.setText(_fromUtf8(filename))
		
	def savesetup_set_factory(self):
		
		self.ui.lineEdit_2.setText('TL-xxx xxx_PowerConsumption')
		self.ui.lineEdit.clear()

	def savesetup_mske_sure(self):
		
		file_name=self.ui.lineEdit_2.text()
		file_path=self.ui.lineEdit.text()
		if file_name=='':
			QtGui.QMessageBox.warning(self,'WARNING','Please Input file name.',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Close)
			return
		if file_path=='':
			QtGui.QMessageBox.warning(self,'WARNING','Please Input file path.',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Close)
			return

		return file_name,file_path

	def powerconsumption_test(self):
		
		
		ini_info	=	self.testmodel_make_sure()
		save_info	=	self.savesetup_mske_sure()
		flag_info	=	[ini_info[3],ini_info[4]]
		if save_info is None:
			return
		
		testlist=seperate_list(ini_info)
		if ini_info[2][0]==1 and ini_info[2][1]==0:
			get_list=singletest(testlist[0])
			save_to_excel(1,get_list,save_info,flag_info)
		
		elif ini_info[2][0]==0 and ini_info[2][1]==1:
			get_list=alltest(testlist[1])
			save_to_excel(2,get_list,save_info)
		
		elif ini_info[2][0] and ini_info[2][1]:
			get_list=completetest(testlist[2])	
			save_to_excel_complete(flag_info,get_list,save_info)
		elif ini_info[2][2]:
			get_list=completetest(testlist[2])
			save_to_excel_complete(flag_info,get_list,save_info)
		else:
			QtGui.QMessageBox.warning(self,'WARNING','Nothing Running! please check the running times.',QtGui.QMessageBox.Ok,QtGui.QMessageBox.Close)
			return

			
def singletest(tmp_info):
	
	SINGLE_TEST.set_powermeter_sample_rate(tmp_info[0])
	sample_number=int (tmp_info[1]/tmp_info[0])
	get_list=SINGLE_TEST.get_powermeter_data(sample_number)
	return get_list
	
def alltest(tmp_info):
	
	ALL_TEST.set_powermeter_sample_rate(tmp_info[1])
	sample_number=int (tmp_info[1]/tmp_info[0])
	get_list=ALL_TEST.get_powermeter_data(sample_number)
	return get_list

def completetest(tmp_info):
	test_thread = []
	get=[]
	test_thread.append(MyThread(singletest,(tmp_info,)))
	test_thread.append(MyThread(alltest,(tmp_info,)))
	for each in test_thread:
		each.start()
	for each in test_thread:
		each.join()
		get.append(each.getResult())
	# single_list	=	get[0]
	# all_list		=	get[1]
	return get
	
def count_value(tmp_list,tmp_value):
	
	count=0
	for eachnumber in range(len(tmp_list)):
		if tmp_list[eachnumber]==tmp_value:
			count=count+1
	return count

def seperate_list(tmp_list):
	
	single=[]
	all=[]
	complete=[]
	for i in range(len(tmp_list)):
		single.append(tmp_list[i][0])
		all.append(tmp_list[i][1])
		complete.append(tmp_list[i][2])
	print single,all,complete
	return single,all,complete
	
def save_to_excel(tmp_type,tmp_datalist,tmp_info,flag):
	
	#constant
	typedict={1:'Single Test',2:'All test'}
	voltage	=tmp_datalist[0]
	current	=tmp_datalist[1]
	power	=tmp_datalist[2]
	
	#initialization
	excelbook=xlwt.Workbook()
	excelsheet=excelbook.add_sheet(typedict[tmp_type])
	excelsheet.write(0,0,"Voltage(V)")
	excelsheet.write(0,1,"Current(A)")
	excelsheet.write(0,2,"Power(W)")
	
	#add data to cell
	for row in range(len(power)):
		excelsheet.write(row+1,0,voltage[row])
		excelsheet.write(row+1,1,current[row])
		excelsheet.write(row+1,2,power[row])
	
	#data process
	excelsheet.col(4).width = 0x1400
	excelsheet.col(5).width = 0x1400
	excelsheet.col(6).width = 0x1400
	excelsheet.col(7).width = 0x1400
	if tmp_type==1:
		flag_list=[flag[0][0],flag[1][0]]
		if(flag_list[0] and flag_list[1]):
			max_power_value=max(power)
			max_power_number=count_value(power,max_power_value)
			average_power_value=sum(power)/len(power)
			excelsheet.write(4,4,'peak_value')
			excelsheet.write(4,5,max_power_value)
			excelsheet.write(4,6,'peak_value_number')
			excelsheet.write(4,7,max_power_number)
			excelsheet.write(5,4,'average_value')
			excelsheet.write(5,5,average_power_value)
		elif(flag_list[0]==1 and flag_list[1]==0):
			max_power_value=max(power)
			max_power_number=count_value(power,max_power_value)
			excelsheet.write(4,4,'peak_value')
			excelsheet.write(4,5,max_power_value)
			excelsheet.write(4,6,'peak_value_number')
			excelsheet.write(4,7,max_power_number)
		elif(flag_list[0]==0 and flag_list[1]==1):
			max_power_value=max(power)
			average_power_value=sum(power)/len(power)
			excelsheet.write(5,4,'average_value')
			excelsheet.write(5,5,average_power_value)
	elif tmp_type==2:
		flag_list=[flag[0][1],flag[1][1]]
		if(flag_list[0] and flag_list[1]):
			max_power_value=max(power)
			max_power_number=count_value(power,max_power_value)
			average_power_value=sum(power)/len(power)
			excelsheet.write(4,4,'peak_value')
			excelsheet.write(4,5,max_power_value)
			excelsheet.write(4,6,'peak_value_number')
			excelsheet.write(4,7,max_power_number)
			excelsheet.write(5,4,'average_value')
			excelsheet.write(5,5,average_power_value)
		elif(flag_list[0]==1 and flag_list[1]==0):
			max_power_value=max(power)
			max_power_number=count_value(power,max_power_value)
			excelsheet.write(4,4,'peak_value')
			excelsheet.write(4,5,max_power_value)
			excelsheet.write(4,6,'peak_value_number')
			excelsheet.write(4,7,max_power_number)
		elif(flag_list[0]==0 and flag_list[1]==1):
			max_power_value=max(power)
			average_power_value=sum(power)/len(power)
			excelsheet.write(5,4,'average_value')
			excelsheet.write(5,5,average_power_value)
			
	#save to excel
	path='%s\\%s.xls'%(tmp_info[1],tmp_info[0])
	excelbook.save(path)

def save_to_excel_complete(tmp_info,tmp_datalist,path_info):
	
	#constant
	single_voltage	=tmp_datalist[0][0]
	single_current	=tmp_datalist[0][1]
	single_power	=tmp_datalist[0][2]
	all_voltage		=tmp_datalist[1][0]
	all_current		=tmp_datalist[1][1]
	all_power		=tmp_datalist[1][2]
	
	#initialization
	excelbook=xlwt.Workbook()
	excelsheet_single=excelbook.add_sheet('single_test')
	excelsheet_all=excelbook.add_sheet('all_test')
	excelsheet_single.write(0,0,"Voltage(V)")
	excelsheet_single.write(0,1,"Current(A)")
	excelsheet_single.write(0,2,"Power(W)")
	excelsheet_all.write(0,0,"Voltage(V)")
	excelsheet_all.write(0,1,"Current(A)")
	excelsheet_all.write(0,2,"Power(W)")
	
	#add data to cell
	for row in range(len(single_power)):
		excelsheet_single.write(row+1,0,single_voltage[row])
		excelsheet_single.write(row+1,1,single_current[row])
		excelsheet_single.write(row+1,2,single_power[row])

	for rowj in range(len(all_power)):
		excelsheet_all.write(rowj+1,0,all_voltage[rowj])
		excelsheet_all.write(rowj+1,1,all_current[rowj])
		excelsheet_all.write(rowj+1,2,all_power[rowj])
	
	#data process
	excelsheet_single.col(4).width = 0x1400
	excelsheet_single.col(5).width = 0x1400
	excelsheet_single.col(6).width = 0x1400
	excelsheet_single.col(7).width = 0x1400
	excelsheet_all.col(4).width = 0x1400
	excelsheet_all.col(5).width = 0x1400
	excelsheet_all.col(6).width = 0x1400
	excelsheet_all.col(7).width = 0x1400
	if(tmp_info[0][2] and tmp_info[1][2]):
		max_power_value=max(single_power)
		max_power_number=count_value(single_power,max_power_value)
		average_power_value=sum(single_power)/len(single_power)
		excelsheet_single.write(4,4,'peak_value')
		excelsheet_single.write(4,5,max_power_value)
		excelsheet_single.write(4,6,'peak_value_number')
		excelsheet_single.write(4,7,max_power_number)
		excelsheet_single.write(5,4,'average_value')
		excelsheet_single.write(5,5,average_power_value)
		max_power_value=max(all_power)
		max_power_number=count_value(all_power,max_power_value)
		average_power_value=sum(all_power)/len(all_power)
		excelsheet_all.write(4,4,'peak_value')
		excelsheet_all.write(4,5,max_power_value)
		excelsheet_all.write(4,6,'peak_value_number')
		excelsheet_all.write(4,7,max_power_number)
		excelsheet_all.write(5,4,'average_value')
		excelsheet_all.write(5,5,average_power_value)
	elif (tmp_info[0][2]==1 and tmp_info[1][2]==0):
		max_power_value=max(single_power)
		max_power_number=count_value(single_power,max_power_value)
		excelsheet_single.write(4,4,'peak_value')
		excelsheet_single.write(4,5,max_power_value)
		excelsheet_single.write(4,6,'peak_value_number')
		excelsheet_single.write(4,7,max_power_number)
		max_power_value=max(all_power)
		max_power_number=count_value(all_power,max_power_value)
		excelsheet_all.write(4,4,'peak_value')
		excelsheet_all.write(4,5,max_power_value)
		excelsheet_all.write(4,6,'peak_value_number')
		excelsheet_all.write(4,7,max_power_number)
	elif (tmp_info[0][2]==0 and tmp_info[1][2]==1):
		max_power_value=max(single_power)
		average_power_value=sum(single_power)/len(single_power)
		excelsheet_single.write(5,4,'average_value')
		excelsheet_single.write(5,5,average_power_value)
		max_power_value=max(all_power)
		average_power_value=sum(all_power)/len(all_power)
		excelsheet_all.write(5,4,'average_value')
		excelsheet_all.write(5,5,average_power_value)		
			
	#save to excel
	path='%s\\%s.xls'%(path_info[1],path_info[0])
	excelbook.save(path)


if __name__=='__main__':
	
	app =QtGui.QApplication(sys.argv) 
	dialog = Dialog() 
	dialog.show()
	sys.exit(app.exec_())












		
# voltage_list.append(tmp_data[0])
# current_list.append(tmp_data[1])
# power_list.append(tmp_data[2])
