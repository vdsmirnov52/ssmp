/**	\file	js/new_call.js
 *	$Id$
 */
function	set_reasn (node, reasn) {	// переходы по дереву опроса
	if (node != '') {
		document.myForm.stack.value = document.myForm.stack.value +':' +node;
	} else	document.myForm.stack.value = '';
	if (reasn != '') {
		$.ajax({data: 'shstat=GET_CALL&reasn=' +reasn +'&' +$('form').serialize()});
	} else {
		$.ajax({data: 'shstat=GET_CALL&node=' +node +'&' +$('form').serialize()});
	}
}

function	change_reasn () {
//	alert (change_reasn);
	$.ajax({data: 'shstat=GET_CALL&change_reasn=on&' +$('form').serialize()});
	}

function	set_DS (ds) {
	document.myForm.stat.value='set_DS';
	$.ajax({data: 'shstat=GET_CALL&set_DS=' +ds +'&' +$('form').serialize()});
	}
/*
function	find_street (street) {
	document.myForm.stat.value='find_street';
	$.ajax({data: 'shstat=GET_CALL&find_street=' +street +'&' +$('form').serialize()});
	}
function	set_house (sid) {
	document.myForm.stat.value='set_house';
	$.ajax({data: 'shstat=GET_CALL&id_street=' +sid +'&' +$('form').serialize()});
	}
*/

function	set_subst (hnum, sector) {
	document.myForm.stat.value='set_subst';
	document.myForm.sector.value=sector;
	document.myForm.house.value=hnum;
	document.myForm.flat.focus();
	$.ajax({data: 'shstat=GET_CALL&' +$('form').serialize()});
	}

function	new_call_save() {	// Сохранить новый вызов
//	alert ('new_call_save');
	if (document.myForm.street.value == '') {
		alert ('Отсутствует Адрес!');
		document.myForm.street.focus();
		return;
	}
	if (document.myForm.kto.value == '') {
		alert ('Отсутствует Кто вызывает!');
		document.myForm.kto.focus();
		return;
	}
	if (document.myForm.pbrg && document.myForm.pbrg.value == '') {
		alert ('Отсутствует Профиль бригады!');
		document.myForm.pbrg.focus();
		return;
	}
	if (document.myForm.subst && document.myForm.subst.value == '') {
		alert ('Отсутствует Подстанция!');
		document.myForm.subst.focus();
		return;
	}
	if (document.myForm.reslt && (document.myForm.reslt.value == '')) {
		alert ('Отсутствует Результат!');
		document.myForm.reslt.focus();
		return;
	}
	if (document.myForm.diagn && (document.myForm.diagn.value == '')) {
		alert ('Отсутствует Диагноз!');
		document.myForm.diagn.focus();
		return;
	}
	document.myForm.stat.value='save';
	$.ajax({data: 'shstat=GET_CALL&' +$('form').serialize()});
	}

function	new_call_refuse () {	// Отказ 
	if (document.myForm.refuse.value == '') {
		alert ('Отсутствует Причина отказа!');
		document.myForm.refuse.focus();
		return;
	}
	document.myForm.stat.value='refuse';
	$.ajax({data: 'shstat=GET_CALL&' +$('form').serialize()});
	}
