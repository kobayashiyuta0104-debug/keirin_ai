var PJ9110View = {
piDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#tan_div'; 
div_Error = '#tan_err_div'; 
prm_div_Error = 'tan_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
$('div[class*="tanten_ari"] span[class="ui-dialog-title"]').text('短評・展開');
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9110Controller.reqTanpyoTenkai(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9110Controller.reqTanpyoTenkai(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
var bold = null;
$('div[class*="tanten_ari"] span[class="ui-dialog-title"]').text(jsondata.title);
$('#piKeirinjyo').text(jsondata.jyoName); 
$('#piGrade').text(jsondata.gGrade); 
$('#piKaisaihi').text(jsondata.kaisaihi); 
$('#piRaceNo').text(jsondata.raceNo); 
$('#piSyumoku').text(jsondata.syumoku); 
if(jsondata.btnResultFlag == 0){
$('#pibtnResult').addClass('disabled');
}else{
$('#pibtnResult').removeClass('disabled');
$('#pibtnResult').attr('onclick', 'pibtnResultClick("' + jsondata.raceBasicURL + '", "' + 
                                                                         jsondata.encPrm + '")');
}
if(jsondata.btnDigestFlag == 0){
$('#pibtnDigest').addClass('disabled');
}else{
$('#pibtnDigest').removeClass('disabled');
$('#pibtnDigest').attr('onclick', 'pibtnDigestClick("' + jsondata.btnDigestURL + '", "' + 
                                                 jsondata.prmJyoCd + '", "' + 
                                                 jsondata.prmKaisaihi + '", "' + 
                                                 jsondata.raceNo + '")');
}
if(jsondata.dspTanpyoFlg == 0){
$('#pidivBs').css('display', 'none');
$('#pidivTenkai').css('display', 'none');
$('#pidivTeikyo').css('display', 'none');
}else{
var bbody = $('#pitbodyBs');
var tukaColor = null;
var bsTyakui = null;
var bsTuka = null;
bbody.empty();
if(jsondata.tanpyoList){
for(var i = 0; i < jsondata.tanpyoList.length; i++){
var tan = jsondata.tanpyoList[i];
if(tan.bsTuka){
bsTuka = tan.bsTuka;
}else{
bsTuka = '';
}
if(tan.bsTukaColor){
tukaColor = tan.bsTukaColor + " bold";
}else{
tukaColor = "";
}
if(tan.boldFlg == 1){
bold = "bold";
}else{
bold = "";
}
if(tan.tyakui){
bsTyakui = tan.tyakui;
}else{
bsTyakui = '';
}
bbody.append('<tr><td class="al-c">' + bsTyakui + '</td>' + 
 '<td class="al-c ' + tukaColor + '">' + bsTuka + '</td>' +
 '<td class="al-c"><div class="lnum ' + tan.syabanColor + '">' + tan.syaban + '</div></td>' +
 '<td class="al-l spacepadding4 ' + bold + '">' + tan.sensyuName + '</td>' +
 '<td class="al-l spacepadding4">' + tan.tanpyo + '</td>');
}
$('#pidivBs').css('display', '');
}else{
$('#pidivBs').css('display', 'none');
$('#pidivTeikyo').css('display', 'none');
}
if(jsondata.tenkaiList){
var developItem = jsondata.tenkaiList;
$('#piTableTenkaiGoing').html(piMakeTenkaiTable("Going"));
$('#piTableTenkaiBell').html(piMakeTenkaiTable("Bell"));
$('#piTableTenkaiHS').html(piMakeTenkaiTable("HS"));
$('#piTableTenkaiBS').html(piMakeTenkaiTable("BS"));
$('#piTableTenkaiGoal').html(piMakeTenkaiTable("Goal"));
var xCnt = [];
xCnt["Going"] = [];
xCnt["Bell"] = [];
xCnt["HS"] = [];
xCnt["BS"] = [];
xCnt["Goal"] = [];
for(var cKey in xCnt){
for(var i = 0 ; i <= 5; i++){
xCnt[cKey][i] = 0;
}
}
var selectId = "";
var insertHtml = "";
for(var diKey in developItem){
insertHtml = '<p><img style="margin-top:-5px!important" class="imgbadge_s2" src="'+ piDataChecker(developItem[diKey].imgGoingPath) +'" /></p>';
selectId = '#pitdGoing_'+ piDataChecker(developItem[diKey].goingXShaft) +'_'+ piDataChecker(developItem[diKey].goingYShaft);
$(selectId).html(insertHtml);
if(piDataChecker(developItem[diKey].imgGoingPath) != ""){
xCnt["Going"][developItem[diKey].goingXShaft]++;
}
insertHtml = '<p><img style="margin-top:-5px!important" class="imgbadge_s2" src="'+ piDataChecker(developItem[diKey].imgTollBellPath) +'" /></p>';
selectId = '#pitdBell_'+ piDataChecker(developItem[diKey].tollBellXShaft) +'_'+ piDataChecker(developItem[diKey].tollBellYShaft);
$(selectId).html(insertHtml);
if(piDataChecker(developItem[diKey].imgTollBellPath) != ""){
xCnt["Bell"][developItem[diKey].tollBellXShaft]++;
}
insertHtml = '<p><img style="margin-top:-5px!important" class="imgbadge_s2" src="'+ piDataChecker(developItem[diKey].imgHSPath) +'" /></p>';
selectId = '#pitdHS_'+ piDataChecker(developItem[diKey].HSXShaft) +'_'+ piDataChecker(developItem[diKey].HSYShaft);
$(selectId).html(insertHtml);
if(piDataChecker(developItem[diKey].imgHSPath) != ""){
xCnt["HS"][developItem[diKey].HSXShaft]++;
}
insertHtml = '<p><img style="margin-top:-5px!important" class="imgbadge_s2" src="'+  piDataChecker(developItem[diKey].imgBSPath) +'" /></p>';
selectId = '#pitdBS_'+ piDataChecker(developItem[diKey].BSXShaft) +'_'+ piDataChecker(developItem[diKey].BSYShaft);
$(selectId).html(insertHtml);
if(piDataChecker(developItem[diKey].imgBSPath) != ""){
xCnt["BS"][developItem[diKey].BSXShaft]++;
}
insertHtml = '<p><img style="margin-top:-5px!important" class="imgbadge_s2" src="'+  piDataChecker(developItem[diKey].imgGoalPath) +'" /></p>';
selectId = '#pitdGoal_'+ piDataChecker(developItem[diKey].goalXShaft) +'_'+ piDataChecker(developItem[diKey].goalYShaft);
$(selectId).html(insertHtml);
if(piDataChecker(developItem[diKey].imgGoalPath) != ""){
xCnt["Goal"][developItem[diKey].goalXShaft]++;
}
if(diKey == 0 && piDataChecker(developItem[diKey].tenkaiMei) != ""){
var mei = 'ＢＳ通過順位・短評・レース展開　情報提供：';
$('#pipTeikyo').html(mei + developItem[diKey].tenkaiMei);
}
}
for(var tKey in xCnt){
for(var i = 1 ; i <= 5; i++){
if(xCnt[tKey][i] == 0){
$('#pitr'+ tKey +'_' + i).css('display', 'none');
} else {
$('#pitr'+ tKey +'_' + i).css('display', '');
}
}
}
$('#pidivTenkai').css('display', '');
$('#pidivTeikyo').css('display', '');
}else{
$('#pidivTenkai').css('display', 'none');
}
}
if(jsondata.dspTanpyoFlg == 1 && jsondata.raceRvFlg == 1){
$('#pipSyabanTitle').text('■車番');
}else{
$('#pipSyabanTitle').text('■着順');
}
var stable = $('#pitableSyaban');
stable.empty();
if(jsondata.raceRvFlg == 0 || jsondata.raceTyusiFlag == 1){
$('#pitableSyaban').css('display', 'none');
$('#piSyabanComment').css('display', 'none');
}else if(jsondata.haraiRvFlg == 1 || jsondata.raceRvFlg == 1){
$('#pitableSyaban').css('display', '');
$('#piSyabanComment').css('display', '');
if(jsondata.dspTanpyoFlg == 0){
stable.append('<thead><tr><th>着</th><th>車番</th><th>選手名</th><th>府県</th></tr></thead>');
}else{
stable.append('<thead><tr><th>車番</th><th>選手名</th><th>府県</th></tr></thead>');
}
var sbody = $('<tbody />');
for(var i = 0; i < jsondata.syabanList.length; i++){
var syaban = jsondata.syabanList[i];
var syabantr = $('<tr class="' + syaban.syabanBgColor + '" />');
if(jsondata.dspTanpyoFlg == 0){
if(syaban.tyakui){
syabantr.append('<td class="al-c">' + syaban.tyakui + '</td>');
}else{
syabantr.append('<td class="al-c">&nbsp;</td>');
}
}
if(jsondata.dspTanpyoFlg == 1 && jsondata.raceRvFlg == 1){
syabantr.append('<td  class="' + syaban.syabanColor + '"><p class="al-c">' + syaban.syaban + '</p></td>');
}else{
syabantr.append('<td  class="al-c"><div class="lnum ' + syaban.syabanColor + '">' + syaban.syaban + '</div></td>');
}
if(syaban.boldFlg == 1){
bold = "bold";
}else{
bold = "";
}
syabantr.append('<td class="al-l spacepadding4 ' + bold + '">' + syaban.sensyuName + '</td>');
syabantr.append('<td class="al-c">' + syaban.huken + '</td>');
sbody.append(syabantr);
}
stable.append(sbody);
$('#pidivSyaban').css('display', '');
if(jsondata.konGuideDispFlag == 1){
$('#piSyabanComment').css('display', '');
} else {
$('#piSyabanComment').css('display', 'none');
}
}else{
$('#pidivSyaban').css('display', 'none');
}
var hgWkTrHtml = "";
if(jsondata.haraiRvFlg == 1 && jsondata.haraiInfo){
var haraiGakuInfo = jsondata.haraiInfo;
var kbn = 0;
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.WH2HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.WT2HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.SH2HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.ST2HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.RH3HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.RT3HaraiGakuDispItemSubData);
hgWkTrHtml += edtHaraiInfo(kbn++, haraiGakuInfo.WHaraiGakuDispItemSubData);
if(haraiGakuInfo.APartReturnDispFlg){
hgWkTrHtml += '<tr><td colspan="8" class="nb-t al-c clearfix v-al-m">'+ piDataChecker(haraiGakuInfo.APartReturn) +'</td></tr>';
}
$('#pitbodyHarai').html(hgWkTrHtml);
$('#pitbodyHarai').css('display', '');
}else if(jsondata.raceRvFlg == 1){
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">2枠複</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">2枠単</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">2車複</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">2車単</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">3連複</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">3連単</th><td style="width: 230px;">&nbsp;</td></tr>';
hgWkTrHtml　+= '<tr><th class="al-l" style="width: 60px;">ワイド</th><td style="width: 230px;">&nbsp;</td></tr>';
$('#pitbodyHarai').html(hgWkTrHtml);
$('#pidivHarai').css('display', '');
}else{
$('#pidivHarai').css('display', 'none');
}
if(jsondata.biko){
$('#pilblBiko').html(jsondata.biko);
$('#pidivBiko').css('display', '');
}else{
$('#pidivBiko').css('display', 'none');
}
}
return;
},
};
function piDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function piMakeTenkaiTable(idName){
var retBodyHtml = "";
for(var xLoop = 5 ; xLoop >= 1; xLoop--){
retBodyHtml += '<tr id="pitr'+ idName +'_'+ xLoop +'">';
for(var yLoop = 1 ; yLoop <= 14; yLoop++){
retBodyHtml += '<td id="pitd'+ idName +'_'+ xLoop +'_'+ yLoop +'" colspan="2" class="al-c">&nbsp;</td>';
}
retBodyHtml += '</tr>';
}
return retBodyHtml;
}
function edtHaraiInfo(kbn, harai){
var kakesiki = ['2枠複', '2枠単', '2車複', '2車単', '3連複', '3連単', 'ワイド'];
var ret = "";
var en = "";
ret += '<tr>';
ret += '<th class="al-l" style="width: 60px;" rowspan="' + harai.length + '">' + kakesiki[kbn] + '</th>';
for(var haraiCnt = 0; haraiCnt < harai.length; haraiCnt++){
if(haraiCnt != 0){
ret += '<tr>';
}
if(harai[haraiCnt].ninkiDispFlg){
en = '円';
}else{
en = '';
}
ret += '<td class="al-l spacepadding4" style="width: 65px;">';
ret += piDataChecker(harai[haraiCnt].kumiBan);
ret += '</td>';
ret += '<td style="width: 115px;" class="nb-r al-r">';
ret += piDataChecker(harai[haraiCnt].haraiGaku) + en;
ret += '</td>';
ret += '<td style="width: 50px; padding-right: 4px;" class="nb-l al-r">';
ret += piDataChecker(harai[haraiCnt].ninki);
ret += '</td>';
ret += '</tr>';
}
return ret;
}
