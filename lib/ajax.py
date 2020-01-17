# -*- coding: utf-8 -*-
"""	Обработка ajax запросов
	$.ajax({data: 'main_fid=XXXL&set_XX=' +... +'&' +$('form').serialize()});
	main_fid - ID функции главного меню b03.list_functions.ch_id = { GET_CALL | BRG_WOKE | CLL_OPER |OO_DOCS | ... }
	set_XX	 - прочие парамерры

	$Id: ajax.py 54 2014-09-26 14:00:32Z vds $
"""

#import	cgi; cgitb.enable()	# (display=0, logdir="/tmp") обработка ошибок (ошибки в log)
import	os, sys, time
import	session
from	myglobal import *
import	call_handling

######################################################################

def	main (script_name, request, referer):
	global	SESSION
	label = 'main'
	try:
		if request.has_key('disp'):
			session_id = "oosmpnn"+ request['disp']
			SESSION = session.session(session_id)
		if request.has_key('main_fid'):
	#		print "shadow|"
			if request['main_fid'] == 'GET_CALL':	# Прием вызова
				if request.has_key('reasn') and request['reasn']:
					label = 'new_call'
					reasn = upper_ru (request['reasn'].strip())	#.decode ("UTF-8").encode("KOI8-R"))
					call_handling.new_call (reasn, request)
					print "~set_reasn|"
					'''
					if request.has_key('reasn_comment') and request['reasn_comment']:
						print "~rcomment|<div class='grey'>",
						ptit_box ("Коментарий к поводу вызова")
						print request['reasn_comment'].decode ("UTF-8").encode("KOI8-R"), "</div>"
					'''
				else:
					import	opros		# Опрос НОВЫЙ
					opros.start (request)
				'''
				if request.has_key('change_reasn'):	# Прием вызова СТАРЫЙ
			#		SESSION.set_obj ('new_call', request)
			#		print "~eval| alert ('change_reasn');"
					del request['reasn']
					del request['stack']
					label = 'change_reasn.set_reasn'
					print "~shadow|"
					print "~set_reasn|", label, request
					import	tree_reasn
					tree_reasn.set_reasn ({})

				elif request.has_key('reasn') and request['reasn'] != '':
					label = 'new_call'
					reasn = upper_ru (request['reasn'].strip().decode ("UTF-8").encode("KOI8-R"))
					call_handling.new_call (reasn, request)
					print "~set_reasn|"
				else:
					label = 'tree_reasn.set_reasn'
					import	tree_reasn
					print "~set_reasn|"
					SESSION.del_obj('GET_CALL')
					tree_reasn.set_reasn (request)
				'''
			elif request['main_fid'] == 'CLL_OPER':	# Все Вызова в Оперативной Обстановке
				import  O_STATUS
				print "~main_fid|"
				O_STATUS.view_oo (request)
			elif request['main_fid'] == 'O_STATUS':	# Статистика
				import	O_STATUS
				print "~main_fid|"
				O_STATUS.disp_03 (request)
				O_STATUS.test (request)
			elif request['main_fid'] == 'VIEW_MSG':
				print "~main_fid|VIEW_MSG", request
			#	import	opros
			#	opros.start (request)
			else:	print "~shadow|", request['main_fid']
			if request.has_key('stat'):	print "~message| stat:", request['stat'] 
			print "~eval| document.mainForm.stat.value='';"
		elif request.has_key('shstat'):		# Опрос НОВЫЙ продолжение
			import	opros
		#	print "~message|", request
			opros.nnext (request)
		else:
			print "message|", script_name, request, referer
			conf = get_config()
	except	SystemExit:	pass
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~message|EXCEPT ajax", label, escape(str(exc_type)), exc_value
	finally:	pass
	'''
		print "~debug|",
	#	plocals (locals ())
		if SESSION:
		#	print "<pre>SESSION:", interrogate (SESSION), "</pre>"
			for k in SESSION.objpkl:        print '<dt>', k, ':</dt><dt>', SESSION.objpkl[k], "</dt>"
	'''
def	plocals (ll):
	print "<pre>locals:"
	for k in ll:	print	k, '->\t', ll[k]
	print "</pre>"

gd = {}
if __name__ == "__main__":
	print assign_values ({'name': 'NAME'}, gd)
	import	dbtools
	"""
	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	print sselect(dboo, {'tab': 'prof', 'key': 's_name', 'val': 'l_name', 'knull': '', 'order': 'ind'}, 'Ф')
#	print sselect(dboo, {'tab': 'reslt', 'key': 'num', 'val': 'name', 'knull': '', 'where': 'num > 0'})
	"""
