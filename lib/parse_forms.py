#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time
'''	-> global_vals.py
img_auto =	'<i class="fa fa-ambulance fa-lg" aria-hidden="true"></i>&nbsp;'
img_call =	'<i class="fa fa-newspaper-o fa-lg" aria-hidden="true"></i>&nbsp;'
img_brig =	'<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>&nbsp;'
fimg_brig =	'<i class="fa fa-medkit fa-lg %s" aria-hidden="true"></i>&nbsp;'

img_brigg =	'<i class="fa fa-medkit fa-lg bfinf" aria-hidden="true"></i>&nbsp;'
img_brigl =	'<i class="fa fa-medkit fa-lg bfligt" aria-hidden="true"></i>&nbsp;'


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

inputText = lambda nm, val, opts:  "<input type='text' name='%s' value='%s' %s />" % (nm, val, opts)
qhistory_calls = lambda tm, disp, sfrom, sset, swhere:	"INSERT INTO history_calls (tm, who_disp, sfrom, sset, swhere) VALUES (%s, %s, '%s', '%s', '%s');" % (tm, disp, sfrom, sset, swhere)
qhistory_brigs = lambda tm, disp, sfrom, sset, swhere:	"INSERT INTO history_brigs (tm, who_disp, sfrom, sset, swhere) VALUES (%s, %s, '%s', '%s', '%s');" % (tm, disp, sfrom, sset, swhere)

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
'''
phforms =	r"/home/vds/03/oopy/forms"

def	parse_forms (opts, obj, fname):
	lifo = []
	skip = False
	try:
		ff = open (os.path.join(phforms, fname))
		ss = fname
		while (ss):
			ss = ff.readline()
			s = ss.strip()	####	??????????????
			# Поиск Условных выражений {% if [not] ... %}
			js = s.find('{%')
			if js >= 0: 
				ks = s.find('%}')
				boll = s[js+2:ks].strip().split(' ')
				if boll[0] == 'if':
					lifo.append(boll)
					if boll[1] != 'not':
						if not obj.get(boll[1]):	skip = True
					else:
						if obj.get(boll[2]):	skip = True
				elif boll[0] == 'else':
					if skip:
						skip = False
					else:	skip = True
				elif boll[0] == 'endif':
					lifo.pop()
					skip = False
				else:	pass
				continue

			if skip:	continue
			print	parse_line (obj, s)
	except IOError:
		print "<div class='bferr'> &nbsp; parse_forms exceptions.IOError. Fail: '%s' </div>" % fname

def	parse_line (obj, s):
	""" Поиск {{ ... }} и Подстановке значений переменных в строку	"""
	oll = [] 
	js = s.find('{{')
	if js == -1:	return	s

	ks = s.find('}}')
	oll.append (s[:js])
	vv = obj.get(s[js+2:ks].strip())
	if vv:	oll.append (str(vv))
	else:	oll.append ('')
	oll.append (parse_line (obj,s[ks+2:]))
	return	"".join(oll).strip()

if __name__ == "__main__":
	obj = {
	'sel_bwfind': '<select name=\'sel_bwfind\' onchange="set_shadow(\'BRG_WOKE\');">\n<option value=\'1\' selected> \xd0\x91\xd1\x80\xd0\xb8\xd0\xb3\xd0\xb0\xd0\xb4\xd1\x8b \xd0\xbd\xd0\xb0 \xd0\xbb\xd0\xb8\xd0\xbd\xd0\xb8\xd0\xb8 </option>\n<option value=\'2\' > \xd0\x94\xd0\xb5\xd0\xb6\xd1\x83\xd1\x80\xd0\xbd\xd1\x8b\xd0\xb9 \xd0\xbd\xd0\xb0\xd1\x80\xd1\x8f\xd0\xb4 </option>\n</select>',
	'online': True,
	'sel_smen': '<select name=\'sel_smen\' onchange="set_shadow(\'BRG_WOKE\');">\n<option value=1> 1 </option>\n<option value=2> 2 </option>\n<option value=3> 3 </option>\n<option value=4 selected> 4 </option></select>',
	}
#	parse_forms ({}, obj, "find_brigs.html")
	parse_forms ({}, {'yes': 123, 'zzz': True}, "ptest.html")
	print	parse_line ({'xxx': 'XXX'}, "parse_line [{{xxx}}] [{{ xxx }}] [{{ yyy }}] [{{zzz}}]")
