#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time

LIBRARY_DIR = r"/home/vds/03/oopy/lib"
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


#	doctor =	{'sname': 'sel_doctor', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name', 'post_name'], 'knull': '', 'order': 'name', 'where': 'n_pst = %s AND n_catg IN (1,2)' % (subst) }
dictin = {
	'statb':	{'tab': 'sp_statb', 'key': 'cod', 'val': 'name'},
	'auto':		{'sname': 'auto', 'tab': 'automobile', 'key': 'id_auto', 'val': 'reg_num', 'knull': '', 'order': 'reg_num', },
	'doctor':	{'sname': 'doctor', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name', 'post_name'], 'knull': '', 'order': 'name', },
	'driver':	{'sname': 'driver', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'name'  },
	'sel_statb':	{'sname': 'sel_statb', 'tab': 'sp_statb', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('BRG_WOKE');\""},
	'sel_subst':	{'sname': 'sel_subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 10', 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('BRG_WOKE');\""},
	'sel_bwfind':   {'sname': 'sel_bwfind', 'tab': 'ss_bwfind', 'key': 'cod', 'val': 'name', 'on': "onchange=\"$('#wdg_bc').html(''); set_shadow('BRG_WOKE');\""    },
	}
#	brignrd	Дежурный наряд
#	bnaryd	Бригады на линии

def	brgs_list (SS, request):
	""" Формировать список бригад	"""
	US_ROW = SS.objpkl.get('us_row')
	print	"brgs_list", US_ROW, request
	print   "~mybody|"
	opts = {}
	obj = {}
	ssubst = sbwfind = sstatb = ssmen = None
	for k in request.keys():
		if k == 'sel_smen':	ssmen = request.get('sel_smen')
		if k == 'sel_subst':	ssubst = request.get('sel_subst')
		if k == 'sel_statb':	sstatb = request.get('sel_statb')
		if k == 'sel_bwfind':	sbwfind = request.get('sel_bwfind')

	sfrom = 'bnaryd'
	if sbwfind in [ '2', '3']:
		obj['online'] = False 
		sfrom = 'brignrd'
		if sbwfind == '3':	ssmen = str(T.next_smena (dboo))
		elif not ssmen:		ssmen = str(T.curr_smena (dboo))
		#	if sbwfind == '3':
		#		ssmen = str(T.next_smena (dboo))
		#	else:	ssmen = str(T.curr_smena (dboo))
	else:	obj['online'] = True

	armid = US_ROW['armid'].strip()
	if armid == 'DISP_PS':
		obj['DISP_PS'] = True
		ssubst = str(US_ROW.get('subst'))
		obj['subst'] =  T.svals (dboo, dictin['sel_subst'], ssubst)
	else:
		obj['sel_subst'] = T.sselect (dboo, dictin['sel_subst'], ssubst)
	obj['sel_smen'] = T.sel_smen (dboo, son = "onchange=\"$('#wdg_bc').html(''); set_shadow('BRG_WOKE');\"", cs = ssmen)
	obj['sel_statb'] = T.sselect (dboo, dictin['sel_statb'], sstatb)
	obj['sel_bwfind'] = T.sselect (dboo, dictin['sel_bwfind'], sbwfind)

	parse_forms (opts, obj, 'find_brigs.html')

	lwheres = []
	if sfrom == 'brignrd':
		if ssmen:	lwheres.append ('smena = %s' % ssmen)
	elif sstatb:	lwheres.append ('stat = %s' % sstatb)

	if ssubst:	lwheres.append ('n_pst = %s' % ssubst)
	if not lwheres:	lwheres.append ('br_id > 0')
	swhere = " AND ".join(lwheres)
	print	"SELECT * FROM %s WHERE %s ORDER BY number" % (sfrom, swhere)
	sorder = "ORDER BY number, smena"
	res = dboo.get_table(sfrom, "%s %s" % (swhere, sorder))
	if not res:
		if not dboo.last_error:
			print "<span class='bfinf'> &nbsp; Нет данных! &nbsp; </span><br>"
		print "brgs_list get_table:", sfrom, swhere, sorder
		return
	d = res[0]
	cignore = colsIgnore[sfrom]

	print """<div id="list_brigs" style="border: thin solid #668; width: 100%; position: absolute; background-color: #fff; padding: 2px; min-height: 20%; max-height: 90%; overflow: auto;">"""
	print "<table id='tbl_brigs' width=100%><tr>"
	print "<th>Бригада</th>"
	for k in d:
		if k in cignore:	continue	#['br_id', 'number', 'profile', 'sector', 'doc_post', 'flag', 'pgr', 'st_begin', 'st_end']:		continue
		print "<th>", cname_brig.get(k), "</th>"
	print "</tr>"
	for r in res[1]:
		sonclick = """ onclick="set_shadow('brg_form&br_id=' +'%s' +'&bfrom=' +'%s');" """ % (r[d.index('br_id')], sfrom)
		bstat = r[d.index('stat')] 
		if not bstat:			bclass = "%s" % 'bferr'
		elif bstat in [5, 6, 7]:	bclass = "%s" % 'bfinf'
		elif bstat == 10:		bclass = "%s" % 'bferr'
		elif bstat in [1, 2, 3, 4]:	bclass = "%s" % 'bfligt'
		else:	bclass = "%s" % 'bfblue'
#	print "<tr class='line %s' id='brid%3d' %s><td>%s%s%s</td>" % (bclass, r[d.index('br_id')], sonclick, img_brig, r[d.index('number')], r[d.index('profile')])
		print "<tr class='line %s' id='brid%3d' %s><td>%s</td>" % (bclass, r[d.index('br_id')], sonclick, slab_brig (r[d.index('number')], r[d.index('profile')], r[d.index('stat')]))
		for k in d:
			if k in cignore:	continue	#['br_id', 'number', 'profile', 'sector', 'doc_post', 'flag', 'pgr', 'st_begin', 'st_end', 'sanitr']:	continue
			if not r[d.index(k)]:
				print "<td> </td>"
			elif k == 'stat':
				print "<td> %s </td>" % T.svals (dboo, dictin['statb'], r[d.index(k)])
			elif k == 'auto':
				print "<td> %s%s </td>" % (img_auto, T.svals (dboo, dictin[k], r[d.index(k)]))
	#			print "<td> %s </td>" % T.svals (dboo, dictin[k], r[d.index(k)])
			elif k in ['tm_beg', 'tm_end', 'stm_beg', 'stm_end', 'st_begin', 'st_end']:
				print "<td> %s </td>" % sdtime(r[d.index(k)], "%H:%M")	# %d.%m.%Y")
			elif k == 'scall':
				print "<td> %s%s </td>" % (img_call, str(r[d.index(k)]))
			elif k == 'tm_work':
				h = int(r[d.index(k)]/3600)
				print "<td> %02d.%02d </td>" % (h, (r[d.index(k)]-h*3600)/60)
			elif k in ['doctor', 'feldsh']:	#, 'sanitr']:
				print "<td> %s </td>" % T.svals (dboo, dictin['doctor'], r[d.index(k)])
			elif k == 'driver':
				print "<td> %s </td>" % T.svals (dboo, dictin['driver'], r[d.index(k)])
			elif k == 'street':
				if r[d.index('house')]:
					print "<td> %s д.%s </td>" % (r[d.index('street')], r[d.index('house')])
				else:	print "<td> %s  </td>" % r[d.index('street')]
			else:
				print "<td> %s </td>" % str(r[d.index(k)])
		print "</tr>"
	'''
	print "<pre>"
	print "</pre>"
	'''
	print	"</table>	<!-- tbl_brigs	-->"
	print	"</div>	<!-- list_brigs	-->"

	print	"""~eval| $('#tbl_brigs tr.line').hover (function () { $('#tbl_brigs tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""
	

def	brg_save (SS, dbrg, request):
	""" Сохранить измененияв карточке бригады	"""
	clist = ['tm_beg', 'tm_end', 't_begin', 't_end', 'doctor', 'feldsh' 'sanitr', 'driver', 'stat']
	lset = []
	for k in request.keys():
		if k not in clist:	print k, '\t', request[k]
	'''
	print "<pre>"
	print "</pre>"
	'''
	querys = []
	for k in ['doctor', 'feldsh', 'sanitr', 'driver']:
		brk = dbrg.get(k)
		rqk = request.get(k) 
	#	print k, str(brk), '\t', rqk
		if str(brk) != rqk:
			if not rqk:
				if brk:		lset.append ('%s = NULL' % k)
			else:	lset.append ('%s = %s' % (k, rqk))
	if request.get('stat'):
		istat = int(request.get('stat'))
		if istat != dbrg['stat']:	lset.append ('stat = %s' % istat)
	if request.get('auto'):
		iauto = int(request.get('auto'))
		if iauto != dbrg['auto']:
			if request.get('bfrom') == 'bnaryd':
				querys.append ("UPDATE bnaryd SET auto = NULL WHERE auto = %s" % iauto)
			lset.append ('auto = %s' % iauto)
#		print "auto", request.get('auto'), request
	elif dbrg['auto']:	lset.append ('auto = NULL')

	if lset:
		bfrom = request.get('bfrom')
		sset = ", ".join(lset) 
		swhere = "br_id = %d" % dbrg.get('br_id')
		querys.append ("%s\nUPDATE %s SET %s WHERE %s" % (qhistory_brigs(int(time.time()), request.get('disp'), bfrom, sset, swhere), bfrom, sset, swhere))
	#	querys.append ("UPDATE %s SET %s WHERE br_id = %d" % (request.get('bfrom'), ", ".join(lset), dbrg.get('br_id')))

	if querys:
		query = ";\n".join(querys)
		print query
		if dboo.qexecute (query):
			return	"<span class='bfinf'> Изменения сделаны успешно. </span>"
		else:	return	"<span class='bferr'>ERROR:</span> %s" % query
	else:	return "<span class='bfinf'> Нет изменений. </span>"

 
def	brg_activ (SS, request):
	print 'request', request
	US_ROW = SS.objpkl.get('us_row')

	dbrg = dboo.get_dict ("SELECT * FROM bnaryd WHERE br_id = %s" % (request.get('br_id')))
	br_id = dbrg.get('br_id')
	obj = {'title': "Бригада на линии"}
	obj['img'] = "%s %s%s" % (img_brig, dbrg.get('number'), dbrg.get('profile'))
	if dbrg.get('doctor'):	obj['doctor'] = T.svals (dboo, dictin['doctor'], dbrg.get('doctor'))
	if dbrg.get('auto'):
		obj['auto'] = T.svals (dboo, dictin['auto'], dbrg.get('auto'))
		obj['driver'] = T.svals (dboo, dictin['driver'], dbrg.get('driver'))
	tm_work = dbrg.get('tm_work')
	if tm_work:	obj['tm_work'] = "%02d.%02d" % (int(tm_work/3600), (tm_work-int(tm_work/3600)*3600)/60)
	obj['smena'] = dbrg.get('smena')
	obj['ncall'] = dbrg.get('ncall')
	obj['subst'] = T.svals (dboo, dictin['sel_subst'], dbrg.get('n_pst'))
	obj['bstat'] = T.svals (dboo, dictin['sel_statb'], dbrg.get('stat'))
	obj['tm_beg'] = sdtime(dbrg.get('tm_beg'), "%H:%M")
	obj['tm_end'] = sdtime(dbrg.get('tm_end'), "%H:%M")
	obj['stm_beg'] = sdtime(dbrg.get('stm_beg'), "%H:%M")
	obj['stm_end'] = sdtime(dbrg.get('stm_end'), "%H:%M")
	if dbrg.get('street'):
		if dbrg.get('house'):
			obj['addres'] = "%s </b> дом <b> %s" % (dbrg['street'], dbrg['house'])
		else:	obj['addres'] = "%s" % dbrg['street']
	cols = ['number', 'profile', 'street', 'house', 'korp', 'reasn', 't_get', 't_send', 't_arrl', 't_done', 't_close', 'cnum_total', 'id_ims']
#	scalls = dboo.get_rows (
	query = "SELECT %s FROM calls WHERE br_ref = %s AND t_send > %s -1800 ORDER BY t_send DESC" % (','.join(cols), br_id, dbrg.get('tm_beg'))
#	obj['query'] = query 
	rows = dboo.get_rows (query)
	c_activ = []
	c_arch = []
	if rows:
		d = dboo.desc
		for r in rows:
			cstt = clc_cstatus(r, d)
			cclass, cimg = cdef2cstt (cstt)
			cnum_total = r[d.index('cnum_total')]
			soncall = """onclick="open_call(%s);" """ % cnum_total
			saddr = "%s" % r[d.index('street')]
			if r[d.index('korp')]:		saddr += " к.%s" % r[d.index('korp')]
			if r[d.index('house')]:		saddr += " д.%s" % r[d.index('house')]
		#	sreasn = "<span class='line %s'> %s %s <b>%s </b> </span>" % (cclass, cimg, r[d.index('number')], r[d.index('reasn')])
			sreasn = "<span class='line %s'> %s %s </span>" % (cclass, cimg, r[d.index('number')])
			stimes = []
			for k in ['t_get', 't_send', 't_arrl', 't_done', 't_close']:
				if r[d.index(k)]:
					stimes.append('<td >%s</td>' % sdtime(r[d.index(k)], "%H:%M"))
				else:	stimes.append('<td >--:--</td>')
			sss = """<tr class='line' %s><td width=100px> %s </td><td ><b> %s </b></td> %s <td> %s </td>""" % (soncall, sreasn,
				r[d.index('reasn')],	# sdtime(r[d.index('t_get')], "%H:%M"),
				"".join(stimes),	saddr)
			if dbrg.get('scall') == r[d.index('number')]:
				obj['scall'] = "<span class='line %s' %s> %s %s <b>%s </b> </span>" % (cclass, soncall, cimg, r[d.index('number')], r[d.index('reasn')])
				c_activ.append (sss)
			elif not r[d.index('t_done')]:
				c_activ.append (sss +"</tr>")
			else:	c_arch.append (sss +"<td>%s</td></tr>" % slab_omc (r[d.index('id_ims')]))
	if c_activ:	obj['c_activ'] = "\n".join(c_activ)
	if c_arch:	obj['c_arch'] = "\n".join(c_arch)

	print	"~wdg_bc|"
	parse_forms ({}, obj, 'brg_activ.html')

	print   """~eval| $('#tbrg_4exec tr.line').hover (function () { $('#tbrg_4exec tr').removeClass('mark'); $('#tbrg_arch tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""
	print   """~eval| $('#tbrg_arch tr.line').hover (function () { $('#tbrg_arch tr').removeClass('mark'); $('#tbrg_4exec tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')});"""

def	brg_form (SS, request):
	""" Показать карточку Бригады / Дежурный наряд 	"""
#	print request
	US_ROW = SS.objpkl.get('us_row')
	tname = request.get('bfrom')
	if not tname:
		print "<span class='bferr'>", request, "</span>"
		return

	obj = {}
	is_edit = False
	dbrg = dboo.get_dict ("SELECT * FROM %s WHERE br_id = %s" % (tname, request.get('br_id')))
	if request.get('exec') == 'SAVE':
		obj['SAVE'] = brg_save (SS, dbrg, request)
		dbrg = dboo.get_dict ("SELECT * FROM %s WHERE br_id = %s" % (tname, request.get('br_id')))
		request['exec'] = "EDIT"

	subst = dbrg.get('n_pst')
#	if subst == 12:	subst = 2
	armid = US_ROW['armid'].strip()
	if armid in ['DISP_PS', 'DISP_NP', 'ZAV_PS']:
		obj['IS_UPDATE'] = True
		print request.get('exec')
		if request.get('exec') == 'EDIT':
			is_edit = True
			obj['UPDATE'] = """<input class='butt' type='button' value='Сохранить' onclick="set_shadow('brg_form&exec=SAVE&br_id=' +'%s' +'&bfrom=' +'%s');" />""" % (dbrg['br_id'], tname)
		else:	obj['UPDATE'] = """<input class='butt' type='button' value='Изменить' onclick="set_shadow('brg_form&exec=EDIT&br_id=' +'%s' +'&bfrom=' +'%s');" />""" % (dbrg['br_id'], tname)
	else:	obj['IS_UPDATE'] = False
	if tname == 'bnaryd':
		obj['IN_WORK'] = True
	else:	obj['IN_WORK'] = False
	obj['img'] = "%s %s%s" % (img_brig, dbrg.get('number'), dbrg.get('profile')) 
	obj['bnum'] = "%s%s" % (dbrg.get('number'), dbrg.get('profile'))
	obj['smena'] = dbrg.get('smena')
#	obj['number'] = dbrg.get('number')
	obj['title'] = T.svals (dboo, dictin['sel_bwfind'], request.get('sel_bwfind'))
	obj['n_pst'] = T.svals (dboo, dictin['sel_subst'], subst)
	bstat = dbrg.get('stat')
	if is_edit and (not bstat or bstat in [1, 2]):
		dictin['sel_statb']['sname'] = 'stat'
		dictin['sel_statb']['where'] = "cod < 3"
		dictin['sel_statb']['on'] = ''
		obj['stat'] = T.sselect (dboo, dictin['sel_statb'], bstat)
	else:	obj['stat'] = T.svals (dboo, dictin['sel_statb'], bstat)
	if obj['IN_WORK']:
		tm_work = dbrg.get('tm_work')
		obj['br_ref'] = "<span class='cbutt'> на линии: %s </span>" % T.ref2brg(dboo, dbrg.get('br_id'), 7)	#cstt)
		if tm_work:
			obj['tm_work'] = "%02d.%02d" % (int(tm_work/3600), (tm_work-int(tm_work/3600)*3600)/60)
		obj['ncall'] = dbrg.get('ncall')
		obj['scall'] = dbrg.get('scall')
		if is_edit:
			obj['tm_beg'] = inputText ('tm_beg', sdtime(dbrg.get('tm_beg'), "%H:%M"), 'size=5')
			obj['tm_end'] = inputText ('tm_end', sdtime(dbrg.get('tm_end'), "%H:%M"), 'size=5')
		else:
			obj['tm_beg'] = sdtime(dbrg.get('tm_beg'), "%H:%M")
			obj['tm_end'] = sdtime(dbrg.get('tm_end'), "%H:%M")
		obj['stm_beg'] = sdtime(dbrg.get('stm_beg'), "%H:%M")
		obj['stm_end'] = sdtime(dbrg.get('stm_end'), "%H:%M")
	else:
		if is_edit:
			obj['t_begin'] = inputText ('t_begin', dbrg.get('t_begin'), 'size=5')	# sdtime(dbrg.get('t_begin'), "%H:%M"), 'size=5')
			obj['t_end'] = inputText ('t_end', dbrg.get('t_end'), 'size=5')	# sdtime(dbrg.get('t_end'), "%H:%M"), 'size=5')
		else:
			obj['t_begin'] = dbrg.get('t_begin')
			obj['t_end'] = dbrg.get('t_end')
	if dbrg.get('street'):
		if dbrg.get('house'):
			obj['addres'] = "%s </b> дом <b> %s" % (dbrg['street'], dbrg['house'])
		else:	obj['addres'] = "%s" % dbrg['street']
	'''
	doctor =	{'sname': 'sel_doctor', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name', 'post_name'], 'knull': '', 'order': 'name', 'where': 'n_pst = %s AND n_catg IN (1,2)' % (subst) }
	feldsh =	{'sname': 'sel_feldsh', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name', 'rvals': ['cod', 'name'], 'knull': '', 'order': 'name', 'where': 'n_pst = %s AND n_catg IN (2,3)' % (subst) }
	sanitr =	{'sname': 'sel_sanitr', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name', 'rvals': ['cod', 'name'], 'knull': '', 'order': 'name', 'where': 'n_pst = %s AND n_catg IN (2,3, 4)' % (subst) }
	driver =	{'sname': 'sel_driver', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name', 'rvals': ['cod', 'name'], 'knull': '', 'order': 'name', 'where': 'n_pst = %s AND n_catg = 8' % (subst) }
	'''
	if is_edit:	#if not obj['IS_UPDATE']:
		pinwork = pers_in_work (dboo, dbrg)
		dictin['doctor']['where'] = 'n_pst = %s AND n_catg IN (1,2) %s' % (subst, pinwork)
	#	dictin['doctor']['where'] = 'n_pst = %s AND stat = 3 AND n_catg IN (1,2) %s' % (subst, pinwork)
		obj['doctor'] = T.sselect (dboo, dictin['doctor'], dbrg.get('doctor'))
		dictin['doctor']['where'] = 'n_pst = %s AND n_catg IN (2,3) %s' % (subst, pinwork)
		dictin['doctor']['sname'] = 'feldsh'
		obj['feldsh'] = T.sselect (dboo, dictin['doctor'], dbrg.get('feldsh'))
		dictin['doctor']['where'] = 'n_pst = %s AND n_catg IN (2,3,4) %s' % (subst, pinwork)
		dictin['doctor']['sname'] = 'sanitr'
		obj['sanitr'] = T.sselect (dboo, dictin['doctor'], dbrg.get('sanitr'))
		dictin['driver']['where'] = 'n_pst = %s AND n_catg = 8 %s' % (subst, pers_in_work (dboo, dbrg, 'driver'))
		obj['driver'] = T.sselect (dboo, dictin['driver'], dbrg.get('driver'))
	#	print dictin['doctor']['where']
		dictin['auto']['where'] = 'n_pst = %s AND stat = 2' % subst
		obj['auto'] = T.sselect (dboo, dictin['auto'], dbrg.get('auto'))
	else:
		if dbrg.get('doctor'):	obj['doctor'] = T.svals (dboo, dictin['doctor'], dbrg.get('doctor'))
		if dbrg.get('feldsh'):	obj['feldsh'] = T.svals (dboo, dictin['doctor'], dbrg.get('feldsh'))
		if dbrg.get('sanitr'):	obj['sanitr'] = T.svals (dboo, dictin['doctor'], dbrg.get('sanitr'))
		if dbrg.get('driver'):	obj['driver'] = T.svals (dboo, dictin['driver'], dbrg.get('driver'))
		if dbrg.get('auto'):	obj['auto'] = "%s%s" % (img_auto, T.svals (dboo, dictin['auto'], dbrg.get('auto')))

	print	"~wdg_bc|"
#	print	"<div id='brg_form' type='hidden' style='top: 160px; left: 500px; width: 600px; min-height: 400px; border: thin solid #668; background-color: #efe; position: absolute; z-index: 1112'>"
	parse_forms ({}, obj, 'cbrg_form.html')
	'''
#	print	request
	print	dbrg
	'''
#	print	"</div>  <!-- brg_form   -->"

def	pers_in_work (dboo, dbrg, cnames = 'doctor, feldsh, sanitr'):
	""" Список работающих сегодня сотрудников	"""
	rows = dboo.get_rows("SELECT %s FROM bnaryd" % cnames)
	if rows:
		lign = []
		for k in cnames.split(','):
			i = dbrg.get(k.strip())
			if i:	lign.append(i)
		ll = []
		for r in rows:
			for i in r:
				if i and i not in lign:	ll.append("%s" %i)
		if ll:	return	"AND cod NOT IN (%s)" %','.join(ll)
	return	''

if __name__ == "__main__":
	print	"lib/brigs.py"
	for k in DICTIN.keys():		print "\t'%s':\t" % k, DICTIN[k] 
