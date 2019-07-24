#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time

BTIMER = 900000000

def	sdtime (tm, frmt = "%H:%M"):
	if not tm:	return	"--:--"
	if tm < 777777777:	tm += BTIMER
	return	time.strftime(frmt, time.localtime(tm))

def	sdater (tm):
	mon = ['января', 'февраля', 'марта', 'апреля', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',]
	if not tm:      ""
	if tm < 777777777:      tm += BTIMER
	tm_year, tm_mon, tm_mday = time.localtime(tm)[:3]
	if tm_mon > 0:  tm_mon -= 1
	return  "%s %s %s" % (tm_mday, mon[tm_mon], tm_year)

def	sval (obj, nm):
	val = obj.get(nm)
	if val:	return	str(val)
	else:	return	''

inputText =	lambda nm, val, opts:  "<input type='text' name='%s' value='%s' %s />" % (nm, val, opts)
qhistory_calls = lambda tm, disp, sfrom, sset, swhere:	"INSERT INTO history_calls (tm, who_disp, sfrom, sset, swhere) VALUES (%s, %s, '%s', '%s', '%s');" % (tm, disp, sfrom, sset, swhere)
qhistory_brigs = lambda tm, disp, sfrom, sset, swhere:	"INSERT INTO history_brigs (tm, who_disp, sfrom, sset, swhere) VALUES (%s, %s, '%s', '%s', '%s');" % (tm, disp, sfrom, sset, swhere)
qrem2calls =	lambda tm, disp, cn, cnttl, cod, txt:	"INSERT INTO rem2calls (tm, disp, cnum, cnum_total, cod, txt) VALUES (%s, %s, %s, %s, %s, '%s');" % (tm, disp, cn, cnttl, cod, txt)

colsIgnore = {
	'brignrd':	['br_id', 'number', 'profile', 'sector', 'doc_post', 'flag', 'pgr', 'st_begin', 'st_end', 'sanitr', 'tm_work', 'ncall', 'house', 'street', 'scall'],
	'bnaryd':	['br_id', 'number', 'profile', 'sector', 'doc_post', 'flag', 'pgr', 'st_begin', 'st_end', 'sanitr', 'tm_work', 'ncall', 'feldsh', 'house', 'stm_beg', 'stm_end'],
	}

cname_brig = {'br_id': "Бригада", 'smena': "Смн", 'tm_beg': "Начало", 'tm_end': "Конец", 'n_pst': "П/С",
	'doc_name': "Старший бригады", 'doctor': "Старший бригады",
	'stat_name': "Статус", 'stat': "Статус", 'street': "Адрес", 'auto': "Машина", 'driver': "Водитель", 'feldsh': "Прочие", 'scall': "Вызов" }

reslt_hospital = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 24, 25, 26, 27, 30, 33, 34, 35, 36, 37, 38, 39, 40]

img_auto =	'<i class="fa fa-ambulance fa-lg" aria-hidden="true"></i>&nbsp;'
img_call =	'<i class="fa fa-newspaper-o fa-lg" aria-hidden="true"></i>&nbsp;'
img_brig =	'<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>&nbsp;'
fimg_brig =	'<i class="fa fa-medkit fa-lg %s" aria-hidden="true"></i>&nbsp;'

img_brigg =	'<i class="fa fa-medkit fa-lg bfinf" aria-hidden="true"></i>&nbsp;'
img_brigl =	'<i class="fa fa-medkit fa-lg bfligt" aria-hidden="true"></i>&nbsp;'

def	slab_brig (number, profile, bstat = None):
	if not bstat:			bclass = "%s" % 'bferr'
	elif bstat in [5, 6, 7]:	bclass = "%s" % 'bfinf'
	elif bstat == 10:		bclass = "%s" % 'bferr'
	elif bstat in [1, 2, 3, 4]:	bclass = "%s" % 'bfligt'
	else:	bclass = "%s" % 'bfblue'
	return	'<span class="%s"> %s%s%s </span>' % (bclass, img_brig, number, profile)

def	slab_omc (id_ims):
	if id_ims:	return	"<span class='omsys'> Есть </span>"
	else:		return	"<span class='omsno'> НЕТ &nbsp; </span>"

DICTIN = {
	'reasn':	{'tab': 'reasn', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'place':	{'tag': 'select', 'tab': 'place', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'kto':		{'sname': 'kto', 'tab': 'who_call', 'key': 'cod', 'val': 'name', 'knull': ''},
	'refuse':	{'tab': 'refuse', 'key': 'cod', 'val': 'name', 'knull': ''},
	'pbrg':		{'sname': 'pbrg', 'tab': 'prof', 'key': 's_name', 'val': 'l_name', 'knull': '', 'order': 'ind', 'on': "onchange=\"document.mainForm.stat.value='sel_subst'; $.ajax({data: 'main_fid=GET_CALL&' +$('form').serialize()});\""},
	'subst':	{'sname': 'subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 15'},
	'doctor':	{'tab': 'person_sp', 'key': 'cod', 'val': 'name', 'rvals': ['cod', 'name']},
	'diagn':	{'tab': 'new_ds', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'reslt':	{'tab': 'reslt', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name']},
	'sel_subst':	{'sname': 'sel_subst', 'tab': 'sp_station', 'key': 'cod', 'val': 'name', 'knull': '', 'order': 'cod', 'where': 'cod > 0 AND cod < 15', 'on': "onchange=\"set_shadow('find_calls');\""},
	'sel_place':	{'sname': 'sel_place', 'tab': 'place', 'key': 'num', 'val': 'name', 'rvals': ['num', 'name'], 'knull': '', 'on': "onchange=\"set_shadow('find_calls');\""},
	'sel_badservis':{'sname': 'sel_badservis', 'tab': 'ss_badservise', 'key': 'label', 'val': 'name', 'knull': '', 'on': "onchange=\"set_shadow('find_calls');\"" },
	'sel_cwfind':	{'sname': 'sel_cwfind', 'tab': 'ss_cwfind', 'key': 'cod', 'val': 'name', 'knull': '', 'on': "onchange=\"set_shadow('find_calls');\""	},
	'sel_corder':	{'sname': 'sel_corder', 'tab': 'ss_corder', 'key': 'cod', 'val': 'name', 'on': "onchange=\"set_shadow('find_calls');\""	},
	}

def	cdef2cstt (cstt):
	if cstt < 2:		res = 	['bferr', img_call]
	elif cstt < 7:		res =   ['bfblue', img_auto]
	elif cstt == 7:		res =   ['bfinf', img_auto]
	elif cstt > 7:		res =   ['bfinf', img_call]
	return	res

def	clc_cstatus (crow, d = None):
	""" Определить состояние Вызова	"""
	cstt = 0
	j = 0
	for k in ['t_get', 't_send', 't_arrl', 't_done', 't_close']:
		if d and crow[d.index(k)]:			cstt += 1 << j
		elif type (crow) == dict and crow.get(k):	cstt += 1 << j 
		j += 1
	return	cstt

def	saddres (street, house = None):
	if not street:	return	str(street)
	if house:	return	"%s </b> дом <b> %s" % (street, house)
	else:		return	"%s" % street

'''
fa_prnf = '<i class="fa fa-print fa-lg" title="Печать" ></i>'	#fa-flip-vertical
fa_prnq = '<i class="fa fa-print fa-lg fa-flip-horizontal" title="Обратная сторона" ></i>'	#fa-flip-vertical
fa_x = '<i class="fa fa-times-circle-o fa-lg" ></i>'
fa_1 = '<i class="fa fa-medkit fa-lg" ></i>'
fa_2 = '<i class="fa fa-plus-square fa-lg" ></i>'
fa_3 = '<i class="fa fa-ambulance fa-lg" ></i>'
fa_4 = '<i class="fa fa-heart fa-lg" ></i>'
fa_4 = '<i class="fa fa-heartbeat fa-lg" ></i>'
fa_4 = '<i class="fa fa-hospital-o fa-lg" ></i>'
fa_wres = '<i class="fa fa-window-restore fa-lg" ></i>'
'''
'''	Поля calls
 'number', 'sector', 'profile', 'subst', 'place',
 'street', 'house', 'korp', 'flat', 'pdzd', 'etj', 'pcod', 'phone',
 'reasn', 'name', 'name2', 'age', 'sex', 'rept', 'kto',
 't_get', 'g_disp', 't_send', 's_disp', 't_arrl', 'a_disp', 't_done', 'd_disp',
 'diagn', 'diat', 'alk', 'reslt', 'kuda', 't_go', 'br_ref',
 'smena', 'nbrg', 'pbrg', 'nsbrg', 'doctor', 'ps',
 'c_disp', 't_close',
 'cnum_total', 'id_ims',
 'tm_hosp', 'disp_hosp', 'tm_ps', 'disp_ps', 'tm_trans', 'disp_trans',
 't_wait', 't_serv', 't_hosp 
'''
viewColumns = {
	'call': [],
	}
