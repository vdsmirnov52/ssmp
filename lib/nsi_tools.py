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
	'sel_subst': {'sname': 'sel_subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 3'},	#, 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('ACCESS_NSI');\""},
	'sel_category': {'sname': 'sel_category', 'tab': 'sp_category', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0'},	#, 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('ACCESS_NSI');\""},
	'sel_stat': {'sname': 'sel_stat', 'tab': 'person_stat', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod >= 0'},	#, 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('ACCESS_NSI');\""},
	'sel_post': {'sname': 'sel_post', 'tab': 'sp_post', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0'},	#, 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('ACCESS_NSI');\""},
	}

def	main (SS, request):
	""" Доступ к НСИ (первичный анализ запроса)	"""
	global	US_ROW, onchange
	US_ROW = SS.objpkl.get('us_row')
	shstat = request.get('shstat')
	onchange = """onchange="$('#wdg_bc').html(''); set_shadow('%s');" """ %  shstat

#	print	"~mybody|"
	print   "nsi_tools.main", US_ROW['armid'], request
	if shstat == 'USERS':
		sform = request.get('FORM')
		if sform and sform != 'save':
			return	open_pform (SS, request)
		else:
			save_pform (SS, request)
		return list_users (SS, request)

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
	print query
	drow = dboo.get_dict (query)
	print drow.keys()
	'''
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

def	list_users (SS, request):
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
	obj['sel_smen'] = T.sel_smen (dboo, son = "onchange=\"$('#wdg_bc').html(''); set_shadow('USERS');\"", cs = ssmen, fs = True)
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

	parse_forms (opts, obj, 'find_users.html')
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
		sonclick = """ onclick="set_shadow('USERS&FORM=view&pcod=' +'%s' +'&pfrom=' +'%s');" """ % (r[d.index('cod')], 'person_sp')
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
	main ({'test': "TEST"})
