var klController = {
    JSON_REQ_ID: "JSJ018",
    rcCreateList: function(params) {      
        Com.getRequestGet(rcController.JSON_REQ_ID, params)
            .done(function(result) {
            klView.bcDrawJSONData(result.jsj018JSONData,params);
            });
    }
};
$(document).ready(function(){
$(document).on("click","#raceresult #bcbtnAllCheck",function(){
var maxsize = $("input[id ^= 'chk']").length;
var chksize = 0;
for (var i = 0; i < maxsize; i++){
if($($("input[id ^= 'chk']")[i]).prop("checked")){
chksize = chksize + 1;
}
}
if(maxsize == chksize){
$("input[id ^= 'chk']").prop("checked",false)
} else {
$("input[id ^= 'chk']").prop("checked",true)
}
});
$(document).on("click","#raceresult .input_bkColor",function(){
chkobj = $(this).children();
if(chkobj.prop("checked")){
chkobj.prop("checked",false);
} else {
chkobj.prop("checked",true);
}
});
$(document).on("click","#raceresult .input_bkColor input",function(e){
e.stopPropagation();
});
$(document).on("click","#raceresult .clc",function(){
var myid = this.id;
piInitialize($("#"+ myid + "Prm").val());
});
$(document).on("click","#raceresult .resultbtn",function(){
var myid = this.id;
var clcbtn = myid.split("bcbtnResult")
var Url = $("#hdnRaceRVURL").val();
var RVPrm = $("#btnracuRVPrm"+ clcbtn[1]).val();
    var prm = {};
    prm = {"encp" : RVPrm,"disp" : "PJ0326"};
commonSubmit.formPost(Url,prm)
});
$(document).on("click","#raceresult .digestbtn",function(){
var myid = this.id;
var Url = $("#hdnRacedigestURL").val();
var clcbtn = myid.split("btndigest")
var clcbtn = clcbtn[1].split("R")
var Url = $("#hdnRacedigestURL").val();
var digestParams = new Array();
var prm = {};
prm.bkcd = $("#hdnklBkcd").val();
prm.kday = $("#hdnklKday").val();
prm.rnum = clcbtn[0];
digestParams.push(prm);
commonSubmit.formPost(Url, { "disp" : "PJ0306", 'prmsDigestList' : JSON.stringify(digestParams) }, "_self");
});
$(document).on("click","#raceresult .rendigestbtn",function(){
var maxsize = $("input[id ^= 'chk']").length;
var Url = $("#hdnRacedigestURL").val();
var clcbtn = {};
var count = 0;
if($("input[id ^= 'chk']:checked").length == 0){
$("#alert_dialog_lock").dialog( 'open' );
return false;
}
var digestParams = new Array();
for (var i = 0; i < maxsize; i++){
if($($("input[id ^= 'chk']")[i]).prop("checked")){
myid = $($("input[id ^= 'chk']")[i])[0].id;
clcbtn = myid.split("chk");
clcbtn = clcbtn[1].split("R");
var prm = {};
prm.bkcd = $("#hdnklBkcd").val();
prm.kday = $("#hdnklKday").val();
prm.rnum = clcbtn[0];
digestParams.push(prm);
}
} 
commonSubmit.formPost(Url,{ "disp" : "PJ0306", 'prmsDigestList' : JSON.stringify(digestParams) }, "_self");
});
});
