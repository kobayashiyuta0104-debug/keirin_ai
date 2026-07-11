var gDisplayMaster = ["PC0101","PC0201","PJ0307","PJ0311","PJ0312"
                      ,"PJ0313","PJ0314","PJ0315","PJ0316","PJ0317"
                      ,"PJ0318","PJ0319","PJ0320","PJ0326","PJ0328"
                      ,"PT0511","PT0512","PT0513","PT0514","PT0515"
                      ,"PT0516","PT0517","PT0531","PT0532","PT0502"];
var gSubHelpMaster = ["PY0101","PY0102","PY0103","PY0104","PY0105","PY0106"];
var gDispOnList = [];                
var gUpdateList = [];                
var gPrmParaK;                       
var gPrmParaR;                       
var gRaceNo;                         
var gBKeirinCd;                      
var gKaisaihi;                       
var gKaisaiParaList = [];            
var gRaceNoParaList = [];            
var gResultRefundList = [];          
var gOddsExistList = [];             
var gRaceStopFlag;                   
var gTaisenInfoExistFlag;            
var gSyumokuTypeResultInfoExistFlag; 
var gDigestInfoExistFlag;            
var gRequestDispId;                  
var gRequestPara;                    
var gReqPrmsObject = [];             
$(document).ready(function(){
switchDisplay();
getDispCtrlInfo();
dateReflection();
$('#sfHdnLink_0').val($('#raceLiveHelp').val());
});
function switchDisplay(){
var dispOnList = ["PC0101","PC0201","PJ0311","PJ0312","PJ0313"];
if(getBtnNo(displayingId) == 6){
displayingId="PT0511";
}
dispOnList.push(displayingId);
var key = "";
for(key in gDisplayMaster){
if(dispOnList.indexOf(gDisplayMaster[key]) >= 0){
$("#" + gDisplayMaster[key]).removeClass('dispoff');
} else {
$("#" + gDisplayMaster[key]).addClass('dispoff');
}
}
if(displayingId == "PJ0307"){
$("#PJ0313").addClass('dispoff');
}
if(displayingId == "PJ0307" || displayingId == "PJ0326"){
$("#PJ0314").addClass('dispoff');
}else{
$("#PJ0314").removeClass('dispoff');
dispOnList.push("PJ0314");
}
if(displayingId == "PJ0307"){
hhChgPattern(1);
}else{
hhChgPattern(2);
}
gDispOnList = [];
gDispOnList = dispOnList;
}
function getDispCtrlInfo() {
if(Object.keys(jsonData["PC0201"]).length == 0){
return;
}
gPrmParaK = "";
gPrmParaR = "";
gKaisaiParaList = [];
gRaceNoParaList = [];
gResultRefundList = [];
gOddsExistList = [];
gRaceStopFlag = false;
gTaisenInfoExistFlag = false;
gSyumokuTypeResultInfoExistFlag = false;
gDigestInfoExistFlag = false;
var wk0201Data = [];
wk0201Data = jsonData["PC0201"].C0201data;
var wkInfo = [];
var wkCnt = 0;
gPrmParaK = wk0201Data.encSelParaK;
gPrmParaR = wk0201Data.encSelParaR;
gRaceNo = wk0201Data.selRaceNo;
gBKeirinCd = wk0201Data.selKjyoCd;
gKaisaihi = wk0201Data.selKaisai;
gKaisaiParaList = [];
gKaisaiParaList[0] = "dammy"
for(wkCnt=1; wkCnt <= wk0201Data.C0201kaisai.length; wkCnt++){
wkInfo = wk0201Data.C0201kaisai[wkCnt - 1];
gKaisaiParaList[wkCnt] = wkInfo.encParaK;
}
gRaceNoParaList = [];
gRaceNoParaList[0] = "dammy"
for(wkCnt=1; wkCnt <= jsonData["PC0201"].C0201data.C0201race.length; wkCnt++){
wkInfo = jsonData["PC0201"].C0201data.C0201race[wkCnt - 1];
gRaceNoParaList[wkCnt] = wkInfo.encParaR;
}
gResultRefundList = [];
gResultRefundList[0] = "dammy"
for(wkCnt=1; wkCnt<= wk0201Data.C0201race.length; wkCnt++){
wkInfo = wk0201Data.C0201race[wkCnt - 1];
if(wkInfo.rcvKekka == "1" || wkInfo.rcvRefund == "1"){
gResultRefundList[wkCnt] = true;
} else {
gResultRefundList[wkCnt] = false;
}
}
gOddsExistList = [];
gOddsExistList[0] = "dammy"
for(wkCnt=1; wkCnt <= wk0201Data.C0201race.length; wkCnt++){
wkInfo = wk0201Data.C0201race[wkCnt - 1];
if(wkInfo.rcvOdds == "1" || wkInfo.rcvOdds == "2"){
gOddsExistList[wkCnt] = true;
} else {
gOddsExistList[wkCnt] = false;
}
}
gRaceStopFlag = wk0201Data.flgRaceCancel;
gTaisenInfoExistFlag = wk0201Data.flgRecodes;
gSyumokuTypeResultInfoExistFlag = wk0201Data.flgActvSyumoku;
gDigestInfoExistFlag = wk0201Data.flgActvDugest;
}
function dateReflection() {
var wkReflectList = [];
if(gUpdateList.length != 0){
wkReflectList = gUpdateList;
} else {
wkReflectList = gDispOnList;
}
for(var key in wkReflectList){
callDrawFunction(wkReflectList[key]);
}
if(displayingId == "PJ0307"){
hhChgActiveBtn(6);
}else{
rbRaceSelectRefresh();
}
if(displayingId == "PJ0328"){
$('#stbtnmyKaime').addClass('active');
} else {
$('#stbtnmyKaime').removeClass('active');
}
resetJsonData();
}
function update(dispId, para, chgKbn, afterRaceNo){
gRequestPara = para;
gReqPrmsObject = [];
resetJsonData();
if(dispId != "PJ0307"){
    $("#apdivRaceBaseInfo").empty();
    $("#apPrintArea").addClass('dispoff');
}
commonLoad.loadingImage('true');
ozzStartFlg = "1";
dispInfoConfirm(dispId, para, chgKbn, afterRaceNo);
}
function updateJson(dispId, para, chgKbn, afterRaceNo,confirmFlg){
gDispOnList = [];
gUpdateList = [];
var ret = false;
var wkObj = {};
if(chgKbn != 1){
gReqPrmsObject["PC0101"] = PC0101Controller.shGetJsonRequestParameter(dispId);
gUpdateList.push("PC0101");
}
if(gRequestDispId == "PJ0328" && chgKbn == 1){
} else {
if(confirmFlg) {
if(Object.keys(jsonData["PC0201"]).length == 0){
wkObj = {};
wkObj["encp"] = gRequestPara;
gReqPrmsObject["PC0201"] = wkObj;
}
gUpdateList.push("PC0201");
}
wkObj = {};
wkObj["encp"] = gRequestPara;
gReqPrmsObject["PJ0311"] = wkObj;
gUpdateList.push("PJ0311");
gReqPrmsObject["PJ0312"] = wkObj;
gUpdateList.push("PJ0312");
}
if(gRequestDispId != "PT0511"){
wkObj = {};
wkObj["encp"] = gRequestPara;
gReqPrmsObject[gRequestDispId] = wkObj;
}
gUpdateList.push(gRequestDispId);
if(gRequestDispId != "PJ0307" && gRequestDispId != "PJ0326"){
wkObj = {};
wkObj["encp"] = gRequestPara;
gReqPrmsObject["PJ0314"] = wkObj;
gUpdateList.push("PJ0314");
}
$.when(jsonRequest())
.done(function(){
if(displayingId != gRequestDispId){
displayingId = gRequestDispId;
switchDisplay();
}
getDispCtrlInfo();
if(chgKbn != 1){
callDrawFunction("PC0101");
}
if(!confirmFlg) {
callDrawFunction("PC0201");
}
dateReflection();
ret = true;
})
.fail(function(){
ret = false;
})
.always(function(){
commonLoad.loadingImage('false');
return ret;
});
}
function btnClickOfFrame(dispId){
update(dispId, gPrmParaR, 1);
}
function btnKaisaiDateClick(index){
update("PJ0315", gKaisaiParaList[index], 3);
}
function btnRaceNoClick(index){
if(getBtnNo(displayingId) == 6){
gRequestDispId = "PT0511";
} else {
if(displayingId == "PJ0307"){
gRequestDispId = "PJ0315";
} else {
gRequestDispId = displayingId;
}
}
update(gRequestDispId, gRaceNoParaList[index], 2, index);
}
function btnKaimeDispClick(){
if(displayingId == "PJ0328"){
return;
}
var auth = $.cookie('auth-info-cookie');
if(auth === undefined || auth === null){
var prm = {};
prm["encp"] = gPrmParaR;
commonSubmit.formPost(
$('#rcUrlLogin').val()
, prm
, "_self"
);
} else {
update("PJ0328", gPrmParaR, 1);
}
}
function btnLiveVoteClick(kbn, para){
if(kbn == 1){
update("PJ0315", para, 4);
} else if(kbn == 2) {
rcChgModeBtn(para);
}
}
function btnCngMode(){
var wkObj = {};
wkObj["disp"] = displayingId;
wkObj["encp"] = gPrmParaR;
rcChgModeBtn(wkObj);
}
function rbRaceSelectRefresh(){
if(gRaceStopFlag){
$("#PJ0313").addClass('dispoff');
return;
} else {
for(var i=1 ; i<=9; i++){
rcChgDisableBtn(1, i);
}
$("#PJ0313").removeClass('dispoff');
}
if(!gTaisenInfoExistFlag){
rcChgDisableBtn(0,3);
}
if(!gSyumokuTypeResultInfoExistFlag){
rcChgDisableBtn(0,4);
}
if(!gOddsExistList[gRaceNo]){
rcChgDisableBtn(0,6);
}
if(!gResultRefundList[gRaceNo]){
rcChgDisableBtn(0,8);
}
if(!gDigestInfoExistFlag){
rcChgDisableBtn(0,9);
}
if(displayingId == "PJ0328"){
rcChgAllUnselectBtn();
} else {
rcChgActiveBtn(getBtnNo(displayingId));
}
if(displayingId == "PJ0326"){
rcDispRacePrintBtn(0);
} else {
rcDispRacePrintBtn(1);
}
rcModeTypeSetting();
}
function dispInfoConfirm(dispId, para, chgKbn, afterRaceNo){
gRequestDispId = dispId;
var confirmFlg = true;
if(chgKbn == 2){
gRaceNo = afterRaceNo;
if(dispId == "PJ0326" && !gResultRefundList[afterRaceNo]){
confirmFlg = false;
} else if(getBtnNo(dispId) == 6){
confirmFlg = false;
gRequestDispId = "PT0511";
}
}else if(chgKbn == 3 || chgKbn == 4){
confirmFlg = false;
}
if(confirmFlg){
return updateJson(dispId, para, chgKbn, afterRaceNo,confirmFlg);
}
var wkObj = {};
wkObj["encp"] = para;
gReqPrmsObject["PC0201"] = wkObj;
var ret = false;
$.when(jsonRequest())
.done(function(){
var wkInfo = [];
var wk0201Data = jsonData["PC0201"].C0201data;
var jsonRaceNo = wk0201Data.selRaceNo;
if(chgKbn == 2){
wkInfo = wk0201Data.C0201race[jsonRaceNo - 1];
if(dispId == "PJ0326"){
if(wkInfo.rcvKekka == "0" && wkInfo.rcvRefund == "0"){
gRequestDispId = "PJ0315";
}
} else if(getBtnNo(dispId) == 6){
if(wkInfo.rcvOdds == "0"){
gRequestDispId = "PJ0315";
}
}
} else if(chgKbn == 3 || chgKbn == 4){
gRaceNo = jsonRaceNo;
}
gRequestPara = wk0201Data.encSelParaR;
gReqPrmsObject = [];
ret = updateJson(dispId, para, chgKbn, afterRaceNo,confirmFlg);
})
.fail(function(){
ret = false;
})
.always(function(){
return ret;
});
}
function btnkeirinjyoClick(para){
update("PJ0315", para, 4);
}
function btnEtcClick(inDispId, inPara, inChgMode){
var dispId;
var para;
var chgMode;
if(inDispId == undefined || inDispId == null || inDispId == ""){
dispId = "PJ0315";
}else{
dispId = inDispId;
}
if(inPara == undefined || inPara == null || inPara == ""){
para = gPrmParaR;
}else{
para = inPara;
}
if(inChgMode == undefined || inChgMode == null || inChgMode == ""){
chgMode = 9; 
}else{
chgMode = inChgMode;
}
update(dispId, para, chgMode);
}
function resetJsonData(){
for(var key in gDisplayMaster){
jsonData[gDisplayMaster[key]] = {};
}
}
function jsonRequest(){
var dispIDs = []; 
var reqPromises = []; 
for (var key in gReqPrmsObject) {
dispIDs.push(key);
var reqID = getReqID(key);
reqPromises.push(Com.getRequestGet(reqID, gReqPrmsObject[key]));
}
var d = new $.Deferred();
$.when.apply(null, reqPromises)
.done(function () {
for (var i = 0; i < arguments.length; i++) {
jsonData[dispIDs[i]] = arguments[i];
}
d.resolve();
})
.fail(function(){
d.reject();
});
return d.promise();
}
function callDrawFunction(dispID){
switch (dispID) {
case 'PC0101':
PC0101View.shDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PC0201':
hhView.hhDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0307':
apView.apDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0311':
stView.stDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0312':
raView.raDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0314':
rfView.rfDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0315':
rbView.rbDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0316':
rlView.rlDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0317':
rwView.rwDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0318':
rsView.rsDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0319':
rtView.rtDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0320':
riView.riDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0326':
rrView.rrDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
break;
case 'PJ0328':
rcView.rcDrawJSONData(jsonData[dispID], gReqPrmsObject[dispID]);
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
bcStart.swichOzzDisplay();
break;
default:
break;
}
}
function getReqID(dispID){
switch (dispID) {
case 'PC0101':
return PC0101Controller.JSON_REQ_ID;
case 'PC0201':
return hhController.JSON_REQ_ID;
case 'PJ0307':
return apController.JSON_REQ_ID;
case 'PJ0311':
return stController.JSON_REQ_ID;
case 'PJ0312':
return raController.JSON_REQ_ID;
case 'PJ0314':
return rfController.JSON_REQ_ID;
case 'PJ0315':
return rbController.JSON_REQ_ID;
case 'PJ0316':
return rlController.JSON_REQ_ID;
case 'PJ0317':
return rwController.JSON_REQ_ID;
case 'PJ0318':
return rsController.JSON_REQ_ID;
case 'PJ0319':
return rtController.JSON_REQ_ID;
case 'PJ0320':
return riController.JSON_REQ_ID;
case 'PJ0326':
return rrController.JSON_REQ_ID;
case 'PJ0328':
return rcController.JSON_REQ_ID;
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
return bcController.JSON_015_ID;
break;
default:
break;
}
}
function getBtnNo(dispID){
var retBtnNo = 0;
switch (dispID) {
case 'PJ0315':
retBtnNo = 1;
break;
case 'PJ0316':
retBtnNo = 2;
break;
case 'PJ0317':
retBtnNo = 3;
break;
case 'PJ0318':
retBtnNo = 4;
break;
case 'PJ0319':
retBtnNo = 5;
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
retBtnNo = 6;
break;
case 'PJ0320':
retBtnNo = 7;
break;
case 'PJ0326':
retBtnNo = 8;
break;
default:
break;
}
return retBtnNo;
}
function tableHeaderClick(helpId) {
for(var key in gSubHelpMaster){
$("#" + gSubHelpMaster[key]).addClass('dispoff');
}
var title;
switch (helpId) {
case 'PY0101':
title = "平均競走得点";
break;
case 'PY0102':
title = "決まり手回数";
break;
case 'PY0103':
title = "B・H・S回数";
break;
case 'PY0104':
title = "勝率・2連対率・3連対率";
break;
case 'PY0105':
title = "直近成績";
break;
case 'PY0106':
title = "調子マーク";
break;
default:
title = "";
break;
}
$('div[class*="raceInfoSubHelp"] span[class="ui-dialog-title"]').text(title);
if(title != ""){
$("#" + helpId).removeClass('dispoff');
$('#raceInfoSubHelp').dialog('open');
}
}
var apController = {
    JSON_REQ_ID: "JSJ002",
    apCreateList: function( params) {
        Com.getRequestGet(apController.JSON_REQ_ID, params)
            .done(function(result) {
                apView.apDrawJSONData(result, params);
            });
    }
};
var apView = {
HDNKEY_ID: 'ppj0307',
apDrawJSONData: function(jsondata, params) {
if(!jsondata) {
$('#apdivRaceBaseInfo').addClass('dispoff');
$('#apErrorArea').removeClass('dispoff');
Com.makePcUpdatePage(
"apErrorArea"
, ""
, params
, function(arg0){
apController.apCreateList(arg0);
}
);
return;
}
else if (jsondata.resultCd == -1){
$('#apdivRaceBaseInfo').addClass('dispoff');
$('#apErrorArea').removeClass('dispoff');
var msg = "";
if(jsondata.message != undefined){
msg = jsondata.message;
}
Com.makePcUpdatePage(
"apErrorArea"
, msg
, params
, function(arg0){
apController.apCreateList(arg0);
}
);
return;
}
else{
$('#apErrorArea').addClass('dispoff');
$('#apdivRaceBaseInfo').removeClass('dispoff');
if(rbDataChecker(jsondata.syusouInfoExistFlg) == "0"){
$('#apdivRaceBaseInfo').addClass('dispoff');
}else{
$('#apdivRaceBaseInfo').removeClass('dispoff');
$("#apPrintArea").removeClass('dispoff');
var raceInfoList = jsondata.raceInfo;
var raceInfoListCnt = raceInfoList.length;
var areaHtml = "";
for(var raceLoop = 0 ; raceLoop < raceInfoListCnt; raceLoop++){
var raceno = raceInfoList[raceLoop]["raceNo"];
areaHtml +='<div class="clear-fix" style="padding-bottom:30px">';
areaHtml +='<div id="apRaceHeader_' + raceno + '">';
areaHtml +='</div>';
areaHtml +='<div class="fl-l race_member_l_1">';
areaHtml +='<table class="race_member">';
areaHtml +='<thead>';
areaHtml +='<tr id="apLeftHeader_1_' + raceno + '" class="forChrome">';
areaHtml +='<td class="race_header_height" style="width: 2%;" rowspan="2"><p><span>枠<br/>番</span></p></td>';
areaHtml +='<td style="width: 2%;" rowspan="2"><p><span>印</span></p></td>';
areaHtml +='<td style="width: 2%;" rowspan="2"><p><span>車<br/>番</span></p></td>';
areaHtml +='<td class="nb-b playername" rowspan="2"><p><span>選手名</span></p><p><span>府県</span><span>/</span><span>級班</span><span class="tbl_val14_fsz">前</span><span>現</span><span>/</span><span>脚質</span></p></td>';
areaHtml +='<td class="wb-r period race_header_height1"><p><span>期別</span></p></td>';
areaHtml +='</tr>';
areaHtml +='<tr id="apLeftHeader_2_' + raceno + '">';
areaHtml +='<td class="wb-r age race_header_height2"><p><span>年齢</span></p></td></tr>';
areaHtml +='</thead>';
areaHtml +='<tbody id="apTableLeftBody_' + raceno + '">';
areaHtml +='</tbody>';
areaHtml +='</table>';
areaHtml +='</div>';
areaHtml +='<div class="fl-l race_member_r_1">';
areaHtml +='<table class="race_member1_1">';
areaHtml +='<thead>';
areaHtml +='<tr id="apRightHeader_1_'+ raceno + '">';
areaHtml +='<td class="wb-r" colspan="11"><p class="dispib">直近4ヶ月成績</p>　<p class="dispib">※ 率は％表示</p></td>';
areaHtml +='<td class="clc" style="width: 30%;" rowspan="2" colspan="5" onclick="tableHeaderClick(\'PY0105\');">';
areaHtml +='<table style="width: 100%;">';
areaHtml +='<thead>';
areaHtml +='<tr>';
areaHtml +='<td class="b-b nb-r nb-t nb-l"><p><span>直近成績</span></p></td>';
areaHtml +='</tr>';
areaHtml +='<tr>';
areaHtml +='<td class="td_row1_height nb-l nb-r nb-b"><p><span>前場所</span></p></td>';
areaHtml +='</tr>';
areaHtml +='<tr>';
areaHtml +='<td class="td_row1_height nb-l nb-r nb-b"><p><span>今場所</span></p></td>';
areaHtml +='</tr>';
areaHtml +='</thead>';
areaHtml +='</table>';
areaHtml +='</td>';
areaHtml +='<td class="clc race_header_height" style="width: 4%;" rowspan="2" onclick="tableHeaderClick(\'PY0106\');">';
areaHtml +='<p><span>調</span></p>';
areaHtml +='<p><span>子</span></p></td>';
areaHtml +='</tr>';
areaHtml +='<tr id="apRightHeader_2_'+ raceno + '">';
areaHtml +='<td class="clc" style="width: 12%;" rowspan="2" onclick="tableHeaderClick(\'PY0101\');">';
areaHtml +='<p><span>競走</span><span>得点</span></p></td>';
areaHtml +='<td class="wb-r  clc" style="width: 18%;" rowspan="2" colspan="4" onclick="tableHeaderClick(\'PY0102\');">';
areaHtml +='<table style="width: 100%;">';
areaHtml +='<tbody>';
areaHtml +='<tr>';
areaHtml +='<td class="b-b nb-r nb-t nb-l" colspan="4">';
areaHtml +='<p><span>決まり手</span></p></td>';
areaHtml +='</tr>';
areaHtml +='<tr>';
areaHtml +='<td class="decisive cb-r" style="width: 25%;">';
areaHtml +='<p><span>逃</span></p></td>';
areaHtml +='<td class="decisive cb-r" style="width: 25%;">';
areaHtml +='<p><span>捲</span></p></td>';
areaHtml +='<td class="decisive cb-r" style="width: 25%;">';
areaHtml +='<p><span>差</span></p></td>';
areaHtml +='<td class="decisive nb-r" style="width: 25%;">';
areaHtml +='<p><span>マ </span></p></td>';
areaHtml +='</tr>';
areaHtml +='</tbody>';
areaHtml +='</table>';
areaHtml +='</td>';
areaHtml +='<td class="wb-r clc" style="width: 14%;" rowspan="2" colspan="3" onclick="tableHeaderClick(\'PY0103\');">';
areaHtml +='<table style="width: 100%; height: 100%;">';
areaHtml +='<tbody>';
areaHtml +='<tr>';
areaHtml +='<td class="td_row2_height decisive al-c cb-r nb-b nb-l" style="width: 33%;"><p><span>B</span></p></td>';
areaHtml +='<td class="td_row2_height decisive al-c cb-r nb-b" style="width: 33%;"><p><span>H</span></p></td>';
areaHtml +='<td class="td_row2_height decisive al-c nb-b nb-r" style="width: 34%;"><p><span>S</span></p></td>';
areaHtml +='</tr>';
areaHtml +='</tbody>';
areaHtml +='</table>';
areaHtml +='</td>';
areaHtml +='<td class="wb-r clc" style="width: 19%;" rowspan="2" colspan="3" onclick="tableHeaderClick(\'PY0104\');">';
areaHtml +='<table style="width: 100%; height: 100%;">';
areaHtml +='<tbody>';
areaHtml +='<tr>';
areaHtml +='<td class="td_row2_height decisive al-c cb-r nb-b nb-l" style="width: 32%;"><p><span>勝率</span></p></td>';
areaHtml +='<td class="td_row2_height decisive al-c cb-r nb-b" style="width: 34%;"><p><span>２連</span><br/><span>対率</span></p></td>';
areaHtml +='<td class="td_row2_height decisive al-c nb-b nb-r" style="width: 34%;"><p><span>３連</span><br/><span>対率</span></p></td>';
areaHtml +='</tr>';
areaHtml +='</tbody>';
areaHtml +='</table>';
areaHtml +='</td>';
areaHtml +='</tr>';
areaHtml +='</thead>';
areaHtml +='<tbody id="apTableRightBody_'+ raceno + '">';
areaHtml +='</tbody>';
areaHtml +='</table>';
areaHtml +='</div>';
areaHtml +='<div id="apYudoYosoInfo_'+ raceno + '">';
areaHtml +='</div>';
areaHtml +='<div id="apYosoBiko_'+ raceno + '">';
areaHtml +='</div>';
areaHtml +='</div>';
}
$('#apdivRaceBaseInfo').html(areaHtml);
var narabiyosoDispFlg = false;
for(var raceLoop = 0 ; raceLoop < raceInfoListCnt; raceLoop++){
var raceno = raceInfoList[raceLoop]["raceNo"];
var sensyuInfo = raceInfoList[raceLoop]["sensyuTypeInfo"];
var headerHtml = "";
var leftHtml = "";
var rightHtml = "";
var yudoYosoHtml = "";
var yosoBikoHtml = [];
var sensyuTypeInfoList = sensyuInfo;
var sensyuTypeInfoListCnt = sensyuInfo.length;
var wakuCheck = ""; 
var wakuIdList = []; 
var ht1stList = rbDataChecker(raceInfoList[raceLoop]["raceResult1Syaban"]).split(",");
var ht2ndList = rbDataChecker(raceInfoList[raceLoop]["raceResult2Syaban"]).split(",");
var bc1stList = rbDataChecker(raceInfoList[raceLoop]["backCnt1Syaban"]).split(",");
var bc2ndList = rbDataChecker(raceInfoList[raceLoop]["backCnt2Syaban"]).split(",");
headerHtml +='<table style="width:100%"><tr><td><p class="nobr">';
headerHtml +='<span style="font-size:18px;" class="bold">';
headerHtml +='第' + raceno + 'レース';
headerHtml +='</span>';
headerHtml +='<span>(' + raceInfoList[raceLoop]["shumokuName"] + ')</span>&nbsp;&nbsp;'
headerHtml +='<span>' + raceInfoList[raceLoop]["kyori"] + 'm(' + raceInfoList[raceLoop]["shukai"] + '周)</span>&nbsp;'
headerHtml +='<span>' + raceInfoList[raceLoop]["kyosoShurui"] + '</span>&nbsp;&nbsp;';
headerHtml +='</p>';
headerHtml +='<p class="nobr">';
if(raceInfoList[raceLoop]["dentoShimekiriMae"] == null || raceInfoList[raceLoop]["dentoShimekiriMae"] == ""){
headerHtml +='<span>発売締切</span>&nbsp;<span class="">' + raceInfoList[raceLoop]["dentoShimekiri"];
headerHtml +='</span>&nbsp;&nbsp;';
}
else{
headerHtml +='<span>発売締切</span>&nbsp;<span class="lineth">' + raceInfoList[raceLoop]["dentoShimekiriMae"];
headerHtml +='</span><span>&nbsp;→&nbsp;</span>';
headerHtml +='<span class="' + raceInfoList[raceLoop]["dentoShimekiriColor"] + ' bold">' + raceInfoList[raceLoop]["dentoShimekiri"];
headerHtml +='</span>&nbsp;&nbsp;';
}
if(raceInfoList[raceLoop]["hassouYoteiMae"] == null || raceInfoList[raceLoop]["hassouYoteiMae"] == ""){
headerHtml +='<span>発走予定</span>&nbsp;<span class="">' + raceInfoList[raceLoop]["hassouYotei"];
headerHtml +='</span>';
}
else{
headerHtml +='<span>発走予定</span>&nbsp;<span class="lineth">' + raceInfoList[raceLoop]["hassouYoteiMae"];
headerHtml +='</span><span>&nbsp;→&nbsp;</span>';
headerHtml +='<span class="' + raceInfoList[raceLoop]["hassouYoteiColor"] + ' bold">' + raceInfoList[raceLoop]["hassouYotei"];
headerHtml +='</span>&nbsp;&nbsp;';
}
headerHtml +='</p>';
headerHtml +='</td>';
headerHtml +='</tr>';
headerHtml +='</table>';
$('#apRaceHeader_' + raceno).html(headerHtml);
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="apLeftItem_' + rbDataChecker(sensyuTypeInfo.syaban) + "_" + raceno + '" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != rbDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == rbDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("aplblWakuban"+ raceno + "_"+ rbDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = rbDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="aplblWakuban' + raceno + '_' + rbDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rbDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + rbDataChecker(sensyuTypeInfo.yosoin) + '</td>';
leftHtml += '  <td class="' + rbDataChecker(sensyuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '    <p class="al-c"><span class="al-c">' + rbDataChecker(sensyuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '  <td class="al-l">';
leftHtml += '    <p><span><a href="javascript:void(0);" onclick="rbSensyuNameClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');" class="txt_underline bold">' + rbDataChecker(sensyuTypeInfo.sensyuName) + '</a></span><span class="' + rbDataChecker(sensyuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + rbDataChecker(sensyuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '    <p><span>' + rbDataChecker(sensyuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + rbEmptyTo3Space(sensyuTypeInfo.prevKyuhan) + '</span><span class="' + rbDataChecker(sensyuTypeInfo.kyuhanSpecialColor) + '">' + rbDataChecker(sensyuTypeInfo.kyuhan) + '</span><span>/</span><span>' + rbDataChecker(sensyuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '  <td class="wb-r clearfix">';
leftHtml += '    <table style="width: 100%; height: 100%;">';
leftHtml += '      <tbody>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-t nb-l period_data">';
leftHtml += '            <p class="al-c"><span>' + rbDataChecker(sensyuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-b nb-l age_data">';
leftHtml += '            <p class="al-c"><span>' + rbDataChecker(sensyuTypeInfo.age) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '      </tbody>';
leftHtml += '    </table>';
leftHtml += '  </td>';
leftHtml += '</tr>';
}
$('#apTableLeftBody_' + raceno).html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
for(var rightLoop = 0 ; rightLoop < sensyuTypeInfoListCnt; rightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rightLoop];
var konResultInfo  = sensyuTypeInfo.konResultInfoSubData;
var tyo4Info       = sensyuTypeInfo.tyo4InfoSubData;
var tokuColorClass = "";
for(var toku1Loop = 0 ; toku1Loop < ht1stList.length; toku1Loop++){
if(ht1stList[toku1Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
tokuColorClass = jsondata.charColor1;
}
}
for(var toku2Loop = 0 ; toku2Loop < ht2ndList.length; toku2Loop++){
if(ht2ndList[toku2Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
tokuColorClass = jsondata.charColor2;
}
}
var backColorClass = "";
for(var back1Loop = 0 ; back1Loop < bc1stList.length; back1Loop++){
if(bc1stList[back1Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
backColorClass = jsondata.charColor1;
}
}
for(var toku2Loop = 0 ; toku2Loop < bc2ndList.length; toku2Loop++){
if(bc2ndList[toku2Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
backColorClass = jsondata.charColor2;
}
}
rightHtml += '<tr id="apRightItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '_1_' + raceno + '" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
rightHtml += '  <td class="al-c clc race_body_height ' + tokuColorClass + '" style="padding:0;" onclick="rbHeikinTokutenClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');" rowspan="2">';
rightHtml += '    <p class="al-c"><span class="bold">' + rbDataChecker(sensyuTypeInfo.heikinTokuten) + '</span></p></td>';
rightHtml += '  <td class="al-c clc wb-r race_body_height" onclick="rbKimariteClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');" style="padding:0;" rowspan="2" colspan="4">';
rightHtml += '    <table style="width: 100%; height: 100%;">';
rightHtml += '      <tbody>';
rightHtml += '        <tr>';
rightHtml += '          <td class="decisive cb-r" style="padding:0;width: 25%;"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.nigeCnt) + '</span></p></td>';
rightHtml += '          <td class="decisive cb-r" style="padding:0;width: 25%;"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.makuriCnt) + '</span></p></td>';
rightHtml += '          <td class="decisive cb-r" style="padding:0;width: 25%;"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.sasiCnt) + '</span></p></td>';
rightHtml += '          <td class="decisive nb-r" style="padding:0;width: 25%;"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.markCnt) + '</span></p></td>';
rightHtml += '        </tr>';
rightHtml += '      </tbody>';
rightHtml += '    </table>';
rightHtml += '  </td>';
rightHtml += '  <td class="wb-r race_body_height" rowspan="2" colspan="3" style="padding:0;">';
rightHtml += '    <table style="width: 100%; height: 100%;">';
rightHtml += '      <tbody>';
rightHtml += '        <tr>';
rightHtml += '          <td class="al-c clc nb-a" onclick="rbBackHomeClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');" style="padding:0;width: 66%;">';
rightHtml += '            <table style="width: 100%; height: 100%;">';
rightHtml += '              <tbody>';
rightHtml += '                <tr>';
rightHtml += '                  <td class="decisive cb-r" style="padding:0;width: 50%;"><p><span class="bold ' + backColorClass + '">' + rbDataChecker(sensyuTypeInfo.backCnt) + '</span></p></td>';
rightHtml += '                  <td class="decisive nb-r" style="padding:0;width: 50%;"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.homeTori) + '</span></p></td>';
rightHtml += '                </tr>';
rightHtml += '              </tbody>';
rightHtml += '            </table>';
rightHtml += '          </td>';
rightHtml += '          <td style="padding:0;width: 34%;" class="al-c clc nb-a cb-l" onclick="rbStandingClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.stTori) + '</span></p></td>';
rightHtml += '        </tr>';
rightHtml += '      </tbody>';
rightHtml += '    </table>';
rightHtml += '  </td>';
rightHtml += '  <td class="wb-r race_body_height" rowspan="2" colspan="3" style="padding:0;">';
rightHtml += '    <table style="width: 100%; height: 100%;">';
rightHtml += '      <tbody>';
rightHtml += '        <tr>';
rightHtml += '          <td class="al-c clc nb-a cb-r chaku_type1" style="padding:0;width: 32.5%;" onclick="rbSyourituClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.syouritu) + '</span></p></td>';
rightHtml += '          <td class="al-c clc nb-a cb-r chaku_type2" style="padding:0;width: 34%;"onclick="rbRentairitu2Click(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.rentairitu2) + '</span></p></td>';
rightHtml += '          <td class="al-c clc nb-a chaku_type3" style="padding:0;width: 34%;"onclick="rbRentairitu3Click(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.rentairitu3) + '</span></p></td>';
rightHtml += '        </tr>';
rightHtml += '      </tbody>';
rightHtml += '    </table>';
rightHtml += '  </td>';
if(tyo4Info == undefined){
rightHtml += '<td class="race_body_height_half" style="padding:0;width: 9%;"><p><span><a href="javascript:void(0);" class="">&nbsp;</a></span></p></td>';
rightHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">&nbsp;</td>';
}else{
rightHtml += '  <td class="race_body_height_half" style="padding:0;width: 9%;"><p><span><a href="javascript:void(0);" onclick="rbTyoJyoGradeClick(\'' + rbDataChecker(tyo4Info.kkParameter) + '\');" class="txt_underline">' + rbDataChecker(tyo4Info.kerinjyoName) + rbDataChecker(tyo4Info.gaiTeiGrade) + '</a></span></p></td>';
if(rbDataChecker(tyo4Info.msg) != ""){
rightHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">' + tyo4Info.msg + '</td>';
}else{
rightHtml += rbMakeTyoResult(tyo4Info.resultInfoSubData);
}
}
rightHtml += '  <td rowspan="2" class="al-c nb-l race_body_height" style="padding:0;">';
if(rbDataChecker(sensyuTypeInfo.imgTyosiPath) == ""){
rightHtml += '&nbsp;';
}else{
rightHtml += '<img width="16" height="27" alt="' + rbDataChecker(sensyuTypeInfo.imgTyosiName) + '" src="' + rbDataChecker(sensyuTypeInfo.imgTyosiPath) + '"/>';
}
rightHtml += '  </td>';
rightHtml += '</tr>';
rightHtml += '<tr id="apRightItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '_2_' + raceno + '" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if(konResultInfo == undefined){
rightHtml += '<td class="race_body_height_half"><p><span>&nbsp;</span></p></td>';
rightHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">&nbsp;</td>';
}else{
rightHtml += '  <td class="race_body_height_half"><p><span>' + rbDataChecker(konResultInfo.gaiTeiGrade) + '</span></p></td>';
rightHtml += rbMakeTyoResult(konResultInfo.resultInfoSubData);
}
rightHtml += '</tr>';
}
$('#apTableRightBody_' + raceno).html(rightHtml);
for(var heightLoop = 0 ; heightLoop < sensyuTypeInfoListCnt; heightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[heightLoop];
var no = rbDataChecker(sensyuTypeInfo.syaban);
var totalHeight1 = $('#apRightItem_' + no + '_1_' + raceno).height();
var totalHeight2 = $('#apRightItem_' + no + '_2_' + raceno).height();
var totalHeight = totalHeight1 + totalHeight2;
$('#apLeftItem_' + no + "_" + raceno).height(totalHeight);
$('#apRightItem_' + no + '_1_' + raceno).height(totalHeight1);
$('#apRightItem_' + no + '_2_' + raceno).height(totalHeight2);
}
yudoYosoHtml += '<div class="dispon" style="margin-top: 16px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rbDataChecker(raceInfoList[raceLoop]["yudoSensyuName"]) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + raceInfoList[raceLoop]["yudoSensyuName"] + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rbDataChecker(raceInfoList[raceLoop]["yosoinMei"]) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + raceInfoList[raceLoop]["yosoinMei"] + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rbDataChecker(raceInfoList[raceLoop]["lastUpdateTime"]) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#apYudoYosoInfo_' + raceno).html(yudoYosoHtml);
yosoBikoHtml = rfEdit(raceInfoList[raceLoop]["PJ0314MainData"], raceno,true);
$('#apYosoBiko_' + raceno).html(yosoBikoHtml.join("").replace(/,/g,""));
if(raceLoop != raceInfoListCnt -1){
$('#brlblNarabiTyui').remove();
}
if(raceInfoList[raceLoop]["PJ0314MainData"]["narabiyoso"]["ryoikiFlg"] == "true" &&
raceInfoList[raceLoop]["PJ0314MainData"]["narabiyoso"]["errFlg"] != "true"){
narabiyosoDispFlg = true;
}
if(raceLoop == raceInfoListCnt -1 && narabiyosoDispFlg){
var narabiyosoHtml = [];
narabiyosoHtml.push('<table class="w100pc"><tbody><tr>');
narabiyosoHtml.push('<td class="al-l">※この並びはあくまで予想の為、実際の並びとは異なることがあります。</td>');
narabiyosoHtml.push('</tr></tbody></table>');
$('#brlblNarabiTyui').html(narabiyosoHtml);
}
}
}
return;
}
}
};
var stController = {
    JSON_REQ_ID: "JSJ003",
    stCreateList: function(params) {      
        Com.getRequestGet(stController.JSON_REQ_ID, params)
            .done(function(result) {
            stView.stDrawJSONData(result,params);
            });
    }
};
$(window).load(function() {
$(document).on("click","a[id^='stlnk']",function(){
myId = this.id;
var params = {};
if(myId != "stlnkSubWin"){
hdnnm = myId.substr(5);
params["kday"] = $("#sthdn" + hdnnm + "PrmKday").attr("value");
params["tuban"] = $("#sthdn" + hdnnm + "PrmTban").attr("value");
params["eizo_kbn"] = $("#sthdn" + hdnnm + "PrmEkbn").attr("value");
params["bkcd"] = $("#sthdn" + hdnnm + "PrmBkcd").attr("value");
commonLink.NewWindow("","1");
commonSubmit.formGet($("#"+myId).attr("href"),params,"subwin");
} else {
commonLink.NewWindow($("#"+myId).attr("href"),"1");
}
return false;
});
});
var stkjcd = "";
var stView = {
    HDNKEY_ID: 'JSJ003',
    stDrawJSONData: function(PJ0311JSONData,params) {
    var stream = $('#stdivracestream');
    var tmp = "";
if ( !PJ0311JSONData ) {
$("#stdivmain").empty();
Com.makePcUpdatePage(
"stdivmain"
, ""
, params
, function(arg0){
stController.stCreateList(arg0);
}
);
} else if ( PJ0311JSONData.resultCd == -1 ) {
$("#stdivmain").empty();
if(!PJ0311JSONData.message){
tmp = "";
} else {
tmp = PJ0311JSONData.message;
}
Com.makePcUpdatePage(
"stdivmain"
, tmp
, params
, function(arg0){
stController.stCreateList(arg0);
}
);
} else {
stdecision();
stmaindisp(PJ0311JSONData,params);
}
}
}
function stCreateStream(JsonData){
if(JsonData.streamFlg == 1){
if(stkjcd != JsonData.kjcd){
DestroyStream();
$("#flashdiv").empty();
$("#flashdiv").append($("<video>").attr("id","videoPlayer").attr("controls","controls"));
if($("#flashdiv").hasClass("dispoff")){
$("#flashdiv").removeClass("dispoff")
}
if($("#stdivmsg").hasClass("msgstream")){
$("#stdivmsg").removeClass("msgstream")
}
$("#stdivmsg").empty();
CreateStream(JsonData.liveUrl);
}
stkjcd = JsonData.kjcd;
} else {
$("#stdivmsg").empty();
$("#stdivmsg").append($("<div>").append($("#sthdnMsgStream").attr("value")));
if(!$("#stdivmsg").hasClass("msgstream")){
$("#stdivmsg").addClass("msgstream")
}
stkjcd = "";
DestroyStream();
$("#flashdiv").empty();
if(!$("#flashdiv").hasClass("dispoff")){
$("#flashdiv").addClass("dispoff")
}
}
}
function stCreateSubWin(JsonData){
var subWinHtml = "";
if(JsonData.subWinFlg == 1){
subWinHtml = ($("<a>").addClass("txt_underline").attr("href",JsonData.jyoIntroUrl+"?bkcd="+ JsonData.bkcd + "&kday="+ JsonData.kday).attr("id","stlnkSubWin")
.append("映像を別ウィンドウで表示")
.append($("<i>").addClass("fa fa-external-link"))
);
} else {
subWinHtml = "";
}
return subWinHtml
}
function stCreateKaime(JsonData){
var kaimebtnHtml = "";
if(JsonData.kaimeFlg == 1){
kaimebtnHtml = $("<button>").addClass("btn onbtn w100pc m-al-c").attr({
type:"button",
id:"stbtnmyKaime",
onclick:"btnKaimeDispClick()"
}).append("自分の買い目表示");
} else {
kaimebtnHtml = $("<button>").addClass("btn onbtn w100pc disabled m-al-c").attr({
type:"button",
id:"stbtnmyKaime",
disabled:"disabled"
}).append("自分の買い目表示");
}
return kaimebtnHtml
}
function stCreateJyoIntro(JsonData){
var jyoIntroHtml = $("<div>");
var JyoIntro = "";
var tmpHtml = "";
jyoIntroHtml.addClass("streamtbl m-al-c");
for (var i=0;i < JsonData.jyoIntroList.length ;i++){
JyoIntro = $(JsonData.jyoIntroList)[i];
tmpHtml =  $("<div>").css("word-break","break-all");
tmpHtml.append($("<a>").addClass("txt_underline").attr("href",JsonData.jyoIntroUrl).attr("id","stlnkjyoInt"+i)
.append($('<img>').addClass("digesticon").attr({
height: "16",
alt: unsanitaiz(JsonData.digestName),
src: JsonData.digestPath
}))
.append(" "+JyoIntro.jyoIntroName)
.append($('<input>').attr({
type: "hidden",
id: "sthdnjyoInt" + i +"PrmTban",
name: "sthdnjyoInt" + i +"PrmTban",
value:JyoIntro.tban
}))
.append($('<input>').attr({
type: "hidden",
id: "sthdnjyoInt" + i +"PrmBkcd",
name: "sthdnjyoInt" + i +"PrmbBkcd",
value:JyoIntro.bkcd
}))
.append($('<input>').attr({
type: "hidden",
id: "sthdnjyoInt" + i +"PrmEkbn",
name: "sthdnjyoInt" + i +"PrmEkbn",
value:JyoIntro.ekbn
}))
.append($('<input>').attr({
type: "hidden",
id: "sthdnjyoInt" + i +"PrmKday",
name: "sthdnjyoInt" + i +"PrmKday",
value:JsonData.kday
}))
);
jyoIntroHtml.append(tmpHtml);
}
return jyoIntroHtml;
}
function stCreateBanner(JsonData){
var bannerHtml = $("<div>");
var Banner = "";
var tmpHtml = "";
var trHtml = $("<tr>");
bannerHtml.addClass("streamtbl m-al-c");
for (var i=0;i < JsonData.bannerList.length;i++){
Banner = $(JsonData.bannerList)[i];
if(i == 1){
    trHtml.append($("<td>").addClass("al-c").append($("<div>)").addClass("w20").append("&nbsp;")));
}
if(Banner.winKbn == 0){
tmpHtml = $("<a>").addClass("txt_underline").attr("href",Banner.bannerUrl);
} else {
tmpHtml = $("<a>").addClass("txt_underline").attr({
href:Banner.bannerUrl,
target:"_blank"
});
}
if(Banner.bannerType == 0){
tmpHtml.append($("<img>").attr({
src:Banner.bannerImgPath,
width:"179",
height:"30"
}));
}else if(Banner.bannerType == 2){
tmpHtml.append(Banner.bannerTxt);
}else if(Banner.bannerType == 3){
tmpHtml.append(Banner.bannerLnkTxt);
}
trHtml.append($("<td>").addClass("al-c w210").append(tmpHtml));
}
    if(JsonData.bannerList.length == 1){
        trHtml.append($("<td>").addClass("al-c w210").append("&nbsp;"));
    }
bannerHtml.append($("<table>").addClass("w100pc").append($("<tbody>").append(trHtml)));
return bannerHtml;
}
function unsanitaiz(sanitaizData){
return $("<div>").append(sanitaizData)[0].innerHTML;
}
function stdecision(){
return stdecisionMain();
}
function stdecisionMain(){
if($("#stdivmainRetryBtn").length == 1){
$("#stdivmain").empty();
$("#stdivmain")
    .append($("<div>").attr("id","stdivmsg").addClass("msgstream m-al-c"))
    .append($("<div>").attr("id","flashdiv"))
    .append($("<div>").attr("id","stdivracestream"));
} else {
$('#stdivracestream').empty();
}
}
function stmaindisp(PJ0311JSONData,params){
return stmain(PJ0311JSONData,params);
}
function stmain(PJ0311JSONData,params){
var stream = $('#stdivracestream');
var tmpHtml = "";
stream.append($('<input>').attr({
type: "hidden",
id: "sthdnMsgStream",
name: "sthdnMsgStream",
value:PJ0311JSONData.divMsg
}));
stCreateStream(PJ0311JSONData);
tmpHtml = $("<table>");
tmpHtml.addClass("streamtbl m-al-c").append($("<tbody>").append($("<tr>")
.append($("<td>").attr("id","sttdsubStream").append(stCreateSubWin(PJ0311JSONData)))
.append($("<td>").append(stCreateKaime(PJ0311JSONData)))
));
stream.append(tmpHtml);
if( PJ0311JSONData.jyoIntroList != null){
stream.append(stCreateJyoIntro(PJ0311JSONData));
}
if( PJ0311JSONData.bannerList != null){
stream.append(stCreateBanner(PJ0311JSONData));
}
}
function raOnSortClick(sortmode){   
var currentsort =$("[id=rasortmode]").attr("value");
var HeldRace = $("#radivHeldRaceListTbl");
var mode=0;
if(sortmode==0){
if (currentsort == 0){
mode = 1;
} else {
mode = 0;    
}
} else if (sortmode==1){
if (currentsort == 2){
mode = 3;
} else {
mode = 2;    
}    
} else {
if (currentsort == 4){
mode = 5;
} else {
mode = 4;    
}        
}
HeldRace.empty();
raView.raCreatebctblRaceList(mode); 
}
function raKeirinjoClick(id){
var ctrlId= "[id=raHdnRaceInfo_"+id+"]";
var param = $(ctrlId).attr("value");
if(param.length > 0){
btnkeirinjyoClick(param);
}
}
var raController = {
    JSON_REQ_ID: "JSJ004",
    init: function() {
        raController.raCreateList();
    },
    raCreateList: function(params) {
        var result = null;
var HeldRace = $("#radivHeldRaceListTbl");
var para = {};
        para["dkbn"] = params;
        Com.getRequestGet(raController.JSON_REQ_ID, para)
            .done(function(result) {
            HeldRace.empty();
            raView.raDrawJSONData(result,params);
            });
        return false;
    }
};
var rakaisaiData;
var ranoRaceMsg;
var ranoRacebgColor;
var raView = {
    HDNKEY_ID: 'JSJ004',
    raDrawJSONData: function(PJ0312JSONData,params) {
    if( !PJ0312JSONData ) {
    $('#radivHeldRaceList').addClass('dispoff');
    $('#radivHeldRaceListTbl').addClass('dispoff');
$('#radivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"radivErrorRaceInfo"
, ""
, params
, function(arg0){
raController.raCreateList(arg0);
}
);
      return;
    } else if( PJ0312JSONData.resultCd == -1 ) {
    $('#radivHeldRaceList').addClass('dispoff');
    $('#radivHeldRaceListTbl').addClass('dispoff');
$('#radivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"radivErrorRaceInfo"
, PJ0312JSONData.message
, params
, function(arg0){
raController.raCreateList(arg0);
}
);
      return;
    } else {
var HeldRace = $("#radivHeldRaceList");
var TblRace = $("#radivHeldRaceListTbl");
var tmpHtml = $("<ul>");
var raceData = [];
HeldRace.empty();
$('#radivErrorRaceInfo').addClass('dispoff');
tmpHtml.addClass("nav-tabs nav")
.append($("<li>").append($("<a>").attr("href","javascript:void(0)").attr("onclick","raController.raCreateList(1)").append(PJ0312JSONData.today)))
.append($("<li>").append($("<a>").attr("href","javascript:void(0)").attr("onclick","raController.raCreateList(2)").append(PJ0312JSONData.tomorrow)));
if(PJ0312JSONData.dateKBN == 1){
$(($(tmpHtml).children())[0]).addClass("active");
$(($(tmpHtml).children())[1]).addClass("txt_underline").addClass("color_blue"); 
} else {
$(($(tmpHtml).children())[1]).addClass("active");
$(($(tmpHtml).children())[0]).addClass("txt_underline").addClass("color_blue"); 
}
HeldRace.append(tmpHtml);
if (PJ0312JSONData.kaisaiData.length <= 0){
noRaceMsg = PJ0312JSONData.divMsg;
noRacebgColor = PJ0312JSONData.bgColor_noRace;
kaisaiData = null;
} else {
for(var i = 0; i < PJ0312JSONData.kaisaiData.length; i++){
HeldData = $(PJ0312JSONData.kaisaiData)[i];
raceData.push([HeldData.bkname,
               HeldData.bkCode,
               HeldData.tyushiKbn,
               HeldData.greadCd,
               HeldData.greadColor,
               HeldData.greadPath,
               HeldData.greadName,
               HeldData.nitijiPath,
               HeldData.nitijiName,
               HeldData.kaisaiKbnPath,
               HeldData.kaisaiKbnName,
               HeldData.huka1Path,
               HeldData.huka1Name,
               HeldData.huka2Path,
               HeldData.huka2Name,
               HeldData.raceNum,
               HeldData.denTime,
               HeldData.denBoldFlg,
               HeldData.denColorFlg,
               HeldData.stColorFlg,
               HeldData.stTime,
               HeldData.raceUrlPrm,
               HeldData.kCode
               ]);
}
}
kaisaiData = raceData;
raView.raCreatebctblRaceList(0);
    }
    },
raCreatebctblRaceList: function(sortmode){
var TblRace = $("#radivHeldRaceListTbl");
var tmpHtml = "";
var tblHtml = $('<table>').attr("id","raRaceData");
var tbodyHtml = $('<tbody>');
var tbodytrHtml = "";
var redClass  = $("[id=rahdnRedFont]").attr("value");
var tmpclass ="";
var raceData = [];
var ascIcon = $("[id=rahdnAscIcon]").attr("value");
var ascName = $("[id=rahdnAscName]").attr("value");
var decIcon = $("[id=rahdnDscIcon]").attr("value");
var decName = $("[id=rahdnDscName]").attr("value");
var nonIcon = $("[id=rahdnNonIcon]").attr("value");
var nonName = $("[id=rahdnNonName]").attr("value");
var sortIcon = [[decIcon,decName,nonIcon,nonName,nonIcon,nonName],
        [ascIcon,ascName,nonIcon,nonName,nonIcon,nonName],
        [nonIcon,nonName,decIcon,decName,nonIcon,nonName],
        [nonIcon,nonName,ascIcon,ascName,nonIcon,nonName],
        [nonIcon,nonName,nonIcon,nonName,decIcon,decName],
        [nonIcon,nonName,nonIcon,nonName,ascIcon,ascName]
        ];
var borderClass_jo ="";
var borderClass ="";
var borderClass_rNo ="";
var borderClass_dTime ="";
var borderClass_rTime ="";
TblRace.empty();
tmpHtml = $("<thead>");
raceData = kaisaiData;
if (raceData==""){
tbodytrHtml = $('<tr>');
tbodytrHtml.append($('<td>').attr({"colspan":"10"}).append(noRaceMsg).addClass("al-c bold ratd "+noRacebgColor+""));
tbodyHtml.append(tbodytrHtml);
tblHtml.append(tbodyHtml);
TblRace.append(tblHtml);
return TblRace;
} else{
tmpHtml.append($("<tr>")
.append($("<td>").addClass("tbl_header2 al-c clc tbltitle_race ratd").attr("val","tblTitle_JyoRace").attr("colspan","8").attr("onclick","raOnSortClick(0)").append($("<div>").addClass("clear-fix")
.append($("<div>").addClass("fl-r").append($("<img>").attr({
src:sortIcon[sortmode][0],
alt:sortIcon[sortmode][1],
})))
.append($("<div>").append("競輪場・レース"))
))
.append($("<td>").addClass("tbl_header2 al-c clc tbltitle_time ratd").attr("val","tblTitle_Dentou").attr("colspan","1").attr("onclick","raOnSortClick(1)").append($("<div>").addClass("clear-fix")
.append($("<div>").addClass("fl-r").append($("<img>").attr({
src:sortIcon[sortmode][2],
alt:sortIcon[sortmode][3],
})))
.append($("<div>").append("発売締切"))
))
.append($("<td>").addClass("tbl_header2 al-c clc tbltitle_time ratd").attr("val","tblTitle_Syusou").attr("colspan","1").attr("onclick","raOnSortClick(2)").append($("<div>").addClass("clear-fix")
.append($("<div>").addClass("fl-r").append($("<img>").attr({
src:sortIcon[sortmode][4],
alt:sortIcon[sortmode][5],
})))
.append($("<div>").append("発走予定"))
))
);
tmpHtml.append($("<hidden>").attr("id","rasortmode").attr("value",sortmode));
tblHtml.append(tmpHtml);
if (sortmode==0){
raceData.sort(rafuncKeirinjoASC);
} else if (sortmode==1){
raceData.sort(rafuncKeirinjoDesc);
} else if (sortmode==2){
raceData.sort(rafuncDentouASC);
} else if (sortmode==3){
raceData.sort(rafuncDentouDesc);
} else if (sortmode==4){
raceData.sort(rafuncSyusouASC);
} else if (sortmode==5){
raceData.sort(rafuncSyusouDesc);
}
var arryLength = raceData.length;
for(var i = 0; i < arryLength; i++){
if(i==0){
borderClass_jo ="b-a nb-r nb-t";
borderClass ="b-a nb-t nb-l nb-r";
borderClass_rNo ="b-a nb-t nb-l";
borderClass_dTime ="tdst al-r b-a nb-t td_hgt shime_tbody";
borderClass_rTime ="tdden al-r b-a nb-t td_hgt time_tbody";
} else {
borderClass_jo ="b-a nb-r";
borderClass ="b-a nb-l nb-r";
borderClass_rNo ="b-a nb-l";
borderClass_dTime ="tdst al-r b-a td_hgt shime_tbody";
borderClass_rTime ="tdden al-r b-a td_hgt time_tbody";
}
tbodytrHtml = $('<tr>');
tbodytrHtml.attr("id","ralnkRaceBasic_"+i);
if(raceData[i][21].length > 0){
tbodytrHtml.addClass(raceData[i][4] + " " + "clc")
}
else{
tbodytrHtml.addClass(raceData[i][4])
}
tbodytrHtml.append($('<td>').append(raceData[i][0]).addClass("tdkeirin "+ borderClass_jo +" ratd pj0312_nopadding_td_jo").attr("onclick","raKeirinjoClick("+i+")"));
if(raceData[i][2] == 1){
tbodytrHtml.append($('<td>').append("中止").addClass("color_red al-l "+ borderClass +"  ratd pj0312_nopadding_td").attr("onclick","raKeirinjoClick("+i+")"));
} else {
tbodytrHtml.append($('<td>').append("").addClass("tdstop  "+ borderClass +"  ratd pj0312_nopadding_td").attr("onclick","raKeirinjoClick("+i+")"));
}
tbodytrHtml.append($('<td>').addClass("tdgicon  "+ borderClass +"  ratd").attr("onclick","raKeirinjoClick("+i+")")
.append($("<img>").addClass("gradeIconSize").attr({
src:raceData[i][5],
alt:raceData[i][6],
}))
);
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass("tdnicon  "+ borderClass )
.append($("<img>").attr({
src:raceData[i][7],
alt:raceData[i][8],
}))
);
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass("tbkicon al-c "+ borderClass)
.append($("<img>").addClass("HoldingIconSize").attr({
src:raceData[i][9],
alt:raceData[i][10],
}))
);
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass("tbhicon al-c  "+ borderClass)
.append($("<img>").addClass("inforIconSize").attr({
src:raceData[i][11],
alt:raceData[i][12],
}))
);
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass("tbkicon al-c  "+ borderClass)
.append($("<img>").addClass("inforIconSize").attr({
src:raceData[i][13],
alt:raceData[i][14],
}))
);
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass("tdrace al-r "+ borderClass_rNo +" td_hgt pj0312_race_no_td").append($("<span>").append(raceData[i][15]).addClass("pj0312_race_no")));
if(raceData[i][17] == 1){
borderClass_dTime = borderClass_dTime + " " + "bold";
}
if(raceData[i][18] == 1){
borderClass_dTime = borderClass_dTime + " " + redClass;
}
if(raceData[i][2] == 1){
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass(borderClass_dTime));
} else {
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").append(raceData[i][16]).addClass(borderClass_dTime));
}
if(raceData[i][19] == 1){
borderClass_rTime = borderClass_rTime + " " + redClass;
}
if(raceData[i][2] == 1){
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").addClass(borderClass_rTime));
} else {
tbodytrHtml.append($('<td>').attr("onclick","raKeirinjoClick("+i+")").append(raceData[i][20]).addClass(borderClass_rTime));
}
tbodytrHtml.append($('<hidden>').attr("id","raHdnRaceInfo_"+i).attr("value",raceData[i][21]).css("display","none")); 
tbodyHtml.append(tbodytrHtml);
}
tblHtml.append(tbodyHtml);
TblRace.append(tblHtml);
return false;
}
}
}
function rafuncKeirinjoASC(a,b){
if (a[3] < b[3]) return 1;
if (a[3] > b[3]) return -1;
if (a[3] == b[3]){ 
if (a[22] < b[22]) return -1;
if (a[22] > b[22]) return 1;
}
return 0;
};
function rafuncKeirinjoDesc(a,b){
if (a[3] < b[3]) return -1;
if (a[3] > b[3]) return 1;
if (a[3] == b[3]){ 
if (a[22] < b[22]) return 1;
if (a[22] > b[22]) return -1;
}
return 0;
};
function rafuncDentouASC(a,b){
if (a[2] < b[2]) return -1;
if (a[2] > b[2]) return 1;
if (a[2] == b[2]){
if (a[16] < b[16]) return -1;
if (a[16] > b[16]) return 1;
if (a[16] == b[16]){
if (a[3] < b[3]) return 1;
if (a[3] > b[3]) return -1;
if (a[3] == b[3]){
if (a[22] < b[22]) return -1;
if (a[22] > b[22]) return 1;
}
}
}
return 0;
};
function rafuncDentouDesc(a,b){
if (a[2] < b[2]) return 1;
if (a[2] > b[2]) return -1;
if (a[2] == b[2]){
if (a[16] < b[16]) return 1;
if (a[16] > b[16]) return -1;
if (a[16] == b[16]){
if (a[3] < b[3]) return 1;
if (a[3] > b[3]) return -1;
if (a[3] == b[3]){
if (a[22] < b[22]) return -1;
if (a[22] > b[22]) return 1;
}
}
}
return 0;
};
function rafuncSyusouASC(a,b){
if (a[2] < b[2]) return -1;
if (a[2] > b[2]) return 1;
if (a[2] == b[2]){
if (a[20] < b[20]) return -1;
if (a[20] > b[20]) return 1;
if (a[20] == b[20]){
if (a[3] < b[3]) return 1;
if (a[3] > b[3]) return -1;
if (a[3] == b[3]){
if (a[22] < b[22]) return -1;
if (a[22] > b[22]) return 1;
}
}
}
return 0;
};
function rafuncSyusouDesc(a,b){
if (a[2] < b[2]) return 1;
if (a[2] > b[2]) return -1;
if (a[2] == b[2]){
if (a[20] < b[20]) return 1;
if (a[20] > b[20]) return -1;
if (a[20] == b[20]){
if (a[3] < b[3]) return 1;
if (a[3] > b[3]) return -1;
if (a[3] == b[3]){
if (a[22] < b[22]) return -1;
if (a[22] > b[22]) return 1;
}
}
}
return 0;
};
$(window).on('load', function() {
if( sessionStorage.length > 0 ) {
sessionStorage.clear();
}
});