# -*- coding: utf-8 -*-
"""	Отображение, Обработка и Управление Вызовами
	$Id: call_handling.py 54 2014-09-26 14:00:32Z vds $
"""

import	os, sys, time
import	session
import	dbtools
from	myglobal import *

######################################################################
#	Прием вызова

def	srs_buttons (lst):
	ss = []
	for n in lst:
		ss.append ("<input type='button' class='butt' value='%02d' onclick='document.mainForm.reslt.value=%d;' />" % (n, n))
	return	"".join(ss)

def	sds_buttons ():
	dsbutton  = (56, 99, 106, 124, 138, 162)	# быстрые диагнозы (DS)
	ss = []
	for n in dsbutton:
		ss.append ("<input type='button' class='butt' value='%03d' onclick=\"document.mainForm.diagn.value=%d; set_DS('diagn');\" />" % (n, n))
	return	"".join(ss)

values_name =	('place','street','house','korp','flat','pdzd','etj','pcod','phone','profile','pbrg','kto','sector', 'subst', 'message_text',
		'diagn','diat','diat2','reslt','rem_reasn','refuse','name','name2','age','sex','kuda','kudat')
dict_currval = {}	# Переменные текущего вызова

def	assign_values (dict_local, dict_glob = {}, vlist = values_name, none = ''):
	for k in values_name:
		if dict_local.has_key(k):
			dict_currval[k] = dict_local[k]
		else:	dict_currval[k] = none
#	dict_currval = dict_glob
	return	dict_currval

def	sinput (name, adict, val = '', sep = ''):
	""" Формирование строки описания полей ввода <input ... />
	name	- Название поля ввода
	adict	- Описатель поля ввода {'label': ..., 'size': ..., 'type': ..., 'on': ... }
		on =	дествие (например onclick ...)
	val	- Значение поля ввода
	sep	- Формат представления я данных
	"""
	ftype = sres = ''
	if adict.has_key('label'):
		label = adict['label'].strip() +':'
	else:	label = ''
	if adict.has_key('size'):
		size = int (adict['size'])
		ftype = 'it'
	else:	size = 0
	if adict.has_key('type'):
		ftype = adict['type']
	if adict.has_key('on'):
		son = adict['on']
	else:	son = ''

	if ftype == 'it':
		if size:
			ssize = "size='%d' maxlength='%d'" % ((size*8/10), size)
		else:	ssize = ""
		if not val:
			val = upper_ru (dict_currval [name].strip())	#.decode ("UTF-8").encode("KOI8-R"))
		sres = "%s%s<input type='text' name='%s' value='%s' %s %s />" % (label, sep, name, val, ssize, son)
	elif ftype == 'button':
		sres = "<input type='button' class='butt' value='%s' %s />" % (label[0:len(label) -1], son)
	if adict.has_key('rem'):
		if sres:	sres += adict['rem']
		else:		sres = "%s%s%s" % (label, sep, adict['rem'])
	if sres:	return	sres
	else:		return	str(adict)

def	sselect (dboo, dict, kval = ''):
	""" Формировать селектор
	dict =	{'tab': 'tname', 'key': '...', 'val': '...'[, 'sname': 'sname', 'order': '...', 'on': '...', 'knull': 'text', 'where': '...']}
		sname =	имя селектора (иначе sname = tname)
		on =	действие (например onclick ...)
		knull =	добавить строку: <option value=''> text </option>"
	kval =	значение ключа (selected)
	"""
	if not (dict.has_key('tab') and dict['tab'] and dict.has_key('key') and dict['key'] and dict.has_key('val') and dict['val']):	return
	if dict.has_key('order') and dict['order']:
		order = "ORDER BY %s" % dict['order']
	else:	order = "ORDER BY %s" % dict['key']
	if dict.has_key('where') and dict['where']:
		where = "WHERE %s" % dict['where']
	else:	where = ''
	query = "SELECT %s, %s FROM %s %s %s;" % (dict['key'], dict['val'], dict['tab'], where, order)
	rows = dboo.get_rows (query)
	if not rows:	return
	ss = []
	if dict.has_key('sname') and dict['sname']:
		sname = dict['sname']
	else:	sname = dict['tab']
	if dict.has_key('on'):
		son = dict['on']
	else:	son = ''
	ss.append ("<select name='%s' %s>" % (sname, son))
	if dict.has_key('knull'):
		ss.append ("<option value=''> %s </option>" % dict['knull'])
	for r in rows:
		if str(kval).strip() == str(r[0]).strip():
			sltd = 'selected'
		else:	sltd = ''
		ss.append("<option value='%s' %s> %s %s </option>" % (str(r[0]).strip(), sltd, str(r[0]), ' '.join(r[1:])))
	ss.append("</select>")
	return	"\n".join(ss)

def	ssex (val = ''):
	sk = ['?', 'М', 'Ж']
	ss = []
	if val:		val = upper_ru (val)	#.decode ("UTF-8").encode("KOI8-R"))
	ss.append ("<select name='sex' >")
	for key in sk:
		if key == val:
			sltd = 'selected'
		else:	sltd = ''
		ss.append("<option value='%s' %s> %s </option>" % (key, sltd, key))
	ss.append("</select>")
	return	"\n".join(ss)

#				label	type	size, maxlength
cproto = {
		'number': (	'N&ordm;', '%dh',	"calls['number']"),
		't_get': (	'Принят', 'dtime',	"calls['t_get']"),	# Передан Прибыл Исполнен
	#	'rem_reasn': { 'label':	'Прим.', 'size': 32},
		'proto': (	None, '%sh',	0, 255	),
	#	't_c2uvd'	"systime()",
	#	'w_c2uvd':	"us_row['disp']",
	#	'rem_c2uvd': (	'%s',   32, 32	)
		}
dictin = 	{
		'rem_reasn':	{'label': 'Прим.',	'size': 32},
		'street':	{'label': 'Улица',	'size': 32, 'on': "onblur=\"find_street('street');\"",
			'rem': "<input type='button' class='butt' value='&gt;' onclick=\"find_street('street'); return false;\" /><span id='rem_street' class='butt'>RS</span>"},
		'house':	{'label': 'Дом',	'size': 5},
		'korp':		{'label': 'Корп.',	'size': 11},
		'flat':		{'label': 'Кв.',	'size': 5},
		'pdzd':		{'label': 'Пд.',	'size': 3, 'on': "onkeypress='return intkey(event)'"},
		'etj':		{'label': 'Эт.',	'size': 3, 'on': "onkeypress='return intkey(event)'"},
		'pcod':		{'label': 'Код',	'size': 5},
		'phone':	{'label': 'Тл.',	'size': 15},
		'name':		{'label': 'Фамил',	'size': 22},
		'name2':	{'label': 'И.О.',	'size': 22},
		'age':		{'label': 'Лет',	'size': 4},
		'reslt':	{'label': 'Резулт.'},
		'message_text':	{'label': 'Прим.',	'size': 48},
		'diagn':	{'label': 'DS',	'size': 53, 'on': "onkeypress='return intkey(event)' onblur=\"set_DS('diagn');\"",
			'rem': "<input type='button' class='butt' value='&gt;' onclick=\"set_DS('diagn'); return false;\" />"},
		'diat':		{'label': 'Осл.',	'size': 53, 'on': "onblur=\"set_DS('diat');\"",
			'rem': "<input type='button' class='butt' value='&gt;' onclick=\"set_DS('diat'); return false;\" >"},
		'diat2':	{'label': 'Текст',	'size': 32},
		'kuda':		{'label': 'Куда',	'size': 26, 'on': "onblur=\"find_street('kuda');\"",
			'rem': "<input type='button' class='butt' value='&gt;' onclick=\"find_street('kuda'); return false;\" />"},
		'kudat':	{'label': '',	'size': 22},
		'sector':	{'label': '&nbsp;Сект.',	'size': 3, 'rem': "<span id='rem_sect' class='butt'>rem_sect</span>"},
		}

def	new_call_refuse (dboo, request):
	print "new_call_refuse<pre>"
	for k in request:
		print k, request[k]
	print "</pre>"

values_string = ('street','house','korp','flat','pcod','phone','profile','pbrg','name','name2','age','sex','kto','kuda','diat')
values_func =	('diagn', 'diat','diat2')
values_cproto =	('stack', 'rem_reasn')

####	'message_text' => ???

def	new_call_save (dboo, request):
	try:
	#	print "new_call_save<pre>"
		assign_values (request)
		if not (request.has_key('reasn') and request.has_key('place') and request.has_key('street') and request.has_key('subst')):
			for k in request:
				print k, request[k]
				return
		jccol = []	# ['number', 't_get', 'cnum_total']
		jcval = []	# [str(12345), str(curr_tm), str(654321)]
		jpcol = []	# ['number', 't_get', 'proto']
		jpval = []	# [str(12345), str(curr_tm), request['stack']]
		for k in dict_currval:
			if request.has_key(k):
				if k in ('diat2', 'kudat', 'message_text'):	continue
				if k in values_cproto:
					jpcol.append(k)
					jpval.append("'%s'" % upper_ru (request[k].strip()))	#.decode ("UTF-8").encode("KOI8-R")))
					continue
				if k == 'diat':
					jccol.append('diat')
					if request.has_key('diat2') and request['diat2'] != '':
						dst = "+%s %s" % (request['diat'][0:3], upper_ru (request['diat2'].strip()))	#.decode ("UTF-8").encode("KOI8-R")))
					else:	dst = "+%s" % request['diat'][0:3]
					jcval.append("'%s'" % dst[0:32])
					continue
				if k == 'kuda':
					jccol.append('kuda')
					kuda = upper_ru (request['kuda'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
					if request.has_key('kudat') and request['kudat'] != '':
						sku = "%s & %s" % (kuda, upper_ru (request['kudat'].strip()))	#.decode ("UTF-8").encode("KOI8-R")))
					else:	sku = kuda
					jcval.append("'%s'" % sku[0:32])
					continue
				jccol.append(k)
				if k in values_string:
					jcval.append("'%s'" % upper_ru (request[k].strip()))	#.decode ("UTF-8").encode("KOI8-R")))
				elif k in values_func:
					if k == 'diagn':
						jcval.append(request[k][0:3])
				else:
					jcval.append("%s" % request[k])
					if k == 'subst':
						ssubst = request[k]
						jccol.append('nsbrg')
						jcval.append("%s" % request[k])
		curr_tm = current_time ()
		scname = ','.join(jccol)
		scval = ','.join(jcval)
		jpcol.append('proto')
		if request.has_key('stack') and request['stack'].strip() != '':
			jpval.append("'%s'" % request['stack'].strip())
		elif request.has_key('reasn_comment') and request['reasn_comment'] != '':
			jpval.append("'reasn_comment'")
		else:	jpval.append("NULL")
		reasn = upper_ru (request['reasn'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
		dboo.print_error = 0	# отменить печать ошибок
		cnumber = insert_into_call (dboo, scname, scval, request['disp'], curr_tm, reasn)
		if cnumber:
			lquery = []
			if request.has_key('stack') and request['stack'][0] == 'N':
				node, tmm = request['stack'].strip().split(':')
				lquery.append ("UPDATE ccomment SET cnum = %d, t_get = %d WHERE tmm = %s;" %(cnumber, curr_tm, tmm))
			lquery.append ("INSERT INTO c_proto (number, t_get, %s) VALUES (%d, %d, %s);" % (','.join(jpcol), cnumber, curr_tm, ','.join(jpval)))
			lquery.append ("INSERT INTO events (subst, cnum, cod, timer) VALUES (%s, %d, 11, %d);" % (ssubst, cnumber, curr_tm))
			'''
			query = """INSERT INTO c_proto (number, t_get, %s) VALUES (%d, %d, %s);
				INSERT INTO events (subst, cnum, cod, timer) VALUES (%s, %d, 11, %d);""" % (
					','.join(jpcol), cnumber, curr_tm, ','.join(jpval), ssubst, cnumber, curr_tm)
			'''
			###	- если повторнеый вызов зафиксировать его в \b second_call
			#"	INSERT INTO second_call VALUES (%d,%d,%d,%d);	(cnumber, curr_tm, prim_cnumber, prim_tget)
			query = "\n".join (lquery)
			print "<pre>", query, "</pre>"
			if dboo.qexecute (query):
				ins_transact_log (dboo, query, request['disp'], "+ c_proto, events, [second_call]", 0, cnumber, curr_tm)
	#	print "</pre>"
		return	cnumber, curr_tm
	except:
		exc_type, exc_value = sys.exc_info()[:2]	# .replace('<', '"').replace('>'
		print "<span class='tit' style='color: #a00;'> new_call_save:", exc_type, exc_value, "</span>"

def	get_last_number (dboo, query):
	print "<br>", query
	dr = dboo.get_dict (query)
	if dr:
		return	dr['cnumber']
	return	0

def	insert_into_call (dboo, scname, scval, disp, curr_tm, reasn):
	cnum_total = get_last_number (dboo, "SELECT nextval ('new_total_call_number') AS cnumber")
	if not cnum_total:	return	False
	for j in range (10):
		if j < 8:
			qsv = "SELECT setval ('new_call_number', (SELECT 1+ max(number) FROM call WHERE number < (SELECT max(number)-count(number) FROM call)));"
		else:	qsv = "SELECT setval ('new_call_number', (SELECT max(number) FROM call));"
		cnum = get_last_number (dboo, "BEGIN WORK; %s SELECT nextval ('new_call_number') AS cnumber;" % qsv)
		if not cnum:
			dboo.qexecute ("ROLLBACK WORK;")
			continue
		query = "INSERT INTO call (number, t_get, g_disp, cnum_total, reasn, %s) VALUES (%d, %d, %s, %d, '%s', %s);" % (
				scname, cnum, curr_tm, disp, cnum_total, reasn, scval)
#		print query
		if dboo.qexecute (query):
			dboo.qexecute ("COMMIT WORK;")
			stit = "Новый вызов <b>%d %d</b> %d!" % (cnum, cnum_total, j)
			ins_transact_log (dboo, query, disp, stit, 0, cnum, curr_tm)
			return	cnum
		else:	dboo.qexecute ("ROLLBACK WORK;")
	print "##" * 22
	stit = "Ошибка приема вызова <b>%d</b>" % cnum
	ins_transact_log (dboo, query, disp, stit, 0, cnum, curr_tm, str(dboo.last_error).replace("'", '"'))
	return	False

def	ins_transact_log (dboo, querys, disp, ctit, br_id, cnum, curr_tm, last_err = ''):
	""" запись информации в transact_log	"""
#	print querys, disp, ctit, br_id, cnum, curr_tm, last_err
	rows = dboo.get_rows ("SELECT cod, tname FROM transact_table ORDER BY cod;")
	if not rows:
		return
	tbm = 0
	jcol = []
	jval = []
	for r in rows:
		cod, tname = r
		if querys.find('%s ' % tname) > 0:
			tbm |= cod

	if last_err != '':
		jcol.append('str_err')
		jval.append("'%s'" % last_err[0:254])
	if br_id > 0:
		jcol.append('br_id')
		jval.append('%d' % br_id)
	if cnum > 0:
		jcol.append('cnum')
		jval.append('%d' % cnum)
	if not curr_tm:		curr_tm = current_time()
#	print "######",	jcol, jval, ','.join(jval)
	query = "INSERT INTO transact_log (%s, who_disp, tm, table_bm, rem_tr, querys, return_cod) VALUES (%s, %s, %d, %d, '%s', '%s', 0);" % (
			','.join(jcol), ','.join(jval), disp, curr_tm, tbm, ctit, querys.replace("'", '"'))
	return	dboo.qexecute (query)

def	set_result (dboo, request, flag = ''):
	""" Форма опроса по результату исполнения	"""
	rsb_gostp = (11, 12, 14, 17)		# быстрые результаты - перевозка
	rsb_close = (8, 10, 11, 21, 22)		# быстрые результаты - закрытие
	if flag == 'C':
		rsbuttons = rsb_close
	else:	rsbuttons = rsb_gostp
	dictin['reslt']['rem'] = sselect(dboo, {'tab': 'reslt', 'key': 'num', 'val': 'name', 'knull': '', 'where': 'num > 0'}, dict_currval['reslt'])
	print """Перевозка<div class='call'><table width='100%%'>
	<tr><td align='right'> %s %s</td></tr>
	<tr><td align='right'> %s %s</td></tr>
	<tr><td align='right'> %s %s </td></tr>
	<tr><td align='right'> %s %s </td></tr>
	</table></div>""" % (sinput('reslt', dictin['reslt'], sep='</td><td>'), srs_buttons (rsbuttons),
			sinput('diagn', dictin['diagn'], sep='</td><td>'), sds_buttons(),
			sinput('diat', dictin['diat'], sep='</td><td>'), sinput('diat2', dictin['diat2']),
			sinput('kuda', dictin['kuda'], sep='</td><td>'), sinput('kudat', dictin['kudat']))

def	set_DS (dboo, request):
	print "~shreslt|"
	pdom = request['set_DS']
	if pdom == 'diagn':
		if request.has_key('diagn') and request['diagn'] and request['diagn'][0:3].isdigit():
			sand = "AND num=%s" % request['diagn'][0:3]
		else:	sand = "ORDER BY num"
		query = "SELECT * FROM new_ds WHERE num < 200 %s;" % sand
		dtit = 'Диагнозы:'
	else:
		if request.has_key('diat') and request['diat'] and request['diat'][0:3].isdigit():
			sand = "AND num=%s" % request['diat'][0:3]
		else:	sand = "ORDER BY num"
		query = "SELECT * FROM new_ds WHERE num > 200 %s;" % sand
		dtit = 'Осложнегия:'
	rows = dboo.get_rows(query)
	print query, "document.mainForm.%s.value='%03d %s'" % (pdom, rows[0][0], rows[0][1])
	if len(rows) == 1:
		print "~eval| document.mainForm.%s.value='%03d %s'" % (pdom, rows[0][0], rows[0][1])
		return
	top = 'top: 320px; max-height: 320px; overflow: auto;'
	print "<div id='find_street' class='tmp' style='width: 950px; left: 182px; position: absolute; min-height: 200px; %s'>" % top
	ptit_box (dtit, mess = request['set_DS'], clear = 'shreslt')
	print "<table width='100%'><tr valign='top'><td>"
	lenrs = int(len(rows)/2)
	j = 0
	for r in rows:
		if not (j % lenrs):	print "</td><td>"
		j += 1
		cod, name = r[0:2]
		print "<a href='' onclick=\"document.mainForm.%s.value='%03d %s'; $('#shreslt').text(''); return false; \"> %03d %s</a><br />" % (pdom, cod, name, cod, name)
	print "</td></tr></table>"
	print "</div>"

obj_type_dict = {}
def	get_tdict (dbrg, type_dict):
	if not len (obj_type_dict):
		rows = dbrg.get_rows ("SELECT * FROM dict_types")
		if rows:
			for r in rows:
				obj_type_dict[r[0]] = r[1]
	return	"<div class='tit'> %s:</div>" % obj_type_dict[type_dict]

def	get_sname (dbrg, ind, sname):
	if ind and ind > 0:
		drow = dbrg.get_dict ("SELECT * FROM oo_street WHERE ind=%d;" % ind)
		if drow:	return	drow['sname']
	return	sname

def	find_street (dboo, request):
	print "~shreslt|"
	pdom = request['find_street']
	dbrg = dbtools.dbtools ('host=127.0.0.1 dbname=region port=5432 user=vds')
	if pdom == 'kuda':
		top = 'top: 320px; max-height: 360px; overflow: auto;'
		rmess = 'Куда доставить'
		street = upper_ru (request['kuda'].strip()).replace(' ', '% ')		#.decode ("UTF-8").encode("KOI8-R")).replace(' ', '% ')
	else:
		top = 'top: 140px; max-height: 480px; overflow: auto;'
		rmess = 'Адрес места вызова'
		street = upper_ru (request['street'].strip()).replace(' ', '% ')	#.decode ("UTF-8").encode("KOI8-R")).replace(' ', '% ')
	query = "SELECT * FROM oo_street WHERE sname LIKE '%s%%' ORDER BY type_dict, sname;" % street
	print query
	rows = dbrg.get_rows (query)
	if len (rows) == 1:
		ind, sname, tag, parent, type_dict = rows[0][:5]
		if tag > 0:	ind = tag
		sname = get_sname (dbrg, tag, sname)
		if pdom == 'kuda':
			print "~eval|document.mainForm.kuda.value='%s';" % sname
		else:	print "~eval|document.mainForm.street.value='%s'; set_house(%d);" % (sname, ind)
	else:
		jt = int (len (rows) /4) +1
	print "<div id='find_street' class='tmp' style='width: 950px; left: 182px; position: absolute; min-height: 200px; %s'>" % top
	ptit_box ('Улица', mess = rmess, clear = 'shreslt')
	print "<table width='100%'><tr valign='top'><td>"
	j = jtd = 0
	if rows:
		for r in rows:
			if j and not j % jt:	print "</td><td>"
			j += 1
			ind, sname, tag, parent, type_dict = r[:5]
			if jtd != type_dict:
				print get_tdict (dbrg, type_dict)
				jtd = type_dict
			if tag > 0:	ind = tag
			stname = get_sname (dbrg, tag, sname)
			if pdom == 'kuda':
				print """<a href='' onclick="document.mainForm.kuda.value='%s';
					$('#shreslt').text(''); document.mainForm.kudat.focus(); return false;">%s</a><br />""" % (stname, sname)
			else:	print """<a href='' onclick="document.mainForm.street.value='%s';
					set_house(%d); return false;">%s</a><br />""" % (stname, ind, sname)
	else:	print "<span class='tit' style='color: #a00;'>Нет такой улицы!</span><hr />"
	print "</td></tr></table></div>"

def	set_subst (dboo, request):
	if request.has_key('cpoint'):
		print "~rem_street|<a href='/cgi/map.cgi?ssid=%s&width=1024&height=768&cpoint=%s' target='map' onclick='alert(%s)'> Место на Карте </a>" % (
				request['session_id'], request['cpoint'], request['cpoint'])
	print "~shreslt|"
	if request.has_key('sector'):
		subst = set_station (dboo, int(request['sector']), request['pbrg'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
		if subst:
			print "~eval|document.mainForm.subst.value='%s';" % subst

def	set_station (dboo, sector, pbrg):
	if sector and pbrg:
		query = "SELECT * FROM subst WHERE sector=%d AND profile='%s';" % (sector, pbrg)
		dr = dboo.get_dict (query)
		if dr:	return	dr['subst']

def	get_sector (dboo, request):
#	print "get_sector", request
	if request.has_key('id_street'):
		query = "SELECT sector, f_home, flag, s_homes FROM cross_shs WHERE street=%s ORDER BY sector;" % request['id_street']
		rows = dboo.get_rows (query)
		if rows:
			for r in rows:
				sector, f_home, flag, s_homes = r
				if flag == 1 or flag == 3:			return	sector
				elif s_homes and request.has_key('house'):
					arrh = s_homes.split(',')
					for jh in arrh:
						if jh == request['house']:	return	sector
	return	0

def	set_house (dboo, request):
	print "~shreslt|"
#	print "get_sector:", get_sector (dboo, request)
#	dbrg = dbtools.dbtools ('host=localhost dbname=region port=5432 user=vds')
	dbrg = dbtools.dbtools ('host=127.0.0.1 dbname=region port=5432 user=vds')
	if not (request.has_key('id_street') and int (request['id_street']) > 0):
		print "<span class='tit' style='color: #a00;'>Нет улицы в БД!</span><hr />"
		return
	query = "SELECT *, length(house_num) FROM oo_house WHERE street_id = %s AND sector > 0 ORDER BY length, house_num" % request['id_street']
	rows = dbrg.get_rows (query)
	if rows == False:
		print "<span class='tit' style='color: #a00;'>Ошибка в:", query, "</span><hr />"
		return
	if not rows:
		print "<div id='set_house' class='tmp' style='width: 920px; left: 180px; top: 150px; position: absolute; max-height: 800px; min-height: 200px'>"
		ptit_box (upper_ru (request['street'].strip()),	#.decode ("UTF-8").encode("KOI8-R")),
				mess="<span class='tit' style='color: #a00;'>Нет домов в базе данных!</span>", clear='shreslt')
		print "</div>"
		print "~eval|setTimeout (\"$('#shreslt').text('');\", 1999)" 
		return	
	rd = dbrg.desc
	if len (rows) == 1:
		r = rows[0]
		print set_station (dboo, r[rd.index('sector')], request['pbrg'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
		if r[rd.index('sector')]:
			sector = r[rd.index('sector')]
		else:
			sector = get_sector (dboo, request)
		if not sector:
			print "~rem_sect| NOT"
		else:
			if r[rd.index('gx')] and r[rd.index('gy')]:
				print "~rem_sect| XY"
			print "~eval|document.mainForm.sector.value='%d';" % r[rd.index('sector')]
			subst = set_station (dboo, r[rd.index('sector')], request['pbrg'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
			if subst:
				print "document.mainForm.subst.value='%s';" % subst
		return
	print "<div id='set_house' class='tmp' style='width: 920px; left: 180px; top: 150px; position: absolute; max-height: 800px; min-height: 100px'>"
#	ptit_box (upper_ru (request['street'].strip().decode ("UTF-8").encode("KOI8-R")), mess='Выбор дома', clear='shreslt')
	ptit_box (upper_ru (request['street'].strip()), mess='Выбор дома', clear='shreslt')
	print "rd", rd
	print "<div style='padding: 10px; margin: 10px;'>"
	for r in rows:
		if r[rd.index('corps')]:
			corps = r[rd.index('corps')].strip()
		else:	corps = ''
		print "<input type='button' class='butt' onclick=\"set_subst('%s', %d); document.mainForm.cpoint.value='[%s,%s]'\" value='%4s %s' />" % (
				r[rd.index('house_num')], r[rd.index('sector')], str(r[rd.index('gx')]), str(r[rd.index('gy')]), r[rd.index('house_num')], corps)
	print "</div>"
	print "</div>"

def	get_norma (dboo, reasn):
	query = "SELECT r.*, n.place, n.sex, n.age, n.profile, n.t_wait, n.t_serv, n.t_hosp, n.t_norm FROM reasn r, norma n WHERE r.num ='%s' AND r.num = n.reasn;" % reasn
	dreasn = dboo.get_dict(query)
	return	dreasn

def	new_call (reasn, request):
	""" Форма опроса вызывающего	"""
#	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	dboo = dbtools.dbtools ('host=127.0.0.1 dbname=b03 port=5432 user=vds')
#	reasn = upper_ru (request['reasn'].strip().decode ("UTF-8").encode("KOI8-R"))
	dreasn = get_norma (dboo, reasn)	#upper_ru (request['reasn'].strip().decode ("UTF-8").encode("KOI8-R")))
	if not dreasn:
		print "~main_fid|<span class='tit' style='color: #a00;'>Нет нормативов для", reasn ,"!</span><hr />"
		return

#	print "~shadow|"
	profile = dreasn['profile']	#.sprip()
	if SESSION and not SESSION.get_key('GET_CALL'):
		print "SESSION:"
		SESSION.set_obj('GET_CALL', {'tm': current_time(), 'rr_tree': request})
	print "<fildset class='hidd'><input type='hidden' name='reasn' value='%s'>" % reasn
	print "<input type='hidden' name='profile' value='%s'>" % profile
	if request.has_key('stack'):
		print "<input type='hidden' value='%s' name='stack'>" % request['stack']
	else:	print "<input type='hidden' value='' name='stack'>"
	print "</fildset>"

	if request.has_key('stat'):
		if request['stat'] == 'save':	cnumber, t_get = new_call_save (dboo, request)
		if request['stat'] == 'refuse':	new_call_refuse (dboo, request)
		if request['stat'] == 'find_street':
			find_street (dboo, request)
			return
		if request['stat'] == 'set_house':	return	set_house (dboo, request)
		if request['stat'] == 'set_subst':	return	set_subst (dboo, request)
		if request['stat'] == 'set_DS':		return	set_DS (dboo, request)
#	print "~main_fid|"
	if 'cnumber' in locals():
		print "<div class='green'><pre>	Вызов успешно сохранен с No <b>%d</b> в %s.</pre></div>" % (cnumber, str_time(t_get, "<b>%H:%M</b> %d/%m/%y"))
###		print "~eval|document.mainForm.reasn.value='';document.mainForm.stack.value=''"
		return
	assign_values (request)
	if not dict_currval.has_key('pbrg') or dict_currval['pbrg'] == '':
		dict_currval['pbrg'] = profile
	else:	dict_currval['pbrg'] = upper_ru (dict_currval['pbrg'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
	#print dict_currval
	#print dreasn
	#	можно сохранить в сессии
	dictin['place'] =	{'label': 'Место', 'rem': sselect(dboo, {'tag': 'select', 'tab': 'place', 'key': 'num', 'val': 'name'}, str(dreasn['place']))}
	dictin['kto'] =	{'label': 'Кто', 'rem': sselect(dboo, {'sname': 'kto', 'tab': 'who_call', 'key': 'cod', 'val': 'name', 'knull': ''}, dict_currval['kto'])}
	dictin['sex'] =	{'label': 'Пол', 'rem': ssex (dict_currval['sex'])}	#(dreasn['sex'].strip(), dict_currval['sex'])}
	dictin['pbrg'] =	{'label': 'Проф.', 'rem': sselect(dboo, {'sname': 'pbrg', 'tab': 'prof', 'key': 's_name', 'val': 'l_name', 'knull': '', 'order': 'ind',
		'on': "onchange=\"document.mainForm.stat.value='set_subst'; $.ajax({data: 'main_fid=GET_CALL&' +$('form').serialize()});\""}, dict_currval['pbrg'])}
	dictin['subst'] =	{'label': 'П/С', 'rem': 
			sselect(dboo, {'sname': 'subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 15'},
				dict_currval['subst'])}

	forma = """<div class='call' style='background-color: #fff0aa;'>
	<table width=''><tr><td width='400px'>%s</td><td>%s</td><td>%s</td><tr></table>
	</div>""" % ("Повод: <a onclick='change_reasn (); return false;' href=''><span class='tit'> %s %s </span></a>" % (dreasn['num'], dreasn['name']),
			sinput('rem_reasn', dictin['rem_reasn']), sinput('place', dictin['place']))
	print forma
	print """<div class='call' style='min-height: 300px;'><table width='100%%' cellpadding='0' cellspacing='0'><tr valign='top'>
	<td><div class='call'><table width='100%%' border=0>
	<tr><td align='right'> %s %s %s </td></tr>
	<tr><td align='right'> %s %s %s %s %s </td></tr>
	</table></div><div class='call'><table width='100%%'>
	<tr><td align='right'> %s %s %s %s </td></tr>
	<tr><td align='right'> %s </td><td align='right'><div style='padding: 2px; background-color: #fc0;'> %s </div></td><td></td></tr>
	</table></div>""" % (
		#	sinput('street', dictin['street'], sep='</td><td>'), sinput('house', dictin['house'], sep='</td><td>'), sinput('korp', dictin['korp']),
			sinput('street', dictin['street'], sep='</td><td>'), sinput('house', dictin['house']), sinput('korp', dictin['korp']),
			sinput('flat', dictin['flat'], sep='</td><td>'), sinput('pdzd', dictin['pdzd']), sinput('etj', dictin['etj']), sinput('pcod', dictin['pcod']),
			sinput('phone', dictin['phone']),
			sinput('name', dictin['name'], sep="</td><td colspan='3'>"),
			sinput('name2', dictin['name2']), sinput('age', dictin['age']), sinput('sex', dictin['sex']),
			sinput('kto', dictin['kto'], sep="</td><td>"), 
			sinput('message_text', dictin['message_text'])	#, sep="</td><td>"),
			)
	if dreasn['flag'] > 1:	set_result (dboo, request)
	print """<div class='grey'><table width='100%%'>
	<tr><td> %s </td><td align='right'> %s </td><td align='right'> %s </td></tr>
	</table></div>""" % (sinput('', {'label': 'Сохранить', 'type': 'button', 'on': 'onclick="new_call_save();"'}),
			sinput ('sel_refuse', {'label': "Причина отказа", 'rem': sselect(dboo, {'tab': 'refuse', 'key': 'cod', 'val': 'name', 'knull': ''}, dict_currval['refuse'])}),
			sinput ('', {'label': 'Отказать', 'type': 'button', 'on': 'onclick="new_call_refuse();"'}))

	print """</td><td>ZZZZZZZZZZZ<div class='call'><table width='100%%'>
	<tr><td align='right'> %s </td></tr>
	<tr><td align='right'> %s </td></tr>
	<tr><td align='right'> %s </td></tr>
	</table></div></td></tr></table>""" % ( sinput('sector', dictin['sector'], sep='</td><td>'),
			sinput('pbrg', dictin['pbrg'], sep='</td><td>'), sinput('subst', dictin['subst'], sep='</td><td>')
			)
	if request.has_key('reasn_comment') and request['reasn_comment']:
		out_ccomment (dboo, request['reasn_comment'])
###		print "~eval| document.mainForm.stack.value='%s';" % request['reasn_comment']
###	print "~eval| document.mainForm.place.focus();"
	print "~eval| $('#calls').css({'z-index': 1111});"

def	out_ccomment (dboo, rcomment):
	""" Коментарий к поводу вызова	"""
	print "~rcomment|<div class='grey'>",
	ptit_box ("Коментарий к поводу вызова")
	node, rcomm = rcomment.split(':')
	if rcomm:
		drow = dboo.get_dict ("SELECT * FROM ccomment WHERE tmm = %s;" % rcomm)
		if drow:	print	drow['rcomment']
	print node, rcomm
	print	"</div>"	

###############################################
