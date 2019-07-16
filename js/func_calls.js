/**	\file	js/func_calls.js
 */

function	set_brig (br_num, br_id, prof) {
//	alert ('set_brig: ' +br_num +' br_id: ' +br_id +' prof:' +prof);
	document.myForm.set_bnumber.value = br_num;
	document.myForm.set_br_ref.value = br_id;
	$('#brg_label').html('<i class="fa fa-medkit fa-lg" aria-hidden="true"></i>&nbsp;' +br_num +prof);
}

function	update_call (cnum_ttl, opts) {
	if (! document.myForm.set_bnumber.value) {
		alert ("Выберите Бригау!");
		return;
	}
//	alert (update_call);
	set_shadow("open_call&cnum_ttl=" +cnum_ttl +'&exec=UPDATE&' +opts);
}

function	open_call (cnum_ttl) {
//	alert ("open_call cnum_ttl: " + cnum_ttl);
	set_shadow("open_call&cnum_ttl=" +cnum_ttl );
}

function	set_t_arrl (cnum_ttl, old_shstat) {
	if (confirm('Бригада действительно Прибыла на место? \n\t')) {
		set_shadow("set_ttime&ttime=t_arrl&cnum_ttl=" +cnum_ttl +'&old_shstat=' +old_shstat);
	}// else alert (set_t_arrl);
}

function	set_t_done(cnum_ttl, old_shstat) {
	if (confirm('Бригада действительно Исполнила вызов? \n\t')) {
		set_shadow("set_ttime&ttime=t_done&cnum_ttl=" +cnum_ttl +'&old_shstat=' +old_shstat);
	}// else alert (set_t_done);
}

function	calls_alert (label, cnum_ttl, cstt) {	// call_refuse |
	set_shadow ('calls_alert&label=' +label +'&cnum_ttl=' +cnum_ttl +'&cstt=' +cstt)
}
/*
function	call_refuse (cnum_ttl, cstt) {
	if (! document.myForm.sel_refuse.value) {
	 	alert ("Укажите причину Отказа.");
		document.myForm.sel_refuse.focus();
	} else {
	//	alert ('document.myForm.sel_refuse: ' + $('#sel_refuse:selected').text());	//document.myForm.sel_refuse.text);
		set_shadow ('call_refuse&cnum_ttl=' +cnum_ttl +'&cstt=' +cstt);
	}
}

function	call_pcancel (cnum_ttl, cstt) {
	if (! document.myForm.sel_pcancel.value) {
	 	alert ("Укажите причину Отмены назначения.");
		document.myForm.sel_pcancel.focus();
	} else {
	//	set_shadow ('call_pcancel&cnum_ttl=' +cnum_ttl +'&cstt=' +cstt);
		set_shadow("open_call&cnum_ttl=" +cnum_ttl +'&exec=UPDATE&' +'opts=pcancel');
	}
}

function	call_pdelay (cnum_ttl, cstt) {
	if (! document.myForm.sel_pdelay.value) {
	 	alert ("Укажите причину Задержки.");
		document.myForm.sel_pdelay.focus();
	} else {
	//	set_shadow ('call_pdelay&cnum_ttl=' +cnum_ttl +'&cstt=' +cstt);
		set_shadow("open_call&cnum_ttl=" +cnum_ttl +'&exec=UPDATE&' +'opts=pdelay');
	}
}
*/
function	call_done (cnum_ttl, sfrom) {
	if (! document.myForm.reslt.value)      {
		alert ("Укажите Резултат."); }
	else if (! document.myForm.diagn.value) {
		alert ("Укажите DS (диагноз)."); }
	else set_shadow('open_call&exec=CLOSE&cnum_ttl=' +cnum_ttl +'&sfrom=' +sfrom);
}
