var comOzz = {
ozzClick : function(flg, id, ozz) {
var kumiban = id.substr(6);
if (flg == "1") {
comKaime.kimDelKaime(kumiban);
} else {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var DN_ozz;
var TP_ozz;
if (kakesikiKbn == "5") {
var ozzArrays = ozz.split("<br>～<br>");
DN_ozz = ozzArrays[0];
TP_ozz = ozzArrays[1];
} else {
DN_ozz = ozz;
TP_ozz = null;
}
comKaime.kimAddKaime(kakesikiKbn, kumiban, DN_ozz, TP_ozz);
}
PT0202Controller.cPT0202BtnChg(jst015Maindata.data.dispKbn);
return;
},
ozzSeigyo : function() {
var out = document.getElementsByName("lblOzzName");
for (var l = 0; l < out.length; l++) {
var wkId = out[l].attributes['id'].value;
$('#' + wkId).addClass("disabled");
}
return;
},
ozzSeigyoClear : function() {
var out = document.getElementsByName("lblOzzName");
for (var l = 0; l < out.length; l++) {
var wkId = out[l].attributes['id'].value;
var btnId = "btn" + wkId;
if ($('#' + btnId).html() != "-----") {
$('#' + wkId).removeClass("disabled");
}
}
return;
},
ozzSelectClear : function() {
var out = document.getElementsByName("btnOzzName");
for (var l = 0; l < out.length; l++) {
var wkId = out[l].attributes['id'].value;
if ($('#' + wkId).hasClass("active")) {
$('#' + wkId).removeClass("active");
}
}
return;
},
ozzSelResultClear : function() {
osView.displayArea(0);
SEARCH_NINKI_LIST　= null;
SEARCH_HYOJUN_LIST　= null;
return ;
}
};