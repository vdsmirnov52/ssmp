# -*- coding: koi8-r -*-

import	cgi, os, sys, time

CONF_PATHNAME = r"/home/vds/03/oopy/oopy.ini" 

BTIMER =	900000000	# смещение tm в b03
USER_TIMER =	40		# время (мин) ожидания действий оператора
SESSION =	None
if os.environ.has_key('REMOTE_ADDR'):
	REMOTE_ADDR = os.environ['REMOTE_ADDR']
else:	REMOTE_ADDR = '127.0.0.1'

img_auto =	'<i class="fa fa-ambulance fa-lg" aria-hidden="true"></i>&nbsp;'
img_call =	'<i class="fa fa-newspaper-o fa-lg" aria-hidden="true"></i>&nbsp;'
img_brig =	'<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>&nbsp;'

def	current_time ():
	return	int(time.time()) -BTIMER

def	str_date (btm, formtt = " %d/%m/%y"):	# вернуть строку дата по формату
	return	time.strftime (formtt, time.localtime(BTIMER +btm))

def	str_time (btm, formtt = " %H:%M"):	# вернуть строку время по формату
	return	time.strftime (formtt, time.localtime(BTIMER +btm))

def	get_config ():
	""" Читать файл конфигурации	"""
	if os.access (CONF_PATHNAME, os.F_OK):
		import ConfigParser
		config = ConfigParser.ConfigParser()
		config.read (CONF_PATHNAME)
		return config
	else:	print 'Отсутствует файл: ', CONF_PATHNAME, '<br />'

def	escape(s, quote = None):
        """ Замена специальных символов HTM "&", "<" и ">". Если quote == Ttue - заменить '"'. """
	s = s.replace("&", "&amp;")
	s = s.replace("<", "&lt;")
	s = s.replace(">", "&gt;")
	if quote:	s = s.replace('"', "&quot;")
	return	s
				 
def	upper_ru (strnig):
	sdn = 	'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
	sup =	'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ'
	sout = ''
	for c in strnig:
		j = sdn.find(c)
		if j >= 0:
			sout = ''.join ((sout, sup[j]))
		else:	sout = ''.join ((sout, c))
	return	sout

def	ptit_box (tit, mess='', clear='', close='', save='', ctime = False, cdate = False):
	""" Вывести заголовок блока данных	"""
	print "<div class='box'><table width='100%%'><tr><td><span class='tit'>%s</span></td><td>%s</td>" % (tit, mess)
	if ctime and cdate:
		print "<td align='center'><span class='tit'>%s</span> от <span class='tit'>%s</span></td>" % (str_time(current_time (), formtt = "%H:%M:%S"), str_date(current_time ()))
	else:
		if ctime:
			print "<td align='center'><span class='tit'>%s</span></td>" % str_time(current_time (), formtt = "%H:%M:%S")
		if cdate:
			print "<td align='center'><span class='tit'>%s</span></td>" % str_date(current_time ())
	if save:
		print """<td align='right' width='20px'><input class='butt' type='button' onclick="%s" value='Сохранить' title='Сохранить' /></td>""" % save
	if close:
		print """<td align='right' width='20px'><img src='/img/error22.png' onclick="%s" alt='Закрыть' title='Закрыть' /></td>""" % close
	if clear:
		print """<td align='right' width='20px'><img src='/img/delt2.png' onclick="$('#%s').text('');" alt='Свернуть' title='Свернуть' /></td>""" % clear
	print "</tr></table></div>"

def	interrogate (item):
	""" Распечатать полезную информацию о item."""
	if hasattr(item, '__doc__'):
		doc = getattr(item, '__doc__')
		if doc:
			doc = doc.strip()   # Remove leading/trailing whitespace.
			firstline = doc.split('\n')[0]
		else:	firstline = doc
	else:	firstline = 'Отсутствует'
	print "DOC:	", firstline
	if hasattr(item, '__name__'):
		print "\tNAME:    ", item.__name__
	if hasattr(item, '__class__'):
		print "\tCLASS:   ", item.__class__.__name__
	print "\tID:      ", id(item)
	print "\tTYPE:    ", type(item)
	print "\tVALUE:   ", repr(item)
	print "\tCALLABLE:",
	if callable(item):	print "Yes"
	else:			print "No"
"""
sname = upper_ru (request['new_sname'].strip().decode ("UTF-8").encode("KOI8-R"))
dcall =	{
	'sector': 179,
	'profile': '\xec ', 
	'subst': 9, 
	'place': 1, 
	'number': 38, 
	'street': '%s', # size="26" maxlength="22" onblur="find_street('street') button value=">>" onclick="find_street('street'); return(false)
	'house': '46', 
	'korp': None, 
	'flat': '90 ',
	'pdzd': 3, 
	'etj': 3,
	'pcod': '\xe4\xe6 ', 
	'phone': '2991947 ',
	'reasn': '26\xec', 
	'name': '\xe2\xf2\xe1\xea\xe3\xe5\xf7\xe1', 
	'name2': '\xee \xe9', 
	'age': '33 ', 
	'sex': '\xf6', 
	'g_disp': 3025, 
	't_get': 464874793,
	's_disp': 2007, 
	't_send': 464875207,
	'doctor': 70,
	'smena': None, 
	'diagn': None,
	'a_disp': 2007,
	't_arrl': 464876318, 
	'reslt': None,
	'c_disp': None,
	't_close': None,
	'd_disp': None,
	't_done': None, 
	'rept': None,
	'kuda': None,
	'nsbrg': 9,
	'pbrg': '\xe6 ', 
	'diat': None,
	'alk': None, 
	't_go': '20', 
	'br_ref': 134, 
	'kto': '2',
	'nbrg': 914,
	'ps': '5 ',
	'cnum_total': 149692, 
	'id_ims': None, 
	} 
#	['number', 'sector', 'profile', 'subst', 'place', 'street', 'house', 'korp', 'flat', 'pdzd', 'etj', 'pcod', 'phone', 'reasn', 'name', 'name2', 'age', 'sex', 'rept', 'kto',
#	't_get', 'g_disp', 't_send', 's_disp', 't_arrl', 'a_disp', 't_done', 'd_disp',
#	'diagn', 'diat', 'alk', 'reslt', 'kuda', 't_go', 'br_ref', 'smena', 'nbrg', 'pbrg', 'nsbrg', 'doctor', 'ps', 'c_disp', 't_close', 'cnum_total', 'id_ims'] 
"""
if __name__ == "__main__":
	ptit_box ("Опрос", "формирование повода вызова", clear= "main_fid", close= "alert('Close')")
	"""
	interrogate (interrogate)
	interrogate (upper_ru)
	interrogate (qset_ustimer)
	print int(time.time())
	print current_time ()
	print str_date(current_time ())
	print time.localtime(current_time ())
	"""
