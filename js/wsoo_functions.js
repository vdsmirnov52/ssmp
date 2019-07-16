/**     \file   /js/atp/wsoo_functions.js
 *      \brief  Обеспечение обмена данными через tWebSocket
 */
//var wsUri = "ws://localhost:9999/"; var output; 
var wsUri = "ws://212.193.103.21:9993/"; var output;
var websocket = null;

function start_ws () {
//	clear_map_object (listTS);
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
