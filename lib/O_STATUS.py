# -*- coding: koi8-r -*-

import	os, sys
import	session
import	dbtools
from	myglobal import *

##############################################
#	Списки Вызовов

#['number', 'sector', 'profile', 'subst', 'place', 'street', 'house', 'korp', 'flat', 'pdzd', 'etj', 'pcod', 'phone', 'reasn', 'name', 'name2', 'age', 'sex', 'rept', 'kto', 't_get', 'g_disp', 't_send', 's_disp', 't_arrl', 'a_disp', 't_done', 'd_disp', 'diagn', 'diat', 'alk', 'reslt', 'kuda', 't_go', 'br_ref', 'smena', 'nbrg', 'pbrg', 'nsbrg', 'doctor', 'ps', 'c_disp', 't_close', 'cnum_total', 'id_ims', 't_wait', 't_serv', 't_hosp'] 


thead_copro = [	'N выз', 'Повод', 'П', 'ПС', 'N бриг.', 'Принят', 'Пердн', 'Прибл', 'Исплн', 'Улица', 'Дом', 'Кв']	# О.Обстановка
thead_cfind = [	'N выз', 'Повод', 'П', 'ПС', 'Принят', 'N Бриг', 'Улица', 'Дом', 'ФИО', 'лет']		# Поиск вызовов
thead_c2brg = [	'N брг', 'См.', 'П/С', 'Улица', 'Дом', 'Врач', 'Статус', 'Доезд', 'W']			# Предложение бригад
thead_dict = {	'N выз': {'c': 'number, cnum_total', 'f': 'scnumber', 'w': 50, 'a': 'right'},
		'Повод': {'c': 'reasn, sector', 'w': 50, 'a': 'right', 'f': 'sreasn'},	'Повд': {'c': 'reasn', 'w': 50, 'a': 'center'},
		'П': {'c': 'profile', 'w': 30, 'a': 'center'}, 'ПС': {'c': 'subst', 'w': 30, 'a': 'center'},
		'Принят': {'c': 't_get', 'f': 'str_time', 'w': 50, 'a': 'center'},	'Пердн': {'c': 't_send', 'f': 'str_time', 'w': 50, 'a': 'center'},
		'Прибл': {'c': 't_arrl', 'f': 'str_time', 'w': 50, 'a': 'center'},	'Исплн': {'c': 't_done', 'f': 'str_time', 'w': 50, 'a': 'center'},
		'N бриг.': {'c': 'nbrg, pbrg, ps, br_ref, number, t_get', 'f': 'ssBrigad', 'w': 80},
		'N Бриг': {'c': 'nbrg, pbrg', 'f': 'sbrigad', 'w': 60},
		'Улица': {'c': 'street', 'w': 180},	'Дом': {'c': 'house, korp'},	# 'w': 170},
		'Кв': {'c': 'flat'},
		'ФИО': {'c': 'name, name2', 'w': 140}, 'лет': {'c': 'age, sex', 'w': 50},
	#	'См.': {'c': 'smena'},	'Врач': {'c': 'doctor'}, 'Статус': {'c': 'br_ref'}, 'Доезд': {'c': 'br_ref'}, 'W': {'c': 'br_ref'},
	#	{'c': ''}, 
		}
#	WHERE t_done IS NULL ORDER BY t_send DESC, number]
##	Описание списков Вызовов (по умолчанию)
dict_callist = {'copro': {'thead': thead_copro, 'w': 820, 'order': 't_send DESC, number', 'table': 'call',
			'where': {'default': 't_done IS NULL ', 'wait': 't_send IS NULL ', 'send': 't_send > 0 AND t_done IS NULL ', 'exec':
				't_send > 0 AND t_done > 0 ', 'work': 't_get > 0'}},
		'cfind': {'thead': thead_cfind, 'w': 820, 'order': 't_get', 'table': 'calls_arch',
			'where': {'default': '(reslt IS NULL OR reslt < 90)'}},
		}

##	Описание и обработка комерческих ООО СМП.
psmp_desc = [	{'label': 'ООО СП1', 'sects': '008,009,011,012,013,014,015,016,017,113,177,188,199', 'phs': '242-03-03, 278-04-04', 'fname': 'ООО Скорая помощь'},
		{'label': 'ООО СП2', 'sects': '127,128,130,131,132,139', 'phs': '245-77-03, 245-88-03', 'fname': 'ООО Скорая помощь'},
		{'label': 'ООО МЭ-НН', 'sects': '114,115,117', 'phs': '282-03-03', 'fname': 'ООО МЕДЭСПРЕСС-НН'},
		{'label': 'ООО Романа', 'sects': '182,184', 'phs': '261-02-54, 423-91-83', 'fname': 'ООО Романа'}
		]

def	its_sooo (sector):	# "&#8593;"
	""" Проверить принадлежность Вызова зоне обслуживания ООО СМП	"""
	ss = '%03d' % sector
	for jooo in psmp_desc:
		if ss in jooo['sects']:	return	True
	return	False

def	scnumber (**kwargs):
	cnum = kwargs['number']
	cnum_total = kwargs['cnum_total']
	return	"""<a href='' onclick="alert ('CALL: %d C%04d'); return false;"><img src='/img/call.gif'> <b>%d</b></a>""" % (
			cnum_total, cnum, cnum)

def	sget_jpsans (br_ref, cnum, t_get):
	query = "SELECT * FROM journal_pst WHERE br_ref = %d AND cnum = %d AND ct_get = %d;" % (br_ref, cnum, t_get)
	drow = dboo.get_dict (query)
	if drow:
		if drow['stat'] == 1:
			return	"<span class='butt' style='color: #070'>%d</span>" % drow['jnum']
		else:	return	"<span class='butt' style='color: #a00'>%d</span>" % drow['jnum']
	return	"<span class='butt' style='color: #a00'>??</span>"

def	sreasn (**kwargs):	#reasn):
	if not kwargs.has_key('reasn'):	return	"XXX"
	global	pre_reasn
	reasn = kwargs['reasn']
	if kwargs.has_key('sector') and its_sooo (kwargs['sector']):
		preasn = '&#8593;%s' % pre_reasn
	else:	preasn = pre_reasn
	reasn_mchs =	"|12С|17М|22Р|22Т|12Р|12Д|"		# События МЧС
	reasn_add02 =	"|10Л|10Т|14С|13Д|14Д|18Д|18Р|18С|24С|"	# Противоправные дайствия
	reasn_state =	"|65Б|65Е|65К|65Р|65Т|65Ф|65Л|65П|65Н|"	# Дежурство
	reasn_first = ''.join (("|10Д|10Е|11Н|11Р|11С|13Л|13Н|14Г|14З|14И|14Р|14Ф|14Ц|15М|15Ц|15Ш|15Ю|17Д|17Ж|17О|17Р|21Д|21К|",
				"21Л|21Н|21Т|23Д|23Л|23Н|24В|24Г|24И|24М|24Р|24Ц|24Ш|24Ю|25Е|25Ж|25К|25Л|25Н|25Я|29Г|29Д|29Т|29Ц|",
				"30К|30Х|31Н|32Г|32Ж|35Д|35Е|35Т|37Т|37У|53Р|61Б|61Е|61К|61Л|61Н|61П|61Р|61Т|62Б|62К|62Н|62П|62Р|62Т|"))
	if reasn in reasn_mchs:		mark = "С"
	elif reasn in reasn_add02:	mark = "М"
	elif reasn in reasn_state:	mark = "Д"
	elif reasn in reasn_first:	mark = "*"
	else:	mark = ''
	return	"<span style='font-family: monospace;'>%s%s %s</span>" % (preasn, mark, reasn)

def	ssBrigad (**kwargs):
	if not kwargs.has_key('nbrg'):	return	""
	if kwargs.has_key('ps'):
		mark = sget_jpsans (kwargs['br_ref'], kwargs['number'], kwargs['t_get'])
		return	"<a href=''><img src='/img/brig.gif'> <b>%s</b>%s</a> %s" % (kwargs['nbrg'], kwargs['pbrg'], mark)
	else:	return  "<a href=''><img src='/img/brig.gif'> <b>%s</b>%s</a>" % (kwargs['nbrg'], kwargs['pbrg'])

def	sbrigad (**kwargs):
	if not kwargs.has_key('nbrg'):	return	""	#str(kwargs)
	return	"<a href=''><img src='/img/brig.gif'> <b>%s</b> %s</a>" % (kwargs['nbrg'], kwargs['pbrg'])

def	sbgcolor (j, place, sector, reslt):
	global	pre_reasn
	if place > 1 and place < 5:
		pre_reasn = "&copy;"
		if j % 2:	bgcolor = '#eeffaa'
		else:		bgcolor = ''
	else:
		pre_reasn = ""
		if j % 2:	bgcolor = '#ffe0e0'
		else:		bgcolor = '#fff0f0'
	return	bgcolor

def	list_calls (dcallist = 'copro', **kwargs):
	"""	Показать списки Вызовов
	kwargs: { table | where | and | order }
	"""
#	print globals()	#['request']
	global	dboo
	callist = dict_callist[dcallist]['thead']
	if kwargs.has_key('order'):
		order = kwargs['order']
	else:	order = dict_callist[dcallist]['order']
	if kwargs.has_key('table'):
		table = kwargs['table']
	else:	table = dict_callist[dcallist]['table']
	if kwargs.has_key('where'):
		if kwargs['where'].split()[0] == 'AND':
			where = ' '.join((dict_callist[dcallist]['where']['default'], kwargs['where']))
		else:	where = kwargs['where']
	else:	where = dict_callist[dcallist]['where']['default']
#	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	dboo = dbtools.dbtools ('host=127.0.0.1 dbname=b03 port=5432 user=vds')
	query = "SELECT * FROM %s WHERE %s ORDER BY %s;" % (table, where, order)
#	print query
	rows = dboo.get_rows (query)
	print "<div class='box' style='background-color: #fff;'>"
	if rows:
		rdesc = dboo.desc
		swidth = "min-width: 820px; max-width: 1000px;"
		print "<div style='padding: 2px; %s'>" % swidth
		print "<table cellpadding='0' cellspacing='0' width=100% style='padding: 0px;'><tr>"
		w = 0
		for c in callist:
			cdict = thead_dict[c]
			if cdict.has_key ('w'):
				w += cdict['w']
				print "<th width='%dpx'>%s</th>" % (cdict['w'], c),
			else:	print "<th>%s</th>" %  c,
		print "<th>&nbsp;%s</th></tr></table></div>" % w
		print "<div style='height: 320px; overflow: auto; padding: 0px; %s'>" % swidth
		print "<table id='%s' cellpadding='0' cellspacing='0' width=100%% style='padding: 0px;'>"  % table
		print "<tbody>"
		j = 0
		for r in rows:
			print "<tr id='r%06d' class='line' valign='top' bgcolor='%s'>" % (
					r[rdesc.index('cnum_total')], sbgcolor (j, r[rdesc.index('place')], r[rdesc.index('sector')], r[rdesc.index('reslt')]))
			j += 1
			for c in callist:
				cdict = thead_dict[c]
				"""
				print "<td>", cdict['c'].split(), "</td>"
				"""
				if cdict.has_key ('w'):
					if cdict.has_key ('a'):
						print "<td width='%dpx' align='%s'>" % (cdict['w'], cdict['a']),
					else:	print "<td width='%dpx'>" % cdict['w'], 
				else:	print "<td>",
				clist = cdict['c'].split(', ')
				if cdict.has_key ('f'):
					if len(clist) == 1:
						if r[rdesc.index(cdict['c'])]:
							print globals()[cdict['f']] (r[rdesc.index(cdict['c'])])
						else:   print '-:-'
					else:
						dcol = {}
						for jc in clist:
							if r[rdesc.index(jc)]:
								dcol[jc] = r[rdesc.index(jc)]
						if dcol:
							print globals()[cdict['f']] (**dcol)
						else:	print "&nbsp;"
				elif clist:
					for jc in clist:	#cdict['c'].split(', '):
						if r[rdesc.index(jc)]:
							print r[rdesc.index(jc)],
						else:	print ' &nbsp; ',
				else:	print ' nbsp ',
				print "</td>"
			print "</tr>"
		print "</tbody></table>"
	print "</div>"
	print "</div>"

def	test (request):
	global	SESSION

#	print "~main_fid|"
	print "O_STATUS.test", request
	SESSION = session.session()	#'oosmpnn7777')
	if SESSION:
		print "<pre>SESSION:", interrogate (SESSION), "\nSESSION.ssident:", SESSION.ssident, SESSION.is_new, "</pre>"
	#	SESSION.set_obj ('test_key', {'TEST': 'object'})
	#	SESSION.del_obj ('test_key')
		for k in SESSION.objpkl:	print '<dt>', k, ':</dt><dt>', SESSION.objpkl[k], "</dt>"
		sso = SESSION.start()
	#	print "<pre>SESSION interrogate:", interrogate (sso), "\nsso:", sso, interrogate (SESSION.objpkl), "</pre>"
	else:
		print "<pre>SESSION:", SESSION
		SESSION = session.session()
		print "SESSION.ssident:", SESSION.ssident
		print "</pre>"

def	disp_03 (request):
	global	SESSION
	SESSION = session.session()
#	print "~main_fid|"
	print "<div class='green'>"	# style='height: 300px; overflow: auto;'>"
	ptit_box ("Статистика диспетчера 03")
	if SESSION.objpkl.has_key('us_row'):
		us_row = SESSION.objpkl['us_row']
	#	for k in us_row:	print '<dt>', k, ':</dt><dt>', us_row[k], "</dt>"
		list_calls (where = 'AND subst IN (1,12)')
	#	list_calls ('cfind')
	print "</div>"
	print "~eval| mark_table('call');" 
	print "~debug|"

def	view_oo (request):
	global	SESSION
	SESSION = session.session()
	print "<div class='green'>"
#	print "<div>"
	ptit_box ("Оперативная Обстановка", ctime = True, cdate = True)
	if SESSION.objpkl.has_key('us_row'):
		us_row = SESSION.objpkl['us_row']
		list_calls()
	print "</div>"
	print "~eval| mark_table('call');"
	print "~debug|"

if __name__ == "__main__":
	print "a, b cd, ef".split()
#	test ({'disp': '7777', 'this': 'ajax', 'sex': '?', 'place': '1', 'main_fid': 'O_STATUS', 'pbrg': '\xd0\x9b'})
