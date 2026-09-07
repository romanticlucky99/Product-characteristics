#!/usr/bin/env python3
# https://www.geeksforgeeks.org/xml-parsing-python/
# good rus manual:
# https://rtfm.co.ua/ru/python-rabota-s-xml-fajlami-i-modul-xml-etree-elementtree/
# of.manual
# https://docs.python.org/3/library/xml.etree.elementtree.html

import xml.etree.ElementTree as ET

#xmlFile = 'test.xml'
xmlFile = 'products_feed.xml'
userFile = 'custom_category.txt'
excSearchList = ['Ширина (мм)',
                 'Длина (мм)',
                 'Высота (мм)',
                 'Размеры прибора',
                 'Длина',
                 'Вес',
                 'Глубина',
                 'Ширина',
                 'Частота',
                 'Высота',
               
                 'Класс качества',
               
                 'Название прайс-листа',
                 'Состояние',
                 'Застосування']

# Выбор пользователя: available = 'true' или обработать ВСЕ
userInputAvail = input('Обработать: available="true" <a> или ВСЕ записи <any>? ')

# Выбор пользователя: использовать ЗАДАННЫЙ список категорий из файла 'userFile' или обработать ВСЕ
userInputCustom = input('Использовать ЗАДАННЫЙ список категорий <c> или обработать все <any>? ')
if userInputCustom == 'c' or userInputCustom == 'C':
	userFileList = []
	try:
		with open(userFile, 'r') as file:
			for line in file:
				if line != '\n':							# не пишем пустые строки
					userFileList.append(line.strip())		# .strip() убирает '\n'
	except FileNotFoundError:
		userInputCustom = ''								# пользовательский файл не найден: обнуляем результат ввода пользователя
		userInputCustomError = input('user file not found. Proceed full data proceccing <y> or Exit <any>? ')
		if userInputCustomError != 'y' and userInputCustomError != 'Y':
			quit()
	#print(userFileList)						# debug
#aaa = input('Stop_user_2')						# debug

# Парсинг xmlFile
tree = ET.parse(xmlFile)									# create element tree object
root = tree.getroot()										# get root element

# Формируем СЛОВАРЬ 'category' вида: {'228876731': 'Сумки, рюкзаки', '241663770': 'Для весов', ...}
categoryDict = {}
if userInputCustom == 'c' or userInputCustom == 'C':		# используем ЗАДАННЫЙ список категорий из файла 'userFile'
	for userCatID in userFileList:
		findItem = f"./shop/categories/category[@id='{userCatID}']"
		for item in root.findall(findItem):
			categoryDict.update({item.attrib['id']: item.text})
else:														# иначе берем ВСЕ категории из 'xmlFile'
	for item in root.findall('./shop/categories/category'):
		categoryDict.update({item.attrib['id']: item.text})
#print(categoryDict)							# debug
#aaa = input('Stop_0')							# debug

# Формируем СПИСОК 'offer'-ов вида:
#  [{'avail': 'true', 'catID': '10577669', 'name': 'Комплект для...', 'vendor': 'BiTEK', 'vendorCode': '7493',
#    'param': {'Максимальное значение нагрузки': '350', 'Материал корпуса': 'Алюминий', 'Назначение': 'Датчик веса'}}
offersList = []
for item in root.findall('./shop/offers/offer'):
	offerAvail = item.attrib['available']
	if userInputAvail == 'a' or userInputAvail == 'A':
		expAvail = f"\'{offerAvail}\' == 'true'"			# обрабатываем только записи <offer id="xxx" available="true">
	else:
		expAvail = f"\'{offerAvail}\' == 'true' or \'{offerAvail}\' == 'false'"	# обрабатываем все записи <offer ...>
	#print(expAvail)							# debug
	#aaa = input('Stop_user_1')					# debug
	if eval(expAvail):
		offerCatID = item.find('categoryId').text
		#print(offerCatID)						# debug
		offerName = item.find('name').text
		#print(offerName)						# debug
		try:
			offerVendor = item.find('vendor').text			# тэга 'vendor' может не быть
		except AttributeError:
			offerVendor = 'NULL'
		#print(offerVendor)						# debug
		offerVendorCode = item.find('vendorCode').text
		#print(offerVendorCode)					# debug
		paramDict = {}
		for item2 in item.findall('param'):					# разбор 'param'-ов
			if item2.attrib['name'] not in excSearchList:	# не берем 'param'-ы из списка Исключений
				paramDict.update({item2.attrib['name']: item2.text})
		offersList.append({'avail':offerAvail,
		                   'catID':offerCatID,
		                   'name':offerName,
		                   'vendor':offerVendor,
		                   'vendorCode':offerVendorCode,
		                   'param':paramDict})
		#aaa = input('STOP')					# debug
#for i in offersList: print(i)					# debug
#print('Length offersList:', len(offersList))	# debug

for catID in categoryDict.keys():							# перебор Номеров Категорий
	#print(catID, categoryDict[catID])			# debug
	catIDList = []											# список offer-ов одной Категории
	paramList = []											# список наименований (ключей) всех param-ов для одной Категории (+ ДУБЛИКАТЫ)
	for i in offersList:									# поиск по Номеру Категории по всем записям (like grep по файлам)
		if i['catID'] == catID:
			catIDList.append(i)
			#print(i)							# debug
			paramList.extend(list(i['param'].keys()))		# ['Максимальное значение нагрузки', 'Материал корпуса', 'Назначение']
			#print(list(i['param'].keys()))		# debug
		#aaa = input('Stop_1')					# debug
	#for z in catIDList: print(z)				# debug
	paramSet = set(paramList)								# получаем Множество вместо списка: убираем дубликаты param-ов
	#print(paramSet)							# debug
	paramList = list(paramSet)								# получаем Список вместо множества
	paramList.sort()										# сортируем список param-ов в алфавитном порядке
	#print(paramList)							# debug
	#aaa = input('Stop_2')						# debug

	# Готовим строки для записи в csv-файл
	csvCatNameStr = 'CategoryName'
	csvVendorCodeStr = 'VendorCode'
	csvVendorStr = 'Vendor'
	csvNameStr = 'Name'
	csvParamList = []
	lenCatIDList = len(catIDList)							# кол-во элементов в данной категории
	lenParamList = len(paramList)							# общее кол-во параметров для всех элементов в данной категории
	print(f'Кол-во элементов в категории "{catID} / {categoryDict[catID]}":', lenCatIDList,
	      ';  кол-во параметров:', lenParamList)			# информация для пользователя
	if lenCatIDList > 0 and len(paramList) == 0:			# если у элементов все параметры попали в исключения 'excSearchList'
		paramList.append('NO_PARAMS')
	for param in paramList:
		csvParam = param
		#print('-----param:', param)			# debug
		for Id in catIDList:
			#print('--Id:', Id)					# debug
			if lenCatIDList != 0:							# выполняем столько раз, сколько имеется элементов в данной категории
				csvCatNameStr = csvCatNameStr + '::' + categoryDict[Id['catID']]	#! CategoryName::Фонари полицейские::Фонари полицейские
				csvVendorCodeStr = csvVendorCodeStr + '::' + Id['vendorCode']		#! VendorCode::9535::6458
				csvVendorStr = csvVendorStr + '::' + Id['vendor']					#! Vendor::Imice и Estone::iMICE
				csvNameStr = csvNameStr + '::' + Id['name']							#! Name::Фонарь полицейский Bailong BL-1812-T6::Фонарь ...
				lenCatIDList -= 1
			if param in Id['param'].keys():
				try:
					csvParam = csvParam + '::' + Id['param'][param]
				except TypeError:
					csvParam = csvParam + '::NONE'
				#print('--csvParam:', csvParam)	# debug
			else:
				csvParam = csvParam + '::NULL'
				#print('--csvParam:', csvParam)	# debug
			#aaa = input('Stop_3')				# debug
		csvParamList.append(csvParam)												#! Список 'param'-ов
		#aaa = input('Stop_4')					# debug

	# Пишем результаты в csv-файл
	#print('-----')								# debug
	#print(csvCatNameStr)						# debug
	#print(csvVendorCodeStr)					# debug
	#print(csvVendorStr)						# debug
	#print(csvNameStr)							# debug
	#for param in csvParamList: print(param)	# debug
	if len(catIDList) > 0:									# пишем в файл, если категория не пустая
		csvFileName = f'file_{catID}.csv'
		with open(csvFileName, 'a', encoding="utf-8") as csvFile:
			csvFile.write(csvCatNameStr + '\n'
			            + csvVendorCodeStr + '\n'
			            + csvVendorStr + '\n'
			            + csvNameStr + '\n')
			for param in csvParamList: csvFile.write(param + '\n')
	#aaa = input('Stop_5')						# debug
