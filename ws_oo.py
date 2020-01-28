#!/usr/bin/python -u
# -*- coding: utf-8 -*-
""" WebSocket сервер:	ws_oo.py
	- Отправляет на http://212.193.103.21/smp/03.html

	nohup /home/vds/03/oopy/ws_oo.py > /home/vds/03/log/ws_oo.log  &
"""
import	os, sys, time
import	urllib, json

import struct	# из него нам нужна функция pack() и unpack_from()
import array	# функция array()
import socket	# Сами сокеты
import threading		# По потоку для каждого подключения
from	hashlib import sha1	#Кодирование Access Key о котором будет дальше 
from	base64 import b64encode	#Кодирование Access Key о котором будет дальше

LIBRARY_DIR = r"/home/vds/03/oopy/lib/"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools

mutex_directory = threading.Lock()      # .acquire() .release() with mutex_
mitex_dtmcodes = threading.Lock()
mitex_inncodes = threading.Lock()

GLOB_DIRECTORY = {}		# Kei = Unut ID (code)  - ID Машины
MAX_DTM =	60
DTM_CODES =	[]
for j in xrange(MAX_DTM):	DTM_CODES.append(None)

INN_CODES =	{}
IDS_bm_ssys =	128	# СМП

dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
dboo = dbtools.dbtools('host=212.193.103.21 dbname=b03 port=5432 user=smirnov')
dbrg = dbtools.dbtools('host=212.193.103.21 dbname=region port=5432 user=smirnov')

def	get_geopos (street, house):
	query = "SELECT gy, gx FROM voo_house WHERE sname = '%s' AND house_num LIKE '%s'" % (street, house)
	dyx = dbrg.get_row (query)
	if dyx:	return float(dyx[0]), float(dyx[1])

mitex_events = threading.Lock()
mitex_dcalls = threading.Lock()
GLOB_CALLSLIST = []
GLOB_DCALLS = {}
GLOB_EVENTS = {}
DDISP = {}

def	actual_events ():
	print "События в ОО (Вызова, назначение Бригад)	actual_events"
	chc = ['t_get', 't_send', 't_arrl', 'tm_hosp', 'tm_trans', 'tm_ps', 'nbrg', 'pbrg']
	while not exit_request:
		res = dboo.get_table ("call", "t_done IS NULL ORDER BY t_get DESC")
		if not res:
			with mitex_events:	GLOB_EVENTS[int(time.time())] = "<span class='bfinf'> Нет Вызовов </span>"
		d = res[0]
		for r in res[1]:
			cnttl = r[d.index('cnum_total')]
			if cnttl in GLOB_DCALLS.keys():	### Check
				if r[d.index('t_done')]:
					with mitex_dcalls:	GLOB_DCALLS[cnttl]['opts'] = 'done'
				isupdt = False
				for k in chc:
					if not r[d.index(k)]:	continue
					if not GLOB_DCALLS[cnttl].get(k) or r[d.index(k)] != GLOB_DCALLS[cnttl][k]:
						with mitex_dcalls:	GLOB_DCALLS[cnttl][k] = r[d.index(k)]
						isupdt = True
				if isupdt:
					with mitex_dcalls:	GLOB_DCALLS[cnttl]['opts'] = 'updt'
			else:	### New
				jdct = {}
				for k in chc:
					if r[d.index(k)]:	jdct[k] = r[d.index(k)]
				jdct['YX'] = get_geopos (r[d.index('street')], r[d.index('house')])
				jdct['addr'] = {'s': r[d.index('street')], 'h': r[d.index('house')], 'k': r[d.index('korp')]}
				jdct['opts'] = 'add'
				with mitex_dcalls:
					GLOB_DCALLS[cnttl] = jdct
					GLOB_CALLSLIST.append(cnttl)
		for t in GLOB_DCALLS.keys():
			if GLOB_DCALLS[t]['opts'] in ['add', 'updt', 'done']:	print t, GLOB_DCALLS[t]['opts'], GLOB_DCALLS[t]['YX']
		print '#'*22, "actual_events", len(res[1])
		time.sleep(11)


def	get_disp (intm, addr, request):
	""" Читать реквизоты пользователя	"""
	global	DDISP
	if request:	disp = request.get('disp')
	ddisp  = DDISP.get(disp)
	if not ddisp:
		ddisp = dboo.get_dict ("SELECT * FROM usr03 WHERE disp = %s" % disp)
		if not ddisp:	return "Not DDISP"
		DDISP[disp] = ddisp
		return	str(ddisp)
	list_where = []
	if ddisp['type'] == 8:	list_where.append("subst = %s" % ddisp['subst'])
	list_where.append("t_done IS NULL")
#	list_where.append("ORDER BY t_get DESC")
	res = dboo.get_table ("call", " AND ".join(list_where) +" ORDER BY t_get DESC")
	if not res:	return "Error"
	lout = []
#	<span class="line bferr"> <i class="fa fa-newspaper-o fa-lg" aria-hidden="true"></i>&nbsp; 1119 <b>18Р </b> </span>
	d = res[0]
	jcalls = []
	for r in res[1]:
		jcalls.append(r[d.index('cnum_total')])
		if ddisp.has_key('calls') and r[d.index('cnum_total')] in ddisp['calls']:	continue
		lout.append("""<li class='bfligt line' onclick="open_call(%s)"> <i class="fa fa-newspaper-o fa-lg" aria-hidden="true"></i> %s %s</li>""" % (
			r[d.index('cnum_total')], r[d.index('number')], r[d.index('reasn')]))	#(intm - r[d.index('t_get')])/60))
		print 
	print jcalls, intm	#"\n".join (lout)
	if jcalls != ddisp.get('calls'):	ddisp['calls'] = jcalls
	if not lout:	return
	lout.insert(0, "<b>Новые вызова: </b>")
	return	"\n".join (lout)

def	actual_directory ():
	print	"Движение Машин / Бригад	actual_directory"
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
	global	INN_CODES, IDS_bm_ssys

	last_id = 0
	bm_ssys = 2
	dsleep = 1
	j = 0
	while not exit_request:
		if last_id == 0:
			rid = dbi.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = %s)" % IDS_bm_ssys)
			last_id = rid[0]
			swhere = 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = %s)' % IDS_bm_ssys
			res = dbi.get_table('vlast_pos', swhere)
		else:
			swhere = 'tinn IN (SELECT inn FROM org_desc WHERE bm_ssys = %s) AND id_dp > %s ORDER BY t' % (IDS_bm_ssys, last_id)
			res = dbi.get_table('vdata_pos', swhere)

		tm = int(time.time())
		jtm = tm % MAX_DTM
		if not res:
			with mitex_dtmcodes:
				DTM_CODES[jtm] = None
			time.sleep(2)
			continue
		codes = [tm]
		d = res[0]
		for r in res[1]:
			code = r[d.index('code')]
			if not code in codes:	codes.append(code)
			with mutex_directory:
				cdct = GLOB_DIRECTORY.get(code)
				if cdct:	# фиксировать текущие изменения
					if cdct['t'] > r[d.index('t')]:		continue
				#	if not cdct.get('gosnum'):	gosnum = r[d.index('gosnum')]
					cdct['r'].insert(0, [float(r[d.index('y')]),  float(r[d.index('x')])])
					if len (cdct['r']) > 10:	cdct['r'].pop(-1)
					cdct['t'] = r[d.index('t')]
					cdct['sp'] = r[d.index('sp')]
					if r[d.index('sp')] < 1:
						try:
							if abs(cdct['r'][0][0] - cdct['r'][1][0]) > 0.0001 or abs(cdct['r'][0][1] - cdct['r'][1][1]) > 0.0001:	cdct['sp'] = 1
						except:	pass
					cdct['opts'] = "%s %s <br>" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (r[d.index('t')])), str_speed(r[d.index('sp')]))
				else:
					gosnum = r[d.index('gosnum')]
					bname = marka = ''
					if 'bname' in d and r[d.index('bname')]:	bname = r[d.index('bname')]
					if 'marka' in d and r[d.index('marka')]:	marka = r[d.index('marka')]
					if marka and bname:				# r[d.index('marka')]:
						rem = "%s<br>%s" % (marka, bname)	#r[d.index('marka')], r[d.index('bname')])
					else:	rem = "%s" % bname			# r[d.index('bname')]
					opts = "%s %s <br>" % (time.strftime("<span class='fligt sz12'>%T</span>", time.localtime (r[d.index('t')])), str_speed(r[d.index('sp')]))
					GLOB_DIRECTORY[code] = {'r': [[float(r[d.index('y')]),  float(r[d.index('x')])]], 'gosnum': gosnum, 't': r[d.index('t')], 'sp': r[d.index('sp')], 'rem': rem, 'opts': opts }
					if (tm - r[d.index('t')]) > 3600:    GLOB_DIRECTORY[code]['style'] = "color: #a77"

			if INN_CODES.has_key(r[d.index('tinn')]):
				if not code in INN_CODES[r[d.index('tinn')]]:
					with mitex_inncodes:
						INN_CODES[r[d.index('tinn')]].append (code)
			else:
				with mitex_inncodes:
					INN_CODES[r[d.index('tinn')]] = [code]
			if 'id_dp' in d:
				if last_id < r[d.index('id_dp')]:	last_id = r[d.index('id_dp')]

		tm = int(time.time())
		jtm = tm % MAX_DTM
		with mitex_dtmcodes:
			DTM_CODES[jtm] = codes

		if len(codes) == 1 and dsleep < 15:
			dsleep += 1
			print "dsleep", dsleep
		else:	dsleep = 1
		'''
		print	"dsleep:", dsleep, len(res[1]), "\tlast_id:", last_id
		time.sleep(1)
		'''
		time.sleep(dsleep)

def	is_legal_ip (addr = None):
	""" Проверка принадлежности IP внутренней сети (разрешенные IP)	"""
	print	addr
	return	True	### DEBUG
	
def	get_calls (intm, request, is_start, addr):
	global	GLOB_DCALLS
	list_calls = []
	y = 44.0
	legal_ip = is_legal_ip(addr)	### Проверка принадлежности IP
	for cnttl in GLOB_DCALLS.keys():
		jdc = GLOB_DCALLS[cnttl].copy()
#		if not jdc['YX']:	continue
		dcode = {}
		if is_start or jdc['opts'] in ['add', 'updt']:
			if jdc['YX']:
				dcode['p'] = jdc['YX']
			else:
				y += .01 
				dcode['p'] = [56.34, y]
			dcode['cnttl'] = cnttl
			if legal_ip:		### Для внутренней сети (разрешенные IP)
				ppups = ["""<div class='bfinf green line bgyellow' onclick="open_call(%s);"> %s <span class='bfligt'> %s </span></div>""" % (cnttl, cnttl, time.strftime("от: %H:%M", time.localtime (jdc['t_get'])))]
			else:	ppups = ["<div class='bfinf'> %s <span class='bfligt'> %s </span></div>" % (cnttl, time.strftime("от: %H:%M", time.localtime (jdc['t_get'])))]
			addr = "<div><span class='bfinf'> %s </span>" % jdc['addr']['s']
			if jdc['addr'].get('h'):	addr += "д.<span class='bfinf'>%s</span> " % jdc['addr']['h']
			if jdc['addr'].get('k'):	addr += "корп.<span class='bfinf'>%s</span> " % jdc['addr']['k']
			ppups.append (addr +"</div>")
			if jdc.get('nbrg'):
				sbrg = "<span class='bfinf'>%s%s</span>" % (jdc.get('nbrg'), jdc.get('pbrg'))
			else:	sbrg = "???"
			if jdc.has_key('t_arrl'):
				ppups.append("<div>Бригада %s прибыла в <span class='bfligt'> %s </spah></div>" % (sbrg, time.strftime("%H:%M", time.localtime (jdc['t_arrl']))))
				img = '<span class="fa-stack fa-2x bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa fa-medkit fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			elif jdc.has_key('t_send'):
				ppups.append("<div>Передан бригаде %s в <span class='bfligt'> %s </spah></div>" % (sbrg, time.strftime("%H:%M", time.localtime (jdc['t_send']))))
				img = '<span class="fa-stack fa-2x bfblue"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa fa-ambulance fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			else:
				img = '<span class="fa-stack fa-2x bferr"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa fa-user fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			dcode['ppup'] = "\n".join(ppups)
			dcode['html'] = '<div class="btn-group bferr"> %s </div>' % img
			with mitex_dcalls:	GLOB_DCALLS[cnttl]['opts'] = 'view'
			list_calls.append(dcode)

	return	list_calls
			

def	str_speed (sp):
	if sp:	return	"<span class='fligt sz12'> v:<b>%s</b>км/ч</span>" % sp
	return 	"<span class='bferr sz12'>Стоит</span>"

def	check_dcode (tm, codes):
	list_data = []
	for jcode in codes:
		dcode = GLOB_DIRECTORY[jcode].copy()
		if dcode:
			dcode['code'] = jcode
			if dcode.get('rem'):		dcode['opts'] = dcode['opts']+ dcode['rem']
			if (tm - dcode['t']) > 3600:	#dcode['style'] = "color: #77a"
				img = '<span class="fa-stack fa-lg bfligt"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.4"></i><i class="fa fa-ambulance fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			elif dcode['sp'] < 1:
				img = '<span class="fa-stack fa-lg bfblue"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.4"></i><i class="fa fa-ambulance fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			else:	img = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa fa-ambulance fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			dcode['html'] = '<div class="btn-group bfinf"> %s </div>' % img
			list_data.append(dcode)
		else:	print "NOT jcode:", jcode, dcode
	return	list_data

def	get_poss (tm, tm_old, request):
	global	GLOB_DIRECTORY, DTM_CODES, MAX_DTM
#	global	INN_CODES, IDS_bm_ssys
#	print 'DTM_CODES', DTM_CODES
#	if (tm-tm_old) > 1:	print	"\t", tm, "\t(tm-tm_old)", (tm-tm_old)

	jtm = tm % MAX_DTM
	if not DTM_CODES[jtm]:	return
	sinn = request.get('org_inn')
	if sinn and sinn.isdigit() and int(sinn) > 1000000000:
		inn = int(sinn)
		if not inn in INN_CODES.keys():		return
	else:	inn = None

	list_data = []
	codes = DTM_CODES[jtm]
	if tm != codes[0]:	#DTM_CODES[jtm][0]:
	#	print "ERR tm:", tm, jtm, codes
		with mitex_dtmcodes:
			DTM_CODES[jtm] = None
		return
	return	check_dcode (tm, codes[1:])
	###

def	get_all_poss (tm, request):
	""" Подгоро	"""
	global  GLOB_DIRECTORY, INN_CODES
	sinn = request.get('org_inn')
	if sinn and sinn.isdigit() and int(sinn) > 1000000000:
		inn = int(sinn)
		if not inn in INN_CODES.keys():		return
	else:	inn = None

	return	check_dcode (tm, GLOB_DIRECTORY.keys())
	###

def parse_sform (sdate = ''):	# 'TEST=atp&view_gosnum=off&view_trace=off&view_routes=off&cod_region=&org_inn=0&bm_ssys=2&snow_stat=&snow_flag=&leaflet-base-layers=on'):
	res = {}
	for sopt in sdate.split('&'):
		try:
			k, v = sopt.split('=', 1)
			if v:	res[k] = v
		except:	pass
	return	res 

HOST = '212.193.103.21'	#'10.10.2.241'
PORT = 9993

def unpack_frame (data):
	""" Эта функция возвращает словарь типа: {'opcode':1, 'length':15, 'fin':1, 'masked':1, 'payload': 'WebSocket rocks' }
	И для обращения к самому сообщению надо просто будет обращаться к data['payload']
	"""
	frame = {}
	byte1, byte2 = struct.unpack_from('!BB', data)
	frame['fin'] = (byte1 >> 7) & 1
	frame['opcode'] = byte1 & 0xf
	masked = (byte2 >> 7) & 1
	frame['masked'] = masked
	mask_offset = 4 if masked else 0
	payload_hint = byte2 & 0x7f
	if payload_hint < 126:
		payload_offset = 2
		payload_length = payload_hint
	elif payload_hint == 126:
		payload_offset = 4
		payload_length = struct.unpack_from('!H',data,2)[0]
	elif payload_hint == 127:
		payload_offset = 8
		payload_length = struct.unpack_from('!Q',data,2)[0]
	frame['length'] = payload_length
	payload = array.array('B')
	payload.fromstring(data[payload_offset + mask_offset:])
	if masked:
		mask_bytes = struct.unpack_from('!BBBB',data,payload_offset)
		for i in range(len(payload)):
			payload[i] ^= mask_bytes[i % 4]
	frame['payload'] = payload.tostring()
	return frame

def pack_frame (buf, opcode, base64=False):
		 
	if base64:	buf = b64encode(buf)
		 
	b1 = 0x80 | (opcode & 0x0f)	# FIN + opcode
	payload_len = len(buf)
	if payload_len <= 125:
		header = struct.pack('>BB', b1, payload_len)
	elif payload_len > 125 and payload_len < 65536:
		header = struct.pack('>BBH', b1, 126, payload_len)
	elif payload_len >= 65536:
		header = struct.pack('>BBQ', b1, 127, payload_len)
	return header+buf

def create_handshake (handshake):
	"""Подробная информация о Sec-WebSocket-Key
	Для Sec-WebSocket-Accept: x3JJHMbDL1EzLkh9GBhXDw == 258EAFA5-E914-47DA-95CA-C5AB0DC85B11, хэшированние SHA-1,
		дает значение x1d29ab734b0c9585240069a6e4e3e91b61da1969 в шестнадцатеричном формате. 
	Кодирование хэша SHA-1 с помощью Base64 дает HSmrc0sMlYUkAGmm5OPpG2HaGWk =, 
		которое является значением Sec-WebSocket-Accept
	"""
	try:
		lines = handshake.splitlines()	# Делим построчно
		for line in lines:		# Итерируемся по строкам
			parts = line.partition(": ")	# Делим по ':'
		#	print parts
			if parts[0] == "Sec-WebSocket-Key":
				key = parts[2]	# Находим необходимый ключ
		key += "258EAFA5-E914-47DA-95CA-C5AB0DC85B11" 
	#	print key
		Acckey=b64encode((sha1(key)).digest())
		return ("\r\n".join ([
			"HTTP/1.1 101 Switching Protocols",
			"Upgrade: websocket",
			"Connection: Upgrade",
			"Sec-WebSocket-Accept: %s" % Acckey, "\r\n"]))
	except:
		print "except: create_handshake", handshake
		return	1002

def handle (s, addr):
	""" И будем в функции handle получать сообщение открывать его, закрывать и посылать обратно	"""
	global	INN_CODES, IDS_bm_ssys
	try:
		data = s.recv(1024)
#		print data
		ans = create_handshake(data)
		if type(ans) == int:
			s.send(pack_frame("%s\r\n" % ans, 0x8))
			return
		s.send(ans)	#create_handshake(data))
		intm = int(time.time())
		tm_old = intm -1	# MAX_DTM
		request = None
		is_start = True
		while True:
			s.settimeout(1)
			try:
				data = s.recv(1024)
			except:
				data = ''
				pass
			if not data:	#	break
				if s.send (pack_frame('PING',0x9)) == 0:	break
				s.settimeout(10)
				data = s.recv(1024)
			unpdata = unpack_frame (data)
		#	print "unpdata", unpdata, time.strftime("\t%T", time.localtime (time.time ()))
			if unpdata['opcode'] == 0x8:	break
			if request == None:
				request = parse_sform (unpdata['payload'])
				print '\trequest', request
			elif unpdata['payload'] != 'PING':
				print "\tSS unpdata:", unpdata['payload'], parse_sform (unpdata['payload'])
	
			texts = [ "~last_time|%s" % time.strftime("%T", time.localtime(intm)) ]
	#		events = actual_events (intm, addr, request)
	#		if events:	texts.append ("~events| %s" % events)
			ddata = calls = events = None
			calls = get_calls (intm, request, is_start, addr)
			if calls:	texts.append ("~eval| get_list_calls (%s)" % json.dumps(calls))
			### TS
			if is_start:	###	Новое соединение
				ddata = get_all_poss (intm, request)	### TS
				is_start = False
			else:
				ddata = get_poss (intm, tm_old, request)
			if ddata:	texts.append ("~eval| get_list_autos (%s)" % json.dumps(ddata))
			dpack = pack_frame ("\n".join(texts), 0x1)
			sendln = 0
			while sendln < len(dpack):
				sln = s.send (dpack[sendln:])
				if sln == 0:	raise RuntimeError("socket connection broken")
				sendln += sln
			
		#	s.send (pack_frame("~last_time|%s" % time.strftime("%T", time.localtime(intm)), 0x1))
			tm_old = intm
			intm = int(time.time())
			time.sleep(1)
			if exit_request:	break
	except:	pexcept ('handle')
	finally:
		s.close()
		print 'Close', addr


def start_server ():
	s = socket.socket()
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#	s.bind(('', 9999))
	s.bind((HOST, PORT))
	s.listen(1)
	while 1:
		conn, addr = s.accept()
		print 'Connected by', addr
		threading.Thread(target = handle, args = (conn, addr)).start()

HEADS = """
Accept: text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Cache-Control: no-cache
Connection: keep-alive, Upgrade
Host: 212.193.103.20:9999
Origin: http://212.193.103.21
Pragma: no-cache
Sec-WebSocket-Extensions: permessage-deflate
Sec-WebSocket-Key: BN1cjfSLyFjHesK9xe5AAQ==
Sec-WebSocket-Version: 13
Upgrade: websocket
User-Agent: Mozilla/5.0 (X11; Linux x86_64…) Gecko/20100101 Firefox/60.0
"""
def	pexcept (mark = None, exit = False):
	exc_type, exc_value = sys.exc_info()[:2]
	print "EXCEPT %s:\t" % mark, exc_type, exc_value
	if exit:	os._exit(exit)

def	test():
	print "TEST"

mutex_exit =  threading.Lock()
exit_request =	False

if __name__ == "__main__": 
	'''
	actual_events()
	test ()
	actual_directory ()
	print HEADS
	print create_handshake (HEADS)
	'''
	try:
		threading.Thread(target = actual_events, args = ()).start()
		time.sleep(1)
		threading.Thread(target = actual_directory, args = ()).start()
		time.sleep(2)
		start_server()
	except	KeyboardInterrupt:
		mutex_exit.acquire()
		exit_request = True
		mutex_exit.release()
	#	pass
	except:	pexcept('MAIN')

