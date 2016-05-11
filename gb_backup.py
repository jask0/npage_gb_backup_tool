import urllib.request
import urllib.parse
import parse
import configparser


config = configparser.ConfigParser()
config.read('parameter.cfg')
url = config.get('Parameter','url')
modus = config.get('Parameter','datei_schreiben')
seite = config.get('Parameter','Seiten_zahl')

if url != "":
	req = urllib.request.Request(url)
	resp = urllib.request.urlopen(req)

	respData = resp.read()

	fp = open("quellcode.html","w")
	fp.write(str(respData))
	fp.close()

fp = open("quellcode.html")
file_content = fp.read()
fp.close()

file_content = file_content.replace('\n',"")
a = parse.search("<body{}</body>", str(file_content))
b = a.fixed

c = parse.search("<b>"+seite+"</b>{}<b>"+seite+"</b>", b[0])

d = c.fixed

keys = parse.findall("""class="gb_title4">{}</td>""", d[0])
values = parse.findall("""<td class="gb_t1">{}</td>""", d[0])

list_key = []
list_value = []
for key in keys:
	s = key[0].replace("  ","")
	s = s.replace("\\n","")
	s = s.replace("<b>","")
	s = s.replace(":</b>","|")
	list_key.append(s)

for value in values:
	s = value[0].replace("  ","")
	s = s.replace("\\n","")
	s = s.replace("&nbsp;"," ")
	s = s.replace("&amp;","&")
	s = s.replace("&lt;","<")
	s = s.replace("&gt;",">")
	s = s.replace("&euro;","€")
	s = s.replace("&copy;","C")
	s = s.replace("&quot;","'")
	s = s.replace("\\xc3\\xb6","ö")
	s = s.replace("\\xc3\\x96","Ö")
	s = s.replace("\\xc3\\xbc","ü")
	s = s.replace("\\xc3\\x9c","Ü")
	s = s.replace("\\xc3\\xa4","ä")
	s = s.replace("\\xc3\\x9fe","ß")
	s = s.replace("&ouml;","ö")
	s = s.replace("&Ouml;","Ö")
	s = s.replace("&uuml;","ü")
	s = s.replace("&Uuml;","Ü")
	s = s.replace("&auml;","ä")
	s = s.replace("&Auml;","Ä")
	s = s.replace("&szlig;","ß")
	s = s.replace(";",":")
	s = s.replace('"',"'")
	list_value.append(s)

i=0	
file = open("backup.txt", modus)
for elem in list_key:
	if elem == "E-Mail|" or elem == "Homepage|":
		temp = parse.search(">{}</a>", list_value[i])
		temp2 = temp.fixed
		list_value[i] = temp2[0]
	elif(str(elem) == "Betreff|"):
		temp = list_value[i].split("gif'> ",1)
		list_value[i]= temp[1]
	elif(str(elem) == "Nachricht|"):
		try:
			src= parse.search("src='{}'",list_value[i])
			src = src.fixed
			img = parse.search('<img {}>',list_value[i])
			img = img.fixed
			old_img = '<img '+img[0]+'>'
			new_img = "<img src='"+src[0]+"' />"
			list_value[i] = list_value[i].replace(old_img, new_img)
		except:
			pass
	file.write(elem+list_value[i]+'\n')
	i+=1

file.close()
csv_file = open("backup.csv", modus)
counter = 0
line = ''
list_of_dic = []
dic = {}

for elem in list_key:
	if (str(elem) == "Name|") and (counter != 0):
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
	
	if(str(elem) == "Name|"):
		dic['Name']= list_value[counter]
	elif(str(elem) == "E-Mail|"):
		dic['E-Mail']= list_value[counter]
	elif(str(elem) == "Homepage|"):
		dic['Homepage']= list_value[counter]
	elif(str(elem) == "Kommentar|") and (list_value[counter][0].isnumeric()):
		dic['Datum']= list_value[counter]
	elif(str(elem) == "Kommentar|") and not(list_value[counter][0].isnumeric()):
		dic['Kommentar']= list_value[counter]
	elif(str(elem) == "Betreff|"):
		dic['Betreff']= list_value[counter]
	elif(str(elem) == "Nachricht|"):
		dic['Nachricht']= list_value[counter]
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
		line = '"'+dic['Name']+'";"'+dic['E-Mail']+'";"'+dic['Homepage']+'";"'+dic['Datum']+'";"'+dic['Betreff']+'";"'+dic['Nachricht']+'";"'+dic['Kommentar']+'"'
		csv_file.write(line+'\n')
csv_file.close()
print("===================================================================================")
print("Gespeicherte Einträge: "+str(len(list_of_dic)))
