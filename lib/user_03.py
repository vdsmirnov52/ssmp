#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time, string

LIBRARY_DIR = r"/home/vds/03/oopy/lib"  # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import  session as SS
import  dbtools
bases = {'oo': 'host=127.0.0.1 dbname=b03 port=5432 user=smirnov',
	'ss': 'host=127.0.0.1 dbname=ss2013 port=5432 user=smirnov',
	}
dboo = dbtools.dbtools (bases['oo'])

def	get_usconf (dboo, request):
	disp = int (request['disp'].strip())
	# DEBUG
#	query = "SELECT u.*, u.type AS utype, t.name AS tname, p.name AS fio FROM usr03 u, person_sp p, sp_usrtype t  WHERE u.type=256 AND u.cod IN (SELECT DISTINCT doctor FROM call WHERE t_done IS NULL AND doctor >0 ORDER BY doctor) AND (u.cod = p.cod) AND (u.type = t.cod) LIMIT 1;"
#	query = "SELECT u.*, u.type AS utype, t.name AS tname, p.name AS fio FROM usr03 u, person_sp p, sp_usrtype t WHERE (u.cod = p.cod) AND (u.type = t.cod) AND u.disp=%d;" % disp
	query = "SELECT u.*, u.type AS utype, t.ch_id AS armid, t.name AS tname, t.ch_id, p.name AS fio FROM usr03 u, person_sp p, loc_user t WHERE (u.cod = p.cod) AND (u.type = t.cod) AND u.disp=%s;" % disp
	row = dboo.get_dict (query)
	return row, 'TEST'
	# Проверка прав пользователя
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
	us_row, message = get_usconf (dboo, request)
	if us_row:
		SESSION = SS.session (session_id)
	#	del	us_row['ip_loc']
		del	us_row['passwd']
		del	us_row['login']
	#	del	us_row['tm_upd']
		del	us_row['options']
		SESSION.sset({'us_row': us_row})
		SESSION.stop()
		print "Set-Cookie: CPYSESSID=" +session_id
	return	us_row, message

def	outform ():
#	<span> <i class="fa fa-times fa-2x" aria-hidden="true"> </span>
	print """~widget|
	<div id="login" style="top: 60px; left: 60px; position: absolute; background-color: #fff; z-index: 1111; padding: 22px;"> <table>
	<tr><td> </td><td align="right"> <i class="fa fa-times fa-2x bfligt" aria-hidden="true" onclick="$('#widget').html('');"></i> </td></tr>
	<tr><td> Код: </td><td> <input name="disp" type="text" size=5 /></td></tr>
	<tr><td> Login: </td><td> <input name="login" type="text" /></td></tr>
	<tr><td> Passwd: </td><td> <input name="passwd" type="text" /></td></tr>
	<tr><td> </td><td> <input value="Регистрация" type="button" onclick="set_shadow('USR_IDNT');" /></td></tr>
	<tr><td id="mssg_login" colspan=2> </td></tr>
	</table></div>
	"""

def	out_menu (US_ROW, request):
	'''
	lout = ["""<div id='menu' style="padding: 4pt; min-height: 200px;">"""	# id="login" style="top: 40px; left: 20px; position: absolute; background-color: #eef; z-index: 1111; padding: 22px;">"""
#	""" <li class="bfligt line" onclick="set_shadow('USR_IDNT');"> Регистрация </li> """,
	]
	'''
	utype = US_ROW.get('utype')
	lout = []
	query = "SELECT * FROM list_functions WHERE ch_id IN ('GET_CALL', 'CLL_OPER', 'O_STATUS', 'USR_IDNT', 'BRG_WOKE') AND mtype & %s > 0 ORDER BY ch_id" % utype
#	lout.append (query)
	rows = dboo.get_rows(query)
	if rows:
		d = dboo.desc
		for r in rows:
			if not r[d.index('ordr')]:	continue 
			lout.append ("""<li class="bfligt line" onclick="$('#wdg_bc').html(''); $('#wdg_bc').html(''); $('#calls').html(''); $('#calls').html(''); set_shadow('%s');"> %s </li>""" % (r[d.index('ch_id')], r[d.index('name')]))
#	lout.append ("""<li class="bfligt line" onclick="$('#menu').html(''); set_shadow('exit');"> Exit </li></div>""")
	lout.append ("""<li class="bfligt line" onclick="$('#menu').html(''); document.myForm.disp.value=''; set_shadow('view_menu');"> Выход </li></div>""")
	lout.append ("""<hr><li class="bfligt line" onclick="set_shadow('KuKu');"> KuKu </li>""")
	print "~menu|", '\n'.join(lout)


def	out_KuKu (SSO, request):
	import cPickle as pickle
	print """~mybody|<div id="list_calls" style="border: thin solid #668; width: 100%; position: absolute; background-color: #fff; padding: 2px; height: 100%">
	"""
	print """ <li class="list-group-item list-group-item-action d-flex justify-content-between align-items-center" onclick="alert('QWE');">ООО "Аркадия клининг"<span class="badge badge-primary badge-pill">8</span></li> """
	disp = request.get('disp')
	if not disp:	return
	print "<pre>SSO.objpkl.keys:"
	for k in SSO.objpkl.keys():
		if k == 'us_row':
			print k
			for p in SSO.objpkl[k]:
				print "\t", p, SSO.objpkl[k][p]
		else:
			print k, SSO.objpkl[k]
	'''
	session_id = "session_03%s" % disp.strip()
	filename = '/tmp/%s.pkl' % session_id
	print "KuKu:", request, session_id
	print "<br>isfile", os.path.isfile (filename)
	fid = open (filename, 'r+b')
	ppp = pickle.load(fid)
	print ppp
#	return
	SESSION = SS.session (session_id)
	print "KuKu:", session_id, SESSION.objpkl.keys()
	SESSION.set_obj('tm', time.time())
	'''
	print "</pre>"
	print """<div id='panrem' style="padding: 4pt; min-height: 300px; border: thin solid #99a; height: 200pt; margin: 2pt;">"""
	query = "SELECT u.disp, t.ch_id AS armid, t.name AS tname FROM usr03 u, loc_user t WHERE (u.type = t.cod) ORDER BY armid"
	rows = dboo.get_rows(query)
	print "<pre>"
	j = 0
	c = ''
	for r in rows:
		j += 1
		if c != r[1]:
			j = 0
			c = r[1]
		elif j > 2:	continue
		print r[0], r[1]
	#	print """<span onclick="document.myForm.disp.value='%s'; set_shadow('view_menu');">""" % r[0], r[0], r[2], "</span>"
	print "</pre>"
	print "</div>"
	'''
	'''
	import	tree_reasn
	print	"<div type='hidden' style='top: 40px; left: 180px; width: 900px; border: thin solid #668; background-color: #ffe; position: absolute; z-index: 1112' >"
	tree_reasn.sset_reasn (dboo, request)
	print	"</div>"
	print "</div>"
'''
SELECT cod, name, mtype, mfunc, ch_id, ref FROM list_functions ORDER BY ordr ;
 cod |      name       | mtype | mfunc |  ch_id   |                    ref                     
-----+-----------------+-------+-------+----------+--------------------------------------------
   1 | Принять Вызов   | 18543 |       | GET_CALL | Прием нового Вызова
   2 | Бригады         | 19069 |       | BRG_WOKE | Список работающих бригад
   3 | Ждущие Вызова   | 16505 |       | CLL_WAIT | Только Ждущие Вызова
   4 | О. Обстановка   | 19325 |       | CLL_OPER | Все Вызова в Оперативной Обстановке
   5 | Поиск вызовов   | 19327 |     7 | CLL_ALL  | Поиск в ОО, Архивах (1 и 10 дней)
   6 | Статистика      | 19071 |     3 | O_STATUS | Оперативная статистика
   7 | Деж. наряд      | 16429 |       | BRG_EDIT | Список работающих бригад для редактировния
   8 | Бриг. на завтра | 16429 |       | BRG_SMEN | Список бригад по сменам для редактировния
   9 | Выбор П/С       | 16388 |       | SET_SUBS | Передача Оперативной Обстановки
  22 | Гемодиализ      |  4128 |       | HMD_SERV | Перевозки Гемодиализа
  15 | Сообщения       | 22911 |     4 | VIEW_MSG | Разрешить обмен сообщениями
  11 | Справка СВ ОО   | 17009 |       | HLP_SVOO | Справка для СВ ОО
  14 | Архив Сп+Стат   | 18161 |       | REF_2_SS | Архив Справки и Статистика
  33 | Документы ОО    | 19327 |       | OO_DOCS  | Документация для сотрудников СМП
  12 | Монитор         | 16384 |       | USR_MNTR | Пользователи в работе
  20 | Журнал ПС       |    57 |       | J_SUBSTS | Журнал выездов Бригад с ПС
  10 | Регистрация     |    -1 |       | USR_IDNT | Регистрация (смена) пользователя
  41 | SS View Calls   |       |       | SS_VCALL | Просмотр вызова в СС
  30 | Call Window     | 24575 |     4 | WIN_CALL | Работа с вызовом в ОО
  31 | Brig Window     | 24575 |     3 | WIN_BRIG | Работа с бригадами на линии
  40 | SS Menu         |       |       | SS_MENU  | Пункты мени СС
  32 | Users Functions | 24575 |     4 | USR_FUNC | Функции пользователей оперативного отдела

SELECT * FROM loc_user ORDER BY cod ;
 cod  |  ch_id   |       name       
------+----------+------------------
    0 | UNKNOWN  | Неизвестный
    1 | SVOO     | Старший врач
    2 | DISP_03  | Дисп. 03
    4 | DISP_NP  | Дисп. направлени
    8 | DISP_PS  | Дисп. ПС
   16 | ZAV_PS   | Зав. ПС
   32 | ZAVOO    | Зав. ОО
   64 | V_CONS   | Врач консультант
  128 | STATIT   | Статистик
  256 | V_LINE   | Врач л. бригады
  512 | TOP_MEN  | Администрация
 1024 | OTHER    | Прочие внешние
 2048 | DS_HOSP  | Дисп. ДДС 03
 4096 | SYS_ADM  | Администратор

SELECT * FROM modif_func ORDER BY cod ;
 cod | cod_func |   ch_id    | mtype |               name               | tmr_mod | who_mod 
-----+----------+------------+-------+----------------------------------+---------+---------
   1 |       30 | MOD_REASN  |     1 | Изменение повода вызова          |         |        
   2 |       30 | VIEW_ONLY  |  3554 | Только просмотр                  |         |        
   3 |       31 | VIEW_ONLY  |  3578 | Только просмотр                  |         |        
   4 |       31 | UPD_STATB  |  1517 | Изменить статус Бригады          |         |        
   5 |       32 | FIND_BRIG  |  2101 | Поиск Бригады по номеру          |         |        
  16 |       31 | WAR_WKEND  |    37 | WAR Конец смены                  |         |        
  17 |       32 | ATT_CREAT  |    33 | Разрешить Создание событий МЧС   |         |        
  18 |        6 | VIEW_OSTAT |  2685 | Разрешить просмотр статистики    |         |        
  19 |        6 | VIEW_EVENT |  2085 | Просмотр событий по вызовам ОО   |         |        
  20 |        6 | VIEW_ATTEN |  2687 | Присмотр событий ЧС ГО           |         |        
  21 |       15 | SYS_MSG    |  4129 | Просмотр системных сообщений     |         |        
  22 |       15 | USR_MSG    |  4145 | Просмотр Пользовательских сообще |         |        
  23 |       15 | CRT_MSG    |  4479 | Создание Пользовательских сообще |         |        
  24 |       32 | AUTO_VREF  |    61 | Показывать машины на ПС в ref.ph |         |        
  25 |       15 | CALL_MSG   |   117 | Сообщеник привязанное к Вызову   |         |        
  26 |        5 | SEL_RESON  |   625 | Искать вызов по поводу           |         |        
  27 |        5 | SEL_DIAGN  |   629 | Искать вызов по диагнозу         |         |        
  28 |        5 | SEL_RESLT  |   629 | Искать вызов по диагнозу         |         |        
  29 |        5 | SEL_SREVIS |   753 | Искать по критериям обслуживания |         |        
  30 |        5 | SEL_SREV+  |   625 | Расширение критериев обслуживани |         |        
  31 |        5 | SEL_SUBST  |   629 | Искать вызов по N П/С            |         |        
  32 |        5 | SEL_NBRIG  |   757 | Искать вызов по N Бригады        |         |        
  33 |       30 | CLOSE_CALL |   268 | Разрешить закрытие вызова        |         |        
  34 |       30 | PRN_CCART  |    25 | Печать Карты вызова              |         |        
  35 |       32 | IS_DELAY   |  6261 | Причины задержки бригад          |         | 
'''	
