function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}
function	mssg (text) {	$("#log").prepend(text + "<br/>");      }

$(document).ready(function () {
	$.ajaxSetup({ url: "/cgi-bin/03.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#panele').css({'height': -44 + document.documentElement.clientHeight +'px'});	//, 'background-color': '#ffe'});
	$('#mybody').css({'height': -150 + document.documentElement.clientHeight +'px', 'width': -204 +document.documentElement.clientWidth +'px'});	//, 'background-color': '#ffe'});
	$('#log').css({'top': -108 + document.documentElement.clientHeight +'px', 'width': -204 +document.documentElement.clientWidth +'px', 'background-color': '#ffe'});
	set_shadow ('USR_IDNT');
//	map_init({'height': '800px', 'width': '800px', 'top': '60px', 'left': '60px'}, [56.32354, 43.99121]);	// null);
//	map_init({'height': '800px', 'width': '800px', 'top': '100px'}, null);
//	map_init(null, null);
});

var mymap = null;

function map_init(css, center) {
	if (mymap) {
		mymap.remove();
		mymap = null;
		$('#map').css({'left': '2200px'});
//		$('#map').css({'z-index': 0});
		return;
	}
	if (css)	$('#map').css(css);
	else		$('#map').css({'height': -60 + document.documentElement.clientHeight +'px', 'width': '100%'});
//	$('#map').css({'z-index': 1111});
//	start_wsmap ();

	if (center)	mymap = L.map('map').setView(center, 14);
	else		mymap = L.map('map').setView([56.309364, 44.007793], 14);

var	osmLayer = new L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', { maxZoom: 18, }).addTo(mymap);

var	yndx = new L.Yandex();
var	ytraffic = new L.Yandex("null", {traffic:true, opacity:0.8, overlay:true});
var	baseMaps = { "OpenStreetMap": osmLayer, 'L.Yandex': yndx };
/**
var	marker = L.marker([56.32354, 43.99121]).addTo(mymap).bindPopup('Позиция маркера.').openPopup();
var	overlays = { "Marker": marker};
**/
var	overlays = {};

var	layersControl = new L.Control.Layers(baseMaps, overlays),
	popup = new L.Popup();

mymap.addControl(layersControl);
/*

mymap.on('click', (e) => {
    popup.setLatLng(e.latlng);
    popup.setContent('Point ' +
      ' (' + e.latlng.lat.toFixed(6) +
      ', ' + e.latlng.lng.toFixed(6) + ')');
    mymap.openPopup(popup);
  })
*/
if (window.location.search) {	set_shadow('GET&get_'+ window.location.search.replace('?', ''))	}
};
