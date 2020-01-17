#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import  os, sys, time

LIBRARY_DIR = r"/home/vds/03/oopy/lib"            # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

bases = {
	'oo': 'host=127.0.0.1 dbname=b03 port=5432 user=smirnov',
	'ss': 'host=127.0.0.1 dbname=ss2013 port=5432 user=smirnov',
	}

import	session, dbtools
import	tools as T
from	global_vals import *
from	parse_forms import *

dboo = dbtools.dbtools (bases['oo'])

def	get_dboo (query):
	return	dboo.get_dict (query)

def	out_form (SS, request):
	cnum_ttl = 127627
	query = "SELECT * FROM calls WHERE cnum_total = %s" % cnum_ttl
	
	dcall = dboo.get_dict (query)
	opts = {}
	obj = {}
	US_ROW = SS.objpkl.get('us_row')
	cbrig = [0,0,0,0,0]
	obj['user'] = "%s, %s" % (US_ROW['cod'], US_ROW['fio'])
	obj['subst'] = "%s %s" % (dcall['subst'], dboo.get_dict("SELECT name FROM sp_station WHERE cod = %s" % dcall['subst'])['name'])
	obj['brigs'] = "%s %s" % (dcall['nbrg'], dcall['pbrg'])	#	nbrg	pbrg	nsbrg	br_ref
	obj['number'] = str(dcall['number'])
	obj['date'] = sdater(dcall['t_get'])
#	obj['date'] = sdtime(dcall['t_get'], "%d %B %Y")
	
	if dcall['doctor']:
		obj['doctor'] = T.svals (dboo, {'sname': 'doctor', 'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['cod', 'name', 'post_name']}, dcall['doctor'])
		ddoc = dboo.get_dict ("SELECT cod, name, post_name, n_catg FROM vperson_sp WHERE cod = %s" % dcall['doctor'])
#		obj['doctor'] = "%s %s %s" % (ddoc['cod'], ddoc['name'], ddoc['post_name'])
		if ddoc['n_catg'] > 0:	cbrig[(ddoc['n_catg'] -1)] += 1
	if dcall['br_ref']:
		dbrg = dboo.get_dict ("SELECT * FROM bnaryd WHERE br_id = %s" % dcall['br_ref'])
		if dbrg['feldsh']:
			obj['feldsh'] = T.svals (dboo, {'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name', 'post_name']}, dbrg['feldsh'])
			cbrig[1] += 1
		if dbrg['sanitr']:
			obj['sanitr'] = T.svals (dboo, {'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name']}, dbrg['sanitr'])
			cbrig[2] += 1
		if dbrg['driver']:
			obj['driver'] = T.svals (dboo, {'tab': 'vperson_sp', 'key': 'cod', 'val': 'name, post_name', 'rvals': ['name']}, dbrg['driver'])
			cbrig[3] += 1
		else:	obj['driver'] = '_'*20
		obj['auto'] = T.svals (dboo, {'tab': 'automobile', 'key': 'id_auto', 'val': 'id_auto, reg_num', 'rvals': ['reg_num']}, dbrg['auto'])
	obj['cbrig'] = str(cbrig)
	
	obj['t_get'] = sdtime(dcall['t_get'])
	obj['t_send'] = sdtime(dcall['t_send'])
	obj['t_arrl'] = sdtime(dcall['t_arrl'])
	obj['t_done'] = sdtime(dcall['t_done'])
	obj['tm_trans'] = sdtime(dcall['tm_trans'])
	obj['tm_hosp'] = sdtime(dcall['tm_hosp'])
	obj['tm_ps'] = sdtime(dcall['tm_ps'])
#	obj['t_get'] = sdtime(dcall['t_get'])

	obj['saddres'] = saddres (dcall['street'], dcall['house'])
	#	korp', 'flat', 'pdzd', 'etj', 'pcod', 'phone', 'name', 'name2', 'kto', 'age', 'sex'
	for k in ['korp', 'flat', 'pdzd', 'etj', 'pcod', 'age', 'sex']:
		if dcall[k]:	obj[k] = "<b>%s</b>" % dcall[k]
		else:		obj[k] = "_"*3
	for k in ['phone', 'name', 'name2']:
		if dcall[k]:	obj[k] = "<b>%s</b>" % dcall[k]
		else:		obj[k] = "_"*23
	obj['kto'] = T.svals(dboo, {'tab': "who_call", 'key': 'cod', 'rvals': ['name']}, dcall['kto'])
	if dcall['t_done'] > 0:
		obj['dtime'] = "%d мин" % ((dcall['t_done'] - dcall['t_get']) // 60)

	obj['g_disp'] = "%s %s" % (dcall['g_disp'], dboo.get_dict("SELECT name FROM person_sp WHERE cod = %s" % dcall['g_disp'])['name'])
#	obj['s_disp'] = "%s %s" % (dcall['s_disp'], dboo.get_dict("SELECT name FROM person_sp WHERE cod = %s" % dcall['s_disp'])['name'])
#	print obj;	return

	obj['j_registr'] = T.scheckboxes (dboo, {'tab': 'j_registr', 'key': 'cod', 'val': 'name', })
	obj['j_social'] = T.scheckboxes (dboo, {'tab': 'j_social', 'key': 'cod', 'val': 'name', })
	obj['j_reason'] = T.scheckboxes (dboo, {'tab': 'j_reason', 'key': 'cod', 'val': 'name', })

	obj['j_cause'] = T.scheckboxes (dboo, {'tab': 'j_cause', 'key': 'cod', 'val': 'name', })
	obj['j_obj_general'] = T.scheckboxes (dboo, {'tab': 'j_obj_general', 'key': 'cod', 'val': 'name', })
	obj['j_obj_behav'] = T.scheckboxes (dboo, {'tab': 'j_obj_behav', 'key': 'cod', 'val': 'name', })
	obj['j_obj_cons'] = T.scheckboxes (dboo, {'tab': 'j_obj_cons', 'key': 'cod', 'val': 'name', })
	obj['j_obj_pupils'] = T.scheckboxes (dboo, {'tab': 'j_obj_pupils', 'key': 'cod', 'val': 'name', })
	obj['j_obj_integ'] = T.scheckboxes (dboo, {'tab': 'j_obj_integ', 'key': 'cod', 'val': 'name', })
	obj['j_obj_breath'] = T.scheckboxes (dboo, {'tab': 'j_obj_breath', 'key': 'cod', 'val': 'name', })
	obj['j_obj_rattles'] = T.scheckboxes (dboo, {'tab': 'j_obj_rattles', 'key': 'cod', 'val': 'name', })
	obj['j_obj_wind'] = T.scheckboxes (dboo, {'tab': 'j_obj_wind', 'key': 'cod', 'val': 'name', })
	obj['j_obj_tones'] = T.scheckboxes (dboo, {'tab': 'j_obj_tones', 'key': 'cod', 'val': 'name', })
	obj['j_obj_noise'] = T.scheckboxes (dboo, {'tab': 'j_obj_noise', 'key': 'cod', 'val': 'name', })
	obj['j_obj_pulse'] = T.scheckboxes (dboo, {'tab': 'j_obj_pulse', 'key': 'cod', 'val': 'name', })
	obj['j_obj_lang'] = T.scheckboxes (dboo, {'tab': 'j_obj_lang', 'key': 'cod', 'val': 'name', })
	obj['j_obj_stom'] = T.scheckboxes (dboo, {'tab': 'j_obj_stom', 'key': 'cod', 'val': 'name', })
	print obj['j_registr']

	print	"""~mybody|<div id="list_calls" style="border: thin solid #668; width: 100%; position: absolute; background-color: #fff; padding: 2px; height: 100%">"""
	print	"<div type='hidden' style='top: 40px; left: 180px; width: 900px; border: thin solid #668; background-color: #ffe; position: absolute; z-index: 1112' >"
#	print	"out_form", obj.keys()
	parse_forms (opts, obj, 'f110u.html')
	print	"</div>"
	print	"</div>"

#def	scheckbox (dboo, dctt, kval = ''):
	
	
if __name__ == "__main__":
	print
	
