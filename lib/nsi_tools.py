#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time

LIBRARY_DIR = r"/home/vds/03/oopy/lib"	    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

bases = {
	'oo': 'host=127.0.0.1 dbname=b03 port=5432 user=smirnov',
	'ss': 'host=127.0.0.1 dbname=ss2013 port=5432 user=smirnov',
	}

import	session, dbtools
import	tools as T
from	parse_forms import *
from	global_vals import *

dboo = dbtools.dbtools (bases['oo'])

dictin = {
	'sel_subst': {'sname': 'sel_subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 3'},
	'sel_category': {'sname': 'sel_category', 'tab': 'sp_category', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0'},
	'sel_stat': {'sname': 'sel_stat', 'tab': 'person_stat', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod >= 0'},
	'sel_post': {'sname': 'sel_post', 'tab': 'sp_post', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0'},
	'sel_usrtype': {'sname': 'sel_usrtype', 'tab': 'sp_usrtype', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod',},
	}

def	main (SS, request):
	""" Доступ к НСИ (первичный анализ запроса)	"""
	global	US_ROW, onchange
	US_ROW = SS.objpkl.get('us_row')
	shstat = request.get('shstat')
	onchange = """onchange="$('#wdg_bc').html(''); set_shadow('%s');" """ %  shstat

#	print	"~mybody|"
#	print   "nsi_tools.main", US_ROW['armid'], request
	if shstat == 'PERSONS':
		sform = request.get('FORM')
		if sform and sform != 'save':
			return	open_pform (SS, request)
		else:	save_pform (SS, request)
		return list_persons (SS, request)
	if shstat == 'USERS':
		sform = request.get('FORM')
		if sform and sform != 'save':
			return	open_uform (SS, request)
		else:	save_uform (SS, request)
		return list_users (SS, request)
	###	main

def	open_uform (SS, request):
	print "pen_uform", request
        print "~wdg_bc|"
	opts = {}
	obj ={}
	obj['title'] = "Пользователь"
	dt = dict_tables.get('tbl_user')
	query = dt['query']
	query += " WHERE u.disp = %s" % request['pkey']
	drow = dboo.get_dict (query)
	print	query
	print 	drow
	for k in drow.keys():
		obj[k] = drow[k]
        parse_forms (opts, obj, "user_form.html")

def	save_uform (SS, request):
	print "save_uform", request

dict_tables = {
	'tbl_user': {
		'table': "<table id='tbl_user' width=700px cellpadding=4 cellspacing=20>",
		'query': "SELECT u.*, p.name AS pname, t.name AS tname, s.name AS sname FROM usr03 u JOIN person_sp p ON u.cod = p.cod LEFT JOIN sp_station s ON subst = s.cod JOIN sp_usrtype t ON type = t.cod",
		'cols': {'disp': "Код", 'pname': "ФИО", 'tname': "Тип (Роль)", 'cod': "Табель.№", 'smena': "Смена", 'sname': "Подстанция", 'login': "Login", 'passwd': "Password", 'ip_loc': "Доступ"},
		'orderl': ['disp', 'pname', 'tname', 'cod', 'smena', 'sname', 'login'],
		'orderf': ['disp', 'pname', 'tname', 'cod', 'smena', 'sname', 'login', 'passwd', 'ip_loc'],
		'pkey': "disp",
		'onclick': "set_shadow('USERS&FORM=view&pfrom=usr03&pkey=%s');",
		}, 
	}
def	list_users (SS, request):
	""" Список пользователей СМП	"""
	global	US_ROW, onchange
	print "list_users", SS, request
	print	"~mybody|"
	print """<div id="list_user" style="width: 100%; position: absolute; background-color: #fff; padding: 2px; min-height: 20%; max-height: 90%; overflow: auto;">"""
	opts = {}
	obj = {}
	sutype = request.get('sel_usrtype')
	dictin['sel_usrtype']['on'] = onchange
	obj['sel_usrtype'] = T.sselect (dboo, dictin['sel_usrtype'], sutype)
	ssubst = request.get('sel_subst')
	dictin['sel_subst']['on'] = onchange
	obj['sel_subst'] = T.sselect (dboo, dictin['sel_subst'], ssubst)
	parse_forms (opts, obj, 'find_users.html')

	wheres = []
	if ssubst:	wheres.append ("subst = %s" % ssubst)
	if sutype:	wheres.append ("type = %s" % sutype)

	out_table_as_list ('tbl_user', where = wheres, order = "pname")
	print "</div>	<!-- list_user	-->"
	print   """~eval| $('#tbl_user tr.line').hover (function () { $('#tbl_user tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""

def	out_table_as_list (mark, where = None, order = None):
	dt = dict_tables.get(mark)
	if not dt:	return

	query = dt['query']
	if where:
		if type(where) == list:
			query += " WHERE %s" % " AND ".join(where)
		else:	query += " WHERE %s" % where
	if order:	query += " ORDER BY %s" % order
	print query
	rows = dboo.get_rows (query)
	d = dboo.desc
	print dt['table'], "<tr>"
	cnames = dt['orderl']
	for k in cnames:	print "<th>%s</th>" % dt['cols'][k]
	jr = 0
	pkey = dt['pkey']
	for r in rows:
		sonclick = 'onclick="%s"' % (dt['onclick'] % r[d.index(pkey)])
		bclass = "%s" % 'bfligt'
		if jr % 2:
			print "<tr class='line %s' id='k%s' bgcolor=#f5f5f5 %s>" % (bclass, r[d.index(pkey)], sonclick)
		else:	print "<tr class='line %s' id='k%s' %s>" % (bclass, r[d.index(pkey)], sonclick)
		jr += 1
		for k in cnames:
			if r[d.index(k)]:
				print "<td>%s</td>" % r[d.index(k)] ,
			else:	print "<td> &nbsp; </td>" ,
		print "</tr>"
	print "</table> <!-- %s\t-->" % mark
	if jr:
		print "<span class='bfinf'> &nbsp; Найдено %s записей &nbsp; </span><br>" % jr
	else:	print "<span class='bfinf'> &nbsp; Нет данных! &nbsp; </span><br>"


def	slist_stat (sform, cod, stat):
	if stat == 0:	return	"Обеспечивает работу СМП"
	lres = []
	if stat > 0:
		query = "SELECT cod, name FROM person_stat WHERE cod & %d > 0" % stat
		rows = dboo.get_rows (query)
		for r in rows:
			lres.append (" %s<br/>" % r[1])
		return	"\n".join(lres)
	else:	
		return	"sform: %s, cod: %s, stat: %s" % (sform, cod, stat)

def	open_pform (SS, request):
	""" Форма Сотрудник СМП (просмотр, редактирование, создание)	"""
#	print	"<div id='prs_form' type='hidden' style='top: 160px; left: 500px; width: 600px; min-height: 400px; border: thin solid #668; background-color: #efe; position: absolute;'>"
	print	"open_pform", request
	opts = {}
	obj = {}
	pcod = request.get('pcod')
	query = """ SELECT p.*, s.name AS sname, ps.name AS psname, c.name AS cname FROM person_sp p
		JOIN sp_station s ON n_pst = s.cod JOIN sp_post ps ON n_post = ps.cod JOIN sp_category c ON n_catg = c.cod
		WHERE p.cod = %s
		""" % pcod
#	print query
	drow = dboo.get_dict (query)
	'''
	print drow.keys()
	['n_catg', 'stat', 'n_pst', 'mdate', 'name', 'smena', 'n_post', 'snils', 'psname', 'sname', 'cod', 'cname']
	'''
	obj['title'] = "Сотрудник СМП"
	sform = request.get('FORM')
	obj['IS_UPDATE'] = True
	cod = drow['cod']
	obj['stat'] = slist_stat (sform, drow['cod'], drow['stat'])
	if sform == 'view':
		obj['UPDATE'] = """<input type='button' class='butt' value='Править' onclick="set_shadow('%s&FORM=edit&pcod=%s')"> """ % (request.get('shstat'), pcod)
		obj['name'] = drow['name']
		if drow['stat'] and (drow['stat'] & 2) == 2:	obj['is_delete'] = "<span class='bferr'> УВОЛЕН </span>"
#	obj['n_pst'], 'n_post', 'n_catg', 
		obj['smena'] = drow['smena']
		obj['snils'] = drow['snils']
		obj['sn_pst'] = drow['sname']
		obj['psname'] = drow['psname']
		obj['cname'] = drow['cname']
		obj['mdate'] = drow['mdate']
		obj['cod'] = drow['cod']
	else:
		obj['UPDATE'] = """<input type='button' class='butt' value='Сохранить' onclick="set_shadow('%s&FORM=save&pcod=%s');">  """ % (request.get('shstat'), pcod)
		obj['name'] = "<input type='text' name='name' value='%s' size=22 />" % sval(drow, 'name')
		obj['cod'] = "<input type='text' name='cod' value='%s' size=3 />" % cod	#sval(dtkt, 'cod')
		obj['snils'] = "<input type='text' name='snils' value='%s' size=12 />" %  sval(drow, 'snils')
		obj['sn_pst'] = T.sselect (dboo, dictin['sel_subst'], sval(drow, 'n_pst'))
	#	obj['sname'] = "<input type='text' name='sname' value='%s' size=3 />" % sval(drow, 'sname')

	obj['pre'] = str(drow)
	
#	print obj
	print "~wdg_bc|"
	parse_forms (opts, obj, "pers_form.html")
#	print	"<div>	<!-- prs_form	-->"

def	save_pform (SS, request):
	print	"save_pform", request

def	list_persons (SS, request):
	""" Показать список Сотрудник СМП	"""
	global	US_ROW, onchange
	print	"~mybody|"
#	US_ROW = SS.objpkl.get('us_row')
#	print	"nsi_tools.main", US_ROW['armid'], request
	opts = {}
	obj = {}
	'''
	spost = request.get('sel_post')
	obj['sel_post'] = T.sselect (dboo, dictin['sel_post'], spost)
	ssmen = request.get('sel_smen')
	obj['sel_smen'] = T.sel_smen (dboo, son = "onchange=\"$('#wdg_bc').html(''); set_shadow('PERSONS');\"", cs = ssmen, fs = True)
	'''
	ssubst = request.get('sel_subst')
	dictin['sel_subst']['on'] = onchange
	obj['sel_subst'] = T.sselect (dboo, dictin['sel_subst'], ssubst)
	scatgr = request.get('sel_category')
	dictin['sel_category']['on'] = onchange
	obj['sel_category'] = T.sselect (dboo, dictin['sel_category'], scatgr)
	sstat = request.get('sel_stat')
	dictin['sel_stat']['on'] = onchange
	obj['sel_stat'] = T.sselect (dboo, dictin['sel_stat'], sstat)

	parse_forms (opts, obj, 'find_persons.html')
	query = """ SELECT p.*, s.name AS sname, ps.name AS psname, c.name AS cname, t.name AS tname FROM person_sp p
		JOIN sp_station s ON n_pst = s.cod
		JOIN sp_post ps ON n_post = ps.cod
		JOIN sp_category c ON n_catg = c.cod
		JOIN person_stat t ON (stat & 253) = t.cod
		"""
	wheres = []
	if not sstat:	wheres.append ("stat & 3 = 1")
	else:		wheres.append ("stat & %s = %s" % (sstat, sstat))
	if ssubst:	wheres.append ("n_pst = %s" % ssubst)
	if scatgr:	wheres.append ("n_catg = %s" % scatgr)
	if wheres:	query += "WHERE %s" % " AND ".join(wheres)
	rows = dboo.get_rows (query)
	if not rows:
		if not dboo.last_error:
			print "<span class='bfinf'> &nbsp; Нет данных! &nbsp; </span><br>"
		else:	print "<span class='bferr'> &nbsp;", dboo.last_error, "&nbsp; </span><br>"
		return
	print """<div id="list_person" style="width: 100%; position: absolute; background-color: #fff; padding: 2px; min-height: 20%; max-height: 90%; overflow: auto;">"""
	print "<table id='tbl_person' width=100%><tr>"
	d = dboo.desc
#	['cod', 'name', 'n_pst', 'n_post', 'n_catg', 'smena', 'stat', 'mdate', 'snils', 'sname', 'psname', 'cname', 'tname']
#	print d
	cnames = ['cod', 'name', 'psname', 'snils', 'sname', 'cname', 'tname']
	for k in cnames:	print "<th>%s</th>" % k
	for r in rows:
		sonclick = """ onclick="set_shadow('PERSONS&FORM=view&pcod=' +'%s' +'&pfrom=' +'%s');" """ % (r[d.index('cod')], 'person_sp')
		bclass = "%s" % 'bfligt'
		print "<tr class='line %s' id='pcod%3d' %s>" % (bclass, r[d.index('cod')], sonclick)
		for k in cnames:
			if r[d.index(k)]:
				print "<td>%s</td>" % r[d.index(k)] ,
			else:	print "<td> &nbsp; </td>"
		print "</tr>"
	print "</table>	<!-- tbl_person		-->"
	print "</div>	<!-- list_person	-->"
	print   """~eval| $('#tbl_person tr.line').hover (function () { $('#tbl_person tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""


def	AUTOS (SS, request):
	print	"AUTOS", request

def	POLIT (SS, request):
	print	"POLIT", request


if __name__ == "__main__":
	SS = {'disp': '4444', 'ch_id': 'SVOO', 'armid': 'SVOO', 'type': 1, 'utype': 1}
	main (SS, {'disp': '4444', 'this': 'ajax', 'shstat': 'PERSONS'})
#	main ({'test': "TEST"})
