#!/usr/bin/python -u
# -*- coding: utf-8 -*-
#	$Id: oo.cgi 54 2014-09-26 14:00:32Z vds $

import  cgi
#import	cgitb; cgitb.enable()	# (display=0, logdir="/tmp") обработка ошибок (ошибки в log)
import	os, sys
import	time
import	urllib
import	urlparse

#LIBRARY_DIR =	r"/home/smirnov/MyTests/03/oopy/lib"
LIBRARY_DIR = r"/home/vds/03/oopy/lib"            # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
request = {}

def	get_theform ():
	theform = cgi.FieldStorage ()
#	request = {}
	for field in theform.keys():
		if theform.has_key(field):
			if  type(theform[field]) != type([]):
				request[field] = theform[field].value
			else:	request[field] = theform.getlist(field)
	return	request

refresh_03 =	"""\n\n<!DOCTYPE html><html><head> <meta http-equiv="refresh" content="0; url=/smp/03.html"></head> %s sstat: %s </html>"""
refresh_logn =	"""\n\n<!DOCTYPE html><html><head> <meta http-equiv="refresh" content="0; url=/smp/login.html"></head> %s sstat: %s </html>"""
shstat = "NOT"

def	check ():
	try:
		get_theform ()
	#	request['this'] = 'ajax'
		shstat = request.get('shstat')
		if os.environ['REQUEST_METHOD'] == 'POST' and request.has_key('this'):
			referer = os.environ['HTTP_REFERER']
			print "~log|"
			import	user_03
			disp = request.get('disp')
			if not disp:
				user_03.outform()
				sys.exit()

			if shstat == 'USR_IDNT':	#, 'view_menu']:
				if shstat == 'USR_IDNT':
					disp = request.get('disp')
					if not disp:
						user_03.outform()
					else:	# Контроль прав пользователя
						session_id = "session_03%s" % disp.strip()
						US_ROW, txt = user_03.check_user (request, session_id)
						print US_ROW, txt
						if not US_ROW:
							print "~mssg_login| <span class='bferr'> Пользователь отсутствует! </span>"
						else:
							user_03.out_menu (US_ROW, request)
							print """~eval| $('#widget').html(''); $('#last_user').html('%s'); $('#last_arm').html('%s'); document.myForm.disp.value='%s';""" % (
								US_ROW['fio'], US_ROW['tname'], US_ROW['disp'])
				#	else:	print """~eval| mssg("%s: %s");""" % (shstat, str(request))

		#		else:	# DEBUD
		#			print "DEBUD:", shstat
		#		print """~eval| mssg("%s: %s");""" % (shstat, str(request))
				sys.exit()

			if shstat == 'find_street':
				import	ws_tools
				print	"~RESULT|"	#, request	#	 'this': 'ajax', 'sex': '?', 'street': 'aa jg Ð³ÐµÑ', 'place': '1'
				print	"<div style='top: 120px; left: 70px; min-width: 400px; background-color: #fff; min-height: 200px; position: absolute; border: thin solid #eee; padding: 4px; '>"	#, request
				print	ws_tools.find_street (request.get('street'), 'street', 'RESULT')
				print	"</div>"
			if shstat == 'view_houses':
				import	ws_tools
				print	"~RESULT|"
				ress = ws_tools.view_houses (request.get('street'), request.get('street_id'))
				if ress:	# request.get('street_id') and request.get('street_id').isdigit():
					print	"<div style='top: 120px; left: 170px; min-width: 400px; background-color: #fff; min-height: 100px; position: absolute; border: thin solid #bbb; padding: 4px; '>"	#, request
					print	ress	#request.get('street'), request.get('street_id')
					print	"</div>"
				else:	print	"view_houses:", request
			if shstat == 'save_columns_tkt':
				import	calls
				print	"save_columns_tkt:", request
				calls.save_columns_tkt (request)
				sys.exit()

			import session
			session_id = "session_03%s" % disp.strip()
			SS = session.session (session_id)
			US_ROW = SS.objpkl.get('us_row')
		#	print "SS", SS.objpkl.keys(), session_id, US_ROW
			if not US_ROW or US_ROW['disp'] != int(disp):	# or Просрочка
				print "US_ROW:", US_ROW
				print """~eval| $('#widget').html(''); $('#last_user').html(''); $('#last_arm').html(''); document.myForm.disp.value='';"""
				print """~eval| mssg('<span class="bferr">Ошибка доступа!</span> disp: %s');""" % disp
				sys.exit()
			if shstat == "calls_alert":
				import	calls
				print	"~RESULT|"
				ress = calls.calls_alert (US_ROW, request)
				if ress:
					print	"<div id='myalert' style='top: 260px; left: 200px; min-width: 400px; background-color: #fff; min-height: 100px; position: absolute; border: thin solid #bbb; padding: 4px; '>"
					print	ress
					print	"</div>"
				else:	print	"calls_alert:", request
			'''
			'''
			if shstat == 'view_menu':	user_03.out_menu (US_ROW, request)
			elif shstat in ['CLL_WAIT', 'CLL_OPER', 'CLL_ALL', 'GET_CALL', 'open_call', 'find_calls', 'set_ttime']:		# Вызова просмотр и поиск
			#	print "<br>shstat:", shstat, US_ROW
				import	calls
				if shstat == 'set_ttime':
					calls.set_ttime(request)
					print "~eval|set_shadow('%s&cnum_ttl=%s');" % (request.get('old_shstat'), request.get('cnum_ttl'))
					sys.exit()
				if shstat == 'open_call':
					calls.out_fcall (US_ROW, request)
				elif shstat == 'GET_CALL':	# Принять Вызов
					calls.get_call (US_ROW, request)
				else:	calls.calls_list (SS, request)
				'''
			elif shstat == 'find_calls':	calls.calls_list (US_ROW, request)
				'''
			elif shstat == 'tree_alert':
				import	tree_reasn
				print	"~log|", request
				'''
				tree_reasn.view_alert(request)
				'''
				if not request.get('reasn'):
					print	"~RESULT|", request
					tree_reasn.view_alert(request)
				else:
					print	"~log|", request
					import	calls
					if request.get('tkt_number'):
						calls.get_call (US_ROW, request)
					if request.get('cnum_total'):
						request['cnum_ttl'] = request.get('cnum_total')
						calls.out_fcall (US_ROW, request)
				
			elif shstat == 'view_alert':
				import	ws_tools
				print	"~RESULT|", request
				'''
				ress = ws_tools.view_alert (US_ROW, request)
				if ress
					print	ress
				else:	"view_menu:", request
				'''
			elif shstat in ['BRG_WOKE', 'brg_form', 'brg_activ']:
				import	brigs
				if shstat == 'BRG_WOKE':	brigs.brgs_list (SS, request)
				if shstat == 'brg_form':	brigs.brg_form (SS, request)
				if shstat == 'brg_activ':	brigs.brg_activ (SS, request)
				
			elif shstat == 'KuKu':		# DEBUD
			#	import	user_03
				user_03.out_KuKu (SS, request)
			elif shstat == 'exit':
				print """~eval| $('#widget').html(''); $('#last_user').html(''); $('#last_arm').html(''); document.myForm.disp.value='';
				"""
				print """~eval| mssg('exit');"""
			else:	print """~eval| mssg("%s");""" % str(request)

		elif os.environ['REQUEST_METHOD'] == 'GET':
			print "~log| GET:", request
		else:
			print "~log| REQUEST_METHOD:", os.environ['REQUEST_METHOD'], request
	except SystemExit:	pass
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print """~eval| alert("%s EXCEPT 03.cgi: %s, %s");""" % (shstat, str(exc_type), str(exc_value))	#cgi.escape(exc_type), exc_value, '<hr>'#, os.environ

		'''
def	docs ():
	print '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
	print '<html xmlns="http://www.w3.org/1999/xhtml">'
	print '<link rel="stylesheet" type="text/css" href="css/style.css" />'
#	cgi.print_environ()
#	cgi.test ()
#	print help (os)
#	print help (cgi)
#	print help (sys)
	print "<hr /><pre>", help(urllib), "</pre>"
	#print "<hr /><pre>", help(urlparse), "</pre>"
	print '</html>'
		'''

if __name__ == "__main__":
	print "Content-Type: text/html; charset=utf-8\n\n"
	try:
		check ()
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT: ", exc_type, exc_value	#, cgi.escape(exc_type), exc_value
