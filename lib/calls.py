#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time

LIBRARY_DIR = r"/home/vds/03/oopy/lib"            # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

bases = {
	'oo': 'host=127.0.0.1 dbname=b03 port=5432 user=smirnov',
	'ss': 'host=127.0.0.1 dbname=ss2013 port=5432 user=smirnov',
	}

import	session, dbtools
dboo = dbtools.dbtools (bases['oo'])

cols = ['number','sector','profile','subst','place','reasn','rept','kto','diagn','diat','alk','reslt','kuda','t_go','br_ref','smena','nbrg','pbrg','nsbrg','doctor','ps','cnum_total']

dct_disp = {'t_get': "Принял", 't_send': "Передал", 't_arrl': "Прибыл", 't_done': "Исполнен", 'c_disp': "Закрыт"}
col_disp = ['t_get','g_disp','t_send','s_disp','t_arrl','a_disp','t_done','d_disp','c_disp','t_close']

col_addr = ['street','house','korp','flat','pdzd','etj','pcod','phone']	# Адрес
col_prsn = ['name','name2','age','sex']		# Больной

# Участвуют в оптимизации при выборе Бригады
col_opt = ['t_wait','t_serv','t_hosp','id_ims','tm_hosp','disp_hosp','tm_ps','disp_ps','tm_trans','disp_trans','is_delay']

def	save_columns_tkt (request):
	""" Обновить данные Контрольного талона 	"""
	tkt_number = request.get('tkt_number')
	print "tkt_number", request.get('tkt_number')
	if tkt_number and tkt_number.isdigit():	#	return
		swhere = "WHERE tkt_number = %s" % tkt_number
		lset = []
		for k in ['street', 'house', 'korp', 'flat', 'pdzd', 'etj', 'pcod', 'phone', 'name', 'name2', 'kto', 'age', 'sex', 'place', 'subst']:
			v = request.get(k)
			if v:	lset.append ("%s = '%s'" % (k, v))
			else:	lset.append ("%s = NULL" % k)
		query = "UPDATE tkt_calls SET %s %s" % (", ".join(lset), swhere)
		print "<br>", query
		return	dboo.qexecute (query)

def	save_get_call (US_ROW, request):
	""" Сохранить данные Нового вызова в таблицах call, c_proto, events	"""
	if not save_columns_tkt (request):		return
#	print  "~log|save_get_call", request	;	return

	tkt_number = request.get('tkt_number')
	query = "SELECT * FROM tkt_calls WHERE tkt_number = %s;" % tkt_number
	dtkt = dboo.get_dict ("SELECT * FROM tkt_calls WHERE tkt_number = %s;" % tkt_number)
	cols = []
	vals = []
	sset = []
	querys = ['BEGIN WORK;']
	stack = None
	for c in dtkt.keys():
		if dtkt[c] == None:	continue
		if c in ['tkt_number', 't_call']:	continue
		if c == 'stack':
			stack = dtkt[c]
			continue
		cols.append (c)
		if c == 'number':	vals.append ("1 + (SELECT max(number) FROM call)") 
		elif c == 'cnum_total':	vals.append ("1 + (SELECT max(cnum_total) FROM call)") 
		elif c == 't_get':	vals.append (str(int(time.time())))
		elif c == 'g_disp':	vals.append (str(US_ROW['disp']))
		else:	vals.append ("'%s'" % dtkt[c])
	if 'profile' in cols:
		cols.append ('pbrg')
		vals.append ("'%s'" % dtkt['profile'])
	if 'subst' in cols:
		cols.append ('nsbrg')
		vals.append ("'%s'" % dtkt['subst'])

	if not request.get('sex'):
		cols.append ('sex')
		vals.append ("'?'")
#	try:
	if cols:
		query = "INSERT INTO call (%s) VALUES (%s); SELECT cnum_total, number, t_get FROM call WHERE cnum_total = (SELECT max(cnum_total) FROM call);" % (", ".join(cols), ", ".join(vals))
		res = dboo.get_dict (query)

		if not res:	#	print "~log|", res
			print "~log|", query, "<br>SQL ERR:", str(dboo.last_error)
			return
		querys = [ "UPDATE tkt_calls SET number = %s, cnum_total = %s, t_get = %s  WHERE tkt_number = %s;" % (res['number'], res['cnum_total'], res['t_get'], tkt_number) ]
		if dtkt['subst']:
			querys.append ("INSERT INTO events (subst, cnum, cod, timer) VALUES (%s, %s, %s, %s);" % (dtkt['subst'], res['number'], 11, res['t_get']))
		else:	querys.append ("INSERT INTO events (cnum, cod, timer) VALUES (%s, %s, %s);" % (res['number'], 11, res['t_get']))
		querys.append ("INSERT INTO c_proto (number, t_get, proto) VALUES (%s, %s, '%s');" % (res['number'], res['t_get'], stack))
		query = "\n".join (querys)
		if dboo.qexecute (query):
			print   "~eval| $('#background').html(''); $('#calls').html(''); set_shadow ('CLL_OPER');"
		else:	print "~log|", query, "<br>SQL ERR:", str(dboo.last_error)
		'''
	except:
		print "~log|EXCEPT", query, "<br>SQL ERR:", str(dboo.last_error)
		return
		'''

def	refuse_call (US_ROW, request):
	cnum_total = request.get ('cnum_ttl')
	crefuse = request.get ('r_refuse')
	armid = US_ROW['armid']
	disp = US_ROW['disp']
	
	print	"refuse_call (US_ROW, request)", cnum_total, crefuse 
	querys = []
	if crefuse and crefuse.isdigit():
		curr_tm = int (time.time())
		irefuse = int(crefuse)
		if irefuse < 10:		# Отказ на приеме
			querys.append ("UPDATE tkt_calls SET ??? WHERE cnum_total = %s" % cnum_total)
			querys.append ("INSERT INTO events (cnum, subst, cod, timer) VALUES (%s, %s, %s, %s);" % (dcall['number'], dcall['subst'], 90, curr_tm))	# Удалить вызов
		elif irefuse > 80:		# Отка и Закрытие
			if armid in ['ZAV_PS', 'SVOO']:		# Закрытие в Архив 
				querys.append ("UPDATE call SEP t_close = %s, c_disp = %s WHERE cnum_total = %s" % (disp, curr_tm, cnum_total))
				querys.append ("INSERT INTO events (cnum, subst, cod, timer) VALUES (%s, %s, %s, %s);" % (dcall['number'], dcall['subst'], 99, curr_tm))	# Вызов удален
			else:					# Закрытие и Оповищение
				querys.append ("UPDATE call SEP t_done = %s, d_disp = % WHERE cnum_total = %s" % (disp, curr_tm, cnum_total))
				querys.append ("INSERT INTO events (cnum, subst, cod, timer) VALUES (%s, %s, %s, %s);" % (dcall['number'], dcall['subst'], 90, curr_tm))	# Удалить вызов
		else:	print "r_refuse:", r_refuse 
	if querys:	print "~RESULT|", "<br>".join(querys)
	
def	get_call (US_ROW, request):
	""" Прием Вызова	"""
	import	tree_reasn

	print "~log| get_call:", request
	if request.get('stat') == 'save':	return	save_get_call (US_ROW, request)
	if request.get('stat') == 'refuse':	return	refuse_call (US_ROW, request)
	
	curr_tm = int(time.time())
	tkt_number = request.get('tkt_number')
	stack = request.get('stack')
	reasn = request.get('reasn')
	dtkt = None
	if tkt_number:
		dtkt = dboo.get_dict ("SELECT * FROM tkt_calls WHERE tkt_number = %s;" % tkt_number)
		if reasn:
			sreasn = "reasn = '%s'" % reasn.strip()
			if stack:	sreasn += ", stack = '%s'" % stack.strip()
	 		if dboo.qexecute ("UPDATE tkt_calls SET t_get = %d, %s WHERE tkt_number = %s" % (curr_tm, sreasn, tkt_number)):
				dtkt = dboo.get_dict ("SELECT * FROM tkt_calls WHERE tkt_number = %s;" % tkt_number)
		else:
			if dtkt['reasn']:		reasn = dtkt['reasn']
			if dtkt['stack']:		stack = dtkt['stack']
		print	"Q"*22, sreasn, tkt_number
	'''
	if request.get ('change_reasn') == 'on':
		print "~eval| alert ('get_call stack: %s reasn: %s, tkt_number: %s' );" % (stack, reasn, tkt_number)
		return
#	else:	reasn = request.get('reasn')
	'''

	print "~background|<div id='shadow' style='top: 0px; left: 0px; width: 100%; height: 100%; background-color: #000; position: absolute; z-index: 1110; opacity: 0.2;'></div>"
	if not reasn:
	#	print "<div id='call_form' type='hidden' style='top: 40px; left: 180px; width: 900px; border: thin solid #668; background-color: #ffe; position: absolute; z-index: 1112'>"
		if not tkt_number:
			rtkt = dboo.get_row ("INSERT INTO tkt_calls (number, cnum_total, g_disp, t_get, t_call) VALUES (0, 0, %s, %s, %s); SELECT max(tkt_number) FROM tkt_calls;" % (US_ROW['disp'], curr_tm, curr_tm))
			tkt_number = rtkt[0]
			dboo.qexecute ("UPDATE tkt_calls SET cnum_total = %s, t_get = %d WHERE tkt_number = %s" % (tkt_number, curr_tm, tkt_number))
			request['tkt_number'] = str(tkt_number)
		elif dtkt:
			if US_ROW['disp'] == dtkt['g_disp']:
				dboo.qexecute ("UPDATE tkt_calls SET g_disp = %s, t_get = %d WHERE tkt_number = %s" % (US_ROW['disp'], curr_tm, tkt_number))
			else:	dboo.qexecute ("UPDATE tkt_calls SET t_get = %d WHERE tkt_number = %s" % (curr_tm, tkt_number))
	#	rrr = tree_reasn.set_reasn(dboo, request)
		tree_reasn.view_alert(request)
	#	print "</div>"
		return
	else:	print "#"*22, request

	dnorm = dboo.get_dict ("SELECT * FROM norma WHERE reasn = '%s'" % reasn)
	if dnorm:
		ssnorm = ", profile = '%s', t_wait = '%s', t_serv = '%s', t_hosp = '%s'" % (dnorm['profile'], dnorm['t_wait'], dnorm['t_serv'], dnorm['t_hosp'])
		if dnorm['place'] > 0:	ssnorm += ", place = %s" % dnorm['place']
	else:	ssnorm = ''
	if request.get('stack'):	ssnorm += ", stack= '%s'" % request.get('stack')
	dtkt = dboo.get_dict ("SELECT * FROM tkt_calls WHERE tkt_number = %s;" % tkt_number)
#	if not dtkt['reasn']:	dboo.qexecute ("UPDATE tkt_calls SET reasn = '%s', t_get = %d WHERE tkt_number = %s" % (reasn.strip(), curr_tm, tkt_number))
	if not dtkt['reasn']:	dboo.qexecute ("UPDATE tkt_calls SET reasn = '%s', t_get = %d %s WHERE tkt_number = %s" % (reasn, curr_tm, ssnorm, tkt_number))

#	return
	print "~calls|"

	opts = {}
	obj = {}
	obj['GET_CALL'] = True
	obj['tkt_number'] = tkt_number
	obj['reasn'] = "%s" % T.svals (dboo, dictin['reasn'], reasn)
#	obj['place'] = "%s" % T.svals (dboo, dictin['place'], request.get('place'))
	obj['place'] = "%s" % T.sselect (dboo, dictin['place'], request.get('place'))
	obj['reasn_rem'] = "<span class='bfinf'>Притечание при опросе</span>"
	obj['t_call'] = sdtime (int (time.time()))
#	obj['street'] = "<input type='text' name='street' size=32 onkeypress='return find_street (event);' />" 
	obj['street'] = "<input type='text' name='street' size=32 value='%s' onkeyup='return find_street (event);' />" % sval(dtkt, 'street')
	obj['house'] = """<input type='text' name='house' size=2 value='%s' onfocus="$('#RESULT').html(''); set_shadow('view_houses'); " />""" % sval(dtkt, 'house')
#	obj['korp'] = """<input type='text' name='korp' size=2 value='%s' onfocus="$('#RESULT').html(''); set_shadow('save_columns_tkt&tkt_number=%s');" />""" % (sval(dtkt, 'korp'), tkt_number)
	obj['korp'] = """<input type='text' name='korp' size=2 value='%s' onfocus="$('#RESULT').html(''); set_shadow('save_columns_tkt');" />""" % sval(dtkt, 'korp')

	obj['flat'] = "<input type='text' name='flat' size=3 value='%s' />" % sval(dtkt, 'flat')
	obj['pdzd'] = "<input type='text' name='pdzd' size=1 value='%s' onkeypress='return intkey(event)' />" % sval(dtkt, 'pdzd')
	obj['etj'] = "<input type='text' name='etj' size=1 value='%s' onkeypress='return intkey(event)' />" % sval(dtkt, 'etj')
	obj['pcod'] = "<input type='text' name='pcod' value='%s' size=3 />" % sval(dtkt, 'pcod')
	obj['phone'] = """<input type='text' name='phone' size=9 value='%s' onfocus="set_shadow('save_columns_tkt');" />""" % sval(dtkt, 'phone')

	obj['name'] = """<input type='text' name='name' value='%s' size=12 onfocus="set_shadow('save_columns_tkt');" />""" % sval(dtkt, 'name')
	obj['name2'] = "<input type='text' name='name2' value='%s' size=12 />" % sval(dtkt, 'name2')
	obj['age'] = """<input type='text' name='age' value='%s' size=2 onfocus="set_shadow('save_columns_tkt');" />""" % sval(dtkt, 'age')
#	obj['sex'] = "<select name='sex' size=1 /><option value='?'>?</option> <option value='М'>М</option> <option value='Ж'>Ж</option> </select>" 
	obj['sex'] = T.sselect (dboo, dictin['sex'], sval(dtkt, 'sex'))
	obj['kto'] = T.sselect (dboo, dictin['kto'], sval(dtkt, 'kto'))
	obj['subst'] = T.sselect (dboo, dictin['subst'], sval(dtkt, 'subst'))
	'''
	obj['S'] = "<input type='text' name='S' size=22 />" 
	obj[''] = 
	'''
	obj['BSTT_SERVS'] = button_box (US_ROW, dtkt, 1)
	parse_forms (opts, obj, 'call.html')

dictin = {
	'reasn':	{'tab': 'reasn', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'place':	{'tag': 'select', 'tab': 'place', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'kto':		{'sname': 'kto', 'tab': 'who_call', 'key': 'cod', 'val': 'name', 'knull': ''},
	'sex':		{'sname': 'sex', 'tab': 'sex', 'key': 'cod', 'val': 'name'},	# 'knull': ''},
	'refuse':	{'sname': 'sel_refuse', 'tab': 'refuse', 'key': 'cod', 'val': 'name', 'knull': ''},
	'pdelay':	{'sname': 'sel_pdelay', 'tab': 'pdelay', 'key': 'cod', 'val': 'name', 'knull': ''},
#	'rem2calls':	{'sname': 'crem', 'tab': 'rem2calls', 'key': 'rid', 'order': 'tm DESC', 'where': 'cnum_total = 0'},
#	'pcancel':	{'sname': 'sel_pcancel', 'tab': 'pcancel', 'key': 'cod', 'val': 'name', 'knull': ''},
	'pcancel':	{'sname': 'sel_pcancel', 'tab': 'new_reslt', 'key': 'num', 'val': 'name', 'knull': '', 'order': 'num', 'where': 'num > 80'},
	'subst':	{'sname': 'subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 10'},
	'doctor':	{'tab': 'person_sp', 'key': 'cod', 'val': 'name', 'rvals': ['cod', 'name']},
	'diagn':	{'sname': 'new_ds', 'tab': 'new_ds', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name'], 'knull': '', 'where': 'num < 200',},
	'reslt':	{'sname': 'reslt', 'tab': 'new_reslt', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name'], 'knull': '', 'order': 'num', },	# 'where': 'num > 0 AND num < 80', },
	'sel_subst':	{'sname': 'sel_subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 10', 'on': "onchange=\"set_shadow('find_calls');\""},
	'sel_place':	{'sname': 'sel_place', 'tab': 'place', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name'], 'knull': '', 'on': "onchange=\"set_shadow('find_calls');\""},
	'sel_badservis':{'sname': 'sel_badservis', 'tab': 'ss_badservise', 'key': 'label', 'val': 'name', 'knull': '' },	# 'on': "onchange=\"set_shadow('find_calls');\"" },
	'sel_cwfind':	{'sname': 'sel_cwfind', 'tab': 'ss_cwfind', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'on': "onchange=\"set_shadow('find_calls');\""	},
	'sel_corder':	{'sname': 'sel_corder', 'tab': 'ss_corder', 'key': 'cod', 'val': 'name', 'on': "onchange=\"set_shadow('find_calls');\""	},
	}
#	reslt_hospital = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 30, 33, 34, 35, 36, 37, 38, 39, 40]	-> global_vals.py

from	global_vals import *
from	parse_forms import *
import	tools as T

'''
	UPDATE bnaryd SET scall=NULL, stat=%d WHERE br_id=$br_id;
	UPDATE call SET t_send=NULL, t_arrl=NULL, s_disp=NULL, a_disp=NULL, br_ref=NULL, nbrg=NULL,  pbrg=NULL, nsbrg=subst, doctor=NULL, ps=NULL, t_go=NULL WHERE number=$cnumber;
	DELETE FROM cal2brg WHERE cnum=$cnumber
	DELETE FROM events WHERE cnum=$cnumber;
	INSERT INTO events (cnum, subst, cod, timer) VALUES ($cnumber, %d, %d, %d); $call_row->subst, $messCod ["CSLEEP"], $cur_time);
'''
def	update_call (US_ROW, dcall, request):
	print "~log|update_call"	#, request
	querys = []
	curr_tm = int(time.time())
	disp = int(request.get('disp'))
	cnum_total = dcall['cnum_total']
	sfrom = request.get ('sfrom')
	opts = request.get ('opts')
	print 'opts:', opts, 'sfrom:', sfrom, 'cnum_total:', cnum_total
	if request.has_key('set_br_ref'):	# Назначение Бригады
#		try:
		#	{'disp': '3043', 'cnum_ttl': '128266', 'shstat': 'open_call', 'exec': 'UPDATE', 'this': 'ajax', 'set_bnumber': '320', 'sel_corder': '1', 'set_br_ref': '648'}
			br_ref = int(request.get('set_br_ref'))
			dbrig = dboo.get_dict ("SELECT * FROM bnaryd WHERE br_id = %s" % request.get('set_br_ref'))
			if not dbrig:	return	False

			if dbrig['scall'] > 0:	# Бобавить в cal2brg
				sttb = dbrig['stat']
			else:
				sttb = 5
				sset_brig = "scall = %s, stat = %s" % (dcall['number'], sttb)
				swhere_brig = "br_id = %s" % br_ref
				querys.append ("UPDATE bnaryd SET %s WHERE %s;" % (sset_brig, swhere_brig))
				querys.append (qhistory_brigs(curr_tm, disp, 'bnaryd', sset_brig, swhere_brig))
			sset_call = "t_send = %s, s_disp = %s, br_ref = %s, nbrg = %s, pbrg = '%s', nsbrg = %s, doctor = %s" % (curr_tm, disp, br_ref, dbrig['number'], dbrig['profile'], dbrig['n_pst'], dbrig['doctor'])
			swhere_call = "cnum_total = %s" % cnum_total
			querys.append ("UPDATE call SET %s WHERE %s;" % (sset_call, swhere_call))
			querys.append (qhistory_calls (curr_tm, disp, 'call', sset_call.replace("'", "''"), swhere_call))
			querys.append ("INSERT INTO cal2brg (cnum, br_ref, tmr1, sttb, cnum_total) VALUES (%s, %s, %s, %s, %s);" % (dcall['number'], br_ref, curr_tm, sttb, cnum_total))
			'''
			print	"<br>".join (querys)	#[sset_call, swhere_call])
			'''
			dboo.qexecute ('\n'.join (querys))
			return	True
#		except:
			print "<br>except:", request
			return	False
#	opts=EDIT
	if opts and opts == 'EDIT':
#		try:
			print 'EDIT', 'sfrom:', sfrom, 'cnum_total:', cnum_total
			sets = []
			for k in ['reslt', 'diagn', 'diat', 'kuda']:
				val = request.get (k)
				if not val:	continue
				if k == 'diagn' and str(dcall['diagn']) == val:	continue
				if k == 'reslt' and str(dcall[k]) == val:	continue
				if k == 'kuda' and dcall[k] != val:		sets.append ("kuda='%s'" % val.strip().replace("'", "''"))
				elif k == 'diat' and (dcall[k] != val or request.get('ds_plus')):
					if request.get('ds_plus'):
						sets.append ("diat='+%s %s'" % (request.get('ds_plus'), val.strip().replace("'", "''")))
					else:	sets.append ("diat='%s'" % val.strip().replace("'", "''"))
				else:
					if dcall[k] != val:	sets.append ("%s=%s" % (k, val))
			if request.get ('ds_plus') and not request.get('diat'):	sets.append ("diat='+%s'" % request.get('ds_plus'))
			if not sets:
				print "~RESULT|", "<span class='bfinf'> &nbsp; Нет изменений. </span>"
				return	False
			sset_call = ", ".join(sets)
			swhere_call = "cnum_total = %s" % cnum_total
			querys.append ("UPDATE %s SET %s WHERE %s;" % (sfrom, sset_call, swhere_call))
			querys.append (qhistory_calls (curr_tm, disp, sfrom, sset_call.replace("'", "''"), swhere_call))
		#	print	"<br>".join (querys)	#[sset_call, swhere_call])
			return	dboo.qexecute ('\n'.join (querys))
#		except:
			print "<br>except:", request
			return	False
	if opts and opts == 'refuse':
		armid = US_ROW['armid']
	#	print armid, request
		prefuse = request.get('sel_refuse')
		sprefuse = T.svals (dboo, dictin['refuse'], prefuse)
		querys.append (qrem2calls (curr_tm, disp, dcall['number'], cnum_total, prefuse, sprefuse))
		if armid in ['SVOO']:		# Закрытие в Архив
			print	"CLOSE"
			sset_call = "reslt = %s, t_done = %s, d_disp = %s" % (90, curr_tm, disp)
		else:
			print	"REM ONLY"
			sset_call = "reslt = %s, t_send=%s, s_disp=%s" % (90, curr_tm, disp)
		querys.append ("UPDATE call SET %s WHERE cnum_total=%s;" % (sset_call, cnum_total))
		querys.append (qhistory_calls (curr_tm, disp, 'call', sset_call, "cnum_total=%s" % cnum_total))
		querys.append ("DELETE FROM events WHERE cnum=%s;" % dcall['number'])
		querys.append ("INSERT INTO events (cnum, subst, cod, timer) VALUES (%s, %s, %s, %s);" % (dcall['number'], dcall['subst'], 9, curr_tm))
#		print	"<br>".join (querys)
		return	dboo.qexecute ('\n'.join (querys))
		
	if opts and opts == 'pdelay':		# Задержки в пути		
#	elif request.has_key('opts') and request['opts'] == 'pdelay':	# Задержки в пути
		pdelay = request.get('sel_pdelay')
		if pdelay and pdelay.isdigit():
			spdelay = T.svals (dboo, dictin['pdelay'], pdelay)
		#	print	qrem2calls (curr_tm, disp, dcall['number'], dcall['cnum_total'], pdelay, spdelay)
			return	dboo.qexecute (qrem2calls (curr_tm, disp, dcall['number'], cnum_total, pdelay, spdelay))

	if opts and opts == 'pcancel':		# Отмена назначения		
#	elif request.has_key('opts') and request['opts'] == 'pcancel':	# Отмена назначения	'sel_pcancel': '91', 'opts': 'pcancel'
		try:
			reslt = request.get('sel_pcancel')
			bstat = 9	### ???
			querys.append ("DELETE FROM cal2brg WHERE cnum=%s;" % dcall['number'])
			sset_brig = "scall=NULL, stat=%s" % bstat
			querys.append ('UPDATE bnaryd SET %s WHERE br_id=%s;' % (sset_brig, dcall['br_ref']))
			querys.append (qhistory_brigs (curr_tm, disp, 'bnaryd', sset_brig, "br_id=%s" % dcall['br_ref']))
			if reslt and reslt.isdigit():
				querys.append (qrem2calls (curr_tm, disp, dcall['number'], cnum_total, reslt, T.svals (dboo, dictin['reslt'], reslt)))
				if int (reslt) in [94, 95, 96, 97, 98]:	# Отмена назначения
					sset_call = "t_send=NULL, t_arrl=NULL, s_disp=NULL, a_disp=NULL, br_ref=NULL, nbrg=NULL,  pbrg=NULL, nsbrg=subst, doctor=NULL, ps=NULL, t_go=NULL" 
				else:		# Отказать
					if armid in ['SVOO']:	# Удаляет SVOO
						sset_call = "reslt = %s, t_done = %s, d_disp = %s, a_disp=NULL, br_ref=NULL, nbrg=NULL,  pbrg=NULL, nsbrg=subst, doctor=NULL, ps=NULL, t_go=NULL" % (reslt, curr_tm, disp)
					else:	sset_call = "reslt = %s, t_send=%s, s_disp=%s, t_arrl=NULL, a_disp=NULL, br_ref=NULL, nbrg=NULL,  pbrg=NULL, nsbrg=subst, doctor=NULL, ps=NULL, t_go=NULL" % (reslt, curr_tm, disp)
			else:	# Вернуть в ОО
				sset_call = "t_send=NULL, t_arrl=NULL, s_disp=NULL, a_disp=NULL, br_ref=NULL, nbrg=NULL,  pbrg=NULL, nsbrg=subst, doctor=NULL, ps=NULL, t_go=NULL"
			querys.append ("UPDATE call SET %s WHERE cnum_total=%s;" % (sset_call, cnum_total))
			querys.append (qhistory_calls (curr_tm, disp, 'call', sset_call, "cnum_total=%s" % cnum_total))
			querys.append ("DELETE FROM events WHERE cnum=%s;" % dcall['number'])
			querys.append ("INSERT INTO events (cnum, subst, cod, timer) VALUES (%s, %s, %s, %s);" % (dcall['number'], dcall['subst'], 10, curr_tm))
			return	dboo.qexecute ('\n'.join (querys))
			'''
			print   "<br>".join (querys)
			return	False
			'''
		except:
			print "<br>except:", request, "<br>", "<br>".join (querys)
			return	False
	elif request.has_key('stack') and  request.has_key('reasn'):
		sset_call = "reasn='%s'" % request['reasn'].strip()
		querys.append ("UPDATE call SET %s WHERE cnum_total=%s;" % (sset_call, cnum_total))
		querys.append (qhistory_calls (curr_tm, disp, 'call', sset_call.replace("'", "''"), "cnum_total=%s" % cnum_total))
	#	querys.append ("UPDATE c_proto SET proto = '%s' WHERE t_get = (SELECT t_get FROM calls WHERE cnum_total = %s);" % (request['stack'], cnum_total))
		querys.append ("UPDATE c_proto SET proto = '%s' WHERE number = %s AND t_get =  %s;" % (request['stack'], dcall['number'], dcall['t_get']))
		return	dboo.qexecute ('\n'.join (querys))
		print   "<br>".join (querys)
	else:
		print request
		return	False
	
def	save_call (US_ROW, dcall, request):
	print "~log|"	#save_call", request
	querys = []
	curr_tm = int(time.time())
	disp = int(request.get('disp'))
	cnum_total = dcall['cnum_total']
	sfrom = request.get ('sfrom')
	opts = request.get ('opts')
	cnames = []
	values = []
	try:
		sets = []
		for k in ['reslt', 'diagn', 'diat', 'kuda']:
			val = request.get (k)
			if not val:	continue
			if k == 'diagn' and str(dcall['diagn']) == val:	continue
			if k == 'reslt' and str(dcall[k]) == val:	continue
			if k == 'kuda' and dcall[k] != val:		sets.append ("kuda='%s'" % val.strip().replace("'", "''"))
			elif k == 'diat' and (dcall[k] != val or request.get('ds_plus')):
				if request.get('ds_plus'):
					sets.append ("diat='+%s %s'" % (request.get('ds_plus'), val.strip().replace("'", "''")))
				else:	sets.append ("diat='%s'" % val.strip().replace("'", "''"))
			else:
				if dcall[k] != val:	sets.append ("%s=%s" % (k, val))
		if request.get ('ds_plus') and not request.get('diat'):	sets.append ("diat='+%s'" % request.get('ds_plus'))
		if sets:
			sset_call = ", ".join(sets)
			swhere_call = "cnum_total = %s" % cnum_total
			querys.append ("UPDATE %s SET %s WHERE %s;" % (sfrom, sset_call, swhere_call))
			querys.append (qhistory_calls (curr_tm, disp, sfrom, sset_call.replace("'", "''"), swhere_call))
			print	"<br>".join (querys)	#[sset_call, swhere_call])
		'''
			if dboo.qexecute ('\n'.join (querys))
			dcall = dboo.get_dict ("SELECT * FROM call WHERE cnum_total = %s" % cnum_total)
		'''
		for k in dcall.keys():
			if k in ['t_wait', 't_serv', 't_hosp']:	continue
			if dcall[k] != None:
				cnames.append (k)
				values.append ("'%s'" % dcall[k])
		'''
		print "<br>", ", ".join (cnames)
		print "<br>", ", ".join (values)
		'''
		querys = ["INSERT INTO calls_arch (%s) VALUES (%s);" % (", ".join (cnames), ", ".join (values))]
		querys.append ("DELETE FROM call WHERE cnum_total = %s;" % cnum_total)
		querys.append ("INSERT INTO history_calls (tm, who_disp, sfrom, sset, swhere, rem) VALUES (%s, %s, '%s', '%s', '%s', '%s');" % (
				curr_tm, disp, 'call', "DELETE", "cnum_total = %s" % cnum_total, "INSERT INTO calls_arch"))
		return	dboo.qexecute ('\n'.join (querys))
		print   "<br>".join (querys)
	except:
		print "<br>except:", request
		return	False

	
def	out_fcall (US_ROW, request):

	cnum_ttl = request.get('cnum_ttl')
	if request.get('is_arch'):
		is_arch = True
	else:	is_arch = False
	if not cnum_ttl:	return
	query = "SELECT * FROM call WHERE cnum_total = %s" % cnum_ttl
	dcall = dboo.get_dict (query)
	print "~log|out_fcall:", 'is_arch:', is_arch
#	return
	if dcall:
		if request.get('reasn'):
			if update_call (US_ROW, dcall, request):	dcall = dboo.get_dict (query)
		
		if not dcall.get('reasn'):
				import	tree_reasn
				request['cnum_total'] = str (cnum_ttl)
				return	tree_reasn.view_alert(request)

		if request.get('exec') and request['exec'] == 'UPDATE':
			if update_call (US_ROW, dcall, request):
				dcall = dboo.get_dict (query)
			else:	return
		if request.get('exec') and request['exec'] == 'CLOSE':
			if save_call (US_ROW, dcall, request):
				print "~RESULT|", "<span class='bfinf'> &nbsp; Вызов %s (%s) успешно сохранен в ахиве. </span>" % (dcall.get('number'), dcall.get('cnum_total'))
				print   """~eval| set_shadow('CLL_OPER');"""
				print "~log|"
				dcall = dboo.get_dict (query)
			else:	print "####"
			return
	else:	# Нет в Оперативной обстановке
		query = "SELECT * FROM calls WHERE cnum_total = %s" % cnum_ttl
		dcall = dboo.get_dict (query)
		if dcall['number'] == 0:
			request['tkt_number'] = str(dcall['cnum_total'])
			return	get_call (US_ROW, request)
		print "ARCH"
		if not dcall:
			print """~eval| alert("out_fcall: Not call cnum_ttl: %s")""" % request.get('cnum_ttl')
			return
		is_arch = True
		if request.get('exec') and request['exec'] == 'UPDATE':
			request['sfrom'] = 'calls'	### Правка в Архиве
			if update_call (US_ROW, dcall, request):
				dcall = dboo.get_dict (query)
			else:	return

	print "US_ROW: ARM:", US_ROW['armid'], US_ROW['disp'], "<br>"
#	print "request:", request, "<br>"
	opts = {}
	obj = {}
	cstt = clc_cstatus (dcall)
	if is_arch:	obj['is_arch'] = True
	for k in dcall.keys():
		if k in ['diagn', 'reslt', 'diat', 'kuda']:	continue
		if dcall[k]:
			if k == 'reasn':
				obj[k] = "%s" % T.svals (dboo, dictin[k], dcall[k])
			elif k == 'br_ref':
				obj[k] = T.ref2brg (dboo, dcall['br_ref'], cstt)	#clc_cstatus (dcall))
			elif k in ['place', 'kto', 'subst', 'doctor']:	#, 'pbrg']:
				obj[k] = "%s" % T.svals (dboo, dictin[k], dcall[k])
		#		obj[k] = "%s" % T.sselect (dboo, dictin['place'], dcall[k])
			elif k in ['t_get', 't_send', 't_arrl', 't_done', 't_close']:
				if k == 't_get':	obj['d_get'] = "%s" % sdtime (dcall[k], "%d.%m.%Y")
				obj[k] = "%s" % sdtime (dcall[k])
		#	elif k in ['diagn', 'reslt']:		obj[k] = T.svals (dboo, dictin[k], dcall[k])
			else:	obj[k] = "%s" % str(dcall[k])
		else:
			if k == 't_done' and not dcall[k]:	obj[k] = """<span class='cbutt' onclick="set_t_done(%s,'%s');"> Исполнен </span>""" % (dcall['cnum_total'], request.get('shstat'))
			if k == 't_arrl' and not dcall[k] and not dcall['t_done']:	obj[k] = """<span class='cbutt' onclick="set_t_arrl(%s,'%s');"> Прибыл </span>""" % (dcall['cnum_total'], request.get('shstat'))
	smessg = T.get_crem_all (dboo, dcall['cnum_total'])
	if smessg:	obj['message_text'] = "<div class='omsno'> %s </div>" % smessg
	#	user_is ("DISP_PS|ZAV_PS|V_LINE", $urow->type)
	fast_DS = [56, 99, 138, 162]		#['158', '159', '161', '162']
	fast_reslt = [8, 10, 11, 21, 22]	#['11', '12', '13', '15', '16', '21', '22', '29']
	if T.user_rights(US_ROW):
		skuda = ds_plus = sdiat =''
		if dcall['kuda']:	skuda = str(dcall['kuda'])
		if dcall['diat']:
			spd = dcall['diat'].split()
			if spd[0][0] in "-+" and spd[0][1:].isdigit():
				ds_plus = spd[0][1:]
				sdiat = " ". join(spd[1:])
			else:	sdiat = dcall['diat']
	#	if dcall['t_done'] and not dcall['reslt'] and dcall['reslt'] < 80:	# and cstt < 16:
		if dcall['t_done'] and cstt in [11, 15]:	#, 27, 29, 31]:
			obj['is_reslt'] = True
			fsr_list = ['&nbsp;']
			for k in fast_reslt:
				fsr_list.append("""<span class='cbutt' onclick="document.myForm.reslt.value = '%s'; "> %02d </span>""" % (k, k))
			dictin['reslt']['where'] = 'num > 0 AND num < 80'
			obj['reslt'] = T.sselect (dboo, dictin['reslt'], dcall['reslt']) + "\n".join(fsr_list)
			fsd_list = ['&nbsp;'] 
			for k in fast_DS:
				fsd_list.append("""<span class='cbutt' onclick="document.myForm.diagn.value = '%s'; "> %s </span>""" % (k, k))

			dictin['diagn']['sname'] = 'diagn'
			obj['diagn'] = T.sselect (dboo, dictin['diagn'], dcall['diagn']) + "\n".join(fsd_list)
			dictin['diagn']['where'] = 'num >= 200'
			dictin['diagn']['sname'] = 'ds_plus'
			obj['ds_plus'] = T.sselect (dboo, dictin['diagn'], ds_plus)
			obj['diat'] = inputText ('diat', sdiat, "size=42")
			obj['kuda'] = inputText ('kuda', skuda, "size=28")
			obj['SAVE'] = """<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('open_call&exec=UPDATE&opts=EDIT&cnum_ttl=%s&sfrom=call');">""" % cnum_ttl
			obj['CLOSE'] = """<input type='button' class='butt' value='Закрыть (в Архив)' onclick="call_done(%s, 'call');">""" % cnum_ttl
	#	elif cstt in [27, 29, 31]:			obj['CALL_CLOSE'] = "<span class='tit'> &nbsp; Результаты для ОМС 111 </span> %s" % dcall['reslt']
			
		else:
			obj['reslt'] = T.svals (dboo, dictin['reslt'], dcall['reslt'])
			obj['diagn'] = T.svals (dboo, dictin['diagn'], dcall['diagn'])
			if ds_plus:	obj['ds_plus'] = T.svals (dboo, dictin['diagn'], ds_plus)
			obj['diat'] = sdiat	#str(dcall['diat'])
			obj['kuda'] = skuda
			print "~log|", dcall['reslt'], type(dcall['reslt'])

		if dcall['reslt']:	obj['is_reslt'] = True

		if cstt in [0, 1]:
			obj['set_refuse'] = "call_refuse(%s, %s);" % (cnum_ttl, cstt)
			obj['refuse'] = T.sselect (dboo, dictin['refuse'], ds_plus)
			obj['set_brigad'] = "update_call(%s)" % cnum_ttl
			obj['SET_BRIGS'] = offer_brigs  (dcall)	#"SET_BRIGS"
		elif cstt == 3:
			obj['set_pdelay'] = "call_pdelay(%s, %s);" % (cnum_ttl, cstt)
			obj['pdelay'] = T.sselect (dboo, dictin['pdelay'], ds_plus)
			obj['set_pcancel'] = "call_pcancel(%s, %s);" % (cnum_ttl, cstt)
			obj['pcancel'] = T.sselect (dboo, dictin['pcancel'], ds_plus)
			obj['BSTT_GOTO'] = "BSTT_GOTO"
		elif cstt == 7:
			if dcall['reslt'] and dcall['reslt'] in reslt_hospital:
				obj['kuda'] = inputText ('kuda', skuda, "size=28")
				obj['SAVE'] = """<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('call_form&exec=SAVE&cnum_ttl=%s&sfrom=call');">""" % cnum_ttl
		elif cstt in [27, 29, 31]:
			obj['CALL_CLOSE'] = "<span class='tit'> &nbsp; Результаты для ОМС 222 </span> %s" % dcall['reslt']
			setobj4oms (obj, dcall)
		else:
			wlist = []
			fff = "<span class='warning'> %s </span>"
			if not dcall['reslt']:	wlist.append (fff % "Отсутствует Резултат!")
			if not dcall['diagn']:	wlist.append (fff % "Отсутствует DS (диагноз) !")
			if dcall['reslt'] and dcall['reslt'] in reslt_hospital:
				if not dcall['kuda']:	wlist.append (fff % "Отсутствует адрес, Куда доставили!")
			if wlist:
			#	obj['CALL_CLOSE'] = "<span class=''> %s </span>" % " &nbsp; ".join(wlist)
				obj['CALL_WAR'] = "<div class=''> %s </div>" % " &nbsp; ".join(wlist)
			else:	#pass
				obj['CALL_CLOSE'] = """<table width=100%%><tr><td><span class='tit'> &nbsp; Результаты для ОМС Else </span></td><td align='right'>
				<input class='butt' type='button' value='Сохранить в Рестре' onclick="set_shadow('call_form&exec=SAVEOMS&cnum_ttl=%s')"></td></tr></table>""" % cnum_ttl
				if dcall.get('age'):	# and dcall['age'].isdigit():
					atm = dcall.get('t_get') - 31536000*int(dcall.get('age'))
				else:	atm = 0
				obj['myar'] = time.strftime("%Y", time.localtime (atm))
				setobj4oms (obj, dcall)

		if not is_arch:	obj['BSTT_SERVS'] = button_box (US_ROW, dcall, cstt)
		
	print "~calls|"
#	print "<div id='call_form' type='hidden' style='top: 60px; left: 300px; width: 900px; min-height: 400px; border: thin solid #668; background-color: #ffe; position: absolute; z-index: 1112'>"
	parse_forms (opts, obj, 'call.html')
#	print	"</div>	<!-- call_form	-->"
	print   """~eval| $('#off_brigs tr.line').hover (function () { $('#off_brigs tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""
	if request.get('exec') == 'UPDATE':
		print	"""~eval| set_shadow('CLL_OPER');"""

def	button_box (US_ROW, dcall, cstt):	# sfrom
	armid = US_ROW['armid']
	if cstt in [11, 15]:	return
	lout = [" &nbsp;! ", " &nbsp;! ", " &nbsp;! ", " &nbsp;! ", " &nbsp;! ", " &nbsp;! ", " &nbsp;! "]
	if cstt == 1:
		if not dcall['number']:
			lout[0] = """<input type='button' class='butt' value='Сохранить' onclick="new_call_save();" />"""
	#	lout[1] = """<input type='button' class='butt' value='Отказать' onclick="call_refuse(%s, %s);" /> """ % (dcall['cnum_total'], cstt)
		lout[1] = """<input type='button' class='butt' value='Отказать' onclick="calls_alert('refuse', %s, %s);" /> """ % (dcall['cnum_total'], cstt)
	#	lout[3] = """<input class="butt" type="button" value="Править" />"""
	#	lout[4] = """<input class="butt" type="button" value="Дублировать" />"""
		lout[6] = """<input class="butt" type="button" value="Повторный" />"""
		return	"</td><td width=14%>".join(lout)
	elif cstt == 3:
		lout[0] = """<input class="butt" type="button" value="Отменить назначение" onclick="calls_alert('pcancel', %s, %s);" />""" % (dcall['cnum_total'], cstt)
		lout[1] = """<input class="butt" type="button" value="Задержка в пути" onclick="calls_alert('pdelay', %s, %s);" />""" % (dcall['cnum_total'], cstt)
	elif armid in ['DISP_NP', 'DISP_PS', 'SVOO']:	# V_LINE - Врач л. бригады
	#	"""<input type='button' class='butt' value='Сохранить' onclick="set_shadow('new_call');" />	""",
	#	"""<input type='button' class='butt' value='Отказать' onclick="{{set_refuse}}" />	""",
		lout[3] = """<input class="butt" type="button" value="Править" />"""
		lout[4] = """<input class="butt" type="button" value="Дублировать" />"""
		lout[5] = """<input class="butt" type="button" value="Вызвать на себя" />"""
	#	lout[6] = """<input class="butt" type="button" value="Повторный" />"""
	return	 "</td><td width=16%>".join(lout)	#	"BSTT_SERVS"	# US_ROW

def	calls_alert (US_ROW, request):	# label, cnum_ttl, cstt):
	alert_nammes = {
		'refuse':	"Отказать в приеме",
		'pcancel':	"Отменить назначение",
		'pdelay':	"Задержка в пути",
		}
	label = request.get('label')
	alabel = alert_nammes.get(request.get('label'))
	cnum_ttl = request.get('cnum_ttl')
	cstt = request.get('cstt')
	'''
	lout = ["""<table width=100%% style="background-color: #c66; color: #eef;"><tr><td> &nbsp; %s </td>
		<td align='right'><span class='cbutt bfinf' onclick="if (document.myForm.r_refuse.value) set_shadow('GET_CALL&stat=refuse&cnum_ttl=%s&cstt=%s'); else alert('ZZZ'); "> Применить </span></td>
		<td align='right' onclick="$('#RESULT').html(''); " ><img src="/smp/img/close_icon.png"></td></tr></table>""" % (alabel, cnum_ttl, cstt)]
	'''
	lout = ["""<table width=100%% style="background-color: #c66; color: #eef;"><tr><td> &nbsp; %s </td>
		<td align='right' onclick="$('#RESULT').html(''); " ><img src="/smp/img/close_icon.png"></td></tr></table>""" % alabel]
	armid = US_ROW['armid'].strip()
#	lout.append (str(request))
	if label in ['refuse', 'pcancel']:
		if armid in ['DISP_03', 'DISP_NP', 'DISP_PS']:
			query = "SELECT cod, name FROM refuse ORDER BY cod"
			rows = dboo.get_rows (query)
			for r in rows:
				cod, name = r
			#	lout.append ("""<li class='line' style="list-style: none;" ><label><input type="radio" name="r_refuse" value='%s'> %s </label></li>""" % (cod, name))
				lout.append ("""<li class='line' style="list-style: none;" onclick="set_shadow('open_call&cnum_ttl=%s&exec=UPDATE&opts=refuse&sel_refuse=%s');" > &nbsp; %s </li>""" % (cnum_ttl, cod, name))
		elif armid in ['ZAV_PS', 'SVOO']:
			query = "SELECT num, name FROM new_reslt WHERE num > 80 ORDER BY num"
			rows = dboo.get_rows (query)
			for r in rows:
				num, name = r
			#	lout.append ("""<li class='line' style="list-style: none;" > &nbsp; %s %s </li>""" % (num, name))
				lout.append ("""<li class='line' style="list-style: none;" onclick="set_shadow('open_call&cnum_ttl=%s&exec=UPDATE&opts=pcancel&sel_pcancel=%s');" > &nbsp; %s </li>""" % (cnum_ttl, num, name))
		'''
	elif label == 'pcancel':
		query = "SELECT num, name FROM new_reslt WHERE num > 80 ORDER BY num"
		rows = dboo.get_rows (query)
		for r in rows:
			num, name = r
		#	lout.append ("""<li class='line' style="list-style: none;" > &nbsp; %s %s </li>""" % (num, name))
			lout.append ("""<li class='line' style="list-style: none;" onclick="set_shadow('open_call&cnum_ttl=%s&exec=UPDATE&opts=pcancel&sel_pcancel=%s');" > &nbsp; %s </li>""" % (cnum_ttl, num, name))
		'''
	elif label == 'pdelay':
		query = "SELECT cod, name FROM pdelay ORDER BY cod"
		rows = dboo.get_rows (query)
		for r in rows:
			cod, name = r
			lout.append ("""<li class='line' style="list-style: none;" onclick="set_shadow('open_call&cnum_ttl=%s&exec=UPDATE&opts=pdelay&sel_pdelay=%s');" > &nbsp; %s </li>""" % (cnum_ttl, cod, name))
	return	"\n".join (lout)	#	True

def	setobj4oms (obj, dcall):
	obj['faml'] = dcall['name']
	if dcall['name2']:
		no = dcall['name2'].replace('.',' ').strip().split(' ')
		if no[0]:	obj['fname'] = no[0]
		if len(no) > 1:	obj['oname'] = no[1]
	obj['msex'] = dcall['sex']
#	if dcall['age'] and dcall['age'].strip().isdigit():	obj['myar'] = "%s" % (2019 - int(dcall['age']))
	'''
	query = "SELECT class FROM new_ds_class WHERE ind = (SELECT class FROM new_ds WHERE num = %s)" % dcall['diagn']
	row = dboo.get_row(query)
	ch_cod = row[0].strip()
	query = "SELECT cod, ch_cod, name FROM mkb_group WHERE ref_group = (SELECT cod FROM mkb_group WHERE ch_cod LIKE '%s %%')" % ch_cod
	'''
	query = "SELECT cod, ch_cod, name FROM mkb_group WHERE ref_group = (SELECT cod FROM mkb_group WHERE ch_cod = (SELECT class FROM new_ds_class WHERE ind = (SELECT class FROM new_ds WHERE num = %s)))" % dcall['diagn']
	print "~log|", query
	rows = dboo.get_rows(query)
	if rows:
		ss_list = []
		for r in rows:	ss_list.append ("<option value='%s'> %s %s </option>" % (r[0], r[1], r[2]))
		obj['mkb_class'] = "\n".join(ss_list)

	query =	"SELECT ch_cod, name FROM mkb10 WHERE id_row IN (SELECT id_mkb FROM mkb2diagn WHERE nds = %s) ORDER BY ch_cod" % dcall['diagn']
	rows = dboo.get_rows(query)
	if rows:
		ss_list = []
		for r in rows:	ss_list.append ("<option value='%s'> %s </option>" % (r[0], r[1]))
		obj['mkb_ds'] = "\n".join(ss_list)
	'''
	"SELECT ch_cod, name FROM mkb10 WHERE id_row IN (SELECT id_mkb FROM mkb2diagn WHERE nds = {$row->num}) OR ch_cod='$mkb_cod' ORDER BY ch_cod"
	"SELECT ch_cod, name FROM mkb10 WHERE id_row IN (SELECT id_mkb FROM mkb2diagn WHERE nds = {$row->num}) ORDER BY ch_cod";
	'''

def	offer_brigs  (dcall):
	""" Предложение Бригад	"""
	if dcall.get('nsbrg'):	nsbrg = dcall.get('nsbrg')
	else:			nsbrg = dcall.get('subst')
	res = dboo.get_table ('vbnaryd', "stat > 0 AND n_pst = %s" % nsbrg)	# dcall.get('nsbrg'))
	if not res:	return "Нет данных"
	d = res[0]
	blist = ["<table id='off_brigs' width=100%>"]
	list_col = ['br_id', 'smena', 'n_pst', 'street', 'doc_name', 'stat_name']
	ll = []
	for k in list_col:
		ll.append (cname_brig.get(k))

	blist.append ("<tr><th>%s</th><th>R</th></tr>" % "</th><th>".join(ll))
	for r in res[1]:
	#	saddres (r[d.index('street')], r[d.index('house')])<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>
		sttr = """<tr class='line' onclick="set_brig (%s, %s, '%s');">""" % (r[d.index('number')], r[d.index('br_id')], r[d.index('profile')])
		blist.append ("%s<td> %s </td><td> %s </td><td> %s </td><td><b> %s </b> </td><td> %s </td><td>  %s </td><td> sss </td></tr>" % (sttr,
			slab_brig (r[d.index('number')], r[d.index('profile')], r[d.index('stat')]),	#r[d.index('number')],
			r[d.index('smena')], r[d.index('n_pst')],
			saddres (r[d.index('street')], r[d.index('house')]),
			r[d.index('doc_name')], r[d.index('stat_name')]))
	blist.append("</table>")
	if blist:
		return	"\n".join(blist)
	

def	calls_list (SS, request):
	""" Список Вызовов в ОО	"""
	US_ROW = SS.objpkl.get('us_row')
	print "calls_list: ZZZ", request
	obj = {}
	opts = {}
	ssubst = splace = scwfind = scorder = sbservis = None
#	print	"~calls|"
	if request.get('shstat') == 'CLL_OPER':		print	"~mybody|"
	for k in request.keys():
		if k == 'sel_subst':			ssubst = request.get('sel_subst')
		if k == 'sel_place':			splace = request.get('sel_place')
		if k == 'sel_cwfind':			scwfind = request.get('sel_cwfind')
		if k == 'sel_corder':			scorder = request.get('sel_corder')
		if k == 'sel_badservis':		sbservis = request.get('sel_badservis')

	lwheres = []
	if request.get('ffc_head'):
		obj['ffc_head']	= True
	#	if request.get('sel_badservis'):	sbservis = request.get('sel_badservis')
		if request.get('like_street'):	lwheres.append ("street LIKE '%s%%'" % request.get('like_street').strip())	# pass
		if request.get('like_house'):	lwheres.append ("house LIKE '%%%s%%'" % request.get('like_house').strip())
		if request.get('like_name'):	lwheres.append ("name LIKE '%s%%'" % request.get('like_name').strip())
		if request.get('call_numbers'):	lwheres.append ('number IN (%s)' % ",".join (request.get('call_numbers').strip().split()))	#pass
		if request.get('sub_numbers'):	pass
		if request.get('brg_numbers'):	lwheres.append ('nsbrg IN (%s)' % ",".join (request.get('brg_numbers').strip().split()))
		if request.get('reslt_cod'):	lwheres.append ('reslt IN (%s)' % ",".join (request.get('reslt_cod').strip().split()))
		if request.get('diagn_cod'):	lwheres.append ('diagn IN (%s)' % ",".join (request.get('diagn_cod').strip().split()))
		if request.get('like_kuda'):	lwheres.append ("kuda LIKE '%%%s%%'" % request.get('like_kuda').strip())
		'''	oms	r9x	cn_total
		if request.get(''):	pass
		if request.get(''):	pass
		if request.get(''):	pass
		'''
	else:	sbservis = None
	if sbservis:	# Обслуживание	select * FROM ss_badservise;
		if sbservis == 't_send':	lwheres.append ("(t_send - t_get) > 1200")	# t_send | Задержки передачи	20 min
		if sbservis == 't_done':	lwheres.append ("(t_arrl > 0 AND (t_done - t_arrl) > 3000) OR (t_arrl IS NULL AND (t_done - t_send) > 3600)")	# t_done | Длит. обслуживание
		if sbservis == 'delete':	lwheres.append ("reslt > 80")			# delete | Удаленные вызова
		if sbservis == 'double':	lwheres.append ("number IN (SELECT number FROM calls2 WHERE (t_get - prim_t) > 0 AND (t_get - prim_t) < 86400 )")	# double | Повторные вызова
		if sbservis == 'letal':		lwheres.append ("reslt IN (28, 29, 30)")	# letal  | Летальные исходы
	
	armid = US_ROW['armid'].strip()
	if armid == 'DISP_PS':
		obj['DISP_PS'] = True
		ssubst = US_ROW.get('subst')
		obj['subst'] =  T.svals (dboo, dictin['sel_subst'], ssubst)
	else:
		obj['sel_subst'] = T.sselect (dboo, dictin['sel_subst'], ssubst)	#, kval"SSS" subst
	obj['sel_place'] = T.sselect (dboo, dictin['sel_place'], splace)	#, kval"SSS" place	Место
	obj['sel_cwfind'] = T.sselect (dboo, dictin['sel_cwfind'], scwfind)	#, kval"SSS" cwfind	Где искать 
	obj['sel_corder'] = T.sselect (dboo, dictin['sel_corder'], scorder)	#, kval"SSS" corder
	obj['sel_badservis'] = T.sselect (dboo, dictin['sel_badservis'], sbservis)
	if request.get('shstat') == 'CLL_OPER':		parse_forms (opts, obj, 'find_calls.html')

	print "~list_calls|"
	sfrom = 'call'
	if scwfind:
		if scwfind == '1':	lwheres.append('t_get > 0 AND t_done IS NULL')	# в Работе
		elif scwfind == '2':	lwheres.append('t_get > 0 AND t_send IS NULL')	# Ждущие
		elif scwfind == '3':		# Исполненые
			sfrom = 'calls_arch'
			lwheres.append('t_done > 0 AND id_ims IS NULL AND reslt < 89')
		elif scwfind == '4':		# Закрытые
			sfrom = 'calls_arch'
			lwheres.append('t_close > 0 AND reslt < 89')
		elif scwfind == '7':
			sfrom = 'tkt_calls'
			lwheres.append('tkt_number > 0')
		elif scwfind == '10':	sfrom = 'calls_arch'
		elif scwfind == '11':	sfrom = 'calls_glob'
		else:	lwheres.append('t_get > 0')
	if not lwheres:	lwheres.append('t_get > 0')
	if ssubst:	lwheres.append("nsbrg = %s" % ssubst)
	if splace:	lwheres.append("place = %s" % splace)

	swhere = " AND ".join(lwheres)	#'t_get > 0'
	sorder = 'ORDER BY t_get DESC'
	if scorder:	# Сортировать	pass
		if scorder == '2':	sorder = 'ORDER BY number'
		elif scorder == '3':	sorder = 'ORDER BY street, t_get DESC'
		elif scorder == '4':	sorder = 'ORDER BY name, t_get DESC'
		
#	print "WHERE", " AND ".join(lwheres), time.time()
	res = dboo.get_table(sfrom, "%s %s" % (swhere, sorder))
	if not res:
		if not dboo.last_error:
			print "<span class='bfinf'> &nbsp; Нет данных! &nbsp; </span><br>"
		print "calls_list get_table:", sfrom, swhere, sorder
		return
	d = res[0]	# r[d.index('')]
	clist = []
	sfrom_oo = ['tkt_calls', 'call', 'call']
	lic =	"""<li class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" onclick="open_call(%s)">"""		#alert('%s');">"""

#	print """<div id="list_calls" style="border: thin solid #668; width: 100%; position: absolute; background-color: #fff; padding: 2px; min-height: 20%; max-height: 90%; overflow: auto;">"""
#	parse_forms ({}, {}, 'list_calls.html')
	print "<table id='tbl_calls' width=100%>"
	'''
	print "<thead>"
	if sfrom in sfrom_oo:
	#	print "<tr><th colspan=2 width=370px> Вызова </th><th>П/С</th><th width=250px> ФИО </th><th colspan=5 width=340px> Обслуживание </th><th width=100px> Бригады </th></th><th> Примечания </th></tr>"
		print "<tr><th colspan=2 > Вызова </th><th>П/С</th><th > ФИО </th><th colspan=5 > Обслуживание </th><th > Бригады </th></th><th> Примечания </th></tr>"
	else:	print "<tr><th colspan=2> Вызова </th><th>П/С</th><th> ФИО </th><th colspan=5> Обслуживание </th><th colspan=1> Бригады </th></th><th> ОМС </th><th> Примечания </th></tr>"
	print "</thead><tbody>"
	'''
	print "<tr style='background: #bcd;'><th colspan=2> Вызова </th><th> П/С  </th><th> ФИО </th><th colspan=5> Обслуживание </th><th colspan=1> Бригады </th></th><th> Примечания </th></tr>"
	for r in res[1]:
		cstt = clc_cstatus(r, d)
		cclass, cimg = cdef2cstt (cstt)
		saddr = "%s" % r[d.index('street')]
		if r[d.index('house')]:		saddr += " д.%s" % r[d.index('house')]
		if r[d.index('korp')]:		saddr += " к.%s" % r[d.index('korp')]
		cnum_total = r[d.index('cnum_total')]
		soncall = """onclick="open_call(%s);" """ % r[d.index('cnum_total')]
		sreasn = "<span class='line %s'> %s %s <b>%s </b> </span>" % (cclass, cimg, r[d.index('number')], r[d.index('reasn')])
		print """<tr class='line' id='c%06d' ><td %s width=140px>%s</td>""" % (cnum_total, soncall, sreasn)
#		print "<td>%s</td>" % r[d.index('nsbrg')]
		print "<td %s width=250px>%s</td>" % (soncall, saddr)
		print "<td width=20px>", r[d.index('nsbrg')], "</td>"
		if r[d.index('name2')]:
			sfio = "<span class=bfligt> %s %s </span> &nbsp; л.%s %s" % (r[d.index('name')], r[d.index('name2')], r[d.index('age')], r[d.index('sex')])
		else:	sfio = "<span class=bfligt> %s </span> &nbsp; л.%s %s" % (r[d.index('name')], r[d.index('age')], r[d.index('sex')])
		print """<td width=250px %s> %s </td>""" % (soncall, sfio)
		tms = []
		knames = {'t_arrl': "Прибл", 't_done': "Исполн", 't_close': "Закрыть"}
		for k in ['t_get', 't_send', 't_arrl', 't_done', 't_close']:
			if r[d.index(k)]:
				tms.append ("<b> %s </b>" % sdtime(r[d.index(k)]))
			elif cstt == 1:
				tms.append ("<span %s>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>" % soncall)
			elif cstt in [3,7] and k in ['t_arrl', 't_done']:
				tms.append ("""<span class='cbutt' onclick="set_%s(%s,'%s');"> %s </span>""" % (k, cnum_total, request.get('shstat'), knames[k]))	#	tms.append (" &nbsp; ")
			elif cstt in [11,15] and k == 't_close':
				tms.append ("""<span class='cbutt' %s"> %s </span>""" % (soncall, 'Закрыть'))
	#		elif cstt > 7:		tms.append (" &nbsp; ")
			else:	tms.append (" &nbsp; ")
	#	tms.append (str("&nbsp;"))
	#	tms.append (str(cstt))
		print "<td width=56px>%s</td>" % "</td><td width=60px>".join(tms)
		if r[d.index('br_ref')]:
			print "<td width=90px align='center'> %s </td>" % T.ref2brg(dboo, r[d.index('br_ref')], cstt)	#clc_cstatus(r, d))
		else:	print "<td width=90px align='center'> &nbsp; </td>"
		screm = T.get_crem_last (dboo, cnum_total)	#"crem"	#T.sselect (dboo, dictin['crem'], 0)	# примечания ???
		if sfrom in sfrom_oo:
		#	dictin['crem']['where'] = "cnum_total = %s" % cnum_total
			'''
			if r[d.index('t_done')]:
				if not r[d.index('reslt')]:	print """<td width=280px><span class='warning'> Отсутствует Резултат. </span> </td>"""
				elif not r[d.index('diagn')]:	print """<td width=280px><span class='warning'> Отсутствует DS (диагноз). </span> </td>"""
				else:				print """<td width=280px><span class='warning'> Нет ОМС &nbsp; </span> </td>"""
			else:
			'''
			print """<td width=280px title="Добавить примечание" onclick="alert('Добавить примечание');"><i class="fa fa-plus fa-lg line bffff" ></i> %s </td>""" % screm
		else:
			if r[d.index('id_ims')]:
				soms = "<span class='green'> ЕСТЬ </span>"
			else:	soms = "<span class='tmp'> &nbsp;НЕТ&nbsp; </span>"
	#		print """<td width=240px> %s </td><td> %s </td>""" % (sfio, soms)	#r[d.index('id_ims')])
			print """<td> %s </td>""" % soms	
			print """<td width=270px > %s </td>""" % screm
		print "<td width=20px> %s </td>" % cstt
	if clist:
		print "\n".join(clist)
	print	"</tbody>"
	print	"</table>	<!-- tbl_calls	-->"
#	print	"</div>	<!-- list_calls	-->"

	print	"""~eval| $('#tbl_calls tr.line').hover (function () { $('#tbl_calls tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""
	print   """~eval| $('#len_list').html(" &nbsp; <span class='bfinf'> &nbsp; Найдено %s Вызовов. &nbsp; </span>"); """ % len(res[1])

#	Отмена назначенного вызова
def	set_ttime (request):
	""" Проставить отметки времени	"""
	print	"AAAAAA", request
	t2disp = {'t_send': 's_disp', 't_arrl': 'a_disp', 't_done': 'd_disp', 'c_disp': 't_clos' }
	try:
		cnum_ttl = int (request.get('cnum_ttl'))
		disp = int (request.get('disp'))
		tname = request.get('ttime')
		if tname not in t2disp.keys ():	
			print "ERROR: not time name '%s'", tname
			return
		curr_tm = int(time.time())
		sset = "%s = %s, %s = %s" % (tname, curr_tm, t2disp.get(tname), disp)
		swhere = "cnum_total = %s" % cnum_ttl
	#	query = "INSERT INTO history_calls (tm, who_disp, sfrom, sset, swhere) VALUES (%s, %s, 'call', '%s', '%s');\nUPDATE call SET %s WHERE %s" % (curr_tm, disp, sset, swhere, sset, swhere)
		query = "%s\nUPDATE call SET %s WHERE %s" % (qhistory_calls (curr_tm, disp, 'call', sset, swhere), sset, swhere)
		print	query, dboo.qexecute (query)
	except:	print "ERROR: set_ttime", request

if __name__ == "__main__":
	US_ROW =	{'disp': 6613, 'ip_loc': '*', 'tm_upd': None, 'utype': 8, 'smena': None, 'subst': 6, 'cod': 606, 'tname': 'Дисп. ПС', 'type': 8, 'fio': 'Татаркина М.Н.'}
	request =	{'disp': '6613', 'this': 'ajax', 'bm_ssys': '2', 'leaflet-base-layers': 'on', 'shstat': 'CLL_OPER'}	# CLL_WAIT CLL_ALL1
	calls_list(US_ROW, request)
"""
N выз	Повд	П	п/с	Принят	N бриг.	Пердн	Прибл	Исплн	Улица	Дом	Задержки
 436 	   34Ф	Ф 	12 	14:18 	 216 	14:18 	14:18 	-:- 	+39 БОЛЬНИЦА 	
	 
 435 	*  13Л	Л 	7 	14:17 	 713 	14:18 	-:- 	-:- 	БОРИСА КОРНИЛОВА 	8 


SELECT * FROM pdelay ORDER BY cod ;
 cod |    mark     |              name              
-----+-------------+--------------------------------
   1 | Пробка      | Автомобильная пробка
   2 | Переезд     | Закрыт железнодорожный переезд
   3 | Территоря   | Закрыт въезд на территорию
   4 | Адрес       | Уточнение (изменение) адреса 
   5 | Ждем МЧС    | Ожидание помощи МЧС
   6 | Ждем полиц. | Ожидание полиции
   7 | Пешком      | Движение пешком
   8 | Ремонт      | Ремонт без отмены вызова
   9 | Ок. помощи  | Остановка для оказания помощи
  10 | Укладка     | Экстренное пополнение укладки
  11 | ГСМ         | Экстренная заправка ГСМ
"""
