#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	os, sys, time
LIBRARY_DIR = r"/home/vds/03/oopy/lib"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools
#dboo = dbtools.dbtools ('host=127.0.0.1 dbname=b03 port=5432 user=smirnov')
dbrgn = dbtools.dbtools ('host=127.0.0.1 dbname=region port=5432 user=smirnov')

def     upper_ru (sinp):
	sdn =   u'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'
	sup =   u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ'
	sout = []

	for c in unicode(sinp, "utf-8"):
		if c in sdn:
			sout.append (sup[sdn.index(c)])
		else:	sout.append (c)
	return  ''.join(sout).encode("utf-8")

def	find_street (lstrt, vname, pdiv, region = None):
	ss = upper_ru(lstrt).strip().replace(' ', '%')
#	query = "SELECT ind, name, tag FROM street WHERE name LIKE '%%%s%%'" % ss
	query =	"SELECT s.ind, s.name, t.ind, t.name FROM street s LEFT JOIN street t ON s.tag = t.ind WHERE s.name LIKE '%%%s%%'" % ss
	row = dbrgn.get_rows (query)
	if not row:	return	lstrt	#query
	lout = []
	for r in row:
		ind, name, tind, tname = r
		if not tind:	tind = ind
		if not tname:	tname = name
		lout.append ("""<li class='line' style="list-style: none;" onclick="document.myForm.%s.value='%s'; document.myForm.%s_id.value='%s'; $('#%s').html('')"> &nbsp; %s</li>""" % (vname, tname, vname, tind, pdiv, name))
	#	lout.append ("""<li class='line' style="list-style: none;" onclick="document.myForm.%s.value='%s'; document.myForm.%s_id.value='%s'; "> &nbsp; %s</li>""" % (vname, tname, vname, tind, name))
	if lout:	return	"\n".join(lout)
	else:		return	query

def	view_houses (street, street_id, pdiv = 'RESULT'):
	if not	(street_id and street_id.isdigit()):	return
	lout = ["<span class='bfinf'> %s:</span><br> " % street]
	query = "SELECT sector, house_num, gx, gy FROM oo_house WHERE street_id = %s" % street_id
	row = dbrgn.get_rows (query)
	if not row:		return
	j = 0
	for r in row:
		sector, house_num, gx, gy = r
		if not house_num:	continue
		lout.append ("""<span class='line omsys' onclick="document.myForm.house.value='%s'; $('#%s').html(''); "> &nbsp; %s &nbsp; </span>""" % (house_num, pdiv, house_num))
		j += 1
		if (j % 10) == 0:	lout.append ("<br>")
	if j == 0:	lout.append (" &nbsp; &nbsp; <span class='bferr'> Домов нет. </span> %s %s %s" % (sector, gx, gy))
	return "\n".join(lout)
	

if __name__ == "__main__":
#	find_street ('+33')
	sss = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ 12345 !@#$%'абвгдеёжзийклмнопрстуфхцчшщьыъэюя'"
	print	sss
	print	upper_ru (sss)
