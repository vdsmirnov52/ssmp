/**	\file	js/oopy.js
 *	$Id$

$(document).ready(function () {
	$.ajaxSetup({ url: "oo.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	})
 */
function	getWindowSize () {
	if (document.documentElement.clientWidth) {
		client = "'client': {'W': "+document.documentElement.clientWidth +", 'H':" +document.documentElement.clientHeight +"}";
	} else  client = "";	// document.write ("Размер документа - Unknown<br>");
	bclient = "'bclient': {'W': " +document.body.clientWidth +", 'H':" +document.body.clientHeight +"}";
	boffset = "'boffset': {'W': " +document.body.offsetWidth +", 'H':" +document.body.clientHeight +"}";
	bscroll = "'bscroll': {'W': " +document.body.scrollWidth +", 'H':" +document.body.scrollHeight +"}";
	return	"{" +bclient +"," +boffset +"," +bscroll +"," +client +"}";
	}
function	set_fmenu (fid) {
	$.ajax({data: 'main_fid=' +fid +'&' +$('form').serialize()});
	}
function	check_user(reg_user) {
	$.ajax({data: 'stat='+ reg_user +'&' +$('form').serialize()});
	alert ('reg_user');
	}

function	intkey(event) {		// фильтр на ввод - только цифры 0-9	onkeypress='return intkey (event);'
	var	chCode = ('charCode' in event) ? event.charCode : event.keyCode;
	return (chCode < 32 || chCode >= 48 && chCode <= 57);	/* '0' - '9' */
	}
function	mark_table (table, sdata) {
	$('#' +table +' tr')
	.click (function () { $('#' +table +' tr').removeClass('mark'); $(this).addClass('mark');
		$.ajax ({data: 'table=' +table +'&tmark=clickt&idrow=' +$(this).get(0).id +'&' +$('form').serialize() }) })
	.dblclick (function (event) {
		$('#' +table +' tr').removeClass('mark'); $(this).addClass('mark');
		$.ajax ({data: sdata +'&table=' +table +'&idrow=' +$(this).get(0).id +'&X=' +event.clientX +'&Y=' +event.clientY +'&' +$('form').serialize()}); });
}

var	s_send = '';
function	find_street (event) {	// Поиск улицы		onkeyup='return find_street (event);
//	alert ('find_street: ' + document.myForm.street.value);
	var	sget = document.myForm.street.value;
	if (sget.length > 2) {
		if (s_send == sget)	return;
		s_send = sget;
	/*	if (websocket != null)
			websocket.send ('shstat=find_street&' +$('form').serialize());
		else	$.ajax ({data: 'shstat=find_street&' +$('form').serialize()});
	*/	$.ajax ({data: 'shstat=find_street&' +$('form').serialize()});
	}
}  

