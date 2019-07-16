# -*- coding: koi8-r -*-

import	cgi, os, sys, time
import	dbtools
from	myglobal import *

############################################################################
#	Формировать повод вызова (reasn)
#	Тип записи дерева опроса таблица tree.type
TT_node =	1        # элемент выбора
TT_ask =	2        # вопрос
TT_goto =	3        # переход
TT_leaf =	4        # лист (конец опроса)

def	select_answer (dboo, node):
	""" Формировать список ответов	"""
	query = "SELECT * FROM tree WHERE parent = %s ORDER BY cod;" % node
	rows = dboo.get_rows (query)
	if not rows:	return
	if len (rows) > 32:
		ls = int(len (rows) /2)
	else:	ls = 16
	j  = 0
	print "<table width='100%'><tr valign='top'><td width=50%>"
	for r in rows:
		cod, parent, ntype, name, cn_id, reasn, go = r
		if ntype == TT_leaf:
			print """ &nbsp; <a href='' onclick="set_reasn (%s, '%s'); return false;">%s</a><br />""" % (cod, reasn, name)
		#	print """<a href='' onclick="$('#set_reasn').html(''); set_reasn (%s, '%s'); return false;">%s</a><br />""" % (cod, reasn, name)
		elif ntype == TT_node or ntype == TT_goto:
			print """ &nbsp; <a href='' onclick="set_reasn (%s, ''); return false;">%s</a><br />""" % (cod, name)
		else:
			print cod, parent, ntype, name, cn_id, reasn, go,"<br>"
		j += 1
		if j == ls:	print "</td><td>"
	print "</td></tr></table><br> &nbsp; "

def	get_motive (dboo, node):
	query = "SELECT * FROM tree WHERE cod = %s;" % node
	row = dboo.get_dict(query)
	print	"<span class='tit' style='color: #a00;'>", row['name'], "</span><hr />"

	query = "SELECT * FROM tree WHERE parent = %s" % row['cod']
	row = dboo.get_dict(query)
	
def	select_motive (dboo, node):
	""" Формировать список поводов	"""
	print node
	query = "SELECT * FROM tree WHERE cod = %s;" % node	# AND cod > 0;" % node
	row = dboo.get_dict(query)
	if not row:	return
	if row['type'] == TT_goto and row['go']:	return select_motive (dboo, row['go'])

	query = "SELECT * FROM tree WHERE parent = %s" % row['cod']
	row = dboo.get_dict(query)
	if not row:	return
#	for k in row:	print k, row[k], "<br />"
	print "<span class='tit' style='color: #a00;'>", row['name'], "</span><hr />"
	nrow = select_answer (dboo, row['cod'])

def	set_reasn (dboo, request):
#	ptit_box ("Опрос", "формирование повода вызова", close= "$('#set_reasn').text('');")	#clear= "set_reasn", alert('Close')"), save="document.myForm.submit();")
	print	"<div id='head_call' style='background-color: #777; color: #eef; padding: 4px;'><table width=100%><tr>"
	print	"<td class='tit'> Опрос </td><td> формирование повода вызова </td>"
	print	"</tr></table></div>"
	print	"<div class='call' style='min-height: 300px; padding: 8px; background-color: #fff0aa;'>"
	'''
	if request.has_key('stack') and request['stack'] != '':
		stack = request['stack']
	'''
	stack = request.get('stack')
	tkt_number = request.get('tkt_number')
	if not tkt_number:	tkt_number = ''
	if stack:
		stlist = stack.split(':')
		stln = len(stlist)
		j = 0
		sst = ''
		for node in stlist:	#	stack.split(':'):
			j += 1
			if not node:
				print """<a href='' onclick="document.myForm.stack.value=''; set_reasn ('', ''); return false;">Начало опроса</a>"""
			else:
				row = dboo.get_dict("SELECT * FROM tree WHERE cod = %s ORDER BY cod;" % node)
				if row:
					print ":->"
					if j == stln:
						print "<span class='tit'>%s</span><br />" % row['name']
					else:	print """<a href='' onclick="document.myForm.stack.value='%s'; set_reasn ('%s', ''); return false;">%s</a>""" % (
							sst[1:], node, row['name'])
				else:	print node
			sst = ':'.join((sst, node))
	else:
		node = '1'
		stack = ''
	print	"""<fildset class='hidd'><input type='hidden' name='stack' value='%s'><input type='hidden' name='tkt_number' value='%s'></fildset>""" % (stack, tkt_number)
	if not stack:
		print "<span class='tit'>Начало опроса</span><br />"

	select_motive (dboo, node)
	print "</div>"
#	print "</div>"
	return	node

def	sset_reasn (dboo, request):
#	ptit_box ("Опрос", "формирование повода вызова", close= "$('#set_reasn').text('');")	#clear= "set_reasn", alert('Close')"), save="document.myForm.submit();")
	print	"~calls|"
	print	"<div id='call_form' type='hidden' style='top: 40px; left: 180px; width: 900px; border: thin solid #668; background-color: #ffe; position: absolute; z-index: 1112'>"

	print	"<div id='head_call' style='background-color: #777; color: #eef; padding: 4px; z-index: 1112'>"
	print	"<table width=100%><tr>"
	print	"<td class='tit'> Опрос </td><td> формирование повода вызова </td>"
	print	"</tr></table></div>"
	print	"<div id='tree' class='call' style='min-height: 300px; padding: 8px; background-color: #fff0aa;'>"
	stack = tkt_number = cnum_total = ''
	if request.get('stack'):	stack = request.get('stack')
	if request.get('tkt_number'):	tkt_number = request.get('tkt_number')
	if request.get('cnum_total'):	cnum_total = request.get('cnum_total')

	print	"""<fildset class='hidd'>
		<input type='hidden' name='stack' value='%s'>
		<input type='hidden' name='tkt_number' value='%s'>
		<input type='hidden' name='cnum_total' value='%s'>
		</fildset>""" % (stack, tkt_number, cnum_total)
	if not stack:
		print "<span class='tit'>Начало опроса</span><br />"

	query = "SELECT * FROM tree WHERE parent =2 ORDER BY cod;"	#	cod, parent, type, name, cn_id, reasn, go
	rows = dboo.get_rows (query)

	jtd = int(len(rows)/2)
#	print "<table width=100%><tr valign='top'><td width=50%>"
	print "<ul id='first'>"
	j = 0
	for r in rows:
		cod, parent, type, name, cn_id, reasn, go = r
		'''
		if reasn != None:
		#	print   """<li id='n%03d' class='line' style="list-style: none;" onclick="document.myForm.reasn.value='%s'; alert ('reasn: %s');">""" % (cod, reasn, reasn), name, "</li>"
			print   """<li id='n%03d' class='line' style="list-style: none;" onclick="document.myForm.stack.value='%s'; alert ('reasn: %s');">""" % (cod, reasn, reasn), name, "</li>"
		else:
		'''
		if go:	ncod = go
		else:	ncod = cod
		print	"""<li id='n%03d' class='line' style="list-style: none;"
			onclick="$('#first li').removeClass('mark'); $(this).addClass('mark'); document.myForm.stack.value='%s'; set_shadow ('tree_alert&node=%s');">""" % (
				cod, cod, ncod), name, reasn, "</li>"
		j += 1
		if j > jtd:
		#	print "</ul></td><td><ul id='first'>"
			j = 0
	print	"</ul>"
		
#	get_motive (dboo, node)
#	select_motive (dboo, node)
	print "<div id='RESULT'></div>"
	print "</div>	<!-- tree	-->"
	print "</div>	<!-- call_form	-->"
	return	#	node

def	view_alert (request):
	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	node = request.get ('node')
	if not node:	return	sset_reasn (dboo, request)	

	stack = request.get ('stack')

	dnod = dboo.get_dict("SELECT * FROM tree WHERE cod = %s ORDER BY cod;" % node)
	if dnod['reasn'] and dnod['reasn'].strip():
		print	"~eval| $('#tree').html('reasn: %s stack: %s')" % (dnod['reasn'], stack)
		return
	print	"<div id='treealert' style='top: 50px; left: 410px; min-width: 460px; background-color: #fff; min-height: 200px; max-height: 540px; position: absolute; border: thin solid #ccc; padding: 4px; overflow: auto; '>"
	print	"""<table width=100%% style="background-color: #777; color: #eef;"><tr><td> &nbsp; %s </td><td align='right' onclick="$('#RESULT').html(''); " ><img src="/smp/img/close_icon.png"></td></tr></table>""" % dnod['name']
	print	out_childs (dboo, node, stack, 0)
	print	"</div>"

def	out_childs (dboo, node, stack, jq):
	rows = dboo.get_rows ("SELECT * FROM tree WHERE parent = %s ORDER BY cod;" % node)
	llis = []
	for r in rows:
		cod, parent, type, name, cn_id, reasn, go = r
		if go:	cod = go;
		if jq > 3:	return	"\n".join(llis)
		if type == 2:		#	bfgrey	bfligt
			llis.append ("<li class='bfligt' style='list-style: none;'> %s </li>" % ( name))
		elif type == 4:
			sstack = "%s:%s:%s" % (stack, parent, cod)
		#	llis.append ("""<li class='line' style='list-style: none;' onclick="document.myForm.stack.value='%s'; set_shadow ('tree_alert&node=%s');" > %s %s </li>""" % (sstack, cod, name, reasn))
			llis.append ("""<li class='line' style='list-style: none;' onclick="document.myForm.stack.value='%s'; set_shadow ('tree_alert&node=%s&reasn=%s');" > %s </li>""" % (sstack, cod, reasn, name))
		else:	llis.append ("""<li class='line bfgrey' onclick=" set_shadow ('tree_alert&node=%s');" > %s %s </li>""" % (cod, type, name))
	#	if type == 2:	llis.append ("<ul>%s</ul>" % out_childs (dboo, cod))
		if not (reasn and reasn.strip()):	llis.append ("<ul>%s</ul>" % out_childs (dboo, cod, stack, jq+1))
	return	"\n".join(llis)
	
if __name__ == "__main__":
	request = {} 
	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	sset_reasn (dboo, request)
