var rcModeLiveVote = -1;
function rcChgActiveBtn(selectKbn) {
for(var i=1 ; i<=9; i++){
$("#rcbtn" + i).removeClass('active');
}
if($("#rcbtn" + selectKbn).prop("disabled")){
$("#rcbtn1").addClass('active');
}else{
$("#rcbtn" + selectKbn).addClass('active');
}
}
function rcChgDisableBtn(disabledKbn, selectKbn) {
if(disabledKbn == 0){
$("#rcbtn" + selectKbn).prop("disabled", true);
}else if(disabledKbn == 1){
$("#rcbtn" + selectKbn).prop("disabled", false);
}
}
function rcChgAllUnselectBtn() {
for(var i=1 ; i<=9; i++){
$("#rcbtn" + i).removeClass('active');
}
}
function rcClickStreamLink() {
commonLink.NewWindow("", 1);
commonSubmit.formGet(
$('#rcUrlStream').val()
, {"kday": gKaisaihi,"bkcd": gBKeirinCd,"rnum": gRaceNo}
, "subwin"
);
}
function rcClickPrintBtn() {
commonSubmit.formPost(
$('#rcUrlRacePrint').val()
, {"kday": gKaisaihi}
, "_blank"
);
}
function rcClickDigestBtn() {
commonLoad.loadingImage("true");
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rcMoveDigest();
return;
}, function(){
commonLoad.loadingImage("false");
});
} else {
comKaime.kimClear();
rcMoveDigest();
return;
}
}
function rcMoveDigest() {
var digestParams = [];
var prm = {};
prm.bkcd = gBKeirinCd;
prm.kday = gKaisaihi;
prm.rnum = gRaceNo;
digestParams.push(prm);
commonSubmit.formPost(
$('#rcUrlDigest').val()
, { "disp" : displayingId, "fdisp" : parentFuncId, 'prmsDigestList' : JSON.stringify(digestParams) }
, "_self"
);
}
function rcDispRacePrintBtn(showKbn) {
if(showKbn == 0){
$("#rcbtnRacePrint").addClass('dispoff');
} else if(showKbn == 1){
$("#rcbtnRacePrint").removeClass('dispoff');
}
}
function rcChgModeBtn(para) {
commonLoad.loadingImage("true");
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rcMoveLiveVoteMode(para);
return;
}, function(){
commonLoad.loadingImage("false");
});
} else {
comKaime.kimClear();
rcMoveLiveVoteMode(para);
return;
}
}
function rcMoveLiveVoteMode(para) {
var wkUrl;
if(rcModeLiveVote == 0){
wkUrl = $('#rcUrlVoteMode').val();
} else if(rcModeLiveVote == 1){
wkUrl = $('#rcUrlLiveMode').val();
}
commonSubmit.formPost(
wkUrl
, para
, "_self"
);
}
function rcClickDispHelp() {
var workUrl = rcGetHelpUrl(displayingId);
if(workUrl != ""){
window.open().location.href = workUrl;
}
}
function rcGetHelpUrl(dispID){
var retUrl = "";
var raceUrl = $('#rcUrlRaceHelp').val();
switch (dispID) {
case 'PJ0307':
if(raceUrl != ""){
retUrl = raceUrl + "#zen_race";
}
break;
case 'PJ0315':
if(raceUrl != ""){
retUrl = raceUrl + "#race_kihon";
}
break;
case 'PJ0316':
if(raceUrl != ""){
retUrl = raceUrl + "#race_tyokkin";
}
break;
case 'PJ0317':
if(raceUrl != ""){
retUrl = raceUrl + "#race_taisen";
}
break;
case 'PJ0318':
if(raceUrl != ""){
retUrl = raceUrl + "#race_syumoku";
}
break;
case 'PJ0319':
if(raceUrl != ""){
retUrl = raceUrl + "#race_tojyo";
}
break;
case 'PJ0320':
if(raceUrl != ""){
retUrl = raceUrl + "#race_comment";
}
break;
case 'PJ0326':
retUrl = $('#rcUrlResultHelp').val();
break;
case 'PJ0328':
retUrl = $('#rcUrlKaimeHelp').val();
break;
case 'PT0511':
case 'PT0512':
case 'PT0513':
case 'PT0514':
case 'PT0515':
case 'PT0516':
case 'PT0517':
case 'PT0531':
case 'PT0532':
case 'PT0502':
if(rcModeLiveVote == 1){
retUrl = $('#rcUrlOddsVoteHelp').val();
}else{
retUrl = $('#rcUrlOddsHelp').val();
}
break;
default:
retUrl = raceUrl;
break;
}
return retUrl;
}
function rcModeTypeSetting(){
var live = $('#rcUrlLiveMode').val();
var vote = $('#rcUrlVoteMode').val();
switch( location.pathname ) {
case live:
$("#rcbtnLive").addClass('active');
$("#rcbtnVote").removeClass('active');
$("#rclblVideoWindow").addClass('dispoff');
$("#rcbtn6").text("オッズ");
rcModeLiveVote = 0;
break;
case vote:
$("#rcbtnVote").addClass('active');
$("#rcbtnLive").removeClass('active');
$("#rclblVideoWindow").removeClass('dispoff');
$("#rcbtn6").text("オッズ投票");
rcModeLiveVote = 1;
break;
default:
$("#rcbtnLive").removeClass('active');
$("#rcbtnVote").removeClass('active');
$("#rclblVideoWindow").removeClass('dispoff');
$("#rcbtn6").text("オッズ");
rcModeLiveVote = -1;
break;
}
}
$(document).on('click', "button[id='rcbtnLive']", function() {
if(rcModeLiveVote == 1){
btnCngMode();
}
else{
}
});
$(document).on('click', "button[id='rcbtnVote']", function() {
if(rcModeLiveVote == 0){
btnCngMode();
}
else{
}
});
function rfdoplayer(raceno){
commonLink.NewWindow("","1");
commonSubmit.formGet(
$("#rfstreamURL").val()
, {"kday": gKaisaihi,"bkcd": gBKeirinCd,"rnum": raceno,"eizo_kbn": "02"}
, "subwin"
);
}
function rfdointerview(raceno){
commonLink.NewWindow("","1");
commonSubmit.formGet(
$("#rfstreamURL").val()
, {"kday": gKaisaihi,"bkcd": gBKeirinCd,"rnum": raceno,"eizo_kbn": "03"}
, "subwin"
);
}
function rfdoKaimebtn(raceno){
$("#kaime_link_" + raceno).removeClass("dispon").addClass("dispoff");
$("#kaime_table_" + raceno).removeClass("dispoff").addClass("dispon");
}
function rfdoSanrentan(raceno,flg){
if(flg){
    paInitialize(hhGetEncSelRList(raceno));
} else {
    paInitialize(hhGetEncSelR());
}
}
var rfController = {
    JSON_REQ_ID: "JSJ005",
    rfCreateList: function( params) {
        Com.getRequestGet(rfController.JSON_REQ_ID, params)
            .done(function(result) {
                rfView.rfDrawJSONData(result, params);
            });
    }
};
var rfView = {
HDNKEY_ID: 'ppj0314',
rfDrawJSONData: function(jsondata, params) {
var outHtml=[];
if(!jsondata) {
$('#rfPaintArea').addClass('dispoff');
$('#rfErrorArea').removeClass('dispoff');
Com.makePcUpdatePage(
"rfErrorArea"
, ""
, params
, function(arg0){
rfController.rfCreateList(arg0);
}
);
}
else if (jsondata.resultCd == -1){
$('#rfPaintArea').addClass('dispoff');
$('#rfErrorArea').removeClass('dispoff');
var msg = "";
if(jsondata.message != undefined){
msg = jsondata.message;
}
Com.makePcUpdatePage(
"rfErrorArea"
, msg
, params
, function(arg0){
rfController.rfCreateList(arg0);
}
);
}
else{
    $('#rfPaintArea').empty();
$('#rfErrorArea').addClass('dispoff');
$('#rfPaintArea').removeClass('dispoff');
outHtml = rfEdit(jsondata, "1");
$('#rfPaintArea').html(outHtml.join("").replace(/,/g,"").replace(/__COMMA__/g,","));
return;
}
}
};
function rfEdit(jsondata, raceno,flg){
var outHtml=[];
if(jsondata["narabiyoso"]["chushiFlg"] == "0"){
return outHtml;
}
else{
outHtml.push('<div class="dispon">'); 
if(jsondata["narabiyoso"]["chushiFlg"] == "1"){
outHtml.push(rfEditBiko(jsondata));
}
else{
outHtml.push('<div class="clear-fix" style="margin-top: 9px;">');
if(jsondata["narabiyoso"]["ryoikiFlg"] == "false" && jsondata["sanrentan"]["ryoikiFlg"] == "false" && jsondata["kaime"]["ryoikiFlg"] == "false") {
}
else{
outHtml.push('<div>');
outHtml.push('<table class="fl-l" style="width: 34%; height:105px;">');
outHtml.push('<tbody>');
if(jsondata["narabiyoso"]["ryoikiFlg"] == "true"){
outHtml.push(rfEditNarabi(jsondata));
}else{
outHtml.push('<tr></tr><tr></tr><tr></tr>'); 
}
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</div>');
outHtml.push('<div>');
outHtml.push('<table class="fl-l" style="width: 31%; margin-left: 1%; height:105px">');
outHtml.push('<tbody>');
if(jsondata["sanrentan"]["ryoikiFlg"] == "true"){
outHtml.push(rfEditSanrentan(jsondata, raceno,flg));
}else{
outHtml.push('<tr></tr><tr></tr><tr></tr>'); 
}
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</div>');
outHtml.push('<div>');
outHtml.push('<table class="fl-r"  style="width: 33%; margin-left: 1%; height:105px;">');
outHtml.push('<tbody>');
if(jsondata["kaime"]["ryoikiFlg"] == "true"){
outHtml.push(rfEditKaime(jsondata, raceno));
}else{
outHtml.push('<tr></tr><tr></tr><tr></tr>'); 
}
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</div>');
}
outHtml.push('</div>'); 
if(jsondata["narabiyoso"]["ryoikiFlg"] == "true" && jsondata["narabiyoso"]["errFlg"] != "true"){
outHtml.push('<div id="brlblNarabiTyui" class="w100pc" style="margin-top: 9px;">');
outHtml.push('<table class="w100pc"><tbody><tr>');
outHtml.push('<td class="al-l">※この並びはあくまで予想の為、実際の並びとは異なることがあります。</td>');
outHtml.push('</tr></tbody></table></div>');
}else{
outHtml.push('<div id="brlblNarabiTyui" class="w100pc" style="margin-top: 9px;"></div>');
}
outHtml.push(rfEditBiko(jsondata, raceno));
}
outHtml.push('</div>'); 
outHtml.push('<input type="hidden" id="rfstreamURL" name="rfstreamURL" value = "' + jsondata["streamURL"] +'" >');
return outHtml;
}
}
function rfEditBiko(jsondata, raceno){
var outHtml=[];
var s_raceno = jsondata["raceNo"];
outHtml.push('<div class="clear-fix dispon printing" style="margin-top: 10px;">');
if(jsondata["sensyuShokaiFlg"] == "2"){
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%;" type="button" onclick="rfdoplayer(\'' + s_raceno + '\');"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">選手紹介</button>');
}
else if(jsondata["sensyuShokaiFlg"] == "1"){
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%;" disabled = "disabled" type="button"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">選手紹介</button>');
}
else{
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%; display:none; " type="button"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">選手紹介</button>');
}
if(jsondata["interViewFlg"] == "2"){
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%; margin-left: 1%;" type="button" onclick="rfdointerview(\'' + s_raceno + '\');"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">インタビュー</button>');
}
else if(jsondata["interViewFlg"] == "1"){
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%; margin-left: 1%;" disabled = "disabled" type="button"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">インタビュー</button>');
}
else{
outHtml.push('<button class="btn onbtn fl-l" style="width: 14%; margin-left: 1%; display:none;" type="button"><img height="16" style="margin-right: 6px;" alt="film" src="' + currentPath + '/static/img/icon/ico_film.png">インタビュー</button>');
}
if(jsondata["biko"]["hyojiFlg"] == "true"){
outHtml.push('<table class="fl-r printing_tbl" style="width: 70%; margin-left: 1%; word-wrap: break-word; table-layout:fixed">');
outHtml.push('<tbody>');
outHtml.push('<tr>');
outHtml.push('<td class="caution">' + jsondata["biko"]["text"].replace(/,/g,"__COMMA__") + '</td>');
outHtml.push('</tr>');
outHtml.push('</tbody>');
outHtml.push('</table>');
}
outHtml.push('</div>');
return outHtml;
}
function rfEditNarabi(jsondata){
var outHtml=[];
outHtml.push('<tr class="b-a tbl_header2" data-toggle="modal" data-target="#narabi_hannrei" style="height:30px">');
outHtml.push('<td class="al-l" style="width: 30%;padding-left:4px">並び予想</td>');
if(jsondata["narabiyoso"]["errFlg"] != "true"){
outHtml.push('<td class="al-c" style="width: 1%;"></td>');
outHtml.push('<td class="al-c" style="width: 30%;"><p class="' + jsondata["narabiyoso"]["lineKeitaiClass"] + '">' + jsondata["narabiyoso"]["lineKeitai"] + '</p></td>');
outHtml.push('<td class="al-c" style="width: 1%;"></td>');
if(jsondata["narabiyoso"]["kyoHyoji"] == "true"){
outHtml.push('<td class="al-c" style="width: 5%;"><p class="' + jsondata["narabiyoso"]["kyoClass"] + '">競</p></td>');
}
else{
outHtml.push('<td class="al-c" style="width: 5%;"> </td>');
}
outHtml.push('<td style="width:auto">&nbsp;</td>');
outHtml.push('</tr>');
outHtml.push('<tr class="b-a" style="background-color:#FFFFFF">');
outHtml.push('<td colspan="6">');
outHtml.push('<table>');
for(var alop = 0; alop < jsondata["narabiyoso"]["maxAxixY"]; alop++ ){
var wlist1 = rfNarabiSort(jsondata, alop);
var dataari = 0;
for(var ilop = 0; ilop < 14; ilop++ ){
if(wlist1[ilop]["shaban"]!=""){
dataari = 1;
break;
}
}
outHtml.push('<tr>');
if(dataari == 1){
if(alop == 0){
outHtml.push('<td><img class="yajirusi_left" src="' + currentPath + '/static/img/member_left_short.png"></td>');
}
else{
outHtml.push('<td>&nbsp;</td>');
}
for(var ilop = 0; ilop < 14; ilop++ ){
outHtml.push('<td><div class="snum ' + wlist1[ilop]["classname"] + '">' + wlist1[ilop]["shaban"] + '</div></td>');
}
}else{
for(var ilop = 0; ilop < 15; ilop++ ){
outHtml.push('<td>&nbsp;</td>');
}
}
outHtml.push('</tr>');
}
outHtml.push('</table>');
outHtml.push('</td>');
outHtml.push('</tr>');
outHtml.push('<tr>');
outHtml.push('<td colspan="6" class="al-r" style="height:25px;width:100%">');
outHtml.push('<table style="width:100%">');
outHtml.push('<tr>');
outHtml.push('<td class="al-r">情報提供：' + jsondata["narabiyoso"]["teikyo"] + '</td>');
outHtml.push('</tr>');
outHtml.push('</table>');
outHtml.push('</td>');
outHtml.push('</tr>');
}
else{
outHtml.push('</tr>');
outHtml.push('<tr class="b-a" style="background-color:#FFFFFF">');
outHtml.push('<td style="text-align:left;padding: 0 10px;">' + jsondata["narabiyoso"]["errMsg"] + '</td>');
outHtml.push('</tr>');
}
return outHtml;
}
function rfNarabiSort(jsondata, index){
var ichi = null;
var flg = 0;
var wlist = [];
for(var ilop = 0; ilop < 14; ilop++ ){
var obj = [];
ichi = index*14 + ilop + 1;
flg = 0;
for(var jlop = 0; jlop < jsondata["narabiyoso"]["shaban"].length; jlop++ ){
if(jsondata["narabiyoso"]["shaban"][jlop]["ichi"] == ichi.toString()){
obj["shaban"] = jsondata["narabiyoso"]["shaban"][jlop]["shaban"];
obj["classname"] = jsondata["narabiyoso"]["shaban"][jlop]["classname"];
wlist.push(obj);
flg = 1;
break;
}
}
if(flg == 0){
obj["shaban"] = "";
obj["classname"] = "base_color_0";
wlist.push(obj);
}
}
return wlist;
}
function rfEditSanrentan(jsondata, raceno,flg){
var outHtml=[];
outHtml.push('<tr class="b-a tbl_header2" style="height:30px">');
outHtml.push('<td class="al-l b-a" style="padding-left:4px">3連単支持率</td>');
outHtml.push('</tr>');
outHtml.push('<tr class="b-a" style="background-color:#FFFFFF">');
if( jsondata["sanrentan"]["shiji"].length >0){
    if(flg){
    outHtml.push('<td class="clc" style="padding-top: 5px; padding-bottom: 5px;" onclick="rfdoSanrentan(' + raceno + '&#44' + flg + ');">');
} else {
    outHtml.push('<td class="clc" style="padding-top: 5px; padding-bottom: 5px;" onclick="rfdoSanrentan(' + raceno + ');">');
}
outHtml.push('<table class="al-c" width=100%>');
outHtml.push('<tbody>');
outHtml.push('<tr>')
outHtml.push('<td class="al-l b-a base_color_10 nob" style="width:18%;height:30px">全体</td>');
outHtml.push('<td>');
outHtml.push('<table width=100%>');
outHtml.push('<tbody>');
outHtml.push('<tr>')
for(var ilop = 0; ilop < jsondata["sanrentan"]["shiji"].length; ilop++ ){
outHtml.push('<td class="al-c b-a ' + jsondata["sanrentan"]["shiji"][ilop]["classname"] + '" style="width: ' + jsondata["sanrentan"]["shiji"][ilop]["ritsu"] + '%;height:30px">' + jsondata["sanrentan"]["shiji"][ilop]["shaban"] + '</td>');
}
outHtml.push('</tr>');
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</td>');
outHtml.push('</tr>');
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</td>');
}
else{
outHtml.push('<td></td>')
}
outHtml.push('</tr>');
outHtml.push('<tr>');
outHtml.push('<td class="al-r" style="height:25px">&nbsp;</td>');
outHtml.push('</tr>');
return outHtml;
}
function rfEditKaime(jsondata, raceno){
var outHtml=[];
outHtml.push('<tr class="b-a tbl_header2" style="height:30px">');
outHtml.push('<td class="al-l" style="width: 50%;padding-left:4px;height:19px">買い目予想</td>');
outHtml.push('</tr>');
if(jsondata["kaime"]["errFlg"] != "true"){
outHtml.push('<tr class="b-a" style="background-color:#FFFFFF">');
outHtml.push('<td class="al-c">');
outHtml.push('<div class="dispon kaime_link" id="kaime_link_' + raceno + '"><button class="btn onbtn" style="width: 150px;" type="button" onclick="rfdoKaimebtn(' + raceno + ');">買い目を表示する</button></div>');
outHtml.push('<div class="dispoff kaime_table" id="kaime_table_' + raceno + '"><table width="100%" style="text-align:left;">');
outHtml.push('<tbody>');
var maxmoji=0;
for(var ilop = 0; ilop < jsondata["kaime"]["yoso"].length; ilop++ ){
if(jsondata["kaime"]["yoso"][ilop].length > maxmoji){
maxmoji = jsondata["kaime"]["yoso"][ilop].length;
}
}
if(maxmoji >= 12){
for(var ilop = 0; ilop < jsondata["kaime"]["yoso"].length; ilop++ ){
outHtml.push('<tr>');
outHtml.push('<td style="width:100%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop] + '</td>');
outHtml.push('</tr>');
}
}
else if(maxmoji >= 6 && maxmoji <= 11){
for(var ilop = 0; ilop < 8; ilop=ilop+2){
outHtml.push('<tr>');
outHtml.push('<td style="width:50%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop] + '</td>');
outHtml.push('<td style="width:50%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop+1] + '</td>');
outHtml.push('</tr>');
}
}
else{
for(var ilop = 0; ilop < 8; ilop=ilop+4){
outHtml.push('<tr>');
outHtml.push('<td style="width:25%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop] + '</td>');
outHtml.push('<td style="width:25%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop+1] + '</td>');
outHtml.push('<td style="width:25%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop+2] + '</td>');
outHtml.push('<td style="width:25%; padding-left:4px;">' + jsondata["kaime"]["yoso"][ilop+3] + '</td>');
outHtml.push('</tr>');
}
}
outHtml.push('</tbody>');
outHtml.push('</table>');
outHtml.push('</div>');
outHtml.push('</td>');
outHtml.push('</tr>');
outHtml.push('<tr>');
outHtml.push('<td class="al-r" style="height:25px;">');
outHtml.push('<table style="width:100%">');
outHtml.push('<tr>');
outHtml.push('<td class="al-r">情報提供：' + jsondata["kaime"]["teikyo"] + '</td>');
outHtml.push('</tr>');
outHtml.push('</table>');
outHtml.push('</td>');
outHtml.push('</tr>');
}
else{
outHtml.push('<tr class="b-a" style="background-color:#FFFFFF">');
outHtml.push('<td style="text-align:left;padding: 0 10px;">' + jsondata["kaime"]["errMsg"] + '</td>');
outHtml.push('</tr>');
}
return outHtml;
}
