from PyQt5 import QtGui, QtWidgets, QtCore
from bs4 import BeautifulSoup as bsoup
import urllib.request, urllib.parse
import sys, os, requests, parse
import threading
import sqlite3
import bt_gui

#############################################################
################ Globale Variablen ##########################
#############################################################
# liste aller zu durchsuchenden URLs
quellen = ""	
source = "internet"
bauckasten = "npage"
# Warnung wenn keine gueltigen quellen angegeben werden	
errorInfo = "Es wurden keine Backup-Quellen angegeben!"	
# database backup connection and cursor	
db_name = "gb_backup.db"
conn = None
cursor = None
#############################################################

def create_db():
	global cursor, conn, db_name
	#os.remove("gb_backup.db")
	if ".db" not in db_name:
		db_name += ".db"
	conn = sqlite3.connect(db_name)
	cursor = conn.cursor()
	cursor.execute("""CREATE TABLE IF NOT EXISTS gb_backup (
						id INTEGER PRIMARY KEY,
						name TEXT,
						e_mail TEXT,
						homepage TEXT,
						datum TEXT,
						betreff TEXT,
						nachricht TEXT,
						kommentar TEXT);""")
	conn.commit()	
class App(QtWidgets.QMainWindow, bt_gui.Ui_MainWindow):
	def __init__(self, parent=None):
		super(App, self).__init__(parent)
		self.setupUi(self)
		self.acBeenden()
		self.acStart()
		self.pStart()
		self.acInternet()
		self.acLokal()
		self.acNPage()
		self.acWebhostel()
		self.actionAnleitung.triggered.connect(self.showAnleitung)
		self.actionAbout.triggered.connect(self.showAbout)
		self.toolButton.clicked.connect(self.btnTool)
		self.lineEdit.textChanged.connect(self.changeDbName)
	
	def changeDbName(self):
		global db_name
		db_name = self.lineEdit.text()
	
	def btnTool(self):
		global db_name
		db_name = QtWidgets.QFileDialog.getOpenFileName(self, "Wahle Datei")[0]
		self.lineEdit.setText(db_name)
		
	def showAnleitung(self):
		Anleitung = """Back-up-Quellen können Webseiten oder lokale Text/HTML-Datein sein. Um die Back-up-Quelle zu ändern, geht man auf den Reiter "Back-up Quelle" und wählt eine Quelle aus. Alle Quellen müssen einzeln angegeben werden und mit dem Separator ";" (Semikolon) getrennt werden.

Das Programm kann GB Back-ups von zwei Baukastenanbietern machen (nPage und Web-Hoste). Um den Anbieter zu wechseln, geht man auf den Reiter "Baukasten" und wählt entsprechend aus.

Ein Klick auf den Knopf "Back-up starten" aktiviert die Sicherung."""
		QtWidgets.QMessageBox.information(self, "Anleitung!", Anleitung)
	
	def	 showAbout(self):
		About_us = """Entwickelt von http://www.jaskoscript.net
Support für das Tool gibt es im Webmasterforum http://homepagehelfer.org!

Version 2.1 beta"""
		QtWidgets.QMessageBox.information(self, "Anleitung!", About_us)
		
	def acNPage(self):
		self.actionNPage.triggered.connect(self.changeBauckastenNPage)
		
	def acWebhostel(self):
		self.actionWebHostel.triggered.connect(self.changeBauckastenWebhostel)
		
	def acLokal(self):
		self.actionLokal.triggered.connect(self.changeSourceLokal)
	
	def acInternet(self):
		self.actionInternet.triggered.connect(self.changeSourceInternet)
	
	def changeSourceInternet(self, state):
		global source
		if state == True:
			source = "internet"
			self.actionInternet.setEnabled(False)
			self.actionLokal.setEnabled(True)
			self.actionLokal.setChecked(False)
	
	def changeSourceLokal(self, state):
		global source
		if state == True:
			source = "lokal"
			self.actionLokal.setEnabled(False)
			self.actionInternet.setEnabled(True)
			self.actionInternet.setChecked(False)
	
	def changeBauckastenNPage(self, state):
		global bauckasten
		if state == True:
			bauckasten = "npage"
			self.actionNPage.setEnabled(False)
			self.actionWebHostel.setEnabled(True)
			self.actionWebHostel.setChecked(False)
	
	def changeBauckastenWebhostel(self, state):
		global bauckasten
		if state == True:
			bauckasten = "webhostel"
			self.actionWebHostel.setEnabled(False)
			self.actionNPage.setEnabled(True)
			self.actionNPage.setChecked(False)
			
	def acBeenden(self):
		self.actionBeenden.triggered.connect(self.close_application)
	
	def acStart(self):
		self.actionStart.triggered.connect(self.backup_start_thread)
		
	def close_application(self):
		sys.exit()
	
	def pStart(self):
		self.pushStart.clicked.connect(self.backup_start_thread)
	
	def backup_start_thread(self):
		t = threading.Thread(target=self.backup_start)
		self.pushStart.setEnabled(False)
		t.start()
		
	# Anzeigefunktion
	def backup_start(self):
		global quellen, errorInfo, source, bauckasten
		quellen = self.plainTextEdit.toPlainText()
		self.plainTextEdit.setPlainText("Backup gestartet -->>")
		quellen = str(quellen).split(";")
		for i in range(len(quellen)):
			quellen[i] = quellen[i].replace('\n','')
			quellen[i] = quellen[i].replace(' ','')
		
		if len(quellen) == 1 and quellen[0] == '':
			QtWidgets.QMessageBox.warning(self, "Fehler!", errorInfo)
			return 0
		if source == "internet":
			for url_ in quellen:
				if "http://" and "." not in url_:
					if "https://" and "." not in url_:
						errorInfo = "Dieser Eintrag '%s' ist keine gültige URL!" % url_
						QtWidgets.QMessageBox.warning(self, "Fehler!", errorInfo)
						return 0
				if "@" in url_:
					errorInfo = "Dieser Eintrag '%s' ist keine gültige URL!" % url_
					QtWidgets.QMessageBox.warning(self, "Fehler!", errorInfo)
					return 0
		
		create_db()
		self.main_backup()
		
	def main_backup(self):
		global quellen, source, bauckasten
		global cursor, conn
		new_quellen = quellen
		if source == "internet":
			new_quellen = []
			i = 0
			for url in quellen:
				resp = requests.get(url)
				respData = resp.content
				
				dateiname = "quellcode_"+str(i)+".html"
				fp = open(dateiname,"w")
				fp.write(str(respData))
				fp.close()
				new_quellen.append(dateiname)
				i+=1

		seite = 1
		counter = 0
		line = ''
		dic = {}
		for quelle in new_quellen:
			fp = open(quelle)
			file_content = fp.read()
			fp.close()
			

			file_content = file_content.replace('  ',"")
			file_content = file_content.replace('\\n',"")
			file_content = file_content.replace('\\r',"")
			file_content = file_content.replace('\\t',"")
			file_content = file_content.replace("&nbsp;"," ")
			file_content = file_content.replace("&amp;","&")
			file_content = file_content.replace("&lt;","<")
			file_content = file_content.replace("&gt;",">")
			file_content = file_content.replace("&euro;","€")
			file_content = file_content.replace("&copy;","C")
			file_content = file_content.replace("&quot;","'")
			file_content = file_content.replace("\\xc3\\xb6","ö")
			file_content = file_content.replace("\\xc3\\x96","Ö")
			file_content = file_content.replace("\\xc3\\xbc","ü")
			file_content = file_content.replace("\\xfc","ü")
			file_content = file_content.replace("\\xc3\\x9c","Ü")
			file_content = file_content.replace("\\xdc","Ü")
			file_content = file_content.replace("\\xc3\\xa4","ä")
			file_content = file_content.replace("\\xe4","ä")
			file_content = file_content.replace("\\xc3\\x9fe","ß")
			file_content = file_content.replace("&ouml;","ö")
			file_content = file_content.replace("&Ouml;","Ö")
			file_content = file_content.replace("&uuml;","ü")
			file_content = file_content.replace("&Uuml;","Ü")
			file_content = file_content.replace("&auml;","ä")
			file_content = file_content.replace("&Auml;","Ä")
			file_content = file_content.replace("&szlig;","ß")
			file_content = file_content.replace(";",":")
			
			soup = bsoup(file_content, "html.parser")

			if bauckasten == "webhostel":
				keys = soup.find_all("td", {"width":"79"})
				values = soup.find_all("td", {"width":"315"})
			elif bauckasten == "npage":
				keys = soup.find_all("td", {"class":"gb_title4"})
				values = soup.find_all("td", {"class":"gb_t1"})
			
			step = len(values)-len(keys)
			values_list = []
			for i in range(step, len(values)):
				values_list.append(values[i])
			
			list_of_dic = []
			for elem in keys:
				elem = elem.text.strip()
				if (str(elem) == "Name:") and (counter != 0):
					if not 'E-Mail' in dic:
						dic['E-Mail']=''
					if not 'Homepage' in dic:
						dic['Homepage']=''
					if not 'Betreff' in dic:
						dic['Betreff']=''
					if not 'Kommentar' in dic:
						dic['Kommentar']=''
					if not 'Name' in dic:
						dic['Name']=''
					list_of_dic.append(dic)
					dic={}
				
				temp_value = values_list[counter].text.strip()
				if temp_value == '':
					temp_value = ' '
				if(str(elem) == "Name:"):
					dic['Name']= temp_value
				elif(str(elem) == "E-Mail:"):
					dic['E-Mail']= temp_value
				elif(str(elem) == "Homepage:"):
					dic['Homepage']= temp_value
				elif((str(elem) == "Kommentar:") and (temp_value[0].isnumeric()) or str(elem) == "Datum, Zeit:"):
					dic['Datum']= temp_value
				elif(str(elem) == "Kommentar:") and not(temp_value[0].isnumeric()):
					dic['Kommentar']= temp_value
				elif(str(elem) == "Betreff:"):
					dic['Betreff']= temp_value
				elif(str(elem) == "Nachricht:"):
					links = values_list[counter].find_all("a")
					temp_str = ""
					for link in links:
						img = link.find_all("img")
						if len(img) > 0:
							temp_str += ("<a href='%s' target='_blank'><img src='%s' /></a>"%(link.get("href"),img[0].get("src")))
						else:
							temp_str += ("<a href='%s' target='_blank'>%s</a>"%(link.get("href"),link.text))
					if len(temp_value+temp_str) > 0:
						dic['Nachricht']= temp_value+temp_str
					else:
						dic['Nachricht']= "Hallo Welt!"
				counter += 1
			if not 'E-Mail' in dic:
				dic['E-Mail']=''
			if not 'Homepage' in dic:
				dic['Homepage']=''
			if not 'Betreff' in dic:
				dic['Betreff']=''
			if not 'Kommentar' in dic:
				dic['Kommentar']=''
			if not 'Name' in dic:
				dic['Name']=''
			list_of_dic.append(dic)
				
			for dic in list_of_dic:
				if 'Nachricht' in dic:
					cursor.execute("INSERT INTO gb_backup (name,e_mail,homepage,datum, betreff, nachricht, kommentar) VALUES(?,?,?,?,?,?,?)",
									(dic['Name'], dic['E-Mail'], dic['Homepage'], dic['Datum'], 
									dic['Betreff'], dic['Nachricht'], dic['Kommentar']))
					conn.commit()
			seite += 1
			counter = 0
		self.plainTextEdit.setPlainText("")
		self.plainTextEdit.appendPlainText("=================================================================")
		self.plainTextEdit.appendPlainText("Backup abgeschloßen")
		self.pushStart.setEnabled(True)
		cursor.close()
		conn.close()
		if source == "internet":
			for quelle in new_quellen:
				os.remove(quelle)
	
app = QtWidgets.QApplication(sys.argv)
form = App()
form.show()
app.exec_()
