# -*- coding: utf-8 -*-
"""	Главная страница
	$Id: main_page.py 54 2014-09-26 14:00:32Z vds $
"""

#import	cgi; cgitb.enable()	# (display=0, logdir="/tmp") обработка ошибок (ошибки в log)
import	os, sys, time, string

LIBRARY_DIR = r"/home/vds/03/oopy/lib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
CONF_PATHNAME = r"/home/vds/03/oopy/oopy.ini" 
config = None

from	myglobal import *
import	session
import  dbtools
dboo = dbtools.dbtools (dbtools.bases['oo'])	#'host=localhost dbname=b03 port=5432 user=vds')

def	get_config ():
	global	config

	if os.access (CONF_PATHNAME, os.F_OK):
		import ConfigParser
		config = ConfigParser.ConfigParser()
		config.read (CONF_PATHNAME)
		return True
	else:	print 'Отсутствует файл: ', CONF_PATHNAME, '<br />'

def	authorize (message = ''):
	print """<div class='box' style='background-color: #ff8; text-align: center; padding: 10px; margin: 10px; width: 440px;'><big><b>%s</b></big><hr width='90%%' />
		<b>GSSMP</b> Версия: %s &nbsp; %s </div>""" % (config.get('System', 'name'), config.get('System', 'version'), config.get('System', 'copy'))
#	print """<div style='color: #a00; font-size: 18px; text-align: center;'><b>Вам необходимо зарегистрироваться!</b></div>"""
	print """<center><div class='form' style='padding: 8px; margin: 4px; border: solid; border-width: 1px; width: 400px;'> <table>
		<tr><td align=right>Код:</td>		<td><input name='disp' type='text' maxlength=5 id='us_disp' size=5 value='' /></td></tr>
		<tr><td align=right>Имя:</td>		<td><input name='login' type='text' maxlength=15 id='us_login' value='' /></td></tr>
		<tr><td align=right>Пароль:</td>	<td><input name='passwd' type='password' maxlength=15 id='us_passwd' value='' /></td></tr></table>
		<input type='submit' id='id_check_user' value='Регистрация' onclick='document.mainForm.stat.value="us_ident";' />
		<div id='rez_authorize'>%s</div>
		</div></center>""" % message
	#	<tr><td align=right>Код:</td><td><input name='disp' type='text' maxlength=5 onchange="check_user('disp_code');" id='us_disp' size=5 /></td></tr>
	#	<input type='submit' id='id_check_user' onclick="check_user('reg_user');" value='Регистрация' />
	#	<input type='button' id='id_close' onclick="window.close();" value='Отменить' />

disp_03 = ['GET_CALL', 'CLL_ALL', 'O_STATUS', 'VIEW_MSG', 'OO_DOCS', 'CLL_OPER']	#, 'USR_IDNT']

def	out_list_functions (us_row, frmt = 'div'):
	query = "SELECT name, ordr, mfunc, ch_id, ref FROM list_functions WHERE (mtype & %s) = %s ORDER BY ordr;" % (us_row['utype'], us_row['utype'])
	rows = dboo.get_rows(query)
	if rows:
		if frmt == 'button':
			print "<td>"
		else:	print "<div class='box' style='height: 300px; overflow: auto;'>"
		for r in rows:
			name, ordr, mfunc, ch_id, ref = r
			if not ordr:	continue
			if frmt == 'button':
				if ch_id in disp_03:
					print """<input class='butt' type='button' onclick="set_fmenu('%s');" value='%s' />""" % (ch_id, name),
			else:	print """<div style='padding: 2px;'><a href='' onclick="set_fmenu('%s'); return false;">%s</a></div>""" % (ch_id, name)
		if frmt == 'button':
			print "</td>"
		else:	print "</div>"
	else:
		return query

def	sftime (tm = None):
	if not tm:	tm = time.time()
	return time.strftime("<span class='tit'>%H:%M:%S</span> от %d/%m/%y", time.localtime(time.time()))

def	list_calls (cdoc):
	query = "SELECT * FROM call WHERE doctor = %d ORDER BY t_send DESC;" % cdoc
	rows = dboo.get_rows(query)
	if not rows:
		print "НЕТ вызовов!", query
		return
	desc = dboo.desc
	print """<fieldset class='call' style='width: 500px;'><table width='100%' cellspacing='0' cellpadding='4'>
		<tr><th>Вызов</th><th>Время</th><th>Адрес</th><th>Рез</th><th>Исполнение</th></tr>"""
	for r in rows:	# r[desc.index('cnum_total')]
		print """<tr class='line' valign='top' onclick="$(this).addClass('mark');
			document.mainForm.stat.value='view_call'; document.mainForm.cnum_total.value=%d; document.mainForm.submit();
			return false;">""" % r[desc.index('cnum_total')],
		print """<td align='right'><a href='' onclick="document.mainForm.stat.value='view_call'; document.mainForm.cnum_total.value=%d;
		document.mainForm.submit(); areturn false;">%3d&nbsp;%s</a></td>""" % (r[desc.index('cnum_total')],r[desc.index('number')], r[desc.index('reasn')])
	#	print "<td>%s&nbsp;%s</td>" % (str_time(r[desc.index('t_get')]).strip(), str_time(r[desc.index('t_send')]).strip())
		print "<td align='center'>%s</td>" % str_time(r[desc.index('t_get')]).strip()
		print "<td>", r[desc.index('street')],
		if r[desc.index('house')]:	print "д.%s" % r[desc.index('house')],
		if r[desc.index('korp')]:	print "кр.%s" % r[desc.index('korp')],
		if r[desc.index('flat')]:	print "кв.%s" % r[desc.index('flat')],
		print "</td>"
#		print "<td>", str_time(r[desc.index('t_send')]), "<td>"
		print "<td>",
		if r[desc.index('reslt')]:	print "%02d" % r[desc.index('reslt')],
	#	if r[desc.index('diagn')]:	print "%03d" % r[desc.index('diagn')],
		print "<td>",
		if r[desc.index('t_done')]:
			print "Исполн. ", str_time(r[desc.index('t_done')]),
		elif r[desc.index('t_arrl')]:
			print str_time(r[desc.index('t_arrl')]), " Прибыл",
		else:	print "В пути",
		print "</td></tr>"
	print "</table></fieldset>"

def	get_object_list (dboo, cnum, t_get):
	query = """SELECT c.*, o.name AS oname, o.oref AS otable FROM call2object c, object_type o
		WHERE cnum=%d AND t_get=%d AND otype=o.cod ORDER BY otype, obj_ref;""" % (cnum, t_get)
	rows = dboo.get_rows (query)
	if rows:
		desc = dboo.desc
		for r in rows:
		#	for c in desc:		print	c, '->', r[desc.index(c)], '<br>'
			ll = r[desc.index('oname')]
			if r[desc.index('otable')] == 'attention':
				qq = "SELECT * FROM %s WHERE id_obj=%d;" % (r[desc.index('otable')], r[desc.index('obj_ref')])
			else:
				qq = "SELECT * FROM %s WHERE id_msg=%d;" % (r[desc.index('otable')], r[desc.index('obj_ref')])
			ro = dboo.get_dict (qq)
			print '&nbsp;', ll, '<b>&nbsp;', ro['text'], '</b><br />'

def	view_call(request):
	if not request['cnum_total'] or not request['cnum_total'].isdigit():
		print "НЕТ данных для ртображения вызова!"
		return
	query = "SELECT * FROM call WHERE cnum_total = %s;" % request['cnum_total']
	crow = dboo.get_dict (query)
	if not crow:
		print "SQL:", query
		return
	cproto = get_cproto (dboo, crow['number'], crow['t_get'])
#	print cproto
	print """<fieldset class='call' style='width: 500px;'><table width='100%' cellspacing='0' cellpadding='4'>
		<tr valign='top'><td><div class='call'><table width='100%'>"""
	print "<tr><td align='right'>Вызов:</td><td><b>", crow['number'], crow['reasn'], get_reasn (dboo, crow['reasn']),
	if cproto['rem_reasn'] and cproto['rem_reasn'].strip() != '':	print "<br /><span style='color: #282;'>", cproto['rem_reasn'].strip(), "</span>"
	print "</b></td></tr>"
	print "<tr><td align='right'>Адрес:</td><td><b>", crow['street']
	if crow['house']:	print "</b>д.<b>%s" % crow['house'],
	if crow['korp']:	print "</b>кр.<b>%s" % crow['korp'],
	if crow['flat']:	print "</b>кв.<b>%s" % crow['flat'],
	print "</b></td></tr>"
	print "<tr><td align='right'>ФИО:</td><td><b>", crow['name']
	if crow['name2']:	print crow['name2']
	if crow['age']:		print "</b>лет: <b>%s" % crow['age'],
	if crow['sex']:		print "</b>пол: <b>%s" % crow['sex'],
	print "</b>"
	if cproto['rem_c2uvd'] and cproto['rem_c2uvd'].strip() != '':	print "<span style='color: #282;'><b> &nbsp; УВД</b></span>"
	print "</td></tr>"
	print	"<tr><td colspan='2'><div style='padding: 1px; border: thin solid #ed7; background-color: #fe8; color: #366;'>",
	get_object_list (dboo, crow['number'], crow['t_get'])
	print	"</div></td></tr>"
	if crow['reslt']:
		print "<tr style='color: #778;'><td align='right'>Резлт:</td><td><b>%02d" % crow['reslt'], get_reslt(dboo, crow['reslt'])
		print "</b></td></tr>"
	if crow['diagn']:
		print "<tr style='color: #778;'><td align='right'>DS:</td><td><b>%03d" % crow['diagn'], get_diagn(dboo, crow['diagn'])
		print "</b></td></tr>"
	if crow['kuda']:
		print "<tr style='color: #778;'><td align='right'>Куда:</td><td><b>", crow['kuda']
		print "</b></td></tr>"
	print "</table></div></td><td><div class='call'><table width='100%' cellspacing='0' cellpadding='4'>"
	print "<tr><td align='right'>Принят:</td><td><b>", str_time(crow['t_get']), "</td></tr>"
	print "<tr><td align='right'>Перед.:</td><td><b>", str_time(crow['t_send']), "</td></tr>"
	if crow['t_arrl']:
		print "<tr><td align='right'>Прибл.:</td><td><b>", str_time(crow['t_arrl']), "</td></tr>"
	else:
		if not crow['t_done']:
			print """<tr><td colspan='2' align='center'><input class='butt' type='button' style='width: 80px;'
				onclick='document.mainForm.stat.value="isarrl"; document.mainForm.cnum_total.value=%s;
				document.mainForm.submit();' value=' Прибыл ' /></td></tr>""" % crow['cnum_total']
	if crow['t_done']:
		print "<tr><td align='right'>Испол.:</td><td><b>", str_time(crow['t_done']), "</td></tr>"
	else:
		print """<tr><td colspan='2' align='center'><input class='butt' type='button' style='width: 80px;'
			onclick='document.mainForm.stat.value="isdone"; document.mainForm.cnum_total.value=%s;
			document.mainForm.submit();' value='Исполнил' /></td></tr>""" % crow['cnum_total']
	print "</table></div>"
	print "</td></tr></table>"
	print "</fieldset>"

def	woke_alb (request, ss, us_row):
	print "<fieldset class='grey' style='width: 500px;'>"
	print "<input type='hidden' name='disp' value='%s' />" % request['disp']
	print "<input type='hidden' name='cnum_total' value='' />"
	print "<table width='100%%'><tr><td><span class='tit'>%s</span> v.%s</td>" % (config.get('System', 'title'), config.get('System', 'version'))
	print "<td><span class='tit'>%s %s</span></td>" % (us_row['disp'], us_row['fio'])
	print time.strftime("<td><span class='tit'>%H:%M:%S</span></td>", time.localtime(time.time()))
	print """<td align='right'><input class='butt' type='button' onclick='document.mainForm.submit();' value='Главная' title='Главная' />"""
	print """<td align='right'><img src='/img/error22.png' onclick='document.mainForm.stat.value="exit"; document.mainForm.submit();' alt='Выход' title='Выход' />"""
#	print """<td align='right'><input class='butt' type='button' onclick='document.mainForm.stat.value="exit"; document.mainForm.submit();' value='Выход' title='Выход' />"""
#	print "<td align='right'><img src='/img/reload3.png' onclick='document.mainForm.submit();' alt='Главная' title='Главная' /></td>"
	print "</tr></table></fieldset>"

	if request.has_key('stat') and request['stat']:
		if request['stat'] == 'isarrl' or request['stat'] == 'isdone':
			udate_stat (request)
			view_call(request)
		elif request['stat'] == 'view_call':
			view_call(request)
		else:
			list_calls (us_row['cod'])
	else:
		list_calls (us_row['cod'])

def	udate_stat (request):
	if request['disp'].isdigit() and request['cnum_total'].isdigit():
		query = "UPDATE call SET t_%s = %d, %s_disp = %s WHERE cnum_total = %s;" % (
				request['stat'][2:], current_time(), request['stat'][2], request['disp'], request['cnum_total'])
		if not dboo.qexecute (query):
			print "<spen class='err'>SQL:", query, "</span>"

def	woke_page (request, ss, us_row):	#session_id):	#us_row):
#	ss = session.session(session_id)
#	us_row = ss.objpkl['us_row']
#	ss.start()
	print "<fieldset class='grey'>"
	print "<input type='hidden' name='disp' value='%s' />" % request['disp']
	print "<table width='100%%'><tr><td><span class='tit'>%s</span> v.%s</td>" % (config.get('System', 'title'), config.get('System', 'version'))
	print "<td><span class='tit'>%s %s</span> (%s)</td>" % (us_row['disp'], us_row['fio'], us_row['tname'])
	print "<td>смена:<span class='tit'>%s</span></td><td> %s </td>" % (get_smena(dboo), sftime())
	out_list_functions(us_row, 'button')
	print """<td><input class='butt' type='button' onclick='document.mainForm.stat.value="exit"; document.mainForm.submit();' value='Выход' title='Выход' />"""
	print "<td align='right'><img src='/img/reload3.png' onclick='document.mainForm.submit();' alt='Reload' title='Reload' /></td>"
	print "</tr></table></fieldset>"
	print "<table width='100%' height='80%' border='0'><tr valign='top'>"
	xxx = us_row['type'] & 0xe	
	if not (us_row['type'] & 0xf):	### 0xe
		print "<td width='160px'>", out_list_functions(us_row), "</td>"
	print "<td id='main_fid'><div class='grey'>"
	print xxx
	print "<pre>", my_rem
#	for k in us_row:		print k, ':', us_row[k]
#	for k in os.environ:		print k, ':', os.environ[k]
	interrogate (SESSION)
	print "</pre>"
	for k in SESSION.objpkl:	print '<dt>', k, ':</dt><dt>', SESSION.objpkl[k], "</dt>"
	print "</div></td></tr></table>"
	print "<div id='set_reasn'>set_reasn</div>"
	print "<div id='rcomment'>rcomment</div>"
#	for k in ss.objpkl:		print k, ':', ss.objpkl[k]
#	print '<hr />is_in_work', is_in_work (dboo, us_row)

def	jscripts (ssrc):
	for c in ssrc:
		print "\t<script type='text/javascript' src='%s'></script>" % c

def	rel_css (ssrc):
	for c in ssrc:
		print "\t<link rel='stylesheet' type='text/css' href='%s' />" % c

jslocal =  """<script type='text/javascript'>
$(document).ready(function () {
	document.mainForm.screen.value = window.screen.width +"x"+ window.screen.height;
	$('#shadow').html ("Экран: " +document.mainForm.screen.value);	//window.screen.width +"x"+ window.screen.height);
	})
	</script>"""

def	is_in_work (dboo, us_row, advanced = False):
	""" Проверка: пользователь находится в работе
	return:	0 - Отсутствует (не работает)
		1 - Работает
		4 - Требуется Logon & Password пользователя
		8 - IP Нет в loc_addr_user
	"""
	query = "SELECT * FROM loc_addr_user WHERE ip_addr = '%s';" % REMOTE_ADDR
	drow = dboo.get_dict (query)
	if drow:	# IP есть в loc_addr_user
		if drow['cod_disp'] == us_row['disp']:
			if drow['yor_timer'] > 0:
				dboo.qexecute("UPDATE loc_addr_user SET yor_timer=%d WHERE ip_addr = '%s';" % (USER_TIMER, REMOTE_ADDR))
				return	1	## пользователь Работает
			else:	return	0	## не работает (Отсутствует)
		elif advanced:	# Поск пользователя на других IP
			ddr = dboo.get_row ("SELECT * FROM loc_addr_user WHERE cod_disp = %d AND yor_timer > 0;" % us_row['disp'])
			if ddr:	return	4	## Работает Другой IP + Требуется Logon & Password пользователя
			else:	return	0	## не работает (Отсутствует)
	if advanced:
		return	8	## IP Нет в loc_addr_user + Требуется Logon & Password
	else:	return	0	## Отсутствует

def	get_smena (dboo):
	row = dboo.get_dict ("SELECT * FROM sys03;")
	if row:	return	row['smena']
	else:	return	0

def	get_reasn (dboo, reasn):
	row = dboo.get_dict ("SELECT * FROM reasn WHERE num = '%s';" % reasn)
	if row:	return	row['name']
	else:	return	"[%s]" % reasn

def	get_reslt (dboo, reslt):
	row = dboo.get_dict ("SELECT * FROM reslt WHERE num = '%s';" % reslt)
	if row:	return	row['name']
	else:	return	"[%s]" % reasn

def	get_diagn (dboo, diagn):
	row = dboo.get_dict ("SELECT * FROM new_ds WHERE num = '%s';" % diagn)
	if row:	return	row['name']
	else:	return	"[%s]" % reasn

def	get_cproto (dboo, cnum, tget):
	query = "SELECT * FROM c_proto WHERE number = %s AND t_get = %s;" % (cnum, tget)
	return	dboo.get_dict (query)

def	get_usconf (dboo, request):
	disp = int (request['disp'].strip())
	# DEBUG
#	query = "SELECT u.*, u.type AS utype, t.name AS tname, p.name AS fio FROM usr03 u, sp_person p, sp_usrtype t  WHERE u.type=256 AND u.cod IN (SELECT DISTINCT doctor FROM call WHERE t_done IS NULL AND doctor >0 ORDER BY doctor) AND (u.cod = p.cod) AND (u.type = t.cod) LIMIT 1;"
	query = "SELECT u.*, u.type AS utype, t.name AS tname, p.name AS fio FROM usr03 u, sp_person p, sp_usrtype t WHERE (u.cod = p.cod) AND (u.type = t.cod) AND u.disp=%d;" % disp
	row = dboo.get_dict (query)
	return row, 'TEST'
	if row:
		if REMOTE_ADDR == '127.0.0.1':	## DEBUG Local Host
			return	row, ''
		if not (row['ip_loc'] == '*' or REMOTE_ADDR in row['ip_loc']):
			return  None, "IP запрещен для пользователя"
		passwd = login = False
		if request.has_key('login') and row['login'] == request['login']:	login = True
		if request.has_key('passwd') and row['passwd'] == request['passwd']:	passwd = True
		is_work = is_in_work (dboo, row, True)
		if is_work == 1:
			return  row, ''
		curr_tm = current_time()
		if is_work == 0 or (is_work == 4 and login and passwd):
		#	row['smena'] = get_smena (dboo)
			qexecute = "UPDATE loc_addr_user SET yor_timer=%d, cod_disp=%d, when_get=%d WHERE ip_addr = '%s';" % (
					USER_TIMER, row['disp'], curr_tm, REMOTE_ADDR)
			if is_work == 4:
				qexecute += "UPDATE loc_addr_user SET cod_disp=NULL WHERE ip_addr = '%s';" % REMOTE_ADDR
		elif is_work == 8 and login and passwd:
			qexecute = "INSERT INTO loc_addr_user (ip_addr, loc_type, loc_user, tmr_mod, who_mod, rem) VALUES ('%s', %d, %d, %d, %d, 'New PI by %d');" % (
					REMOTE_ADDR, row['type'], row['type'], curr_tm, row['disp'], row['disp'])
		elif login and passwd:
			return  None, "В доступе отказано! [is_work: %d]" % is_work
		else:	return  None, "Введите Login и Password."
		if 'qexecute' in locals():
			if dboo.qexecute(qexecute):
				return  row, ''
			else:	return	None, qexecute
		else:	return  None, "is_in_work %d" % is_work
	return	None, "Пользователь %s отсутствует!" % request['disp']
"""
if os.path.isfile(path):	# это файл
if os.path.isdir(path):		# это директория

"""

def	is_session (session_id):
	max_dtime = 3600	# время жизни
	path = session_id.join((r'/tmp/', '.pkl'))
	if os.path.isfile(path):		# этот файл существует
		mtime = os.path.getmtime(path)	# дата последней модификации в секундах с начала эпохи
		atime = os.path.getatime(path)	# дата последнего доступа в секундах с начала эпохи
		dtime = int (time.time() - max(mtime, atime))
		if dtime < max_dtime:	return	True
		return	max_dtime - dtime
		print "is_session:", path, dtime, (mtime - atime)
	return 	0

def	check_user (request, session_id):
#	import	dbtools, session
#	dboo = dbtools.dbtools ('host=localhost dbname=b03 port=5432 user=vds')
	us_row, message = get_usconf (dboo, request)
	if us_row:
	#	SESSION = session.session (session_id)
	#	del	us_row['ip_loc']
		del	us_row['passwd']
		del	us_row['login']
		del	us_row['tm_upd']
		del	us_row['options']
	#	SESSION.sset({'us_row': us_row})
	#	SESSION.stop()
		print "Set-Cookie: CPYSESSID=" +session_id
	return	us_row, message

my_rem = """<div class='green'><pre>
	+ изменить повод к вызову
	контроть ввода при сохранении вызова (pdzd, etj) str.isdigit()
	сохранить message_text
	+ поиск сектора по старому алгоритму
	+ отобразить наличие (отсутствие) координат места
	http://localhost/cgi/map.cgi?ssid=ip127.0.0.1&width=1024&height=768&cpoint=[43.928990,56.344800]
		обновление, машта, позиция 0х0, место вызова
	Списки Вызовов по категориям пользователей
	</pre></div>"""
	
def	main (request):
	global	SESSION

	if request.has_key('disp'):
		session_id = "oosmpnn"+ request['disp']
	#	is_session (session_id)
	#	if not os.environ.has_key('HTTP_COOKIE') or os.environ['HTTP_COOKIE'].find(request['disp']) < 0:
	#	iss = is_session (session_id)
		if request.has_key('stat'):
			if request['stat'] == 'us_ident':
				us_row, message = check_user (request, session_id)
				if us_row:	# and is_in_work (dboo, us_row):
					pass
				else:	session_id = ""
			elif request['stat'] == 'exit':
				dboo.qexecute ("UPDATE loc_addr_user SET cod_disp=NULL WHERE ip_addr = '%s';" % REMOTE_ADDR)
				session_id = ""
				message = 'Введите код пользователя.'
		else:
			iss = is_session (session_id)
			if iss <= 0:
				session_id = ""
				message = "Долгое отсутствие. %d<br />Введите код пользователя." % iss
			else:
			#	ss = session.session (session_id)
				message = request['disp']
			#	print "QQQ"
	else:
		session_id = ""
		message = 'Введите код пользователя.'

	print '\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'
	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		get_config ()
		print "<head> <meta name='Author' content='V.Smirnov' /><title>%s</title>" % config.get('System', 'title')
		print "<meta name='viewport' content='width=device-width, initial-scale=0.9, minimum-scale=0.8' />"
		rel_css ((r'/smp/css/style.css', ))
		jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/smp/js/oopy.js', r'/smp/js/new_call.js', r'/smp/js/tree.js'))
		print jslocal, "</head>"
		print """<body><center>"""
	#	print request
	#	is_session ('oosmpnn7777')
	#	print os.environ.has_key('HTTP_COOKIE')
	#	print os.environ['HTTP_COOKIE'], os.environ['HTTP_COOKIE'].find(request['disp'])
		if os.environ.has_key('SCRIPT_NAME'):
			print "<form name='mainForm' action='%s' method='post'>" % os.environ['SCRIPT_NAME']
		else:	print "<form name='mainForm' action='%s' method='post'>" % 'SCRIPT_NAME'
		print """<fieldset class='hidd'>
		<input type='hidden' name='stat' value='' />
		<input type='hidden' name='cpoint' value='' />
		<input type='hidden' name='screen' value='' />
		</fieldset>"""
		if session_id:	#request.has_key('disp'):
			SESSION = session.session(session_id)
			if request.has_key('stat') and request['stat'] == 'us_ident':
				SESSION.set_obj('us_row', us_row)
				if os.environ['SCRIPT_NAME'] == '/03/alb/oo.cgi':
					woke_alb (request, SESSION, us_row)
				elif os.environ['SCRIPT_NAME'] == '/03/oopy/oo.cgi':
					woke_page (request, SESSION, us_row)
				else:	print "SCRIPT_NAME:", os.environ['SCRIPT_NAME']
			elif SESSION.objpkl.has_key('us_row'):
				us_row = SESSION.objpkl['us_row']
				if os.environ['SCRIPT_NAME'] == '/03/alb/oo.cgi':
					woke_alb (request, SESSION, us_row)
				elif os.environ['SCRIPT_NAME'] == '/03/oopy/oo.cgi':
					woke_page (request, SESSION, us_row)
				else:	print "SCRIPT_NAME:", os.environ['SCRIPT_NAME']
			else:
				print "<hr />", session_id, "<hr />",SESSION.objpkl, "<hr />",locals ().has_key('us_row')
		#	print "<hr />SESSION", SESSION.start()
			in_work = is_in_work (dboo, us_row)
			woke_page (request, SESSION, us_row)	#session_id)
		else:	authorize (message)
	#	print 'main', request, config.get('System', 'version'), config.get('System', 'copy')
		print "<div id='shadow'>shadow</div>"
		print "</form>"
	#	print "<img src='img/nn10.png' />"	# width='128px' height='128px' />"
		if os.environ['SCRIPT_NAME'] != '/03/alb/oo.cgi':
			print "<div id='shreslt'>shreslt</div>"
			print "<div id='message'>message</div>"
			print "<div id='debug'>debug</div>"
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'><pre> EXCEPT main_page:", exc_value, "</pre></span>"
	finally:
#		if SESSION:	SESSION.stop()
		print "</center></body></html>"

if __name__ == '__main__':
	print "get_usconf", get_usconf (dboo, {'disp': '7777'})
	main ({'stat': 'us_ident', 'disp': '7777'})
	interrogate (SESSION)
