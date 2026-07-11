var khView = {
HDNKEY_ID: 'ppj0304',
khDrawJSONData: function(maindata, params) {
if ( !maindata ) {
Com.viewErrorPage(null);
} else if ( maindata.resultCd == -1 ) {
var messageCd = "";
if(maindata.messageCd != undefined){
messageCd = maindata.messageCd;
}
Com.viewErrorPage(messageCd);
} else {
var $editDate = $('#khlblUpdate');
var strEditDateHtml =[];
strEditDateHtml.push(maindata.upDateTime);
$editDate[0].innerHTML = strEditDateHtml.join("");
if(maindata.noMessageFlg){
if($("#khdivKaisaiDayInfo").hasClass("dispon")) {
$("#khdivKaisaiDayInfo").addClass("dispoff").removeClass("dispon");
}
if($("#khdivNomsg").hasClass("dispoff")) {
$("#khdivNomsg").addClass("dispon").removeClass("dispoff").addClass(maindata.noMessageColor);
}
if($("#khdivGuide").hasClass("dispon")) {
$("#khdivGuide").addClass("dispoff").removeClass("dispon");
}
var $noMsg = $('#khlblNomsg');
var strNoMsgHtml =[];
strNoMsgHtml.push(maindata.noMessage);
$noMsg[0].innerHTML = strNoMsgHtml.join("");
} else {
if($("#khdivKaisaiDayInfo").hasClass("dispoff")) {
$("#khdivKaisaiDayInfo").addClass("dispon").removeClass("dispoff");
}
if($("#khdivNomsg").hasClass("dispon")) {
$("#khdivNomsg").addClass("dispoff").removeClass("dispon");
}
if($("#khdivGuide").hasClass("dispoff")) {
$("#khdivGuide").addClass("dispon").removeClass("dispoff");
}
var $kaisaiday = $('#khtblKaisaiDayInfo');
var strKaisaiDayHtml =[];
strKaisaiDayHtml.push(' <tbody>');
strKaisaiDayHtml.push(' <tr class="tr_h">');
for(var iloop = 0; iloop < maindata.headList.length; iloop++ ){
strKaisaiDayHtml.push(' <td class="tbl_header ');
strKaisaiDayHtml.push(maindata.headList[iloop].headColor);
strKaisaiDayHtml.push('" style="width: ');
strKaisaiDayHtml.push(maindata.headList[iloop].headPercent);
strKaisaiDayHtml.push('%;">');
strKaisaiDayHtml.push(maindata.headList[iloop].headItem);
strKaisaiDayHtml.push('</td>');
}
strKaisaiDayHtml.push(' </tr>');
for(var iloop = 0; iloop < maindata.bodyList.length; iloop++ ){
if(iloop % 2 == 0){
strKaisaiDayHtml.push(' <tr class="tr_h altertable_guusu">');
} else {
strKaisaiDayHtml.push(' <tr class="tr_h">');
}
if(maindata.bodyList[iloop].dispHukenFlg){
strKaisaiDayHtml.push(' <td class="al-c td_body" rowspan="');
strKaisaiDayHtml.push(maindata.bodyList[iloop].dispRowSpan);
strKaisaiDayHtml.push('">');
strKaisaiDayHtml.push(maindata.bodyList[iloop].hukenName);
strKaisaiDayHtml.push('</td>');
}
if(maindata.bodyList[iloop].honbaFlg == "0"){
strKaisaiDayHtml.push('<td class="al-c td_body"><a class="txt_underline" onclick="khShowUriba(\'');
strKaisaiDayHtml.push(maindata.bodyList[iloop].linkFuncId);
strKaisaiDayHtml.push('\',\'');
strKaisaiDayHtml.push(maindata.bodyList[iloop].uribaCode);
strKaisaiDayHtml.push('\',\'');
strKaisaiDayHtml.push(maindata.kaisaiDate);
strKaisaiDayHtml.push('\',\'');
strKaisaiDayHtml.push(maindata.bodyList[iloop].prm0304);
strKaisaiDayHtml.push('\')"><b>');
strKaisaiDayHtml.push(maindata.bodyList[iloop].uribaName);
strKaisaiDayHtml.push('</b></a></td>');
} else {
strKaisaiDayHtml.push('<td class="al-c td_body">');
strKaisaiDayHtml.push('<b>');
strKaisaiDayHtml.push(maindata.bodyList[iloop].uribaName);
strKaisaiDayHtml.push('</b></td>');
}
for(var iloop_2 = 0; iloop_2 < maindata.bodyList[iloop].kaisaiDataList.length; iloop_2++ ){
strKaisaiDayHtml.push('<td class="al-c td_body">');
if(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationTime != ""){
strKaisaiDayHtml.push('<span class="soldtime">');
strKaisaiDayHtml.push(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationTime);
strKaisaiDayHtml.push('</span>');
}
if(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRace1 != ""){
if(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationTime != ""){
strKaisaiDayHtml.push('<br>');
}
strKaisaiDayHtml.push('<span class="');
strKaisaiDayHtml.push(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRaceColor);
strKaisaiDayHtml.push('">');
strKaisaiDayHtml.push(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRace1);
strKaisaiDayHtml.push('</span>');
}
if(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRace2 != ""){
if(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationTime != ""
&& maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRace1 == ""){
strKaisaiDayHtml.push('<br>');
}
strKaisaiDayHtml.push('<span>');
strKaisaiDayHtml.push(maindata.bodyList[iloop].kaisaiDataList[iloop_2].hatubaiSituationRace2);
strKaisaiDayHtml.push('</span>');
}
strKaisaiDayHtml.push('</td>');
}
strKaisaiDayHtml.push(' </tr>');
}
strKaisaiDayHtml.push(' </tbody>');
strKaisaiDayHtml.push(' </table>');
$kaisaiday[0].innerHTML = strKaisaiDayHtml.join("");
}
if( maindata.urlInfo != undefined ) {
var $areahdnInfo = $('#khhdnInfo');
var strhdnInfoHtml =[];
strhdnInfoHtml.push('<input type="hidden" id="khhdnUrl0704" value="');
strhdnInfoHtml.push(maindata.urlInfo.urlPj0704);
strhdnInfoHtml.push('" >');
strhdnInfoHtml.push('<input type="hidden" id="khhdnUrl0708" value="');
strhdnInfoHtml.push(maindata.urlInfo.urlPj0708);
strhdnInfoHtml.push('" >');
$areahdnInfo[0].innerHTML = strhdnInfoHtml.join("");
}
}
return;
}
};
function khDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
