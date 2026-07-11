function slGetParam(childDispID, raceno){
var racePrm = hhGetEncSelRList(raceno);
if(childDispID == null){
return { "encp" : racePrm };
}else{
return { "disp" : childDispID, "encp" : racePrm }; 
}
}
function slDigestClick(raceno){
var digestParams = new Array();
var prm = {};
prm.bkcd = slView.slKeirinCd;
prm.kday = slView.slKaisaihi;
prm.rnum = raceno;
digestParams.push(prm);
commonSubmit.formPost($('#slDigestURL').val(), { "disp" : "PJ0305", 'prmsDigestList' : JSON.stringify(digestParams) }, "_self");
}
function slLiveVoteClick(raceno){
commonSubmit.formPost($('#slRaceBasicInfoURL').val(), slGetParam("PJ0315", raceno), "_self");
}
function slOzzClick(raceno){
commonSubmit.formPost($('#slRaceBasicInfoURL').val(), slGetParam("PT0511", raceno), "_self");
}
function slResultClick(raceno){
commonSubmit.formPost($('#slRaceBasicInfoURL').val(), slGetParam("PJ0326", raceno), "_self");
}
function slSensyuClick(sensyuno){
commonSubmit.formGet($('#slProfileURL').val(), { "snum" : sensyuno }, "_self");
}
function slPrintClick(){
commonSubmit.formPost($('#slSyusoPrintURL').val(), { "disp" : "PJ0333", "kday" : slView.slKaisaihi }, "_blank");
}
function slDigestContinuationClick(){
if($('[name=slchkContinuationReplay]:checked').size() == 0){
$('#alert_dialog_lock').dialog( 'open' );
return false;
}else{
var digestParams = new Array();
$('[name=slchkContinuationReplay]:checked').each(function(idx, elm){
var prm = {};
prm.bkcd = slView.slKeirinCd;
prm.kday = slView.slKaisaihi;
prm.rnum = $(elm).val();
digestParams.push(prm);
});
commonSubmit.formPost($('#slDigestURL').val(), { "disp" : "PJ0305", 'prmsDigestList' : JSON.stringify(digestParams) }, "_self");
}
}
function slContinuationReplayClick(element){
var id = '#' + element.id; 
var chkSel = id + '> :checkbox'; 
if($(id).hasClass("active")){
$(id).removeClass("active");
$(chkSel).prop('checked', false);
$(chkSel).removeClass("active");
}else{
$(id).addClass("active");
$(chkSel).prop('checked', true);
$(chkSel).addClass("active");
}
}
