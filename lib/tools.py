#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	time

MAX_SMEN = 4
def	curr_smena (dboo):
	try:
		dsys = dboo.get_dict("SELECT * FROM sys03")
		return	dsys.get('smena')
	except:	return	0

def	next_smena (dboo):
	smena = curr_smena (dboo)
	if smena == MAX_SMEN:
		return	1
	else:	return	smena +1

def	ref2brg (dboo, br_ref, cstt = None):
	if not br_ref:	return	br_ref
	img_brg = '<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>&nbsp;'
	if cstt == 3:
		img_brg = '<i class="fa fa-ambulance fa-lg" aria-hidden="true"></i>&nbsp;'
		clss = 'bfblue'
	elif cstt == 7:
		clss = 'bfinf'
	elif cstt > 26:
		clss = 'mbody'
	else:	clss = 'bfligt'
	try:
		dbrg =dboo.get_dict ("SELECT * FROM vbnaryd WHERE br_id = %s" % br_ref)
		if cstt > 26:	return  """<span class='%s'> %s %s%s </span>	""" % (clss, img_brg, dbrg['number'], dbrg['profile'])
		if dbrg['stat'] in [2, 10]:	clss = 'bferr'
		return	"""<span class='line %s' title='%s' onclick="set_shadow('brg_activ&br_id=%s');"> %s %s%s </span>""" % (clss, dbrg['stat_name'], br_ref, img_brg, dbrg['number'], dbrg['profile'])
		
	except:	return	''

def	sel_smen (dboo, son = None, cs = None):
	if not cs:	cs = curr_smena (dboo)
	if not son:	son = ''
	print 
	ss = ["<select name='sel_smen' %s>" % son]
	for j in xrange(4):
		ns = 1 + j
		if cs and ns == int (cs):
			ss.append ("<option value=%s selected> %s </option>" % (ns, ns))
		else:	ss.append ("<option value=%s> %s </option>" % (ns, ns))
	return	"\n".join(ss)

def	user_rights(US_ROW):
	""" Проверить права пользователя	"""
	return	True

def	get_crem_last (dboo, cnum_total):
	drow = dboo.get_dict ("SELECT * FROM rem2calls WHERE cnum_total = %s ORDER BY tm DESC;" % cnum_total)
	if drow:	return	drow['txt']
	return	""

def	get_crem_all (dboo, cnum_total, cols = ['disp', 'txt']):
	rows = dboo.get_rows ("SELECT %s FROM rem2calls WHERE cnum_total = %s ORDER BY tm DESC;" % (",".join(cols), cnum_total))
#	return "SELECT %s FROM rem2calls WHERE cnum_total = %s ORDER BY tm DESC;" % (cols, cnum_total)
	if rows:
		res = []
		for r in rows:		res.append ("%s %s" % (r[0], r[1]))
		return	"<br>".join(res)
	return  ""

def	sselect (dboo, dctt, kval = ''):
	""" Формировать селектор
	dctt =	{'tab': 'tname', 'key': '...', 'val': '...'[, 'sname': 'sname', 'order': '...', 'on': '...', 'knull': 'text', 'where': '...', 'rvals': {'*' | ['...', ...]}]}
		sname =	имя селектора (иначе sname = tname)
		on =	действие (например onclick ...)
		knull =	добавить строку: <option value=''> text </option>"
	kval =	значение ключа (selected)
	"""

	if not (dctt.has_key('tab') and dctt['tab'] and dctt.has_key('key') and dctt['key'] and dctt.has_key('val') and dctt['val']):	return
	if dctt.has_key('order') and dctt['order']:
		order = "ORDER BY %s" % dctt['order']
	else:	order = "ORDER BY %s" % dctt['key']
	if dctt.has_key('where') and dctt['where']:
		where = "WHERE %s" % dctt['where']
	else:	where = ''
	query = "SELECT %s, %s FROM %s %s %s;" % (dctt['key'], dctt['val'], dctt['tab'], where, order)
#	return "query", query
	rows = dboo.get_rows (query)
	if not rows:	return	query
	drow = dboo.desc
	ss = []
	if dctt.has_key('sname') and dctt['sname']:
		sname = dctt['sname']
	else:	sname = dctt['tab']
	if dctt.has_key('on'):
		son = dctt['on']
	else:	son = ''
	ss.append ("<select name='%s' %s>" % (sname, son))
	if dctt.has_key('knull'):
		ss.append ("<option value=''> %s </option>" % dctt['knull'])
	rvals = dctt.get('rvals')
	for r in rows:
		if str(kval).strip() == str(r[0]).strip():
			sltd = 'selected'
		else:	sltd = ''
		if rvals and rvals == '*':
			ss.append ("<option value='%s' %s> %s %s </option>" % (str(r[0]).strip(), sltd, str(r[0]), ' '.join(r[1:])))
		elif rvals and type(rvals) == list:
			ccc = []
			for v in dctt['rvals']:
				if v in drow:	ccc.append (str(r[drow.index(v)]))
			ss.append ("<option value='%s' %s> %s </option>" % (str(r[0]).strip(), sltd, ' '.join(ccc)))
		else:	ss.append ("<option value='%s' %s> %s </option>" % (str(r[0]).strip(), sltd, ' '.join(r[1:])))
	ss.append ("</select>")
	return	"\n".join(ss)

def	svals (dboo, dctt, kval, vals = None):
	"""
	vals = [vn1, vn2, ...] наименвание полей и их последовательность в строке результата
	"""
	if not kval:	return	"--"
	try:
		query = "SELECT * FROM %s WHERE %s = '%s'" % (dctt['tab'], dctt['key'], kval)
	#	print "<br>", query
		drow = dboo.get_dict(query)
		if dctt.has_key('rvals'):
			ccc = []
			for v in dctt['rvals']:
				ccc.append (str(drow[v]))
			return " ".join(ccc)
		return	str(drow[dctt['val']])
	except:	return	"<span class='bferr'>Not (%s %s)</span>"	%(dctt['tab'], kval)
'''	global_vals.py
BTIMER = 900000000

def	sdtime (tm, frmt = "%H:%M"):
	if not tm:	return	"--:--"
	if tm < 777777777:	tm += BTIMER
	return	time.strftime(frmt, time.localtime(tm))
'''
if __name__ == '__main__':
	import dbtools
	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	print sselect (dboo, {'tab': "j_registr", 'key': 'cod', 'val': 'name', 'sname': "sel_name", 'on': "onselect=alert('zzz')", 'knull': '', 'rvals': ['cod', 'name'] })
