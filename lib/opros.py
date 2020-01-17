# -*- coding: utf-8 -*-
"""	Отображение таблицы new_tree (начало опроса)
	$Id$
"""

import	os, sys, time, string

LIBRARY_DIR = r"/home/vds/03/nsi/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

#from	tbrief import *
import	dbtools

#dbtree = dbtools.dbtools ('host=localhost dbname=tree port=5432 user=vds')
dbtree = dbtools.dbtools ('host=127.0.0.1 dbname=tree port=5432 user=vds')

def	asc2koi ():
	asc = []
	koi = []
	query = "SELECT num, label FROM reasn ORDER BY num;"
	rows = dbtree.get_rows (query)
	if rows:
		for num, label in rows:
			l = str(label)[2]
			n = str(num)[2]
			if l in asc:
				if koi[asc.index(l)] == n:	continue
				else:	print "\t", num, label, ord(koi[asc.index(l)]), '|=', ord(n)
			else:
				asc.append(l)
				koi.append(num[2])
	return	asc, koi

def	get_grouplist (gcod):
	glist = []
	query = "SELECT * FROM new_tree WHERE cod > 0 AND gcod = %d ORDER BY cod;" % gcod
	rows = dbtree.get_rows (query)
	if rows:
		for r in rows:
			if r[dbtree.desc.index('cod')] == r[dbtree.desc.index('gcod')]:
				glist.append("<span class='tit'> %s </span>" % r[dbtree.desc.index('label')])
			else:
				onclick = """onclick="document.mainForm.node.value=%d; $.ajax({data: 'shstat=next_node&iddom=dtree&' +$('form').serialize()}); return false;" """ % r[dbtree.desc.index('cod')]
				glist.append("<a href='' %s> %s </a>" % (onclick, r[dbtree.desc.index('label')]))
	return	glist

def	opros():
	ordr = [[3], [1, 2], [4,5,6]]
	query = "SELECT * FROM new_tree WHERE cod > 0 AND cod < 99 ORDER BY cod;"
	rows = dbtree.get_rows (query)
	if rows:
		print "<table width=100%%><tr valign='top'>"
		for jc in range(len(ordr)):
			print "<td>"
			for j in ordr[jc]:
				r = rows[j-1]
				glist = get_grouplist(r[dbtree.desc.index('gcod')])
				print glist[0]
				print "<div class='grey' style='padding: 4px;'>"
				print "<br />".join(glist[1:])
				print "</div>"
			print "</td>"
		print "</tr></table>"

def	test(request = None):
	place = node = age = amond = aday = ''
	if request:
		if request.has_key('place'):	place = request['place']
		if request.has_key('node'):	node = request['node']
		if request.has_key('age'):	aday = request['set_age']
		if request.has_key('amond'):	amond = request['set_mond']
		if request.has_key('aday'):	aday = request['set_day']

	print "<fieldset class='hidd'><input type='hidden' value='' name='reasn_comment'><input type='hidden' value='' name='reasn'></fieldset>"
	#$.ajax({data: 'shstat=view_trow&iddom=dright&pkey=' +pkey +'&idrow=' +idrow +'&' +$('form').serialize()});
	print """<table width=100%%><tr><th>Тестирование опроса</th>
	<th align='center'>Место:<input type='text' name='place' size=1 value='%s' /></th>
	<th align='center'>Возраст:<input type='text' name='set_age' size=2 value='%s' />л.
	<input type='text' name='set_mond' size=2 value='%s' />м.
	<input type='text' name='set_day' size=2 value='%s' />дней</th>
	<th align='center'>Sex:<input type='text' name='set_sex' size=1 value='' /></th>
	<th align='center'>Node:<input type='text' name='node' size=4 value='%s' /></th>
	<th align='right'><input class='butt' type='button' value='Начать опрос' onclick="document.mainForm.node.value=''; document.mainForm.submit(); " /></th>
	<th align='right'><input class='butt' type='button' value='Повторить опрос' onclick="$.ajax({data: 'shstat=next_node&iddom=dtree&' +$('form').serialize()}); " /></th>
	<th align='right'><input class='butt' type='button' value='Завершить опрос' onclick="alert ('TEST'); " /></th>
	</tr></table>""" % (place, age, amond, aday, node)
	print "<div id='dtree'class='green' style='width: 1000px;height: 540px; overflow: auto;'>"
	if node.isdigit():
		print node
	else:
		opros ()
	print "</div>"

def	ssel_place (place):
	plist = ['1 квартира', '2 улица', '3 обществ.место', '4 рабочее место', '5 подстанция', '6 леч.учреждение']
	psel = ["<select name='place'>"]
	for ss in plist:
		if ss[0] == place:
			psel.append ("<option value='%s' selected> %s </option>" % (ss[0], ss))
		else:	psel.append ("<option value='%s' > %s </option>" % (ss[0], ss))
	psel.append ("</select>")
	return	"\n".join (psel)

def	start (request = None):
	place = node = age = amond = aday = ''
	if request:
		if request.has_key('place'):	place = request['place']
		if request.has_key('node'):	node = request['node']
		if request.has_key('age'):	aday = request['set_age']
		if request.has_key('amond'):	amond = request['set_mond']
		if request.has_key('aday'):	aday = request['set_day']
	if node.isdigit():
		print "~message|<b>НЕ ПОНЯЛ !!! Опрос уже идет !!!</b>", node, request
		return

	print "~set_reasn|"
	print "~main_fid|"
	print "<fieldset class='hidd'><input type='hidden' value='' name='reasn_comment'><input type='hidden' value='' name='reasn'></fieldset>"
	#$.ajax({data: 'shstat=view_trow&iddom=dright&pkey=' +pkey +'&idrow=' +idrow +'&' +$('form').serialize()});
	print "<table width=1000 cellspacing=0><tr><th align='center'>Место:", ssel_place (place), "</th>"
	print """<th align='center'>Возраст:<input type='text' name='set_age' size=2 value='%s' />л.
	<input type='text' name='set_mond' size=2 value='%s' />м.
	<input type='text' name='set_day' size=2 value='%s' />дней</th>
	<th align='center'>Пол:<input type='text' name='set_sex' size=1 value='' /></th>
	<th align='center'>Node:<input type='text' name='node' size=4 value='%s' /></th>
	<th align='right'><input class='butt' type='button' value='Начало' onclick="document.mainForm.node.value=''; set_fmenu('GET_CALL'); " /></th>
	<th align='right'><input class='butt' type='button' value='Повторить опрос' onclick="$.ajax({data: 'shstat=next_node&iddom=dtree&' +$('form').serialize()}); " /></th>
	</tr></table>""" % (age, amond, aday, node)
	print "<div id='dtree'class='green' style='width: 1000px;height: 540px; overflow: auto;'>"
	opros ()
	print "</div>"

from	tree_nods import *
def	nnext (request):
	if not (request.has_key('node') and request['node'].isdigit()):
		print "QQQQQQQQQQQQQQQQQQ", request
		return
	if request.has_key('iddom'):
		id_dom = "~%s|" % request['iddom']
	if not dbtree:
		print "NOT dbtree"
		return
	else:	dbx = dbtree
#	dbx = dbtools.dbtools ('host=localhost dbname=tree port=5432 user=vds')

	if request['shstat'] == 'next_node':
		print id_dom
		next_node (dbx, request)
	elif request['shstat'] == 'mclick':
		if request.has_key('cname'):
			if request['cname'] == 'clc_mbody':
				clc_mbody (request)
			elif request['cname'] == 'clc_medev':
				clc_medev (dbx, request)
			else:   print   id_dom, request
	elif request['shstat'] == 'check_finish':
		complect = check_finish (dbx, request)
		if complect:
			drow = dbtree.get_dict ("SELECT * FROM reasn WHERE label = '%s';" % request['reasn_label'])
			print "~one_reasn|<span class='tit'>", drow['num'], drow['name'], "</span>"
			print "~eval|document.mainForm.reasn.value='%s'; document.mainForm.butt_finish.disabled=0;" % drow['num']
	else:	print "XXXXXX"

if __name__ == "__main__":
	print "MAIN pylib/opros.py"
