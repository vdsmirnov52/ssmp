/**     \file   /js/atp/wsoo_functions.js
 *      \brief  Обеспечение обмена данными через tWebSocket
 */
//var wsUri = "ws://localhost:9999/"; var output; 
var wsUri = "ws://212.193.103.21:9993/"; var output;
var websocket = null;

function start_ws () {
//	clear_map_object (list_autos);
//	clear_map_object (list_tracks);
	if (websocket != null)   websocket.close();

	websocket = new WebSocket(wsUri);
	websocket.onopen = function(evt) { websocket.send ('TEST=atp&' + $('form').serialize());	}
	websocket.onmessage = function(evt) {
		$('#log').html('');
		var inc_message = evt.data;
		parse_message (inc_message);
	}
	websocket.onerror = function(evt) { $('#log').html('<span style="color: red; font-weight: bold;">WS ERROR:' +evt.data+ '</span>');      }
	websocket.onclose = function(evt) { $('#log').html('<span style="color: red; font-weight: bold;">DISCONNECTED</span>');   }
}
function seld2wsoo (txt) {
	if (websocket != null) {
		websocket.send ('TEST=seld2wsoo&' + txt +$('form').serialize());
	} else {
		alert ('WebSocket is close!');
	}
}
//function close_ws () {	if (websocket != null) { websocket.onclose = function(evt) { $('#log').html('<span style="color: red;">DISCONNECTED</span>');   }}}

function parse_message (data) {
	if  (data == 'submit') {
		document.mainForm.submit ();
	} else {
		var arr = data.split  ('~');
		for  (var j in arr) {
			var vall = arr [j].split  ('|');
			if ('eval' == vall [0]) {
				eval (vall [1]);
			} else if ((vall [0] != '') && (document.getElementById(vall [0]))) {
				document.getElementById(vall [0]).innerHTML = vall [1];
			}
		}
	}
}

function	clear_map_object (obj) {
	if (! obj)	return;
	for (k in obj) {
		if (obj.hasOwnProperty(k))	obj[k].remove();
		delete(obj[k]);
	}
}
var	list_autos = {},
	list_calls = {};

function	get_list_autos (data) {	// читать Маштны (Бригады)
	if (mymap == null)	return;
	var plist = eval(data);
	for (var i=0; i<=plist.length-1; i++) {
		var gosnum = plist[i]['gosnum'];
		var code = plist[i]['code'];
		var YX = plist[i]['r'][0];
		if (list_autos[code]) {
			list_autos[code].remove();
			delete(list_autos[code]);
		}
		var str_ppup = "<span class='bfinf'>"+ gosnum +"</span> " +plist[i]['opts'];
		if (plist[i]['html']) {
			var str_html = plist[i]['html'];
		} else {
			var img = '<span class="fa-stack fa-lg bfinf"><i class="fa fa-circle fa-stack-2x" style="opacity: 0.6"></i><i class="fa fa-ambulance fa-stack-1x fa-inverse" aria-hidden="true"></i></span>'
			var str_html = '<div class="btn-group bfinf">'+ img +'</div>';
		}
		list_autos[code] = L.marker(YX, {icon: L.divIcon({className: 'icon', iconAnchor: [12,24], html: str_html})}).addTo(mymap).bindPopup(str_ppup);
	}
}

function	get_list_calls (data) {	// читать Вызов 
	if (mymap == null)	return;
	var clist = eval(data);
	for (var i=0; i<=clist.length-1; i++) {
		if (clist[i]['p'] == null)		continue;
		var cnttl = clist[i]['cnttl'];
		if (list_calls[cnttl]) {
			list_calls[cnttl].remove();
			delete(list_calls[cnttl]);
			if (clist[i]['opts'] == 'done')	continue;
		}
		var YX = clist[i]['p']
		var str_ppup = clist[i]['ppup'];
		var str_html = clist[i]['html'];
		
		list_calls[cnttl] = L.marker(YX, {icon: L.divIcon({className: 'icon', iconAnchor: [24,28], html: str_html})}).addTo(mymap).bindPopup(str_ppup);
	}
}
