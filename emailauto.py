# -*- coding:utf-8 -*-
import itchat
from email.mime.text import MIMEText  
from email.mime.multipart import MIMEMultipart
import smtplib
import datetime
import pymysql

def connect_ueba():
	mysqlconn = pymysql.connect(
		host = 'x.x.x.x',
		port = 3306,
		user = 'xxx',
		password = 'xxx',
		database = 'ueba'
		)
	cursor = mysqlconn.cursor()
	cursor.execute("SELECT char_length(info) FROM unnormaldown ORDER BY id  DESC LIMIT 1")
	row_1 = cursor.fetchone()
    if row_1[0] == 7:
		return 1
	else:
		return 0

def sendmail(msg,subject,fromaddr,toaddrs,password):
	mail_msg = MIMEMultipart()
	if not isinstance(subject,unicode):  
    	subject = unicode(subject, 'utf-8')
	mail_msg['Subject'] = subject
	mail_msg['From'] = fromaddr
	mail_msg['To'] = ','.join(toaddrs)  
    mail_msg.attach(MIMEText(msg,_subtype='plain',_charset='utf-8'))
	try:
		s = smtplib.SMTP()  
        s.connect('zzz')
        s.login(fromaddr,password) 
        s.sendmail(fromaddr, toaddrs, mail_msg.as_string())
        s.quit()  
    except Exception,e:  
       print "Error: unable to send email"  
       print traceback.format_exc()

def wechatwarning(result):
	itchat.auto_login(enableCmdQR=2,hotReload=True)
	if result == 1:
		itchat.send(u'邮件已发送')

	else:
		itchat.send(u'请发送线上数据下载审计邮件', 'filehelper')

if __name__ == '__main__':
	fromaddr = "zzz"  
	toaddrs = ["zzz"]
	password = "zzz"
#get today & yestoday 
	today_date = datetime.datetime.now()
	yestoday_date = today_date + datetime.timedelta(days = -1)
	today = today_date.strftime('%Y-%m-%d')
	yestoday = yestoday_date.strftime('%Y-%m-%d')
	subject = "违规下载数据审计报告 " + today + " 20:00" + " - " + yestoday + " 20:00"
	msg = "审计结论：\n   1、今日审计发现sz到本地操作共0次，涉及人员0人，没有经过审批的操作共0次，涉及人员0人；\n   2、今日审计发现sftp下载数据到本地操作共0次"
	
	result == 
	if result == 1:
		sendmail(msg,subject,fromaddr,toaddrs,password)
	else:
		wechatwarning()
