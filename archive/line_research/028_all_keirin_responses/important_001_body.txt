function rbSensyuNameClick(sensyuRegistNo) {
rbMoveSensyu(sensyuRegistNo);
}
function rbMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rbUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_blank"
);
}
function rbHeikinTokutenClick(sensyuRegistNo) {
ptInitialize(hhGetEncSelR(), sensyuRegistNo);
}
function rbKimariteClick(sensyuRegistNo) {
pwInitialize(hhGetEncSelR(), sensyuRegistNo, 1);
}
function rbBackHomeClick(sensyuRegistNo) {
pbhInitialize(hhGetEncSelR(), sensyuRegistNo, 1);
}
function rbStandingClick(sensyuRegistNo) {
pscInitialize(hhGetEncSelR(), sensyuRegistNo, 1);
}
function rbSyourituClick(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 1, 1);
}
function rbRentairitu2Click(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 2, 1);
}
function rbRentairitu3Click(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 3, 1);
}
function rbTyoJyoGradeClick(para) {
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rbMoveRaceProgram(para);
return;
});
} else {
comKaime.kimClear();
rbMoveRaceProgram(para);
return;
}
}
function rbMoveRaceProgram(para) {
commonSubmit.formPost(
$('#rbUrlRaceProgram').val()
, {"disp": "PJ0301", "encp": para}
, "_self"
);
}
function rbTyokinResultClick(para) {
piInitialize(para);
}
var rbController = {
    JSON_REQ_ID: "JSJ006",
    rbCreateList: function( params) {
        Com.getRequestGet(rbController.JSON_REQ_ID, params)
            .done(function(result) {
            rbView.rbDrawJSONData(result, params);
            });
    }
};
var rbView = {
HDNKEY_ID: 'ppj0315',
rbDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rbdivRaceBaseInfo').addClass('dispoff');
$('#rbdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rbdivErrorRaceInfo"
, ""
, params
, function(arg0){
rbController.rbCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rbdivRaceBaseInfo').addClass('dispoff');
$('#rbdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rbdivErrorRaceInfo"
, rbDataChecker(maindata.message)
, params
, function(arg0){
rbController.rbCreateList(arg0);
}
);
} else {
$('#rbdivErrorRaceInfo').addClass('dispoff');
if(rbDataChecker(maindata.syusouInfoExistFlg) == "0" || maindata.syusouInfoExistFlg == undefined){
$('#rbdivRaceBaseInfo').addClass('dispoff');
}else{
$('#rbdivRaceBaseInfo').removeClass('dispoff');
var leftHtml = "";
var rightHtml = "";
var yudoYosoHtml = "";
var sensyuTypeInfoList = maindata.sensyuTypeInfo;
var sensyuTypeInfoListCnt = sensyuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
var ht1stList = rbDataChecker(maindata.raceResult1Syaban).split(",");
var ht2ndList = rbDataChecker(maindata.raceResult2Syaban).split(",");
var bc1stList = rbDataChecker(maindata.backCnt1Syaban).split(",");
var bc2ndList = rbDataChecker(maindata.backCnt2Syaban).split(",");
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="rbLeftItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != rbDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == rbDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("rblblWakuban"+ rbDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = rbDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rblblWakuban' + rbDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rbDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
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
$('#rbTableLeftBody').html(leftHtml);
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
tokuColorClass = maindata.charColor1;
}
}
for(var toku2Loop = 0 ; toku2Loop < ht2ndList.length; toku2Loop++){
if(ht2ndList[toku2Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
tokuColorClass = maindata.charColor2;
}
}
var backColorClass = "";
for(var back1Loop = 0 ; back1Loop < bc1stList.length; back1Loop++){
if(bc1stList[back1Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
backColorClass = maindata.charColor1;
}
}
for(var toku2Loop = 0 ; toku2Loop < bc2ndList.length; toku2Loop++){
if(bc2ndList[toku2Loop] == rbDataChecker(sensyuTypeInfo.syaban)){
backColorClass = maindata.charColor2;
}
}
rightHtml += '<tr id="rbRightItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '_1" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
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
rightHtml += '          <td class="al-c clc nb-a cb-r chaku_type1" style="padding:0;width: 32%;" onclick="rbSyourituClick(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.syouritu) + '</span></p></td>';
rightHtml += '          <td class="al-c clc nb-a cb-r chaku_type2" style="padding:0;width: 34%;"onclick="rbRentairitu2Click(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.rentairitu2) + '</span></p></td>';
rightHtml += '          <td class="al-c clc nb-a chaku_type3" style="padding:0;width: 34%;"onclick="rbRentairitu3Click(\'' + rbDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p><span class="bold">' + rbDataChecker(sensyuTypeInfo.rentairitu3) + '</span></p></td>';
rightHtml += '        </tr>';
rightHtml += '      </tbody>';
rightHtml += '    </table>';
rightHtml += '  </td>';
if(tyo4Info == undefined){
rightHtml += '<td class="race_body_height_half" style="padding:0;width: 9%;"><p><span><a href="javascript:void(0);">&nbsp;</a></span></p></td>';
rightHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">&nbsp;</td>';
}else{
rightHtml += '<td class="race_body_height_half" style="padding:0;width: 9%;"><p><span><a href="javascript:void(0);" onclick="rbTyoJyoGradeClick(\'' + rbDataChecker(tyo4Info.kkParameter) + '\');" class="txt_underline">' + rbDataChecker(tyo4Info.kerinjyoName) + rbDataChecker(tyo4Info.gaiTeiGrade) + '</a></span></p></td>';
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
rightHtml += '<img width="16" height="26" alt="' + rbDataChecker(sensyuTypeInfo.imgTyosiName) + '" src="' + rbDataChecker(sensyuTypeInfo.imgTyosiPath) + '"/>';
}
rightHtml += '  </td>';
rightHtml += '</tr>';
rightHtml += '<tr id="rbRightItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '_2" class="' + rbDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if(konResultInfo == undefined){
rightHtml += '<td class="race_body_height_half"><p><span>&nbsp;</span></p></td>';
rightHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">&nbsp;</td>';
}else{
rightHtml += '<td class="race_body_height_half"><p><span>' + rbDataChecker(konResultInfo.gaiTeiGrade) + '</span></p></td>';
rightHtml += rbMakeTyoResult(konResultInfo.resultInfoSubData);
}
rightHtml += '</tr>';
}
$('#rbTableRightBody').html(rightHtml);
for(var heightLoop = 0 ; heightLoop < sensyuTypeInfoListCnt; heightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[heightLoop];
var no = rbDataChecker(sensyuTypeInfo.syaban);
var rtotalHeight1 = $('#rbRightItem_' + no + '_1').height();
var rtotalHeight2 = $('#rbRightItem_' + no + '_2').height();
var totalHeight = rtotalHeight1 + rtotalHeight2;
$('#rbLeftItem_' + no).height(totalHeight);
$('#rbRightItem_' + no + '_1').height(rtotalHeight1);
$('#rbRightItem_' + no + '_2').height(rtotalHeight2);
}
yudoYosoHtml += '<div class="dispon" style="margin-top: 16px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rbDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rbDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rbDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#rbYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function rbDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function rbMakeTyoResult(resultInfo) {
var retHtml = "";
var resultInfoCnt = resultInfo.length;
var trLoopCnt = 0;
var strClass = "al-l nb-a nb-l";
var strStyle = "padding:0;width: 25%;";
if(resultInfoCnt > 0){
trLoopCnt = Math.floor((resultInfoCnt - 1) / 4) + 1;
}
retHtml += '<td class="race_body_height_half" colspan="4" style="padding:0;">';
retHtml += '  <table class="nb-a" style="width: 100%;height: 100%">';
for(var trLoop = 0 ; trLoop < trLoopCnt; trLoop++){
retHtml += '<tr>';
var tyoMaxCnt = resultInfoCnt - (trLoop * 4);
if(tyoMaxCnt > 4){
tyoMaxCnt = 4;
}
for(var tyoLoop = 0 ; tyoLoop < tyoMaxCnt; tyoLoop++){
var resultListIndex = tyoLoop + (trLoop * 4);
if(rbDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rbDataChecker(resultInfo[resultListIndex].imgTyakuiName) == ""){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'"><p></p>';
} else if(rbDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rbDataChecker(resultInfo[resultListIndex].imgTyakuiName) != ""){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'font-size: 16px;">';
retHtml += rbDataChecker(resultInfo[resultListIndex].imgTyakuiName);
} else if(rbDataChecker(resultInfo[resultListIndex].kkrParameter) == ""){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'">';
retHtml += '<p class="imgbadge_s3" style="background-image:url(' + rbDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;"></p>';
} else {
retHtml += '<td class="clc '+ strClass +'" style="'+ strStyle +'" onclick="rbTyokinResultClick(\''+ rbDataChecker(resultInfo[resultListIndex].kkrParameter) + '\');">';
retHtml += '<p class="imgbadge_s3" style="background-image:url(' + rbDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;"></p>';
if(rbDataChecker(resultInfo[resultListIndex].backTori) == "1"){
retHtml += '<p class="imgbadge_s3_B">B</p>';
}
}
retHtml += '</td>';
}
var nonMaxCnt = 4 - tyoMaxCnt;
for(var nonLoop = 0 ; nonLoop < nonMaxCnt; nonLoop++){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'"><p></p></td>';
}
retHtml += '</tr>';
}
retHtml += '  </table>';
retHtml += '</td>';
return retHtml;
}
function rbEmptyTo3Space(str) {
var ret;
if(rbDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function rlSensyuNameClick(sensyuRegistNo) {
    rlMoveSensyu(sensyuRegistNo);
}
function rlMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rlUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_self"
);
}
function rlTyoKaisaiClick(para) {
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rlMoveRaceProgram(para);
return;
});
} else {
comKaime.kimClear();
rlMoveRaceProgram(para);
return;
}
}
function rlMoveRaceProgram(para) {
commonSubmit.formPost(
$('#rlUrlRaceProgram').val()
, {"disp": "PJ0301", "encp": para}
, "_self"
);
}
function rlTyokinResultClick(para) {
piInitialize(para);
}
var rlController = {
    JSON_REQ_ID: "JSJ007",
    rlCreateList: function( params) {
        Com.getRequestGet(rlController.JSON_REQ_ID, params)
            .done(function(result) {
            rlView.rlDrawJSONData(result, params);
            });
    }
};
var rlView = {
HDNKEY_ID: 'ppj0316',
rlDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rldivRaceTyoResultInfo').addClass('dispoff');
$('#rldivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rldivErrorRaceInfo"
, ""
, params
, function(arg0){
rlController.rlCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rldivRaceTyoResultInfo').addClass('dispoff');
$('#rldivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rldivErrorRaceInfo"
, rlDataChecker(maindata.message)
, params
, function(arg0){
rlController.rlCreateList(arg0);
}
);
} else {
$('#rldivErrorRaceInfo').addClass('dispoff');
if(rlDataChecker(maindata.syusouInfoExistFlg) == "0"){
$('#rldivRaceTyoResultInfo').addClass('dispoff');
}else{
$('#rldivRaceTyoResultInfo').removeClass('dispoff');
var leftHtml = "";
var rightHead = "";
var rightBody = "";
var yudoYosoHtml = "";
var sensyuTypeInfoList = maindata.sensyuTypeInfo;
var sensyuTypeInfoListCnt = sensyuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="rlLeftItem_' + rlDataChecker(sensyuTypeInfo.syaban) + '" class="' + rlDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != rlDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == rlDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("rllblWakuban"+ rlDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = rlDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rllblWakuban' + rlDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rlDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + rlDataChecker(sensyuTypeInfo.yosoin) + '</td>';
leftHtml += '<td class="' + rlDataChecker(sensyuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '<p class="al-c"><span class="al-c">' + rlDataChecker(sensyuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '<td class="al-l">';
leftHtml += '<p><span class="bold">' + rlDataChecker(sensyuTypeInfo.sensyuName) + '</span><span class="' + rlDataChecker(sensyuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + rlDataChecker(sensyuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '<p><span>' + rlDataChecker(sensyuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + rlEmptyTo3Space(sensyuTypeInfo.prevKyuhan) + '</span><span class="' + rlDataChecker(sensyuTypeInfo.kyuhanSpecialColor) + '">' + rlDataChecker(sensyuTypeInfo.kyuhan) + '</span><span>/</span><span>' + rlDataChecker(sensyuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '<td class="wb-r clearfix">';
leftHtml += '<table style="width: 100%; height: 100%;">';
leftHtml += '<tbody>';
leftHtml += '<tr>';
leftHtml += '<td class="nb-r nb-t nb-l period_data">';
leftHtml += '<p class="al-c"><span>' + rlDataChecker(sensyuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '</tr>';
leftHtml += '<tr>';
leftHtml += '<td class="nb-r nb-b nb-l age_data">';
leftHtml += '<p class="al-c"><span>' + rlDataChecker(sensyuTypeInfo.age) + '</span></p></td>';
leftHtml += '</tr>';
leftHtml += '</tbody>';
leftHtml += '</table>';
leftHtml += '</td>';
leftHtml += '</tr>';
}
$('#rlTableLeftBody').html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
var tyoResultHeadCnt = parseInt(maindata.tyoResultCnt) + 1;
rightHead += '<tr id="rlRightHeader_1">';
rightHead += '  <td class="race_header_height1 al-l clc last_td2" colspan="'+ tyoResultHeadCnt +'" onclick="tableHeaderClick(\'PY0105\');">';
rightHead += '<p style="padding-left: 300px;">直近の成績</p></td>';
rightHead += '</tr>';
rightHead += '<tr id="rlRightHeader_2">';
for(var rheadLoop = 0 ; rheadLoop < tyoResultHeadCnt; rheadLoop++){
var chromeTdLast = "";
if(rheadLoop == (tyoResultHeadCnt - 1)){chromeTdLast = "last_td2";}
rightHead += '<td class="race_header_height2 tbl_header2 al-c '+ chromeTdLast +'"><p><span>';
if(rheadLoop == 0){
rightHead += '今回';
} else {
rightHead += '直近' + rheadLoop;
}
rightHead += '</span></p></td>';
}
rightHead += '</tr>';
$('#rlTableRightHead').html(rightHead);
var tyoResultBodyCnt = parseInt(maindata.tyoResultCnt);
for(var rBodyLoop = 0 ; rBodyLoop < sensyuTypeInfoListCnt; rBodyLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rBodyLoop];
rightBody += '<tr id="rlRightItem_' + rlDataChecker(sensyuTypeInfo.syaban) + '" class="' + rlDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
for(var rResultLoop = 0 ; rResultLoop < tyoResultHeadCnt; rResultLoop++){
var konTyoResultInfo = "";
if(rResultLoop == 0){
konTyoResultInfo = sensyuTypeInfo.konResultInfoSubData;
}else{
konTyoResultInfo = sensyuTypeInfo.tyoInfoSubData[rResultLoop - 1];
}
var chromeTdLast = "";
if(rResultLoop == (tyoResultHeadCnt - 1)){chromeTdLast = "last_td2";}
rightBody += '<td class="outertd2 '+ chromeTdLast +' ">';
rightBody += '  <p class="clearfix">';
if(konTyoResultInfo == undefined){
rightBody += '<span class="fl-l">&nbsp;</span>';
rightBody += '<span class="fl-r">';
rightBody += '  <a href="javascript:void(0);" class="al-r">&nbsp;</a>';
rightBody += '</span>';
} else {
rightBody += '<span class="fl-l">' + rlDataChecker(konTyoResultInfo.kaisaiFirst) + '</span>';
rightBody += '<span class="fl-r">';
rightBody += '  <a href="javascript:void(0);" onclick="rlTyoKaisaiClick(\''+ rlDataChecker(konTyoResultInfo.kkParameter) + '\');" class="al-r txt_underline">';
rightBody += rlDataChecker(konTyoResultInfo.kerinjyoName) + rlDataChecker(konTyoResultInfo.gaiTeiGrade) + '</a>';
rightBody += '  </a>';
rightBody += '</span>';
}
rightBody += '  </p>';
rightBody += '  <table class="clear-fix" style="width: 136px;">';
rightBody += '    <tbody>';
if(konTyoResultInfo == undefined){
rightBody += '<tr>';
rightBody += '<td class="fl-l" colspan="4" style="padding-top: 5px;"><p>&nbsp;</p></td>';
rightBody += '</tr>';
} else if(rlDataChecker(konTyoResultInfo.msg) != ""){
rightBody += '<tr>';
rightBody += '<td class="fl-l" colspan="4" style="padding-top: 5px;width: 136px;"><p>'+ rlDataChecker(konTyoResultInfo.msg) +'</p></td>';
rightBody += '</tr>';
}else {
rightBody += rlMakeTyoResult(konTyoResultInfo.resultInfoSubData);
}
rightBody += '    </tbody>';
rightBody += '  </table>';
rightBody += '</td>';
}
rightBody += '</tr>';
}
$('#rlTableRightBody').html(rightBody);
for(var heightLoop = 0 ; heightLoop < sensyuTypeInfoListCnt; heightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[heightLoop];
var no = rlDataChecker(sensyuTypeInfo.syaban);
var totalHeight = $('#rlRightItem_' + no).height();
$('#rlLeftItem_' + no).height(totalHeight);
$('#rlRightItem_' + no).height(totalHeight);
}
yudoYosoHtml += '<div class="dispon" style="margin-top: 7px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rlDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rlDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rlDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#rlYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function rlDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function rlMakeTyoResult(resultInfo) {
var retHtml = "";
var resultInfoCnt = resultInfo.length;
var trLoopCnt = 0;
if(resultInfoCnt > 0){
trLoopCnt = Math.floor((resultInfoCnt - 1) / 4) + 1;
}
for(var trLoop = 0 ; trLoop < trLoopCnt; trLoop++){
retHtml += '<tr>';
var tyoMaxCnt = resultInfoCnt - (trLoop * 4);
if(tyoMaxCnt > 4){
tyoMaxCnt = 4;
}
for(var tyoLoop = 0 ; tyoLoop < tyoMaxCnt; tyoLoop++){
var resultListIndex = tyoLoop + (trLoop * 4);
if(rlDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rlDataChecker(resultInfo[resultListIndex].imgTyakuiName) == ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;"><p>&nbsp;</p>';
} else if(rlDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rlDataChecker(resultInfo[resultListIndex].imgTyakuiName) != ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;font-size: 16px;">';
retHtml += rlDataChecker(resultInfo[resultListIndex].imgTyakuiName);
} else if(rlDataChecker(resultInfo[resultListIndex].kkrParameter) == ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;">';
retHtml += '<p class="imgbadge_s4" style="background-image:url(' + rlDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;"></p>';
} else {
retHtml += '<td class="fl-l clc" style="padding-top: 5px;" onclick="rlTyokinResultClick(\''+ rlDataChecker(resultInfo[resultListIndex].kkrParameter) +'\');">';
retHtml += '<p class="imgbadge_s4" style="background-image:url(' + rlDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;">&nbsp;</p>';
if(rlDataChecker(resultInfo[resultListIndex].backTori) == "1"){
retHtml += '<p class="imgbadge_s4_B">B</p>';
}
}
retHtml += '</td>';
}
var nonMaxCnt = 4 - tyoMaxCnt;
for(var nonLoop = 0 ; nonLoop < nonMaxCnt; nonLoop++){
retHtml += '<td class="fl-l"><p>&nbsp;</p></td>';
}
retHtml += '</tr>';
}
return retHtml;
}
function rlEmptyTo3Space(str) {
var ret;
if(rlDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function rwSensyuNameClick(sensyuRegistNo) {
rwMoveSensyu(sensyuRegistNo);
}
function rwMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rwUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_self"
);
}
function rwWinLossRecordsClick(sensyuRegistNo, rivalRegistNo) {
psInitialize( hhGetEncSelR(), sensyuRegistNo, rivalRegistNo);
}
var rwController = {
    JSON_REQ_ID: "JSJ008",
    rwCreateList: function( params) {
        Com.getRequestGet(rwController.JSON_REQ_ID, params)
            .done(function(result) {
            rwView.rwDrawJSONData(result, params);
            });
    }
};
var rwView = {
HDNKEY_ID: 'ppj0317',
rwDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rwdivRaceTaisenInfo').addClass('dispoff');
$('#rwdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rwdivErrorRaceInfo"
, ""
, params
, function(arg0){
rwController.rwCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rwdivRaceTaisenInfo').addClass('dispoff');
$('#rwdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rwdivErrorRaceInfo"
, rwDataChecker(maindata.message)
, params
, function(arg0){
rwController.rwCreateList(arg0);
}
);
} else {
$('#rwdivErrorRaceInfo').addClass('dispoff');
if(rwDataChecker(maindata.syusouInfoExistFlg) == "0"){
$('#rwdivRaceTaisenInfo').addClass('dispoff');
}else{
$('#rwdivRaceTaisenInfo').removeClass('dispoff');
var leftHtml = "";
var rightHead = "";
var rightBody = "";
var yudoYosoHtml = "";
var sensyuTypeInfoList = maindata.sensyuTypeInfo;
var sensyuTypeInfoListCnt = sensyuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="rwLeftItem_' + rwDataChecker(sensyuTypeInfo.syaban) + '" class="' + rwDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != rwDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == rwDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("rwlblWakuban"+ rwDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = rwDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rwlblWakuban' + rwDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rwDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + rwDataChecker(sensyuTypeInfo.yosoin) + '</td>';
leftHtml += '  <td class="' + rwDataChecker(sensyuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '    <p class="al-c"><span class="al-c">' + rwDataChecker(sensyuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '  <td class="al-l">';
leftHtml += '    <p><span class="bold">' + rwDataChecker(sensyuTypeInfo.sensyuName) + '</span><span class="' + rwDataChecker(sensyuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + rwDataChecker(sensyuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '    <p><span>' + rwDataChecker(sensyuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + rwEmptyTo3Space(sensyuTypeInfo.prevKyuhan) + '</span><span class="' + rwDataChecker(sensyuTypeInfo.kyuhanSpecialColor) + '">' + rwDataChecker(sensyuTypeInfo.kyuhan) + '</span><span>/</span><span>' + rwDataChecker(sensyuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '  <td class="wb-r clearfix">';
leftHtml += '    <table style="width: 100%; height: 100%;">';
leftHtml += '      <tbody>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-t nb-l period_data">';
leftHtml += '            <p class="al-c"><span>' + rwDataChecker(sensyuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-b nb-l age_data">';
leftHtml += '            <p class="al-c"><span>' + rwDataChecker(sensyuTypeInfo.age) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '      </tbody>';
leftHtml += '    </table>';
leftHtml += '  </td>';
leftHtml += '</tr>';
}
$('#rwTableLeftBody').html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
rightHead += '<td class="tbl_header2 al-c wb-r race_header_height2"><p><span>総合</span></p></td>';
for(var rHeadLoop = 0 ; rHeadLoop < sensyuTypeInfoListCnt; rHeadLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rHeadLoop];
rightHead += '<td class="tbl_header2 al-c"><p><span>' + rwDataChecker(sensyuTypeInfo.rivalSensyuName) + '</span></p></td>';
}
$('#rwRightHeader_2').html(rightHead);
var taisenWidth = 100 / (sensyuTypeInfoListCnt + 1);
for(var rBodyLoop = 0 ; rBodyLoop < sensyuTypeInfoListCnt; rBodyLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rBodyLoop];
var taisenInfo = sensyuTypeInfo.taisenSubData;
rightBody += '<tr class="' + rwDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
rightBody += '  <td class="wb-r bold" style="width:'+ taisenWidth +'%;"><p>' + rwDataChecker(taisenInfo.taisenTotal) + '</td>';
for(var rTaiLoop = 1 ; rTaiLoop <= sensyuTypeInfoListCnt; rTaiLoop++){
var rivalInfo = sensyuTypeInfoList[rTaiLoop - 1];
if(taisenInfo["taisen" + rTaiLoop + "EventFlg"] == "true"){
rightBody += '<td style="width:'+ taisenWidth +'%;" class="clc bold" onclick="rwWinLossRecordsClick(\'' + sensyuTypeInfo.sensyuRegistNo + '\',\''+ rivalInfo.sensyuRegistNo + '\');"><p>' + rwDataChecker(taisenInfo["taisen" + rTaiLoop +"Syaban"]) + '</p></td>';
} else {
rightBody += '<td style="width:'+ taisenWidth +'%;"><p>' + rwDataChecker(taisenInfo["taisen" + rTaiLoop +"Syaban"]) + '</p></td>';
}
}
rightBody += '</tr>';
}
$('#rwTableRightBody').html(rightBody);
yudoYosoHtml += '<div class="dispon" style="margin-top: 16px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rwDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rwDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rwDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#rwYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function rwDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = $.trim(str);
}
return ret;
}
function rwEmptyTo3Space(str) {
var ret;
if(rwDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function rsSensyuNameClick(sensyuRegistNo) {
rsMoveSensyu(sensyuRegistNo);
}
function rsMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rsUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_self"
);
}
function rsKimariteClick(sensyuRegistNo) {
pwInitialize(hhGetEncSelR(), sensyuRegistNo, 4);
}
function rsBackHomeClick(sensyuRegistNo) {
pbhInitialize(hhGetEncSelR(), sensyuRegistNo, 4);
}
function rsStandingClick(sensyuRegistNo) {
pscInitialize(hhGetEncSelR(), sensyuRegistNo, 4);
}
function rsSyourituClick(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 1, 4);
}
function rsRentairitu2Click(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 2, 4);
}
function rsRentairitu3Click(sensyuRegistNo) {
phInitialize(hhGetEncSelR(), sensyuRegistNo, 3, 4);
}
function rsWakunai1Click(sensyuRegistNo) {
p1wInitialize(hhGetEncSelR(), sensyuRegistNo, "4");
}
function rsWakunai2Click(sensyuRegistNo) {
p2wInitialize(hhGetEncSelR(), sensyuRegistNo, "4");
}
function rsTyokinResultClick(para) {
piInitialize(para);
}
var rsController = {
    JSON_REQ_ID: "JSJ009",
    rsCreateList: function( params) {
        Com.getRequestGet(rsController.JSON_REQ_ID, params)
            .done(function(result) {
            rsView.rsDrawJSONData(result, params);
            });
    }
};
var rsView = {
HDNKEY_ID: 'ppj0318',
rsDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rsdivRaceSyumokuInfo').addClass('dispoff');
$('#rsdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rsdivErrorRaceInfo"
, ""
, params
, function(arg0){
rsController.rsCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rsdivRaceSyumokuInfo').addClass('dispoff');
$('#rsdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rsdivErrorRaceInfo"
, rsDataChecker(maindata.message)
, params
, function(arg0){
rsController.rsCreateList(arg0);
}
);
} else {
$('#rsdivErrorRaceInfo').addClass('dispoff');
if(rsDataChecker(maindata.syusouInfoExistFlg) == "0"){
$('#rsdivRaceSyumokuInfo').addClass('dispoff');
}else{
$('#rsdivRaceSyumokuInfo').removeClass('dispoff');
var leftHtml = "";
var rightHtml = "";
var yudoYosoHtml = "";
var syumokuTypeInfoList = maindata.syumokuTypeInfo;
var syumokuTypeInfoListCnt = syumokuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
for(var leftLoop = 0 ; leftLoop < syumokuTypeInfoListCnt; leftLoop++){
var syumokuTypeInfo = syumokuTypeInfoList[leftLoop];
leftHtml += '<tr id="rsLeftItem_' + rsDataChecker(syumokuTypeInfo.syaban) + '" class="' + rsDataChecker(syumokuTypeInfo.syabanBgColorInfo) + '">';
if("" != rsDataChecker(syumokuTypeInfo.wakuban) && wakuCheck == rsDataChecker(syumokuTypeInfo.wakuban)){
wakuIdList.push("rslblWakuban"+ rsDataChecker(syumokuTypeInfo.wakuban));
}else{
wakuCheck = rsDataChecker(syumokuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rslblWakuban' + rsDataChecker(syumokuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rsDataChecker(syumokuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + rsDataChecker(syumokuTypeInfo.yosoin) + '</td>';
leftHtml += '  <td class="' + rsDataChecker(syumokuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '    <p class="al-c"><span class="al-c">' + rsDataChecker(syumokuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '  <td class="al-l">';
leftHtml += '    <p><span class="bold">' + rsDataChecker(syumokuTypeInfo.sensyuName) + '</span><span class="' + rsDataChecker(syumokuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + rsDataChecker(syumokuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + rsEmptyTo3Space(syumokuTypeInfo.prevKyuhan) + '</span><span class="' + rsDataChecker(syumokuTypeInfo.kyuhanSpecialColor) + '">' + rsDataChecker(syumokuTypeInfo.kyuhan) + '</span><span>/</span><span>' + rsDataChecker(syumokuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '  <td class="wb-r clearfix">';
leftHtml += '    <table style="width: 100%; height: 100%;">';
leftHtml += '      <tbody>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-t nb-l period_data">';
leftHtml += '            <p class="al-c"><span>' + rsDataChecker(syumokuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-b nb-l age_data">';
leftHtml += '            <p class="al-c"><span>' + rsDataChecker(syumokuTypeInfo.age) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '      </tbody>';
leftHtml += '    </table>';
leftHtml += '  </td>';
leftHtml += '</tr>';
}
$('#rsTableLeftBody').html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
for(var rightLoop = 0 ; rightLoop < syumokuTypeInfoListCnt; rightLoop++){
var syumokuTypeInfo = syumokuTypeInfoList[rightLoop];
var resultInfo  = syumokuTypeInfo.resultInfoSubData;
var tokuColorClass;
if(rsDataChecker(syumokuTypeInfo.backCntOrder) == "1" && rsDataChecker(syumokuTypeInfo.backCnt) != "0"){
tokuColorClass = rsDataChecker(maindata.charColor1);
} else if (rsDataChecker(syumokuTypeInfo.backCntOrder) == "2" && rsDataChecker(syumokuTypeInfo.backCnt) != "0"){
tokuColorClass = rsDataChecker(maindata.charColor2);
} else {
tokuColorClass = "";
}
rightHtml += '<tr class="' + rsDataChecker(syumokuTypeInfo.syabanBgColorInfo) + '">';
rightHtml += '  <td class="race_body_height al-c clc bold"  colspan="4" style="padding:0;" onclick="rsKimariteClick(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <table style="width: 100%;height: 100%;table-layout:fixed">';
rightHtml += '      <tr>';
rightHtml += '        <td class="al-c decisive" style="padding:0;width: 25%;"><p><span>' + rsDataChecker(syumokuTypeInfo.nigeCnt) + '</span></p></td>';
rightHtml += '        <td class="al-c decisive" style="padding:0;width: 25%;"><p><span>' + rsDataChecker(syumokuTypeInfo.makuriCnt) + '</span></p></td>';
rightHtml += '        <td class="al-c decisive" style="padding:0;width: 25%;"><p><span>' + rsDataChecker(syumokuTypeInfo.sasiCnt) + '</span></p></td>';
rightHtml += '        <td class="al-c decisive" style="padding:0;width: 25%;"><p><span>' + rsDataChecker(syumokuTypeInfo.markCnt) + '</span></p></td>';
rightHtml += '      </tr>';
rightHtml += '    </table>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc bold"  colspan="2" style="padding:0" onclick="rsBackHomeClick(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <table style="width: 100%;height:100%;table-layout:fixed">';
rightHtml += '      <tr>';
rightHtml += '        <td class="decisive" style="padding:0;width: 50%;">';
rightHtml += '          <p><span class="bold '+ tokuColorClass +'">' + rsDataChecker(syumokuTypeInfo.backCnt) + '</span></p>';
rightHtml += '        </td>';
rightHtml += '        <td class="decisive nb-r" style="padding:0;width: 50%;">';
rightHtml += '          <p><span>' + rsDataChecker(syumokuTypeInfo.homeTori) + '</span></p>';
rightHtml += '        </td>';
rightHtml += '      </tr>';
rightHtml += '    </table>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc wb-r bold stbody" style="padding:0;" onclick="rsStandingClick(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.stTori) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td colspan="3" style="padding:0;" class="wb-l">';
rightHtml += '    <table style="width: 100%;height:100%;table-layout:fixed">';
rightHtml += '      <tr>';
rightHtml += '  <td class="al-c clc bold decisive" style="padding:0;" onclick="rsSyourituClick(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.syouritu) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc bold decisive" style="padding:0;" onclick="rsRentairitu2Click(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.rentairitu2) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc bold nb-a" style="padding:0;" onclick="rsRentairitu3Click(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.rentairitu3) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '      </tr>';
rightHtml += '    </table>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc bold wb-l" style="padding:0;" onclick="rsWakunai1Click(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.cnt1st) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c clc bold" style="padding:0;" onclick="rsWakunai2Click(\'' + rsDataChecker(syumokuTypeInfo.sensyuRegistNo) + '\');">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.cnt2nd) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td class="al-c bold" style="padding:0;">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.cnt3rd) + '</span></p>';
rightHtml += '  </td>';
rightHtml += '  <td class="wb-r al-c bold" style="padding:0;">';
rightHtml += '    <p><span>' + rsDataChecker(syumokuTypeInfo.cntOut) + '</span></p>';
rightHtml += '  </td>';
rightHtml += rsMakeTyoResult(syumokuTypeInfo.resultInfoSubData);
rightHtml += '</tr>';
}
$('#rsTableRightBody').html(rightHtml);
var rs1headHeight = $('#rsRightHeader_1').height();
var rs2headHeight = $('#rsRightHeader_2').height();
var headHeight = (rs1headHeight + rs2headHeight) / 2;
$('#rsLeftHeader_1').height(headHeight);
$('#rsLeftHeader_2').height(headHeight);
$('#rsRightHeader_1').height(rs1headHeight);
$('#rsRightHeader_2').height(rs2headHeight);
yudoYosoHtml += '<div class="dispon" style="margin-top: 16px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rsDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rsDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rsDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#rsYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function rsDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function rsMakeTyoResult(resultInfo) {
var retHtml = "";
var resultInfoCnt = resultInfo.length;
var trLoopCnt = 0;
retHtml += '<td class="" style="padding: 0px;" colspan="5">';
retHtml += '  <table style="width: 100%; height: 100%; table-layout: fixed;">';
retHtml += '    <tbody>';
retHtml += '      <tr>';
var strClass = "al-l nb-a";
var strStyle = "padding:0;width: 20%;";
for(var tyoLoop = 0 ; tyoLoop < resultInfoCnt; tyoLoop++){
if(rsDataChecker(resultInfo[tyoLoop].imgTyakuiPath) == "" &&
rsDataChecker(resultInfo[tyoLoop].imgTyakuiName) == ""){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'"><p></p>';
} else if(rsDataChecker(resultInfo[tyoLoop].imgTyakuiPath) == "" &&
rsDataChecker(resultInfo[tyoLoop].imgTyakuiName) != ""){
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'">';
retHtml += rsDataChecker(resultInfo[tyoLoop].imgTyakuiName);
} else {
retHtml += '<td class="clc '+ strClass +'" style="'+ strStyle +'" onclick="rsTyokinResultClick(\'' + rsDataChecker(resultInfo[tyoLoop].kkrParameter) + '\');">';
retHtml += '<p class="imgbadge_s3" style="background-image:url(' + rsDataChecker(resultInfo[tyoLoop].imgTyakuiPath) + ')!important;"></p>';
if(rsDataChecker(resultInfo[tyoLoop].backTori) == "1"){
retHtml += '<p class="imgbadge_s3_B">B</p>';
}
}
retHtml += '</td>';
}
var nonMaxCnt = 5 - resultInfoCnt;
for(var nonLoop = 0 ; nonLoop < nonMaxCnt; nonLoop++){
strClass = "al-l nb-a";
retHtml += '<td class="'+ strClass +'" style="'+ strStyle +'"><p>&nbsp;</p></td>';
}
retHtml += '      </tr>';
retHtml += '    </tbody>';
retHtml += '  </table>';
retHtml += '</td>';
return retHtml;
}
function rsEmptyTo3Space(str) {
var ret;
if(rsDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function rtSensyuNameClick(sensyuRegistNo) {
rtMoveSensyu(sensyuRegistNo);
}
function rtMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rtUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_self"
);
}
function rtTyoKaisaiClick(para) {
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rtMoveRaceProgram(para);
return;
});
} else {
comKaime.kimClear();
rtMoveRaceProgram(para);
return;
}
}
function rtMoveRaceProgram(para) {
commonSubmit.formPost(
$('#rtUrlRaceProgram').val()
, {"disp": "PJ0301", "encp": para}
, "_self"
);
}
function rtTyokinResultClick(para) {
piInitialize(para);
}
var rtController = {
    JSON_REQ_ID: "JSJ010",
    rtCreateList: function( params) {
        Com.getRequestGet(rtController.JSON_REQ_ID, params)
            .done(function(result) {
            rtView.rtDrawJSONData(result, params);
            });
    }
};
var rtView = {
HDNKEY_ID: 'ppj0319',
rtDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rtdivRaceTyoResultInfo').addClass('dispoff');
$('#rtdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rtdivErrorRaceInfo"
, ""
, params
, function(arg0){
rtController.rtCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rtdivRaceTyoResultInfo').addClass('dispoff');
$('#rtdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rtdivErrorRaceInfo"
, rtDataChecker(maindata.message)
, params
, function(arg0){
rtController.rtCreateList(arg0);
}
);
} else {
$('#rtdivErrorRaceInfo').addClass('dispoff');
if(rtDataChecker(maindata.syusouInfoExistFlg) == "0"){
$('#rtdivRaceTyoResultInfo').addClass('dispoff');
}else{
$('#rtdivRaceTyoResultInfo').removeClass('dispoff');
var leftHtml = "";
var rightHead = "";
var rightBody = "";
var yudoYosoHtml = "";
var sensyuTypeInfoList = maindata.sensyuTypeInfo;
var sensyuTypeInfoListCnt = sensyuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="rtLeftItem_' + rtDataChecker(sensyuTypeInfo.syaban) + '" class="' + rtDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != rtDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == rtDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("rtlblWakuban"+ rtDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = rtDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rtlblWakuban' + rtDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + rtDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + rtDataChecker(sensyuTypeInfo.yosoin) + '</td>';
leftHtml += '<td class="' + rtDataChecker(sensyuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '<p class="al-c"><span class="al-c">' + rtDataChecker(sensyuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '<td class="al-l">';
leftHtml += '<p><span class="bold">' + rtDataChecker(sensyuTypeInfo.sensyuName) + '</span><span class="' + rtDataChecker(sensyuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + rtDataChecker(sensyuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '<p><span>' + rtDataChecker(sensyuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + rtEmptyTo3Space(sensyuTypeInfo.prevKyuhan) + '</span><span class="' + rtDataChecker(sensyuTypeInfo.kyuhanSpecialColor) + '">' + rtDataChecker(sensyuTypeInfo.kyuhan) + '</span><span>/</span><span>' + rtDataChecker(sensyuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '<td class="wb-r clearfix">';
leftHtml += '<table style="width: 100%; height: 100%;">';
leftHtml += '<tbody>';
leftHtml += '<tr>';
leftHtml += '<td class="nb-r nb-t nb-l period_data">';
leftHtml += '<p class="al-c"><span>' + rtDataChecker(sensyuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '</tr>';
leftHtml += '<tr>';
leftHtml += '<td class="nb-r nb-b nb-l age_data">';
leftHtml += '<p class="al-c"><span>' + rtDataChecker(sensyuTypeInfo.age) + '</span></p></td>';
leftHtml += '</tr>';
leftHtml += '</tbody>';
leftHtml += '</table>';
leftHtml += '</td>';
leftHtml += '</tr>';
}
$('#rtTableLeftBody').html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
var tyoResultHeadCnt = parseInt(maindata.tyoResultCnt) + 1;
rightHead += '<tr id="rtRightHeader_1">';
rightHead += '  <td class="race_header_height1 al-l clc last_td2" colspan="'+ tyoResultHeadCnt +'" onclick="tableHeaderClick(\'PY0105\');">';
rightHead += '<p style="padding-left: 300px;">直近の成績</p></td>';
rightHead += '</tr>';
rightHead += '<tr id="rtRightHeader_2">';
for(var rheadLoop = 0 ; rheadLoop < tyoResultHeadCnt; rheadLoop++){
var chromeTdLast = "";
if(rheadLoop == (tyoResultHeadCnt - 1)){chromeTdLast = "last_td2";}
rightHead += '<td class="race_header_height2 tbl_header2 al-c '+ chromeTdLast +'"><p><span>';
if(rheadLoop == 0){
rightHead += '今回';
} else {
rightHead += '直近' + rheadLoop;
}
rightHead += '</span></p></td>';
}
rightHead += '</tr>';
$('#rtTableRightHead').html(rightHead);
var tyoResultBodyCnt = parseInt(maindata.tyoResultCnt);
for(var rBodyLoop = 0 ; rBodyLoop < sensyuTypeInfoListCnt; rBodyLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rBodyLoop];
rightBody += '<tr id="rtRightItem_' + rtDataChecker(sensyuTypeInfo.syaban) + '" class="' + rtDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
for(var rResultLoop = 0 ; rResultLoop < tyoResultHeadCnt; rResultLoop++){
var konTyoResultInfo = "";
if(rResultLoop == 0){
konTyoResultInfo = sensyuTypeInfo.konResultInfoSubData;
}else{
konTyoResultInfo = sensyuTypeInfo.tyoInfoSubData[rResultLoop - 1];
}
var chromeTdLast = "";
if(rResultLoop == (tyoResultHeadCnt - 1)){chromeTdLast = "last_td2";}
rightBody += '<td class="outertd2 '+ chromeTdLast +' ">';
rightBody += '  <p class="clearfix">';
if(konTyoResultInfo == undefined){
rightBody += '<span class="fl-l">&nbsp;</span>';
rightBody += '<span class="fl-r">';
rightBody += '  <a href="javascript:void(0);" class="al-r">&nbsp;</a>';
rightBody += '</span>';
} else {
rightBody += '<span class="fl-l">' + rtDataChecker(konTyoResultInfo.kaisaiFirst) + '</span>';
rightBody += '<span class="fl-r">';
rightBody += '  <a href="javascript:void(0);" onclick="rtTyoKaisaiClick(\''+ rtDataChecker(konTyoResultInfo.kkParameter) + '\');" class="al-r txt_underline">';
rightBody += rtDataChecker(konTyoResultInfo.kerinjyoName) + rtDataChecker(konTyoResultInfo.gaiTeiGrade) + '</a>';
rightBody += '  </a>';
rightBody += '</span>';
}
rightBody += '  </p>';
rightBody += '  <table class="clear-fix" style="width: 136px;">';
rightBody += '    <tbody>';
if(konTyoResultInfo == undefined){
rightBody += '<tr>';
rightBody += '<td class="fl-l" colspan="4" style="padding-top: 5px;"><p>&nbsp;</p></td>';
rightBody += '</tr>';
} else if(rtDataChecker(konTyoResultInfo.msg) != ""){
rightBody += '<tr>';
rightBody += '<td class="fl-l" colspan="4" style="padding-top: 5px;width: 136px;"><p>'+ rtDataChecker(konTyoResultInfo.msg) +'</p></td>';
rightBody += '</tr>';
}else {
rightBody += rtMakeTyoResult(konTyoResultInfo.resultInfoSubData);
}
rightBody += '    </tbody>';
rightBody += '  </table>';
rightBody += '</td>';
}
rightBody += '</tr>';
}
$('#rtTableRightBody').html(rightBody);
for(var heightLoop = 0 ; heightLoop < sensyuTypeInfoListCnt; heightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[heightLoop];
var no = rtDataChecker(sensyuTypeInfo.syaban);
var totalHeight = $('#rtRightItem_' + no).height();
$('#rtLeftItem_' + no).height(totalHeight);
$('#rtRightItem_' + no).height(totalHeight);
}
yudoYosoHtml += '<div class="dispon" style="margin-top: 7px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(rtDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(rtDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
yudoYosoHtml += '        <td class="al-r" style="width: 39%;">&nbsp;</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + rtDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#rtYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function rtDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function rtMakeTyoResult(resultInfo) {
var retHtml = "";
var resultInfoCnt = resultInfo.length;
var trLoopCnt = 0;
if(resultInfoCnt > 0){
trLoopCnt = Math.floor((resultInfoCnt - 1) / 4) + 1;
}
for(var trLoop = 0 ; trLoop < trLoopCnt; trLoop++){
retHtml += '<tr>';
var tyoMaxCnt = resultInfoCnt - (trLoop * 4);
if(tyoMaxCnt > 4){
tyoMaxCnt = 4;
}
for(var tyoLoop = 0 ; tyoLoop < tyoMaxCnt; tyoLoop++){
var resultListIndex = tyoLoop + (trLoop * 4);
if(rtDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rtDataChecker(resultInfo[resultListIndex].imgTyakuiName) == ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;"><p>&nbsp;</p>';
} else if(rtDataChecker(resultInfo[resultListIndex].imgTyakuiPath) == "" &&
rtDataChecker(resultInfo[resultListIndex].imgTyakuiName) != ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;font-size: 16px;">';
retHtml += rtDataChecker(resultInfo[resultListIndex].imgTyakuiName);
} else if(rtDataChecker(resultInfo[resultListIndex].kkrParameter) == ""){
retHtml += '<td class="fl-l" style="padding-top: 5px;">';
retHtml += '<p class="imgbadge_s4" style="background-image:url(' + rtDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;"></p>';
} else {
retHtml += '<td class="fl-l clc" style="padding-top: 5px;" onclick="rtTyokinResultClick(\''+ rtDataChecker(resultInfo[resultListIndex].kkrParameter) +'\');">';
retHtml += '<p class="imgbadge_s4" style="background-image:url(' + rtDataChecker(resultInfo[resultListIndex].imgTyakuiPath) + ')!important;">&nbsp;</p>';
if(rtDataChecker(resultInfo[resultListIndex].backTori) == "1"){
retHtml += '<p class="imgbadge_s4_B">B</p>';
}
}
retHtml += '</td>';
}
var nonMaxCnt = 4 - tyoMaxCnt;
for(var nonLoop = 0 ; nonLoop < nonMaxCnt; nonLoop++){
retHtml += '<td class="fl-l"><p>&nbsp;</p></td>';
}
retHtml += '</tr>';
}
return retHtml;
}
function rtEmptyTo3Space(str) {
var ret;
if(rtDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function riSensyuNameClick(sensyuRegistNo) {
riMoveSensyu(sensyuRegistNo);
}
function riMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#riUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_self"
);
}
function rip1wClick(sensyuRegistNo) {
p1wInitialize(hhGetEncSelR(), sensyuRegistNo, "1");
}
function rip2wClick(sensyuRegistNo) {
p2wInitialize(hhGetEncSelR(), sensyuRegistNo, "1");
}
var riController = {
    JSON_REQ_ID: "JSJ011",
    riCreateList: function( params) {
        Com.getRequestGet(riController.JSON_REQ_ID, params)
            .done(function(result) {
                riView.riDrawJSONData(result, params);
            });
    }
};
var riView = {
HDNKEY_ID: 'ppj0320',
riDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#ridivRaceCommentInfo').addClass('dispoff');
$('#ridivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"ridivErrorRaceInfo"
, ""
, params
, function(arg0){
riController.riCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#ridivRaceCommentInfo').addClass('dispoff');
$('#ridivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"ridivErrorRaceInfo"
, riDataChecker(maindata.message)
, params
, function(arg0){
riController.riCreateList(arg0);
}
);
} else {
$('#ridivErrorRaceInfo').addClass('dispoff');
if(riDataChecker(maindata.syusouInfoExistFlg) == "0"){
$('#ridivRaceCommentInfo').addClass('dispoff');
}else{
$('#ridivRaceCommentInfo').removeClass('dispoff');
var leftHtml = "";
var rightHtml = "";
var yudoYosoHtml = "";
var sensyuTypeInfoList = maindata.sensyuTypeInfo;
var sensyuTypeInfoListCnt = sensyuTypeInfoList.length;
var wakuCheck = ""; 
var wakuIdList = []; 
for(var leftLoop = 0 ; leftLoop < sensyuTypeInfoListCnt; leftLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[leftLoop];
leftHtml += '<tr id="riLeftItem_' + riDataChecker(sensyuTypeInfo.syaban) + '" class="' + riDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
if("" != riDataChecker(sensyuTypeInfo.wakuban) && wakuCheck == riDataChecker(sensyuTypeInfo.wakuban)){
wakuIdList.push("rilblWakuban"+ riDataChecker(sensyuTypeInfo.wakuban));
}else{
wakuCheck = riDataChecker(sensyuTypeInfo.wakuban);
leftHtml += '  <td class="wakuban" id="rilblWakuban' + riDataChecker(sensyuTypeInfo.wakuban) + '"><p class="al-c"><span>' + riDataChecker(sensyuTypeInfo.wakuban) + '</span></p></td>';
}
leftHtml += '  <td>' + riDataChecker(sensyuTypeInfo.yosoin) + '</td>';
leftHtml += '  <td class="' + riDataChecker(sensyuTypeInfo.syabanCharColorInfo) + '">';
leftHtml += '    <p class="al-c"><span class="al-c">' + riDataChecker(sensyuTypeInfo.syaban) + '</span></p></td>';
leftHtml += '  <td class="al-l">';
leftHtml += '    <p><span class="bold">' + riDataChecker(sensyuTypeInfo.sensyuName) + '</span><span class="' + riDataChecker(sensyuTypeInfo.ketujyouTuikaHojyuColorInfo) + '">' + riDataChecker(sensyuTypeInfo.ketujyouTuikaHojyu) + '</span></p>';
leftHtml += '    <p><span>' + riDataChecker(sensyuTypeInfo.huKen) + '</span><span>/</span><span class="tbl_val14_fsz">' + riEmptyTo3Space(sensyuTypeInfo.prevKyuhan) + '</span><span class="' + riDataChecker(sensyuTypeInfo.kyuhanSpecialColor) + '">' + riDataChecker(sensyuTypeInfo.kyuhan) + '</span><span>/</span><span>' + riDataChecker(sensyuTypeInfo.kyakusitu) + '</span></p></td>';
leftHtml += '  <td class="wb-r clearfix">';
leftHtml += '    <table style="width: 100%; height: 100%;">';
leftHtml += '      <tbody>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-t nb-l period_data">';
leftHtml += '            <p class="al-c"><span>' + riDataChecker(sensyuTypeInfo.sotugyouki) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '        <tr>';
leftHtml += '          <td class="nb-r nb-b nb-l age_data">';
leftHtml += '            <p class="al-c"><span>' + riDataChecker(sensyuTypeInfo.age) + '</span></p></td>';
leftHtml += '        </tr>';
leftHtml += '      </tbody>';
leftHtml += '    </table>';
leftHtml += '  </td>';
leftHtml += '</tr>';
}
$('#riTableLeftBody').html(leftHtml);
for(var wakuLoop = 0 ; wakuLoop < wakuIdList.length; wakuLoop++){
$("#" + wakuIdList[wakuLoop]).attr("rowspan","2");
}
for(var rightLoop = 0 ; rightLoop < sensyuTypeInfoListCnt; rightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[rightLoop];
var commentInfo = sensyuTypeInfo.commentOrderCntSubData;
rightHtml += '<tr id="riRightItem_' + rbDataChecker(sensyuTypeInfo.syaban) + '" class="' + riDataChecker(sensyuTypeInfo.syabanBgColorInfo) + '">';
rightHtml += '  <td class="" style="padding:0;width:11%" ><p>' + riDataChecker(commentInfo.homeBank) + '</p></td>';
rightHtml += '  <td class="bold" style="padding:0;width:10%" >';
if(riDataChecker(commentInfo.gearBefore) == ""){
rightHtml += '<p>' + commentInfo.gearAfter + '</p>';
} else {
rightHtml += '<p><span class="lineth">' + commentInfo.gearBefore + '</span></p>';
rightHtml += '<p><span class="' + riDataChecker(commentInfo.gearColor) + '">'+ riDataChecker(commentInfo.gearArrow) + riDataChecker(commentInfo.gearAfter) + '</span></p>';
}
rightHtml += '  </td>';
rightHtml += '  <td style="padding:0;width: 5%;" class="wb-r bold"><p>' + riDataChecker(commentInfo.shikkakuPoint) + '</p></td>';
rightHtml += '  <td style="padding:0;" class="clc bold" onclick="rip1wClick(\'' + riDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p>' + riDataChecker(commentInfo.tyo4Tyaku1st) + '</p></td>';
rightHtml += '  <td style="padding:0;" class="clc bold" onclick="rip2wClick(\'' + riDataChecker(sensyuTypeInfo.sensyuRegistNo) + '\');"><p>' + riDataChecker(commentInfo.tyo4Tyaku2nd) + '</p></td>';
rightHtml += '  <td style="padding:0;" class="bold"><p>' + riDataChecker(commentInfo.tyo4Tyaku3rd) + '</p></td>';
rightHtml += '  <td style="padding:0;" class="wb-r bold"><p>' + riDataChecker(commentInfo.tyo4TyakuOut) + '</p></td>';
rightHtml += '  <td style="padding:0;word-wrap: break-word;white-space: pre-wrap;" class="al-l"><p>' + riDataChecker(commentInfo.sensyuComment) + '</p></td>';
rightHtml += '</tr>';
}
$('#riTableRightBody').html(rightHtml);
for(var heightLoop = 0 ; heightLoop < sensyuTypeInfoListCnt; heightLoop++){
var sensyuTypeInfo = sensyuTypeInfoList[heightLoop];
var no = riDataChecker(sensyuTypeInfo.syaban);
var totalHeight = $('#riRightItem_' + no).height();
$('#riLeftItem_' + no).height(totalHeight);
$('#riRightItem_' + no).height(totalHeight);
}
yudoYosoHtml += '<div class="dispon" style="margin-top: 7px;">';
yudoYosoHtml += '  <table style="width: 100%;">';
yudoYosoHtml += '    <tbody>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td style="width: 3%;">&nbsp;</td>';
if(riDataChecker(maindata.yudoSensyuName) == ""){
yudoYosoHtml += '<td style="width: 18%;">&nbsp</td>';
} else {
yudoYosoHtml += '<td style="width: 18%;">誘導&nbsp' + maindata.yudoSensyuName + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(riDataChecker(maindata.yosoinMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: auto;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: auto;">予想印　情報提供：' + maindata.yosoinMei + '</td>';
}
yudoYosoHtml += '        <td style="width: 1%;">&nbsp;</td>';
if(riDataChecker(maindata.senComMei) == ""){
yudoYosoHtml += '<td class="al-r" style="width: 39%;">&nbsp;</td>';
} else {
yudoYosoHtml += '<td class="al-r" style="width: 39%;">コメント　情報提供：' + maindata.senComMei + '</td>';
}
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '      <tr>';
yudoYosoHtml += '        <td class="al-r" colspan="6">' + riDataChecker(maindata.lastUpdateTime) + '</td>';
yudoYosoHtml += '      </tr>';
yudoYosoHtml += '    </tbody>';
yudoYosoHtml += '  </table>';
yudoYosoHtml += '</div>';
$('#riYudoYosoInfo').html(yudoYosoHtml);
}
}
return;
}
};
function riDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function riEmptyTo3Space(str) {
var ret;
if(riDataChecker(str) == ""){
ret = "&nbsp;&nbsp;&nbsp;";
} else {
ret = str;
}
return ret;
}
function rrSensyuNameClick(sensyuRegistNo) {
    rrMoveSensyu(sensyuRegistNo);
}
function rrMoveSensyu(sensyuRegistNo) {
commonSubmit.formGet(
$('#rrUrlSensyu').val()
, {"snum": sensyuRegistNo}
, "_blank"
);
}
function rrClickDigestBtn() {
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
rrMoveDigest();
return;
});
} else {
comKaime.kimClear();
rrMoveDigest();
return;
}
}
function rrMoveDigest() {
var digestParams = [];
var prm = {};
prm.bkcd = gBKeirinCd;
prm.kday = gKaisaihi;
prm.rnum = gRaceNo;
digestParams.push(prm);
commonSubmit.formPost(
$('#rrUrlDigest').val()
, { "disp" : displayingId, "fdisp" : parentFuncId, 'prmsDigestList' : JSON.stringify(digestParams) }
, "_self"
);
}
var rrController = {
    JSON_REQ_ID: "JSJ012",
    rrCreateList: function( params) {
        Com.getRequestGet(rrController.JSON_REQ_ID, params)
            .done(function(result) {
            rrView.rrDrawJSONData(result, params);
            });
    }
};
var rrView = {
HDNKEY_ID: 'ppj0326',
rrDrawJSONData: function(maindata, params) {
if ( !maindata ) {
$('#rrdivRaceResultInfo').addClass('dispoff');
$('#rrdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rrdivErrorRaceInfo"
, ""
, params
, function(arg0){
rrController.rrCreateList(arg0);
}
);
} else if ( maindata.resultCd == -1 ) {
$('#rrdivRaceResultInfo').addClass('dispoff');
$('#rrdivErrorRaceInfo').removeClass('dispoff');
Com.makePcUpdatePage(
"rrdivErrorRaceInfo"
, rrDataChecker(maindata.message)
, params
, function(arg0){
rrController.rrCreateList(arg0);
}
);
} else {
$('#rrdivErrorRaceInfo').addClass('dispoff');
$('#rrdivRaceResultInfo').removeClass('dispoff');
var tenkiHtml = "";
if(rrDataChecker(maindata.tenki) != ""){
tenkiHtml += maindata.tenki;
}
if(rrDataChecker(maindata.tenki) != "" && rrDataChecker(maindata.husoku) != ""){
tenkiHtml += '：';
}
if(rrDataChecker(maindata.husoku) != ""){
tenkiHtml += '風速&nbsp;' + maindata.husoku + 'ｍ';
}
$('#rrDispTenki').html(tenkiHtml);
if(!maindata.shortCriticismDispFlg){
$('#rrDispShortCriticism').addClass('dispoff');
$('#rrDispRaceTenkai').addClass('dispoff');
$('#rrlblTenkaiMei').html('');
}else{
var shortCriticismInfo = maindata.shortCriticismItemSubData;
if(shortCriticismInfo == undefined){
$('#rrDispShortCriticism').addClass('dispoff');
}else{
var scBodyHtml = "";
for(var scKey in shortCriticismInfo){
scBodyHtml += '<tr class="ht_32">';
scBodyHtml += '  <td class="al-c">'+ rrDataChecker(shortCriticismInfo[scKey].tyaku) +'</td>';
scBodyHtml += '  <td class="al-c '+ rrDataChecker(shortCriticismInfo[scKey].jyuniBSClass) +'">'+ rrDataChecker(shortCriticismInfo[scKey].jyuniBS) +'</td>';
scBodyHtml += '  <td class="al-c"><div class="lnum '+ rrDataChecker(shortCriticismInfo[scKey].syabanCharColor) +'">'+ rrDataChecker(shortCriticismInfo[scKey].syaban) +'</div></td>';
scBodyHtml += '  <td class="al-l pd_l5"><a href="javascript:void(0);" onclick="rrSensyuNameClick(\'' + rrDataChecker(shortCriticismInfo[scKey].sensyuRegistNo) + '\');" class="uline bold">'+ rrDataChecker(shortCriticismInfo[scKey].sensyuName) +'</a></td>';
scBodyHtml += '  <td class="al-l pd_l5">'+ rrDataChecker(shortCriticismInfo[scKey].shortCriticism) +'</td>';
scBodyHtml += '</tr>';
}
$('#rrTableShortCriticismBody').html(scBodyHtml);
$('#rrDispShortCriticism').removeClass('dispoff');
}
var developItem = maindata.developItemSubData;
if(developItem == undefined){
$('#rrDispRaceTenkai').addClass('dispoff');
}else{
$('#rrTableTenkaiGoing').html(rrMakeTenkaiTable("Going"));
$('#rrTableTenkaiBell').html(rrMakeTenkaiTable("Bell"));
$('#rrTableTenkaiHS').html(rrMakeTenkaiTable("HS"));
$('#rrTableTenkaiBS').html(rrMakeTenkaiTable("BS"));
$('#rrTableTenkaiGoal').html(rrMakeTenkaiTable("Goal"));
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
insertHtml = '<p class="imgbadge_s2" style="background-image:url('+ rrDataChecker(developItem[diKey].imgGoingPath) +')!important;"></p>';
selectId = '#rrtdGoing_'+ rrDataChecker(developItem[diKey].goingXShaft) +'_'+ rrDataChecker(developItem[diKey].goingYShaft);
$(selectId).html(insertHtml);
if(rrDataChecker(developItem[diKey].imgGoingPath) != ""){
xCnt["Going"][developItem[diKey].goingXShaft]++;
}
insertHtml = '<p class="imgbadge_s2" style="background-image:url('+ rrDataChecker(developItem[diKey].imgTollBellPath) +')!important;"></p>';
selectId = '#rrtdBell_'+ rrDataChecker(developItem[diKey].tollBellXShaft) +'_'+ rrDataChecker(developItem[diKey].tollBellYShaft);
$(selectId).html(insertHtml);
if(rrDataChecker(developItem[diKey].imgTollBellPath) != ""){
xCnt["Bell"][developItem[diKey].tollBellXShaft]++;
}
insertHtml = '<p class="imgbadge_s2" style="background-image:url('+ rrDataChecker(developItem[diKey].imgHSPath) +')!important;"></p>';
selectId = '#rrtdHS_'+ rrDataChecker(developItem[diKey].HSXShaft) +'_'+ rrDataChecker(developItem[diKey].HSYShaft);
$(selectId).html(insertHtml);
if(rrDataChecker(developItem[diKey].imgHSPath) != ""){
xCnt["HS"][developItem[diKey].HSXShaft]++;
}
insertHtml = '<p class="imgbadge_s2" style="background-image:url('+ rrDataChecker(developItem[diKey].imgBSPath) +')!important;"></p>';
selectId = '#rrtdBS_'+ rrDataChecker(developItem[diKey].BSXShaft) +'_'+ rrDataChecker(developItem[diKey].BSYShaft);
$(selectId).html(insertHtml);
if(rrDataChecker(developItem[diKey].imgBSPath) != ""){
xCnt["BS"][developItem[diKey].BSXShaft]++;
}
insertHtml = '<p class="imgbadge_s2" style="background-image:url('+ rrDataChecker(developItem[diKey].imgGoalPath) +')!important;"></p>';
selectId = '#rrtdGoal_'+ rrDataChecker(developItem[diKey].goalXShaft) +'_'+ rrDataChecker(developItem[diKey].goalYShaft);
$(selectId).html(insertHtml);
if(rrDataChecker(developItem[diKey].imgGoalPath) != ""){
xCnt["Goal"][developItem[diKey].goalXShaft]++;
}
if(diKey == 0 && jQuery.trim(rrDataChecker(developItem[diKey].tenkaiMei)) != ""){
var mei = 'ＢＳ通過順位・短評・レース展開　情報提供：';
$('#rrlblTenkaiMei').html(mei + developItem[diKey].tenkaiMei);
}
}
for(var tKey in xCnt){
for(var i = 1 ; i <= 5; i++){
if(xCnt[tKey][i] == 0){
$('#rrtr'+ tKey +'_' + i).addClass('dispoff');
} else {
$('#rrtr'+ tKey +'_' + i).removeClass('dispoff');
}
}
}
$('#rrDispRaceTenkai').removeClass('dispoff');
}
}
if(!maindata.tyakujyunDispFlg){
$('#rrDispTyakuJyun').addClass('dispoff');
} else {
var tyakujyunItemInfo = maindata.tyakujyunItemSubData;
if(tyakujyunItemInfo == undefined){
$('#rrDispTyakuJyun').addClass('dispoff');
} else {
var tjBodyHtml = "";
for(var tjKey in tyakujyunItemInfo){
tjBodyHtml += '<tr class=" ht_32">';
tjBodyHtml += '  <td class="wakuban"><p class="al-c"><span>'+ rrDataChecker(tyakujyunItemInfo[tjKey].tyaku) +'</span></p></td>';
tjBodyHtml += '  <td class="al-c"><div class="lnum '+ rrDataChecker(tyakujyunItemInfo[tjKey].syabanCharColor) +'">'+ rrDataChecker(tyakujyunItemInfo[tjKey].syaban) +'</div></td>';
tjBodyHtml += '  <td class="al-l pd_l5"><a href="javascript:void(0);" onclick="rrSensyuNameClick(\'' + rrDataChecker(tyakujyunItemInfo[tjKey].sensyuRegistNo) + '\');" class="uline bold nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].sensyuName) +'</a></td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].age) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].huken) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].sotugyouki) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].kyuhan) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].tyakusa) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].agari) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].kimarite) +'</td>';
tjBodyHtml += '  <td class="al-c nowrap">'+ rrDataChecker(tyakujyunItemInfo[tjKey].BH) +'</td>';
var kojinItem = tyakujyunItemInfo[tjKey].kojinStateItemSubData;
if(kojinItem == undefined){
tjBodyHtml += '<td class="al-l">&nbsp;</td>';
} else {
tjBodyHtml += '<td class="al-l">';
for(var kiLoop = 0; kiLoop < kojinItem.length; kiLoop++){
if(kiLoop != 0){
tjBodyHtml += ' '; 
}
var charColorClass = "";
var kojinHosoku = rrDataChecker(kojinItem[kiLoop].tyakuNote);
if(kojinHosoku != ""){
charColorClass = rrDataChecker(kojinItem[kiLoop].kojinStateClass);
}
tjBodyHtml += '<span class="nowrap">';
tjBodyHtml += '<span class="'+ charColorClass +'">' + rrDataChecker(kojinItem[kiLoop].kojinState) +'</span>';
tjBodyHtml += '<span>' + kojinHosoku +'</span>';
tjBodyHtml += '</span>';
if(kiLoop == (kojinItem.length - 1)){
var inLine = rrDataChecker(tyakujyunItemInfo[tjKey].inLineJyuni);
if(inLine != ""){
tjBodyHtml += '<span class="nowrap"> 入線順位：'+ inLine + '</span>';
}
}
}
tjBodyHtml += '</td>';
}
tjBodyHtml += '</tr>';
}
$('#rrTableTyakuJyunBody').html(tjBodyHtml);
$('#rrDispTyakuJyun').removeClass('dispoff');
}
}
$('#rrlblLastUpdateTime').html(rrDataChecker(maindata.lastUpdateTime));
if(!maindata.haraiGakuDispFlg){
$('#rrDispHaraiGaku').addClass('dispoff');
$('#rrDispHaraiGaku2').addClass('dispoff');
} else {
var haraiGakuInfo = maindata.haraiGakuSubData;
if(haraiGakuInfo == undefined){
$('#rrDispHaraiGaku').addClass('dispoff');
$('#rrDispHaraiGaku2').addClass('dispoff');
} else {
var hgBodyHtml = "";
var hgWkTrHtml = "";
var widthOzzName = 15;
var widthOzzTable = 35;
var widthOzzKumi = 24;
var widthOzzGaku = 53;
var widthOzzNin  = 23;
$('#rrDispHaraiGaku').removeClass('dispoff');
$('#rrDispHaraiGaku2').removeClass('dispoff');
hgWkTrHtml += '<tr>';
var wh2 = haraiGakuInfo.WH2HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c" style="width: '+ widthOzzName +'%;">2枠複</td>';
hgWkTrHtml += '<td class="nb-r nb-l" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var wh2Cnt = 0; wh2Cnt < wh2.length; wh2Cnt++){
hgWkTrHtml += '<tr>';
if(!wh2[wh2Cnt].ninkiDispFlg && !wh2[wh2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!wh2[wh2Cnt].ninkiDispFlg && wh2[wh2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="nb-a al-r">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(wh2[wh2Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
var rh3 = haraiGakuInfo.RH3HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c" style="width: '+ widthOzzName +'%;">3連複</td>';
hgWkTrHtml += '<td class="nb-l" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var rh3Cnt = 0; rh3Cnt < rh3.length; rh3Cnt++){
hgWkTrHtml += '<tr>';
if(!rh3[rh3Cnt].ninkiDispFlg && !rh3[rh3Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!rh3[rh3Cnt].ninkiDispFlg && rh3[rh3Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="nb-a al-r">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(rh3[rh3Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
hgWkTrHtml += '</tr>';
hgWkTrHtml += '<tr>';
var wt2 = haraiGakuInfo.WT2HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c nb-b" style="width: '+ widthOzzName +'%;">2枠単</td>';
hgWkTrHtml += '<td class="nb-r nb-l nb-b" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var wt2Cnt = 0; wt2Cnt < wt2.length; wt2Cnt++){
hgWkTrHtml += '<tr>';
if(!wt2[wt2Cnt].ninkiDispFlg && !wt2[wt2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!wt2[wt2Cnt].ninkiDispFlg && wt2[wt2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="nb-a al-r">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(wt2[wt2Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
var rt3 = haraiGakuInfo.RT3HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c nb-b" style="width: '+ widthOzzName +'%;">3連単</td>';
hgWkTrHtml += '<td class="nb-l nb-b" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var rt3Cnt = 0; rt3Cnt < rt3.length; rt3Cnt++){
hgWkTrHtml += '<tr>';
if(!rt3[rt3Cnt].ninkiDispFlg && !rt3[rt3Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="bold nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!rt3[rt3Cnt].ninkiDispFlg && rt3[rt3Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="bold nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="bold nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="bold nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="bold nb-a al-r">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="bold nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(rt3[rt3Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
hgWkTrHtml += '</tr>';
$('#rrDispHaraiGaku').html(hgWkTrHtml);
hgWkTrHtml ="";
hgWkTrHtml += '<tr>';
var sh2 = haraiGakuInfo.SH2HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c" style="width: '+ widthOzzName +'%;">2車複</td>';
hgWkTrHtml += '<td class="nb-r nb-l" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var sh2Cnt = 0; sh2Cnt < sh2.length; sh2Cnt++){
hgWkTrHtml += '<tr>';
if(!sh2[sh2Cnt].ninkiDispFlg && !sh2[sh2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!sh2[sh2Cnt].ninkiDispFlg && sh2[sh2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="nb-a al-r">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(sh2[sh2Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
var wide = haraiGakuInfo.WHaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c" style="width: '+ widthOzzName +'%;" rowspan="2">ワイド</td>';
hgWkTrHtml += '<td class="nb-l" style="width: '+ widthOzzTable +'%;" rowspan="2">';
hgWkTrHtml += '<table style="width: 100%";>';
for(var wCnt = 0; wCnt < wide.length; wCnt++){
hgWkTrHtml += '<tr>';
if(!wide[wCnt].ninkiDispFlg && !wide[wCnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(wide[wCnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!wide[wCnt].ninkiDispFlg && wide[wCnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wide[wCnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(wide[wCnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(wide[wCnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="nb-a al-r">';
hgWkTrHtml += rrDataChecker(wide[wCnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(wide[wCnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
hgWkTrHtml += '</tr>';
hgWkTrHtml += '<tr>';
var st2 = haraiGakuInfo.ST2HaraiGakuDispItemSubData;
hgWkTrHtml += '<td class="tbl_header2 al-c" style="width: '+ widthOzzName +'%;">2車単</td>';
hgWkTrHtml += '<td class="nb-r nb-l" style="width: '+ widthOzzTable +'%;">';
hgWkTrHtml += '<table style="width: 100%;height:37px";>';
for(var st2Cnt = 0; st2Cnt < st2.length; st2Cnt++){
hgWkTrHtml += '<tr>';
if(!st2[st2Cnt].ninkiDispFlg && !st2[st2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ (widthOzzKumi + widthOzzGaku + widthOzzNin) +'%;" class="bold nb-a al-c pd_l10 pd_r10" colspan="3">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else if(!st2[st2Cnt].ninkiDispFlg && st2[st2Cnt].kumiDispFlg){
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="bold nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ (widthOzzGaku + widthOzzNin) +'%;" class="bold nb-a al-c pd_r10" colspan="2">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].haraiGaku);
hgWkTrHtml += '</td>';
} else {
hgWkTrHtml += '<td style="width: '+ widthOzzKumi +'%;" class="bold nb-a al-l pd_l10">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].kumiBan);
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzGaku +'%;" class="bold nb-a al-r">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].haraiGaku) + '円';
hgWkTrHtml += '</td>';
hgWkTrHtml += '<td style="width: '+ widthOzzNin +'%;" class="bold nb-a al-r pd_r10">';
hgWkTrHtml += rrDataChecker(st2[st2Cnt].ninki);
hgWkTrHtml += '</td>';
}
hgWkTrHtml += '</tr>';
}
hgWkTrHtml += '</table>';
hgWkTrHtml += '</td>';
hgWkTrHtml += '</tr>';
if(haraiGakuInfo.APartReturnDispFlg){
hgWkTrHtml += '<tr><td colspan="4" class="nb-t al-c clearfix v-al-m">'+ rrDataChecker(haraiGakuInfo.APartReturn) +'</td></tr>';
}
$('#rrDispHaraiGaku2').html(hgWkTrHtml);
}
}
if(!maindata.syabanItemDispFlg){
$('#rrDispSyabanItem').addClass('dispoff');
} else {
var syabanItemInfo = maindata.syabanItemSubData;
if(syabanItemInfo == undefined){
$('#rrDispSyabanItem').addClass('dispoff');
} else {
var siBodyHtml = "";
for(var siKey in syabanItemInfo){
siBodyHtml += '<tr class="ht_32 '+ rrDataChecker(syabanItemInfo[siKey].syabanBgColor) +'">';
siBodyHtml += '  <td class="'+ rrDataChecker(syabanItemInfo[siKey].syabanCharColor) +'"><p class="al-c"><span class="al-c">'+ rrDataChecker(syabanItemInfo[siKey].syaban) +'</span></p></td>';
siBodyHtml += '  <td class="al-l pd_l5"><a href="javascript:void(0);" onclick="rrSensyuNameClick(\'' + rrDataChecker(syabanItemInfo[siKey].sensyuRegistNo) + '\');" class="uline">'+ rrDataChecker(syabanItemInfo[siKey].sensyuName) +'</a></td>';
siBodyHtml += '  <td class="al-c">'+ rrDataChecker(syabanItemInfo[siKey].huken) +'</td>';
siBodyHtml += '</tr>';
}
$('#rrTableSyabanItemBody').html(siBodyHtml);
$('#rrDispSyabanItem').removeClass('dispoff');
}
}
if(!maindata.digestBtnActiveFlg){
$('#rrbtnDigest').prop("disabled", true);
} else {
$('#rrbtnDigest').prop("disabled", false);
}
if(!maindata.bikouDispFlg){
$('#rrDispRaceBikou').addClass('dispoff');
} else {
$('#rrpRaceBikou').html(rrDataChecker(maindata.raceBikou));
$('#rrDispRaceBikou').removeClass('dispoff');
}
}
return;
}
};
function rrDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function rrMakeTenkaiTable(idName){
var retBodyHtml = "";
for(var xLoop = 5 ; xLoop >= 1; xLoop--){
retBodyHtml += '<tr id="rrtr'+ idName +'_'+ xLoop +'">';
for(var yLoop = 1 ; yLoop <= 14; yLoop++){
retBodyHtml += '<td id="rrtd'+ idName +'_'+ xLoop +'_'+ yLoop +'" colspan="2" class="al-c">&nbsp;</td>';
}
retBodyHtml += '</tr>';
}
return retBodyHtml;
}
var rcController = {
    JSON_REQ_ID: "JSJ013",
    rcCreateList: function(params) {      
        Com.getRequestGet(rcController.JSON_REQ_ID, params)
            .done(function(result) {
            rcView.rcDrawJSONData(result,params);
            });
    }
};
var exportRoot, sh;
var rcView = {
    HDNKEY_ID: 'JSJ013',
    rcDrawJSONData: function(PJ0328JSONData,params) {
    var kaimeDiv = $("#kaimeInquiry");
    var tmp = "";
    if($('#PM0116_tekichu').dialog('isOpen')){
        $('#PM0116_tekichu').dialog('close');
    }
    if($('#PM0116_omedetou').dialog('isOpen')){
        $('#PM0116_omedetou').dialog('close');
    }
if ( !PJ0328JSONData ) {
    kaimeDiv.empty();
Com.makePcUpdatePage(
"kaimeInquiry"
, ""
, params
, function(arg0){
rcController.rcCreateList(arg0);
}
);
} else if ( PJ0328JSONData.resultCd == -1 ) {
    kaimeDiv.empty();
if(!PJ0328JSONData.message){
tmp = "";
} else {
tmp = PJ0328JSONData.message;
}
Com.makePcUpdatePage(
"kaimeInquiry"
, tmp
, params
, function(arg0){
rcController.rcCreateList(arg0);
}
);
    } else {
    kaimeDiv.empty();
    if( PJ0328JSONData.dispTohyoFlg == 0 && PJ0328JSONData.dispRsultFlg == 0){
    if(PJ0328JSONData.msgdiv != ""){
    var tblHtml = $("<table>")
    var colHtml = $("<colgroup>")
    var theadHtml = $('<tr>');
    var tbodyHtml = $('<tbody>');
    tblHtml.addClass("w100pc").attr("id","rctblvoteInf");
    colHtml.append($("<col>").attr("id","rcColKakesikiProcedures"));
    colHtml.append($("<col>").attr("id","rcColKumiban"));
    colHtml.append($("<col>").attr("id","rcColKumisu"));
    colHtml.append($("<col>").attr("id","rcColKonyuGakuTotal"));
    colHtml.append($("<col>").attr("id","rcColKonyuGaku"));
    colHtml.append($("<col>").attr("id","rcColOzz"));
    colHtml.append($("<col>").attr("id","rcColNinki"));
    colHtml.append($("<col>").attr("id","rcColSupHaraiGaku"));
    tblHtml.append(colHtml);
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("賭式・方式"));
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組番"));
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組数"));
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("購入金額").attr("colspan","2"));
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("オッズ").attr("colspan","2"));
    theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("想定払戻金額"));
    tblHtml.append($('<thead>').append(theadHtml));
    tbodyHtml.append($("<tr>").append($("<td>").addClass("v-al-t").attr("colspan","6").append(PJ0328JSONData.msgdiv)));
    tblHtml.append(tbodyHtml);
    kaimeDiv.append(tblHtml);
    }
    } else if(PJ0328JSONData.dispTohyoFlg == 1) {
    kaimeDiv.append(rcCreateVotingInfo(PJ0328JSONData));
    } else if(PJ0328JSONData.dispRsultFlg == 1) {
    kaimeDiv.append(rcCreateResultInfo(PJ0328JSONData));
if(PJ0328JSONData.animationFlg != 0){
    rcAnimetionCanvas(PJ0328JSONData.animationFlg);
   rcCreateOmedetoSubDailog(PJ0328JSONData);
    }
    }
    }
    }
}
function rcCreateVotingInfo (JsonData) {
var tblHtml = $("<table>")
var colHtml = $("<colgroup>")
var theadHtml = $('<tr>');
var tbodyHtml = $('<tbody>');
var tbodytrHtml = $('<tr>');
var kaime ="";
var tmp = "";
var count = 0;
tblHtml.addClass("w100pc").attr("id","rctblvoteInf");
colHtml.append($("<col>").attr("id","rcColKakesikiProcedures"));
colHtml.append($("<col>").attr("id","rcColKumiban"));
colHtml.append($("<col>").attr("id","rcColKumisu"));
colHtml.append($("<col>").attr("id","rcColKonyuGakuTotal"));
colHtml.append($("<col>").attr("id","rcColKonyuGaku"));
colHtml.append($("<col>").attr("id","rcColOzz"));
colHtml.append($("<col>").attr("id","rcColNinki"));
colHtml.append($("<col>").attr("id","rcColSupHaraiGaku"));
tblHtml.append(colHtml);
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("賭式・方式"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組番"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組数"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("購入金額").attr("colspan","2"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("オッズ").attr("colspan","2"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("想定払戻金額"));
tblHtml.append($('<thead>').append(theadHtml));
for(var i = 0; i < JsonData.RsultData.length; i++){
tbodytrHtml = $('<tr>');
kaime = $(JsonData.RsultData)[i];
tbodytrHtml.append($("<td>").append(kaime.rsultBetType).addClass("b-a al-c"));
tbodytrHtml.append($("<td>").append(rcEdtKumibann(kaime.kumiban)).addClass("bold b-a al-l"));
tbodytrHtml.append($("<td>").append(kaime.kumisu).addClass("b-a al-r"));
if(kaime.dispTotalFlg == '1'){
tbodytrHtml.append($("<td>").append("計").addClass("b-l b-t b-b"));
} else {
tbodytrHtml.append($("<td>").append("").addClass("b-l b-t b-b"));
}
tbodytrHtml.append($("<td>").append(kaime.kingaku).addClass("b-r b-t b-b al-r"));
tmp = kaime.ozz;
if(tmp == "0.0" || tmp == "0"){
    tmp = "-----";
}else{
    if(kaime.dnozz != null){
    tmp = tmp + "～" + kaime.dnozz + "&nbsp;&nbsp;&nbsp;";
    }
}
tbodytrHtml.append($("<td>").append(tmp).addClass("b-l b-t b-b al-r"));
tbodytrHtml.append($("<td>").append(kaime.ninki).addClass("b-r b-t b-b al-r"));
tbodytrHtml.append($("<td>").append(kaime.totalRefundAmount).addClass("b-a al-r"));
tbodyHtml.append(tbodytrHtml);
}
tbodyHtml.addClass("altertable");
tblHtml.append(tbodyHtml);
return tblHtml;
}
function rcCreateResultInfo (JsonData) {
var tblHtml = $("<table>")
var colHtml = $("<colgroup>")
var theadHtml = $('<tr>');
var tbodyHtml = $('<tbody>');
var tbodytrHtml = $('<tr>');
var kaime ="";
var kessya = "";
var rank = "";
var tmp = "";
var rsultkumiDiv = $("<div>");
var rsultkinDiv = $("<div>");
var rsultninDiv = $("<div>");
tblHtml.addClass("w100pc").attr("id","rctblresult");
colHtml.append($("<col>").attr("id","rcColKakesikiProcedures"));
colHtml.append($("<col>").attr("id","rcColKumiban"));
colHtml.append($("<col>").attr("id","rcColKumisu"));
colHtml.append($("<col>").attr("id","rcColkonyuGakuTotal"));
colHtml.append($("<col>").attr("id","rcColKonyuGaku"));
colHtml.append($("<col>").attr("id","rcColHenkan"));
colHtml.append($("<col>").attr("id","rcColHarai"));
colHtml.append($("<col>").attr("id","rcColresultKumiban"));
colHtml.append($("<col>").attr("id","rcColRsultKinGaku"));
colHtml.append($("<col>").attr("id","rcColresultninki"));
tblHtml.append(colHtml);
if(JsonData.rankudivFlg == 1){
rank = $("<div>");
tmp = "";
if(JsonData.ranku1Flg == 1){
tmp = tmp + "1着:" + JsonData.ranku1 + "&nbsp;";
}
if(JsonData.ranku2Flg == 1){
tmp = tmp + "2着:" + JsonData.ranku2 + "&nbsp;";
}
if(JsonData.ranku3Flg == 1){
tmp = tmp + "3着:" + JsonData.ranku3;
}
rank.append(tmp);
}
if(JsonData.kessyaFlg == 1){
kessya = $("<div>");
kessya.append("欠車 "+JsonData.kessyaSyaban).addClass(JsonData.kessyaColor　+ " bold");
}
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("賭式・方式"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組番"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("組数"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("購入金額").attr("colspan","2"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("返還金額"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("払戻金額"));
theadHtml.append($("<td>").addClass("tbl_header2 al-c b-a").append("レース結果").append(rank).append(kessya).attr("colspan","3"));
tblHtml.append($('<thead>').append(theadHtml));
for(var i = 0; i < JsonData.RsultData.length; i++){
tbodytrHtml = $('<tr>');
kaime = $(JsonData.RsultData)[i];
tmp = "";
var rsultkumiTd = $("<td>");
var rsultkinTd = $("<td>");
var rsultninTd = $("<td>");
tbodytrHtml.append($("<td>").append(rcEdtKakehou(kaime.rsultBetType)).addClass("b-a al-c"));
tbodytrHtml.append($("<td>").append(rcEdtKumibann(kaime.kumiban)).addClass("b-a al-l"));
tbodytrHtml.append($("<td>").append(kaime.kumisu).addClass("b-a al-r"));
if(kaime.dispTotalFlg == '1'){
tbodytrHtml.append($("<td>").append("計").addClass("b-l b-t b-b"));
} else {
tbodytrHtml.append($("<td>").append("").addClass("b-l b-t b-b"));
}
tbodytrHtml.append($("<td>").append(kaime.kingaku).addClass("b-r b-t b-b al-r"));
tbodytrHtml.append($("<td>").append(kaime.totalReturnMoney).addClass("b-a al-r"));
tmp = tmp = "b-a al-r";
if(kaime.hitFlg == 1){
tmp = JsonData.hitColor + " " + tmp;
} 
tbodytrHtml.append($("<td>").append(kaime.totalRefundAmount).addClass(tmp));
for (var j= 0;j < $(kaime.rsultList).length;j++){
rsultList = $(kaime.rsultList)[j];
if(rsultList.rsultKumiban){
    if(rsultList.rsultKumiban.indexOf("-") == -1 && rsultList.rsultKumiban.indexOf("=") == -1){
    rsultkumiTd.append($("<div>").addClass("al-c").append(rsultList.rsultKumiban));
    } else {
    rsultkumiTd.append($("<div>").append(rsultList.rsultKumiban));
    }
}
rsultkinTd.append($("<div>").addClass("al-r").append(rsultList.rsultmoney));
rsultninTd.append($("<div>").addClass("al-r").append(rsultList.rsultninki));
}
tbodytrHtml.append(rsultkumiTd.addClass("b-a al-l"));
tbodytrHtml.append(rsultkinTd.addClass("b-l b-t b-b al-r"));
tbodytrHtml.append(rsultninTd.addClass("b-r b-t b-b al-c"));
if(kaime.hitFlg == 1){
tbodytrHtml.addClass(JsonData.hitbkColor);
}
tbodyHtml.append(tbodytrHtml);
}
tblHtml.append(tbodyHtml);
return tblHtml;
}
function rcEdtKumibann(kaimekumiban){
var kumiban = kaimekumiban;
var kumibantmp1 = "";
var kumibantmp2 = ""; 
if(10 < kumiban.length){
count = kumiban.indexOf("=")
if(count == -1){
count = kumiban.indexOf("-")
}
kumibantmp1 = kumiban.substr(0,count+1)
kumibantmp2 = kumiban.substr(count+1);
if(10 < kumibantmp2.length){
count = kumibantmp2.indexOf("=")
if(count == -1){
count = kumibantmp2.indexOf("-")
}
kumibantmp2 = kumibantmp2.substr(0,count+1)+ "<br />" + kumibantmp2.substr(count+1);
}
kumiban = kumibantmp1 + "<br />" + kumibantmp2;
}
return kumiban
}
function rcEdtKakehou(kaimekakehou){
var temp = $("<div>").append(kaimekakehou);
var kakehou = temp.text();
var kakeshiki = "";
var hoshiki ="";
if(3 < kakehou.length){
kakeshiki = kakehou.substr(0,3);
hoshiki = kakehou.substr(3);
kakehou = kakeshiki + "<br />" + hoshiki;
}
return kakehou
}
var showOmedetou = function(){
window.clearInterval(sh);
$('#PM0116_tekichu').dialog('close');
$('#PM0116_omedetou').removeClass("dispoff");
$('#PM0116_omedetou').dialog('open');
}
function rcAnimetionCanvas(animationFlg){
var tmp = "";
var srcRoot = "";
    var jsSrc = "";
    var appendFlg = false;
tmp = $("script").attr("src");
tmp = tmp.split("/static/js/");
srcRoot = tmp[0];
createjs.MotionGuidePlugin.install();
if ("1" == animationFlg) {
    jsSrc = srcRoot + "/static/js/PC_hyoushou_canvas.js";
    if($('script[src$="PC_hyoushou_canvas.js"]').length == 0){
        $.getScript(jsSrc,function(){
            exportRoot = new lib.PC_hyoushou_canvas();
            rcCreateCanvas(exportRoot);
        });
        appendFlg = true;
    } else {
        exportRoot = new lib.PC_hyoushou_canvas();
        rcCreateCanvas(exportRoot);
    }
} else if ("2" == animationFlg) {
    jsSrc = srcRoot + "/static/js/PC_cracker_canvas.js";
    if($('script[src$="PC_cracker_canvas.js"]').length == 0){
        $.getScript(jsSrc,function(){
            exportRoot = new lib.PC_cracker_canvas();
            rcCreateCanvas(exportRoot);
        });
        appendFlg = true;
    } else {
        exportRoot = new lib.PC_cracker_canvas();
        rcCreateCanvas(exportRoot);
    }
} else if ("3" == animationFlg) {
    jsSrc = srcRoot + "/static/js/PC_kusudama_canvas.js";
    if($('script[src$="PC_kusudama_canvas.js"]').length == 0){
        $.getScript(jsSrc,function(){
            exportRoot = new lib.PC_kusudama_canvas();
            rcCreateCanvas(exportRoot);
        });
        appendFlg = true;
    } else {
        exportRoot = new lib.PC_kusudama_canvas();
        rcCreateCanvas(exportRoot);
    }
}
if(appendFlg == true){
    $("head").append($("<script>").attr({
        src:jsSrc,
        type:"text/javascript"
    }));
}
}
function rcCreateCanvas(exportRoot){
    var stage = new createjs.Stage($("#canvas").get(0));
    $("#canvas").empty();
stage.addChild(exportRoot);
stage.update();
createjs.Ticker.setFPS(lib.properties.fps);
createjs.Ticker.addEventListener("tick", stage);
setTimeout(function(){
    if($('#PM0116_tekichu').dialog('isOpen')){
    showOmedetou();
    }
},6000);
}
function rcCreateOmedetoSubDailog(Jsondata) {
var omedetouHtml = '';
var tekityukaimeInfoList = Jsondata.RsultData;
omedetouHtml += '<tr>';
omedetouHtml += '<td colspan="6" class="b-l b-r b-t hei20">&nbsp;</td>';
omedetouHtml += '</tr>';
omedetouHtml += '<tr>';
omedetouHtml += '<td colspan="6" class="b-l b-r fsz24 bold al-c">的中した買い目</td>';
omedetouHtml += '</tr>';
omedetouHtml += '<tr>';
omedetouHtml += '<td colspan="6" class="b-l b-r">&nbsp;</td>';
omedetouHtml += '</tr>';
for (var i = 0; i < tekityukaimeInfoList.length; i++) {
var tekityukaimeInfo = tekityukaimeInfoList[i];
if(tekityukaimeInfo.hitFlg == 1){
omedetouHtml += '<tr>';
omedetouHtml += '<td class="al-l b-l spaser30"">&nbsp;</td>';
omedetouHtml += '<td class="al-l fsz20 bold v-al-t kakeshiki">' + $("<div>").append(tekityukaimeInfo.rsultBetType).text() + '</td>';
omedetouHtml += '<td class="al-l fsz20 bold v-al-b kumiban">' + rcEdtKumibann(tekityukaimeInfo.kumiban) + '</td>';
omedetouHtml += '<td class="al-l fsz20 bold v-al-b harai">払戻金</td>';
omedetouHtml += '<td class="al-r fsz20 bold v-al-b haraimoney">' + tekityukaimeInfo.totalRefundAmount + '</td>';
omedetouHtml += '<td class="al-r b-r spaser30">&nbsp;</td>';
omedetouHtml += '</tr>';
}
}
omedetouHtml += '<tr>';
omedetouHtml += '<td colspan="6" class="b-l b-r b-b hei30">&nbsp;</td>';
omedetouHtml += '</tr>';
$("#PM0116_tekityuKaimeInfo").empty();
$("#PM0116_tekityuKaimeInfo").html(omedetouHtml);
$('#PM0116_tekichu').dialog( 'open' );
};
$(document).on("click","#UNQ_skip",function(){
$('#PM0116_tekichu').dialog('close');
});
$(document).on("dialogclose","#PM0116_tekichu",function(){
$('#PM0116_omedetou').dialog('open');
});
function paInitialize(prmEn){
var prm = {};
prm.encp = prmEn;
paController.paCreateList(prm);
}
var paController = {
JSON_REQ_ID: "JSJ066",
paCreateList: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['encp'] = prm;
}
commonLoad.loadingImage("true");
Com.getRequestGet(paController.JSON_REQ_ID, params)
.done(function(result) {
paView.paDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#y3rentan').dialog( 'open' );
});
}
};
var paView = {
HDNKEY_ID: 'JSJ066',
paDrawJSONData: function(maindata,params) {
if(!maindata){
$('#padivGousya').addClass('dispoff');
$('#padivnodata').removeClass('dispoff');
Com.makePcUpdatePage("padivnodata", "", params, function(arg0){
paController.paCreateList(arg0);
}
);
return;
} else if ( maindata.resultCd == -1 ) {
$('#padivGousya').addClass('dispoff');
$('#padivnodata').removeClass('dispoff');
Com.makePcUpdatePage("padivnodata", paDataChecker(maindata.message), params, function(arg0){
paController.paCreateList(arg0);
}
);
return;
} else {
if(paDataChecker(maindata.lenDataExistFlg) == "false"){
$('#padivGousya').addClass('dispoff');
$('#padivnodata').removeClass('dispoff');
Com.makePcUpdatePage("padivnodata", "", params, function(arg0){
paController.paCreateList(arg0);
}
);
}else{
$('#padivGousya').removeClass('dispoff');
$('#padivnodata').addClass('dispoff');
var sunrentan = maindata.sanrentanShijiList;
var shijikubunMaster = ['全体','1着','2着','3着'];
var setDataDiv = $('#padivGousya');
var makeTable = "";
var makeTd = "";
var makeTbody = "";
var makeTr = "";
var shijikubun = "";
var shijiritu = "";
var syabanColor = "";
setDataDiv.empty();
for( var i_loop = 0; i_loop < Object.keys(sunrentan).length; i_loop++){
makeTable = $('<table>').addClass("y3rentan_tbl" + (i_loop + 1)).attr("style","width:" + 100 + "%;");
makeTd = $('<td>');
makeTbody = $('<tbody>');
makeTr = $('<tr>');
for( var j_loop = 0; j_loop < Object.keys(sunrentan[i_loop]).length; j_loop++){
shijiritu = sunrentan[i_loop][j_loop].shijiritu;
if(sunrentan[i_loop][j_loop].shijiFlg == true){
shijikubun = shijikubunMaster[sunrentan[i_loop][j_loop].shijikubun];
syabanColor = sunrentan[i_loop][j_loop].syabanColor[0];
makeTd.addClass(syabanColor).addClass('entry').attr("style","width:" + shijiritu + "%;")
if(sunrentan[i_loop][j_loop].syabanFlg == true){
makeTd.append(j_loop + 1);
}else{
makeTd.append("");
}
}else{
makeTd.addClass('dispoff');
}
makeTr.append(makeTd);
makeTd = $('<td>');
}
setDataDiv.append($('<table>').addClass("y3rentan_tbl" + (i_loop + 1)).append($('<tbody>')
.append($('<tr>').append($('<td>').addClass("title").attr("style","width : 40px;")
.append((shijikubun))).append($('<td>').append(makeTable.append(makeTbody.append(makeTr)))))));
}
}
}
return;
}
}
function paDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function ptInitialize(prmEn, prmSn){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
ptController.ptCreateList(prm);
}
function pwInitialize(prmEn, prmSn, prmsk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.skbn = prmsk;
PJ9103Controller.pwCreateList(prm);
}
var PJ9103Controller = {
JSON_REQ_ID: "JSJ068",
pwCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9103Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9103View.pwDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#kimarite').dialog( 'open' );
});
}
};
var PJ9103View = {
HDNKEY_ID: 'JSJ068',
pwDrawJSONData: function( jsondata, reqPrm) {
div_Success = '#pw_div'; 
div_Error = '#pw_err_div'; 
prm_div_Error = 'pw_err_div'; 
$(div_Success).html('');
$(div_Error).html('');
var kimari = [ "chaku", "nige", "makuri", "sasi", "mark"];
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9103Controller.pwCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9103Controller.pwCreateList(arg0);});
} else {
if(!jsondata.kimariteExistFlg){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Error).addClass('dispoff');
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml = '<div class="">';
outHtml += '<table class="kimarite_tbl">';
outHtml += '<tr>';
outHtml += '<td class="tbl_header">着</td>';
for( var i = 1; i < kimari.length; i++)
{
outHtml += '<td class="tbl_header">' + jsondata[ kimari[ i]].cdName + '</td>';
}
outHtml += '</tr>';
outHtml += '<tr>';
outHtml +='<td class="tbl_header">1着</td>';
for( var i = 1; i < kimari.length; i++)
{
outHtml += '<td class="bold">' + jsondata[ kimari[ i]].F_Cnt + '</td>';
}
outHtml += '</tr>';
outHtml += '<tr>';
outHtml+='<td class="tbl_header">2着</td>';
for( var i = 1; i < kimari.length; i++)
{
outHtml += '<td class="bold">' + jsondata[ kimari[ i]].S_Cnt + '</td>';
}
outHtml += '</tr>';
outHtml += '<tr>';
outHtml += '<td class="tbl_header">計</td>';
for( var i = 1; i < kimari.length; i++)
{
outHtml += '<td class="bold">' + jsondata[ kimari[ i]].Sum_Cnt + '</td>';
}
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</div>';
$(div_Success).html(outHtml);
}
return;
}
}
};
function pwDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function pbhInitialize(prmEn, prmSn, prmsk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.skbn = prmsk;
PJ9104Controller.pbhCreateList(prm);
}
function pbhgetParm(obj){
var para = {};
if( !$(".prm[name='encp']", obj)[0]) {
return;
}
para["encp"] = $(".prm[name='encp']", obj).val();
$('#B15').dialog( 'close' );
piInitialize(para);
}
function pbhSetEvent()
{
$(function(){
$("[id^=B15_tanten_click]").on( "click", function(){
pbhgetParm(this);
});
})
}
var PJ9104Controller = {
JSON_REQ_ID: "JSJ069",
pbhCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9104Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9104View.pbhDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#B15').dialog( 'open' );
});
}
};
var PJ9104View = {
HDNKEY_ID: 'JSJ069',
pbhDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#pbh_div'; 
div_Error = '#pbh_err_div'; 
prm_div_Error = 'pbh_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9104Controller.pbhCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9104Controller.pbhCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Success).html('');
$(div_Error).html('');
$(div_Error).addClass('dispoff');
if(pbhDataChecker(jsondata.bhDataExistFlg) == "false"){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml = '<div class="">';
outHtml += '<table class="B15_tbl">';
outHtml += '<tr>';
outHtml += '<td class="tbl_header">競輪場</td>';
outHtml += '<td class="tbl_header">グレード</td>';
outHtml += '<td class="tbl_header">開催日</td>';
outHtml += '<td class="tbl_header">R</td>';
outHtml += '<td class="tbl_header">種目</td>';
outHtml += '<td class="tbl_header">着</td>';
outHtml += '<td class="tbl_header">B</td>';
outHtml += '<td class="tbl_header">H</td>';
outHtml += '</tr>';
var tblBH = jsondata.tblBHRace;
for( var ilop = 0; ilop < tblBH.length; ilop++)
{
outHtml += '<tr class="clc" id="B15_tanten_click' + ilop +'">';
outHtml += '<td>' + tblBH[ ilop ].pbhlblKeirinjo;
outHtml += '<input type="hidden" name="encp" class="prm" value="' + tblBH[ ilop ].pbhPrmencp + '" />';
outHtml += '</td>';
outHtml += '<td class="grade">' + tblBH[ ilop ].pbhlblGrade + '</td>';
outHtml += '<td class="kdate">' + tblBH[ ilop ].pbhlblDate + '</td>';
outHtml += '<td>' + tblBH[ ilop ].pbhlblRace + '</td>';
outHtml += '<td>' + tblBH[ ilop ].pbhlblSyumoku + '</td>';
outHtml += '<td style="padding-top:0px"><p><img class="imgbadge_s4" src="' + tblBH[ ilop ].pbhimgTyakui + '"/></p></td>';
outHtml += '<td style="padding-top:5px" class="kigou">' + pbhConvBH( tblBH[ ilop ].pbhlblBacktori) + '</td>';
outHtml += '<td style="padding-top:5px" class="kigou">' + pbhConvBH( tblBH[ ilop ].pbhlblHometori) + '</td>';
outHtml += '</tr>';
}
outHtml += '</table>';
outHtml += '</div>';
$(div_Success).html(outHtml);
pbhSetEvent();
}
return;
}
}
};
function pbhDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function pbhConvBH(str) {
var ret;
ret = "&nbsp;";
if(str == undefined || str == null){
} else {
if( str == true)
{
ret = "○"
}
}
return ret;
}
function pscInitialize(prmEn, prmSn, prmsk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.skbn = prmsk;
PJ9105Controller.pscCreateList(prm);
}
function pscgetParm(obj){
var para = {};
if( !$(".prm[name='encp']", obj)[0]) {
return;
}
para["encp"] = $(".prm[name='encp']", obj).val();
$('#S17').dialog( 'close' );
piInitialize(para);
}
function pscSetEvent()
{
$(function(){
$("[id^=S17_tanten_click]").on( "click", function(){
pscgetParm(this);
});
})
}
var PJ9105Controller = {
JSON_REQ_ID: "JSJ070",
pscCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9105Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9105View.pscDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#S17').dialog( 'open' );
});
}
};
var PJ9105View = {
HDNKEY_ID: 'JSJ070',
pscDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#psc_div'; 
div_Error = '#psc_err_div'; 
prm_div_Error = 'psc_err_div'; 
$(div_Success).html('');
$(div_Error).html('');
var setPrm = null;
if(jsondata && jsondata.reqPrm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9105Controller.pscCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9105Controller.pscCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Error).addClass('dispoff');
if(pwDataChecker(jsondata.scDataExistFlg) == "false"){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml = '<div class="">';
outHtml += '<table class="S17_tbl">';
outHtml += '<tr>';
outHtml += '<td class="tbl_header">競輪場</td>';
outHtml += '<td class="tbl_header">グレード</td>';
outHtml += '<td class="tbl_header">開催日</td>';
outHtml += '<td class="tbl_header">R</td>';
outHtml += '<td class="tbl_header">種目</td>';
outHtml += '<td class="tbl_header">着</td>';
outHtml += '</tr>';
var tblS = jsondata.tblSRace;
for( var ilop = 0; ilop < tblS.length; ilop++)
{
outHtml += '<tr class="clc" id="S17_tanten_click' + ilop +'">';
outHtml += '<td>' + tblS[ ilop ].psclblKeirinjo;
outHtml += '<input type="hidden" name="encp" class="prm" value="' + tblS[ ilop ].pscPrmencp + '" />';
outHtml += '</td>';
outHtml += '<td class="grade">' + tblS[ ilop ].psclblGrade + '</td>';
outHtml += '<td class="kdate">' + tblS[ ilop ].psclblDate + '</td>';
outHtml += '<td>' + tblS[ ilop ].psclblRace + '</td>';
outHtml += '<td>' + tblS[ ilop ].psclblSyumoku + '</td>';
outHtml += '<td style="padding-top:0px"><p><img class="imgbadge_s4" src="' + tblS[ ilop ].pscimgTyakuiP + '" /></p></td>';
outHtml += '</tr>';
}
outHtml += '</table>';
outHtml += '</div>';
$(div_Success).html(outHtml);
pscSetEvent();
}
return;
}
}
};
function pscDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function psInitialize(prmEn, prmSn1, prmSn2){
var prm = {};
prm.encp = prmEn;
prm.snum1 = prmSn1;
prm.snum2 = prmSn2;
PJ9106Controller.psCreateList(prm);
}
function psgetParm(obj){
var para = {};
if( !$(".prm[name='encp']", obj)[0]) {
return;
}
para["encp"] = $(".prm[name='encp']", obj).val();
$('#taisen_seiseki2').dialog( 'close' );
piInitialize(para);
}
function psSetEvent()
{
$(function(){
$("[id^=taisen_seiseki2_tanten_click]").on( "click", function(){
psgetParm(this);
});
})
}
var PJ9106Controller = {
JSON_REQ_ID: "JSJ071",
psCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9106Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9106View.psDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#taisen_seiseki2').dialog( 'open' );
});
}
};
var PJ9106View = {
HDNKEY_ID: 'JSJ071',
psDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#ps_div'; 
div_Error = '#ps_err_div'; 
prm_div_Error = 'ps_err_div'; 
$(div_Success).html('');
$(div_Error).html('');
var setPrm = null;
if(jsondata && jsondata.reqPrm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9106Controller.psCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9106Controller.psCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Error).addClass('dispoff');
if(pwDataChecker(jsondata.psDataExistFlg) == "0"){
$(div_Success).addClass('dispoff');
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outhtml  = '<div class="" style="line-height:1">';
var tblDouji = jsondata.tblDoujiRace;
var back1 = "";
var back2 = "";
var cssWin1 ="";
var cssWin1atr ="";
var cssWin2atr ="";
var kima1 = "";
var kima2 = "";
for( var ilop = 0; ilop < tblDouji.length; ilop++)
{
if( ilop == 0){
outHtml += '<table class="taisen_seiseki2_tbl">';
outHtml += '<thead>';
outHtml += '<tr>';
outHtml += '<td class="tbl_header" style="width: 70px" rowspan="2">競輪場</td>';
outHtml += '<td class="tbl_header" style="width: 60px" rowspan="2">グレード</td>';
outHtml += '<td class="tbl_header" style="width:145px" rowspan="2">開催日</td>';
outHtml += '<td class="tbl_header" style="width: 30px" rowspan="2">R</td>';
outHtml += '<td class="tbl_header" style="width:110px" rowspan="2">種目</td>';
outHtml += '<td class="tbl_header" colspan="2">成績</td>';
outHtml += '</tr>';
outHtml += '<tr>';
outHtml += '<td class="tbl_header sname bold" style="width:110px">' + tblDouji[ ilop].psSensyu1_NM + '</td>';
outHtml += '<td class="tbl_header sname bold" style="width:110px">' + tblDouji[ ilop].psSensyu2_NM + '</td>';
outHtml += '</tr>';
outHtml += '</thead>';
outHtml += '<tbody>';
}
outHtml += '<tr class="clc" id="taisen_seiseki2_tanten_click' + ilop +'">';
outHtml += '<td>'+ tblDouji[ ilop].psJoNM;
outHtml += '<input type="hidden" name="encp" class="prm" value="' +tblDouji[ ilop].psPrmencp + '" />';
outHtml += '</td>';
outHtml += '<td>'+ tblDouji[ ilop].psGrade + '</td>';
outHtml += '<td>'+ tblDouji[ ilop].psKaisai + '</td>';
outHtml += '<td>'+ tblDouji[ ilop].psRaceNo + '</td>';
outHtml += '<td>'+ tblDouji[ ilop].psSyumoku + '</td>';
back1 = "";
back2 = "";
if( tblDouji[ ilop].psBack1 == "true")
{
back1 = "B";
}
if( tblDouji[ ilop].psBack2 == "true")
{
back2 = "B";
}
cssWin1 = "";
cssWin2 = "";
cssWin1atr = "";
cssWin2atr = "";
kima1 = "";
kima2 = "";
kima1 = tblDouji[ ilop].psKimari1;
kima2 = tblDouji[ ilop].psKimari2;
if( tblDouji[ ilop].psKachi1 == "true")
{
cssWin1 = " kachi";
cssWin1atr = " class=\"kachi\"";
}
if( tblDouji[ ilop].psKachi2 == "true")
{
cssWin2 = " kachi";
cssWin2atr = " class=\"kachi\"";
}
outHtml += '<td' + cssWin1atr + '>';
outHtml += '<div style="padding: 0 6px;">';
outHtml += '<table class="sub_taisen_seiseki2_tbl">';
outHtml += '<tr>';
outHtml += '<td class="at-r' + cssWin1 + '"><span>' + back1 + '</span></td>';
outHtml += '<td' + cssWin1atr + '>';
outHtml += '<p><img style="margin-top:-5px !important" class="imgbadge_s4" src="' + tblDouji[ ilop].psCyakui1P + '" /></p>';
outHtml += '</td>';
outHtml += '<td class="at-l' + cssWin1 + '"><span>'+ kima1 + '</span></td>';
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</div>';
outHtml += '</td>';
outHtml += '<td' + cssWin2atr + '>';
outHtml += '<div style="padding: 0 6px;">';
outHtml += '<table class="sub_taisen_seiseki2_tbl">';
outHtml += '<tr>';
outHtml += '<td class="at-r' + cssWin2 + '"><span>' + back2 +'</span></td>';
outHtml += '<td' + cssWin2atr+ '>';
outHtml += '<p><img style="margin-top:-5px !important" class="imgbadge_s4" src="' + tblDouji[ ilop].psCyakui2P + ' " /></p>';
outHtml += '</td>';
outHtml += '<td class="at-l' + cssWin2 + '"><span>'+ kima2 + '</span></td>';
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</div>';
outHtml += '</td>';
outHtml += '</tr>';
}
outHtml += '</tbody>';
outHtml += '</table>';
outHtml += '</div>';
$(div_Success).html(outHtml);
psSetEvent();
}
return;
}
}
};
function psDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function phInitialize(prmEn, prmSn, prmRank, prmSk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.fnid = prmRank;
prm.skbn = prmSk;
PJ9107Controller.phCreateList(prm);
}
function phgetParm(obj){
var para = {};
if( !$(".prm[name='encp']", obj)[0]) {
return;
}
para["encp"] = $(".prm[name='encp']", obj).val();
$('#chaku').dialog( 'close' );
piInitialize(para);
}
function phSetEvent()
{
$(function(){
$("[id^=chaku_tanten_click]").on( "click", function(){
phgetParm(this);
});
})
}
var PJ9107Controller = {
JSON_REQ_ID: "JSJ072",
phCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9107Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9107View.phDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#chaku').dialog( 'open' );
});
}
};
var PJ9107View = {
HDNKEY_ID: 'JSJ072',
phDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#ph_div'; 
div_Error = '#ph_err_div'; 
prm_div_Error = 'ph_err_div'; 
$(div_Success).html('');
$(div_Error).html('');
phAddCancelBtn( reqPrm.fnid);
var setPrm = null;
if(jsondata && jsondata.reqPrm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9107Controller.phCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9107Controller.phCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Error).addClass('dispoff');
if(pwDataChecker(jsondata.phDataExistFlg) == "false"){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml = '<div class="">';
outHtml += '<table class="chaku_tbl">';
outHtml += '<tr>';
outHtml += '<td class="tbl_header">競輪場</td>';
outHtml += '<td class="tbl_header">グレード</td>';
outHtml += '<td class="tbl_header">開催日</td>';
outHtml += '<td class="tbl_header">R</td>';
outHtml += '<td class="tbl_header">種目</td>';
outHtml += '<td class="tbl_header">成績</td>';
outHtml += '</tr>';
var tblT = jsondata.tblTyakuRace;
for( var ilop in tblT)
{
var lblBack =""; 
if( tblT[ ilop ].phBack == "true")
{
lblBack = "B";
}
outHtml += '<tr class="clc" id="chaku_tanten_click' + ilop +'">';
outHtml += '<td>' + tblT[ ilop ].phJoNM;
outHtml += '<input type="hidden" name="encp" class="prm" value="' + tblT[ ilop ].phPrmencp + '" />';
outHtml += '</td>';
outHtml += '<td class="grade">' + tblT[ ilop ].phGrade + '</td>';
outHtml += '<td class="kdate">' + tblT[ ilop ].phKaisai + '</td>';
outHtml += '<td>' + tblT[ ilop ].phRaceNo + '</td>';
outHtml += '<td>' + tblT[ ilop ].phSyumoku + '</td>';
outHtml += '<td>';
outHtml += '<div style="padding: 0 6px;">';
outHtml += '<table class="sub_chaku_tbl">';
outHtml += '<tr>';
if( tblT[ ilop ].phBack == "true") {
outHtml += '<td class="at-r bold"><p style="margin-top:-1px">B</p></td>';
} else {
outHtml += '<td class="at-r"><span></span></td>';
}
outHtml += '<td><p><img style="margin-top:-5px!important" class="imgbadge_s4" src="' + tblT[ ilop ].phCyakuiP + '" /></p></td>';
outHtml += '<td class="at-l bold"><p style="margin-top:-1px">' + tblT[ ilop ].phKimari + '</p></td>';
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</div>';
outHtml += '</td>';
outHtml += '</tr>';
}
outHtml += '</table>';
outHtml += '</div>';
$(div_Success).html(outHtml);
phSetEvent();
}
return;
}
}
};
function phDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function phAddCancelBtn( tyaku)
{
var lbl = "";
if( tyaku > 1) {
lbl = "～" + tyaku;
}
$( '.ui-dialog-cancel').remove();
$( '.sub_dlg_title').remove();
$( '.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="title">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('.ui-dialog-cancel').after('\
<div id="chaku_title" class="sub_dlg_title clear-fix">1' + lbl + '着時のレース一覧</div>\
');
}
function p1wInitialize(prmEn, prmSn, prmSk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.skbn = prmSk;
PJ9108Controller.p1wCreateList(prm);
}
var PJ9108Controller = {
JSON_REQ_ID: "JSJ073",
p1wCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9108Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9108View.p1wDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#tejun1').dialog( 'open' );
});
}
};
var PJ9108View = {
HDNKEY_ID: 'JSJ073',
p1wDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#p1w_div'; 
div_Error = '#p1w_err_div'; 
prm_div_Error = 'p1w_err_div'; 
div_table = '#p1w_tbluchiwake';
$(div_table).html('');
$(div_Error).html('');
var setPrm = null;
if(jsondata && jsondata.reqPrm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9108Controller.p1wCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9108Controller.p1wCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Error).addClass('dispoff');
if(pwDataChecker(jsondata.p1wDataExistFlg) == "false"){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml += '<tr>';
var idx = 0;
outHtml += p1wPutKimariteTD( jsondata.p1wtblNige, jsondata.p1wKimarite, jsondata.p1wKimarite.nigeNM, jsondata.p1wKimarite.nigeClass, idx);
outHtml += p1wPutKimariteTD( jsondata.p1wtblMakuri, jsondata.p1wKimarite, jsondata.p1wKimarite.makuriNM, jsondata.p1wKimarite.makuriClass, idx);
outHtml += p1wPutKimariteTD( jsondata.p1wtblSasi, jsondata.p1wKimarite, jsondata.p1wKimarite.sasiNM, jsondata.p1wKimarite.sasiClass, idx);
outHtml += p1wPutKimariteTD( jsondata.p1wtblMark, jsondata.p1wKimarite, jsondata.p1wKimarite.markNM, jsondata.p1wKimarite.markClass, idx);
outHtml += '</tr>';
outHtml += '</table>';
$(div_table).html(outHtml);
p1wEdtUchiwakeBoder();
}
return;
}
}
};
function p1wDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function p1wPutKimariteTD( objKte, objKDsp, kNM, kCls) {
var outHtml = '';
if( objKte.fFlg == "true"){
var span = (function( col){
if( col > 1){
return ' colspan="' + col + '"';
} else {
return('');
}
})( objKte.fFlgCnt);
var k_css = '';
var k_lbl = '&nbsp;';
if( objKte.fLblFlg == "true"){
k_css = ' class="' + kCls + ' bold"';
k_lbl = kNM;
} else {
k_css = ' class="' + kCls + '"';
}
outHtml += '<td style="width:' + objKte.fSize + '%;">';
outHtml += '<table>';
outHtml += '<tr>';
outHtml += '<td' + span + k_css + '>' + k_lbl + '</td>';
outHtml += '</tr>';
outHtml += '<tr>';
outHtml += p1wPutAiteTD( objKDsp.nigeClass, objKte.fs_NigeFlg, objKte.fs_NigeLbl, objKte.fs_NigeSize);
outHtml += p1wPutAiteTD( objKDsp.makuriClass, objKte.fs_MakuriFlg, objKte.fs_MakuriLbl, objKte.fs_MakuriSize);
outHtml += p1wPutAiteTD( objKDsp.sasiClass, objKte.fs_SasiFlg, objKte.fs_SasiLbl, objKte.fs_SasiSize);
outHtml += p1wPutAiteTD( objKDsp.markClass, objKte.fs_MarkFlg, objKte.fs_MarkLbl, objKte.fs_MarkSize);
outHtml += p1wPutAiteTD( objKDsp.nasiClass, objKte.fs_NasiFlg, objKte.fs_NasiLbl, objKte.fs_NasiSize);
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</td>';
}
return outHtml;
}
function p1wPutAiteTD( ccl, flg, lbl, size) {
var outHtml = '';
if( flg == "true"){
outHtml += '<td class="' + ccl + '" style="width: ' + size + '%;">';
if( lbl == "true"){
outHtml += '<p class="bold">' + size + '</p>';
}
outHtml += '</td>';
}
return outHtml;
}
function p1wEdtUchiwakeBoder() {
$('#p1w_tbluchiwake tr td table').addClass('dwb-l dwb-t dwb-b');
$('#p1w_tbluchiwake tr td table tr:odd').addClass('dwb-t');
$('#p1w_tbluchiwake tr td table:last').addClass('dwb-r');
}
function p2wInitialize(prmEn, prmSn, prmSk){
var prm = {};
prm.encp = prmEn;
prm.snum = prmSn;
prm.skbn = prmSk;
PJ9109Controller.p2wCreateList(prm);
}
var PJ9109Controller = {
JSON_REQ_ID: "JSJ074",
p2wCreateList: function(prm) {
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9109Controller.JSON_REQ_ID, prm)
.done(function(result) {
PJ9109View.p2wDrawJSONData(result,prm);
commonLoad.loadingImage("false");
$('#tejun2').dialog( 'open' );
});
}
};
var PJ9109View = {
HDNKEY_ID: 'JSJ074',
p2wDrawJSONData: function(jsondata, reqPrm) {
div_Success = '#p2w_div'; 
div_Error = '#p2w_err_div'; 
prm_div_Error = 'p2w_err_div'; 
div_table = '#p2w_tbluchiwake';
$(div_table).html('');
$(div_Error).html('');
var setPrm = null;
if(jsondata && jsondata.reqPrm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if(!jsondata || Object.keys(jsondata).length == 0) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_Error, null, setPrm, function(arg0){PJ9109Controller.p2wCreateList(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff');
var message = "";
if( jsondata.message != 'undefaind' ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_Error, message, setPrm, function(arg0){PJ9109Controller.p2wCreateList(arg0);});
} else {
$(div_Success).removeClass('dispoff');
$(div_Error).addClass('dispoff');
$(div_Error).addClass('dispoff');
if(pwDataChecker(jsondata.p2wDataExistFlg) == "false"){
var outHtml = "";
outHtml += '<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">';
 outHtml += '<p class="place list-inline">'+jsondata.message+'</p>';
 outHtml += '</div>';
$(div_Error).html(outHtml);
$(div_Success).addClass('dispoff');
$(div_Error).removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
}else{
$(div_Success).removeClass('dispoff');
var outHtml = "";
outHtml += '<tr>';
var idx = 0;
outHtml += p2wPutKimariteTD( jsondata.p2wtblNige, jsondata.p2wKimarite, jsondata.p2wKimarite.nigeNM, jsondata.p2wKimarite.nigeClass, idx);
outHtml += p2wPutKimariteTD( jsondata.p2wtblMakuri, jsondata.p2wKimarite, jsondata.p2wKimarite.makuriNM, jsondata.p2wKimarite.makuriClass, idx);
outHtml += p2wPutKimariteTD( jsondata.p2wtblSasi, jsondata.p2wKimarite, jsondata.p2wKimarite.sasiNM, jsondata.p2wKimarite.sasiClass, idx);
outHtml += p2wPutKimariteTD( jsondata.p2wtblMark, jsondata.p2wKimarite, jsondata.p2wKimarite.markNM, jsondata.p2wKimarite.markClass, idx);
outHtml += '</tr>';
outHtml += '</table>';
$(div_table).html(outHtml);
p2wEdtUchiwakeBoder();
}
return;
}
}
};
function p2wDataChecker(str) {
var ret;
if(str == undefined || str == null){
ret = "";
} else {
ret = str;
}
return ret;
}
function p2wPutKimariteTD( objKte, objKDsp, kNM, kCls) {
var outHtml = '';
if( objKte.fFlg == "true"){
var span = (function( col){
if( col > 1){
return ' colspan="' + col + '"';
} else {
return('');
}
})( objKte.fFlgCnt);
var k_css = '';
var k_lbl = '&nbsp;';
if( objKte.fLblFlg == "true"){
k_css = ' class="' + kCls + ' bold"';
k_lbl = kNM;
} else {
k_css = ' class="' + kCls + '"';
}
outHtml += '<td style="width:' + objKte.fSize + '%;">';
outHtml += '<table>';
outHtml += '<tr>';
outHtml += p2wPutAiteTD( objKDsp.nigeClass, objKte.fs_NigeFlg, objKte.fs_NigeLbl, objKte.fs_NigeSize);
outHtml += p2wPutAiteTD( objKDsp.makuriClass, objKte.fs_MakuriFlg, objKte.fs_MakuriLbl, objKte.fs_MakuriSize);
outHtml += p2wPutAiteTD( objKDsp.sasiClass, objKte.fs_SasiFlg, objKte.fs_SasiLbl, objKte.fs_SasiSize);
outHtml += p2wPutAiteTD( objKDsp.markClass, objKte.fs_MarkFlg, objKte.fs_MarkLbl, objKte.fs_MarkSize);
outHtml += '</tr>';
outHtml += '<tr>';
outHtml += '<td' + span + k_css + '>' + k_lbl + '</td>';
outHtml += '</tr>';
outHtml += '</table>';
outHtml += '</td>';
}
return outHtml;
}
function p2wPutAiteTD( ccl, flg, lbl, size) {
var outHtml = '';
if( flg == "true"){
outHtml += '<td class="' + ccl + '" style="width: ' + size + '%;">';
if( lbl == "true"){
outHtml += '<p class="bold">' + size + '</p>';
}
outHtml += '</td>';
}
return outHtml;
}
function p2wEdtUchiwakeBoder() {
$('#p2w_tbluchiwake tr td table').addClass('dwb-l dwb-t dwb-b');
$('#p2w_tbluchiwake tr td table tr:odd').addClass('dwb-t');
$('#p2w_tbluchiwake tr td table:last').addClass('dwb-r');
}
$(document).ready(function(){
    $.each(["addClass","removeClass"],function(i,methodname){
        var oldmethod = $.fn[methodname];
        $.fn[methodname] = function(e){
            oldmethod.apply(this,arguments);
            var txt = e;
            if(txt&&~txt.indexOf('dispoff')){
            txt="dispoff";
            this.trigger(methodname+"Event" + txt);
            }
            return this;
        }
    });
    var funcPT0511Add = function(e){
if("PT0511"== e.target.id){
$("#ozzArea").addClass("dispoff");
        }
    };
    var funcPT0511Rem = function(e){
if("PT0511"== e.target.id){
$("#ozzArea").addClass("dispoff");
    }
    };
    $("#PT0511").on("addClassEventdispoff",funcPT0511Add);
    $("#PT0511").on("removeClassEventdispoff",funcPT0511Rem);
});
var bcStart = {
swichOzzDisplay : function() {
$("#ozzArea").addClass("dispoff");
if (ozzStartFlg === "1") {
var dtd1 = $.Deferred();
var wait1 = function(dtd1) {
bcController.getKakesikiInfo(dtd1);
return dtd1.promise();
};
var dtd2 = $.Deferred();
var wait2 = function(dtd2) {
otController.getSyusohyoInfo(dtd2);
return dtd2.promise();
}
$.when(wait1(dtd1)).then(function() {
$.when(wait2(dtd2)).then(function() {
o3tController.getOzzInfo();
});
});
} else {
bcView.kakesikiChangeStart();
otView.syusohyoStart();
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (kakesikiKbn == "6") {
o3tView.ozz3RentanStart();
} else if (kakesikiKbn == "2") {
o2tView.ozz2SyatanStart();
} else if (kakesikiKbn == "7") {
o3fView.ozz3RenhukuStart();
} else if (kakesikiKbn == "4") {
o2fView.ozz2SyahukuStart();
} else if (kakesikiKbn == "3") {
owtView.ozz2WakutanStart();
} else if (kakesikiKbn == "1") {
owfView.ozz2WakuhukuStart();
} else if (kakesikiKbn == "5") {
owView.ozzWideStart();
}
$("#ozzArea").removeClass('dispoff');
}
$("button[id^='btnKake']").click(function() {
if ($(this).hasClass("btn onbtn al-c")) {
if ($(this).hasClass("active")) {
} else {
bcView.doKaimeDel($(this), "1");
}
}
return false;
});
$("button[id^='btnHyoji']").click(function() {
if ($(this).hasClass("btn onbtn al-c")) {
if ($(this).hasClass("active")) {
} else {
bcView.doKaimeDel($(this), "2");
}
}
return false;
});
}
}
var bcController = {
JSON_015_ID : "JST015",
getKakesikiInfo : function(dtd) {
var result = null;
var params = {};
if(parentFuncId == "FPT0001"){
params["mode"] = "1";
}else if(parentFuncId == "FPJ0315"){
params["mode"] = "0";
}else{
params["mode"] = "2";
}
params["encp"] = gPrmParaR;
Com.getRequestGet(bcController.JSON_015_ID, params).done(function(result) {
$("#ozzJst015ErrMsg").remove();
if(!result || result.resultCd == -1){
if(jst015Maindata){
jst015Maindata.resultCd = -1;
}else{
jst015Maindata = {"resultCd":-1};
}
$("#ozzArea > div").addClass("dispoff");
if(parentFuncId == "FPT0001"){
$("#ozzArea").append('<span id="ozzJst015ErrMsg" class="empcolor_red">ただいま、オッズ投票は行えません。</span>');
}else{
$("#ozzArea").append('<span id="ozzJst015ErrMsg" class="empcolor_red">オッズ情報が受信できませんでした。</span>');
}
}else{
jst015Maindata = result;
$("#ozzArea > div").removeClass("dispoff");
}
bcView.kakesikiChangeStart();
dtd.resolve(result);
});
}
};
var bcView = {
kakesikiChangeStart : function() {
if (jst015Maindata.resultCd == -1) {
return false;
}
var kakesikiKbn = jst015Maindata.data['kakesikiKbn'];
var dispKbn = jst015Maindata.data['dispKbn'];
if (jst015Maindata.data['hatubai3Rentan'] == 1) {
$("#btnKake3Rentan").show();
} else if (jst015Maindata.data['hatubai3Rentan'] == 0) {
$("#btnKake3Rentan").hide();
}
if (jst015Maindata.data['hatubai2Syatan'] == 1) {
$("#btnKake2Syatan").show();
} else if (jst015Maindata.data['hatubai2Syatan'] == 0) {
$("#btnKake2Syatan").hide();
}
if (jst015Maindata.data['hatubai3Renhuku'] == 1) {
$("#btnKake3Renhuku").show();
} else if (jst015Maindata.data['hatubai3Renhuku'] == 0) {
$("#btnKake3Renhuku").hide();
}
if (jst015Maindata.data['hatubai2Syahuku'] == 1) {
$("#btnKake2Syahuku").show();
} else if (jst015Maindata.data['hatubai2Syahuku'] == 0) {
$("#btnKake2Syahuku").hide();
}
if (jst015Maindata.data['hatubai2Wakutan'] == 1) {
$("#btnKake2Wakutan").show();
} else if (jst015Maindata.data['hatubai2Wakutan'] == 0) {
$("#btnKake2Wakutan").hide();
}
if (jst015Maindata.data['hatubai2Wakuhuku'] == 1) {
$("#btnKake2Wakuhuku").show();
} else if (jst015Maindata.data['hatubai2Wakuhuku'] == 0) {
$("#btnKake2Wakuhuku").hide();
}
if (jst015Maindata.data['hatubaiWide'] == 1) {
$("#btnKakeWide").show();
} else if (jst015Maindata.data['hatubaiWide'] == 0) {
$("#btnKakeWide").hide();
}
$("button[id^='btnKake']").removeClass("active");
if (kakesikiKbn == 6) {
$("#btnKake3Rentan").addClass("active");
} else if (kakesikiKbn == 2) {
$("#btnKake2Syatan").addClass("active");
} else if (kakesikiKbn == 7) {
$("#btnKake3Renhuku").addClass("active");
} else if (kakesikiKbn == 4) {
$("#btnKake2Syahuku").addClass("active");
} else if (kakesikiKbn == 3) {
$("#btnKake2Wakutan").addClass("active");
} else if (kakesikiKbn == 1) {
$("#btnKake2Wakuhuku").addClass("active");
} else if (kakesikiKbn == 5) {
$("#btnKakeWide").addClass("active");
}
$("button[id^='btnHyoji']").removeClass("active");
if (dispKbn == 1) {
$("#btnHyojiHyojun").addClass("active");
if ($('#divOzzSearch').hasClass("dispon")) {
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
}
} else if (dispKbn == 2) {
$("#btnHyojiNinOrder").addClass("active");
if ($('#divOzzSearch').hasClass("dispon")) {
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
}
} else if (dispKbn == 3) {
$("#btnHyojiOzzSearch").addClass("active");
if ($('#divHyojunNinki').hasClass("dispon")) {
$('#divHyojunNinki').removeClass("dispon");
$('#divHyojunNinki').addClass("dispoff");
$('#divOzzSearch').addClass("dispon");
}
}
},
doKaimeDel : function(it, flg) {
var mode = comKaime.kimGetEditMode();
var editKaimeGroup = comKaime.kimGetNoSetKaimeGroup();
var id = it.attr("id");
if ((mode == 2 || mode == 5)  && editKaimeGroup != null
&& (flg == "1" || (flg == "2" && id == "btnHyojiOzzSearch"))) {
$(document).off("click", ".ui-widget-overlay");
$('#conf_cancel').dialog('open');
$('#ozz_ok_btn').click(function() {
comKaime.kimClearTmp();
if (flg == "1") {
bcView.doKakesikiChg(it);
} else {
bcView.doDispChg(it);
}
$('#ozz_ok_btn').unbind("click");
$('#ozz_cancel_btn').unbind("click");
$('#conf_cancel').dialog('close');
return false;
});
$('#ozz_cancel_btn').click(function() {
$('#ozz_ok_btn').unbind("click");
$('#ozz_cancel_btn').unbind("click");
$('#conf_cancel').dialog('close');
return false;
});
} else {
if (flg == "1") {
bcView.doKakesikiChg(it);
} else {
bcView.doDispChg(it);
}
}
return false;
},
doKakesikiChg : function(it) {
$("button[id^='btnKake']").removeClass("active");
it.addClass("active");
var id = it.attr("id");
commonLoad.loadingImage("true");
if (id == "btnKake3Rentan") {
jst015Maindata.data.kakesikiKbn = "6";
} else if (id == "btnKake2Syatan") {
jst015Maindata.data.kakesikiKbn = "2";
} else if (id == "btnKake3Renhuku") {
jst015Maindata.data.kakesikiKbn = "7";
} else if (id == "btnKake2Syahuku") {
jst015Maindata.data.kakesikiKbn = "4";
} else if (id == "btnKake2Wakutan") {
jst015Maindata.data.kakesikiKbn = "3";
} else if (id == "btnKake2Wakuhuku") {
jst015Maindata.data.kakesikiKbn = "1";
} else if (id == "btnKakeWide") {
jst015Maindata.data.kakesikiKbn = "5";
}
var dtd = $.Deferred();
var wait = function(dtd) {
otController.getSyusohyoInfo(dtd);
return dtd.promise();
};
var dispKbn = jst015Maindata.data.dispKbn;
if (dispKbn == "1") {
$.when(wait(dtd)).done(function() {
o3tController.getOzzInfo();
});
} else if (dispKbn == "2") {
$.when(wait(dtd)).done(function() {
opController.getNinkiOrderInfo();
});
} else if (dispKbn == "3") {
osView.ozzSearchStart();
}
if (parentFuncId == "FPT0001") {
PT0202Controller.cPT0202btnOzzSearch(jst015Maindata);
}
},
doDispChg : function(it) {
$("button[id^='btnHyoji']").removeClass("active");
it.addClass("active");
var id = it.attr("id");
commonLoad.loadingImage("true");
var dtd = $.Deferred();
var wait = function(dtd) {
otController.getSyusohyoInfo(dtd);
return dtd.promise();
};
if (id == "btnHyojiHyojun") {
jst015Maindata.data.dispKbn = "1";
$.when(wait(dtd)).done(function() {
o3tController.getOzzInfo();
});
} else if (id == "btnHyojiNinOrder") {
jst015Maindata.data.dispKbn = "2";
$.when(wait(dtd)).done(function() {
opController.getNinkiOrderInfo();
});
} else if (id == "btnHyojiOzzSearch") {
jst015Maindata.data.dispKbn = "3";
osView.ozzSearchStart();
}
if (parentFuncId == "FPT0001") {
PT0202Controller.cPT0202btnOzzSearch(jst015Maindata);
}
}
};
var otController = {
JSON_010_ID : "JST010",
getSyusohyoInfo : function(dtd) {
var result = null;
var params = {};
if (!jst015Maindata || jst015Maindata.resultCd == -1) {
dtd.resolve(result);
return false;
} 
params["url.media.flg"] = "1";
params["encp"] = gPrmParaR;
Com.getRequestGet(otController.JSON_010_ID, params).done(function(result) {
if(!result || result.resultCd == -1){
if(jst010Maindata){
jst010Maindata.resultCd = -1;
}else{
jst010Maindata = {"resultCd":-1};
}
}else{
jst010Maindata = result;
}
otView.syusohyoStart();
dtd.resolve(result);
});
}
}
var otView = {
syusohyoStart : function() {
if( jst010Maindata.resultCd == -1 ) {
$('#syusou_table').html("");
return false;
}
var jst010Data = jst010Maindata.data;
var sensyuList = jst010Maindata.data.sensyuInfoList;
var outWakuban = "";
var outSyaban = '<td class="tbl_header2">車番</td>';
var outSensyuMei = '<td class="tbl_header2">選手名</td>';
var outKetuJyo = '<td class="tbl_header2"></td>';
var outHuken = '<td class="tbl_header2">府県</td>';
var outKyuhan = '<td class="tbl_header2">級班/脚質</td>';
if (jst010Data.wakuKbn == "1"){
outWakuban += '<tr>';
outWakuban = '<td class="tbl_header2 b-b">枠番</td>';
var wkWakuban = sensyuList[0].wakuBan;
var wkSyacnt = 0;
for (var i = 0; i < sensyuList.length; i++) {
if (wkWakuban == sensyuList[i].wakuBan){
wkSyacnt = wkSyacnt + 1;
}else{
outWakuban +=  '<td colspan=' + wkSyacnt + ' class="al-c b-b">' + wkWakuban + '</td>';
wkSyacnt = 1;
}
wkWakuban = sensyuList[i].wakuBan;
}
outWakuban +=  '<td colspan=' + wkSyacnt + ' class="al-c b-b">' + wkWakuban + '</td>';
outStr += '</tr>';
}
var ketujyoFlg = 0;
for (var i = 0; i < sensyuList.length; i++) {
var syaban = sensyuList[i].syaban;
var syaColor1 = sensyuList[i].syabanColor1;
var syaColor2 = sensyuList[i].syabanColor2;
outSyaban += '<td class="' + syaColor2 + ' al-c"><div class="lnum ' + syaColor1 + '">' + syaban + '</div></td>';
var sensyuMei = sensyuList[i].sensyuSei3Char;
if (jst015Maindata.data.kakesikiKbn == "6" && jst015Maindata.data.dispKbn == "1"){
outSensyuMei += '<td class="'+ syaColor2 +' al-c"><a class="txt_underline" id="o3tLnkSyaban' + syaban + '" value="o3tSyaban' + syaban + '">' + sensyuMei + '</a></td>';
}else{
outSensyuMei += '<td class="'+ syaColor2 +' al-c">' + sensyuMei + '</td>';
}
outKetuJyo　+= '<td class="' + syaColor2 + ' al-c ' + sensyuList[i].colorCd +'">'+ sensyuList[i].kejyoHojyuAdd +'</td>';
var huken = sensyuList[i].huken3Char;
outHuken += '<td class="' + syaColor2 + ' al-c">' + huken + '</td>';
var kyuhan = sensyuList[i].kyuhan2Char;
var kyasitu = sensyuList[i].kyasitu1Char;
outKyuhan += '<td class="' + syaColor2 + ' al-c">' + kyuhan + '/' + kyasitu + '</td>';
}
var out = document.getElementById("syusou_table");
var outStr = '<table class="syusou_list_tbl">';
if (jst015Maindata.data.kakesikiKbn == "3" || jst015Maindata.data.kakesikiKbn == "1"){
outStr += outWakuban;
}
outStr += '<tr>';
outStr += outSyaban;
outStr += '</tr>';
outStr += '<tr>';
outStr += outSensyuMei;
outStr += '</tr>';
outStr += '<tr>';
outStr += outKetuJyo;
outStr += '</tr>';
outStr += '<tr>';
outStr += outHuken;
outStr += '</tr>';
outStr += '<tr>';
outStr += outKyuhan;
outStr += '</tr>';
outStr += "</table>";
out.innerHTML=outStr;
if (jst015Maindata.data.kakesikiKbn == "6" && jst015Maindata.data.dispKbn == "1"){
$("a[id^='o3tLnkSyaban']").click( function() {
var value = $(this).attr("value");
document.getElementById("ozz_table").scrollTop = document.getElementById(value).offsetTop;
return false;
});
}
}
}
$(function() {
$('#btnOzzUpd').click(function() {
doubleClick($(this).attr("id"));
commonLoad.loadingImage("true");
var dtd = $.Deferred();
var wait = function(dtd) {
otController.getSyusohyoInfo(dtd);
return dtd.promise();
};
$.when(wait(dtd)).done(function() {
var dispKbn = jst015Maindata.data.dispKbn;
if (dispKbn == "1") {
o3tController.getOzzInfo();
} else if (dispKbn == "2") {
opController.getNinkiOrderInfo();
} else if (dispKbn == "3") {
}
});
return false;
});
})
var o3tController = {
JSON_011_ID : "JST011",
JSON_017_ID : "JST017",
getOzzInfo : function() {
var result = null;
var params = {};
if (!jst015Maindata|| jst015Maindata.resultCd == -1 
|| !jst010Maindata || jst010Maindata.resultCd == -1) {
if (parentFuncId == "FPT0001") {
$('#ozz_table').html("ただいま、オッズ投票は行えません。");
}else{
$('#ozz_table').html("オッズ情報が受信できませんでした。");
}
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
$("#ozzArea").removeClass('dispoff');
commonLoad.loadingImage("false");
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
if (jst015Maindata.data.kakesikiKbn == "6") {
anaOddsType = "PT0511";
} else if (jst015Maindata.data.kakesikiKbn == "2") {
anaOddsType = "PT0512";
} else if (jst015Maindata.data.kakesikiKbn == "7") {
anaOddsType = "PT0513";
} else if (jst015Maindata.data.kakesikiKbn == "4") {
anaOddsType = "PT0514";
} else if (jst015Maindata.data.kakesikiKbn == "3") {
anaOddsType = "PT0515";
} else if (jst015Maindata.data.kakesikiKbn == "1") {
anaOddsType = "PT0516";
} else if (jst015Maindata.data.kakesikiKbn == "5") {
anaOddsType = "PT0517";
}
params["kake"] = jst015Maindata.data.kakesikiKbn;
params["mode"] = jst015Maindata.data.mode;
params["encp"] = gPrmParaR;
var dtd = $.Deferred();
var wait = function(dtd) {
o3tController.reqOzzInfo(dtd, o3tController.JSON_011_ID, params);
return dtd.promise();
};
$.when(wait(dtd))
.done(function(result) {
jst011Maindata = result;
if(parentFuncId == "FPT0001"){
PT0202View.btnControl();
}
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1 
|| !jst011Maindata.data) {
if (parentFuncId == "FPT0001") {
$('#ozz_table').html("ただいま、オッズ投票は行えません。");
}else{
$('#ozz_table').html("オッズ情報が受信できませんでした。");
}
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
$("#ozzArea").removeClass('dispoff');
commonLoad.loadingImage("false");
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
if (jst011Maindata.data
&& jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
$("#ozzArea").removeClass('dispoff');
commonLoad.loadingImage("false");
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (kakesikiKbn == "6") {
o3tView.ozzTableCreate();
} else if (kakesikiKbn == "2") {
o2tView.ozzTableCreate();
} else if (kakesikiKbn == "7") {
o3fView.ozzTableCreate();
} else if (kakesikiKbn == "4") {
o2fView.ozzTableCreate();
} else if (kakesikiKbn == "3") {
owtView.ozzTableCreate();
} else if (kakesikiKbn == "1") {
owfView.ozzTableCreate();
} else if (kakesikiKbn == "5") {
owView.ozzTableCreate();
}
o3tView.ozzDataSet();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
$("#ozzArea").removeClass('dispoff');
commonLoad.loadingImage("false");
});
},
reqOzzInfo : function(dtd,JSON_ID,params){
var retData='';
Com.getRequestGet(JSON_ID, params)
.done(function(result){
retData = result;
if (!retData 
|| retData.resultCd == -1 
|| !retData.data) {
dtd.resolve(retData);
}
if (parentFuncId == "FPT0001"
&& !(retData.data.karaGamenFlg == "1")
&& retData.data.hatubaiStatus == "1") {
Com.getRequestGet(o3tController.JSON_017_ID, params)
.done( function(result){
var tmpData = result;
if (!tmpData 
|| tmpData.resultCd == -1 
|| !tmpData.data) {
retData.resultCd = -1
dtd.resolve(retData);
}else{
retData.data.hatubaiStatus = tmpData.data.hatubaiStatus;
retData.data.errorMsg = tmpData.data.errorMsg;
retData.data.ozzHyojiFlg=tmpData.data.ozzHyojiFlg;
if ("1"==tmpData.data.guideMsgHyojiFlg){
retData.data.guideMsgHyojiFlg = "1";
}
dtd.resolve(retData);
}
});
}else{
dtd.resolve(retData);
}
});
},
}
var o3tView = {
ozz3RentanStart : function() {
if (jst011Maindata.data == null
|| jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#lblGuideMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
o3tView.ozzTableCreate();
o3tView.ozzDataSet();
return false;
},
ozzTableCreate : function() {
if ($('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').removeClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var syaCnt = jst010Maindata.data.syaCnt;
var sensyuList = jst010Maindata.data.sensyuInfoList;
var outStr = '<table class="ozu_tbl">';
var col = syaCnt * 3 + 1;
var rol = syaCnt - 2;
var cellColor;
var lnkSyabanId;
for (var i = 1; i <= syaCnt; i++) {
cellColor = sensyuList[i-1].syabanColor1;
lnkSyabanId = "o3tSyaban" + i;
outStr += '<tr><td  id= ' + lnkSyabanId + ' class=' + cellColor
+ ' align="center" colspan=' + col + '>' + i + '</td></tr>';
for (var j = 1; j <= rol; j++) {
outStr += "<tr>";
if (j == 1) {
outStr += '<td class=' + cellColor + ' rowspan=' + rol
+ '>' + i + '</td>';
}
for (var k = 1; k <= syaCnt; k++) {
if (k != i) {
cellColor = sensyuList[k-1].syabanColor1;
if (j == 1) {
outStr += '<td class=' + cellColor + ' rowspan='
+ rol + '>' + k + '</td>';
}
var dd = 1;
for (var l = 1; l <= syaCnt; l++) {
if (l != k && l != i) {
if (dd == j) {
outStr += '<td class=' + cellColor + '>'
+ l + '</td>';
var kumiban = "OZZ" + i + k + l
var ozzColor = sensyuList[i-1].syabanColor2 + " o3twd";
if (jst011Maindata.data.ozzHyojiFlg == "1") {
ozzColor += " btn";
}
outStr += '<td  class="' + ozzColor
+ '" id=' + kumiban
+ ' name="lblOzzName"></td>';
}
dd = dd + 1;
}
}
}
}
outStr += "</tr>";
}
}
outStr += "</table>";
out.innerHTML = outStr;
},
ozzDataSet : function() {
var ozzData = "";
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (kakesikiKbn == "6") {
ozzData = jst011Maindata.data.ozz3RentanData;
} else if (kakesikiKbn == "2") {
ozzData = jst011Maindata.data.ozz2SyatanData;
} else if (kakesikiKbn == "7") {
ozzData = jst011Maindata.data.ozz3RenhukuData;
} else if (kakesikiKbn == "4") {
ozzData = jst011Maindata.data.ozz2SyahukuData;
} else if (kakesikiKbn == "3") {
ozzData = jst011Maindata.data.ozz2WakutanData;
} else if (kakesikiKbn == "1") {
ozzData = jst011Maindata.data.ozz2WakuhukuData;
} else if (kakesikiKbn == "5") {
ozzData = jst011Maindata.data.ozzWideData;
}
comKaime.kimChangePrimeKey(jst015Maindata.data.kaisaiDate,
jst015Maindata.data.keirinJyoCd, jst015Maindata.data.raceNo,
jst015Maindata.data.kakesikiKbn, ozzData.UP_DATE);
var date = ozzData.UP_DATE;
if (date != null) {
var hour = date.substr(8, 2);
var minutes = date.substr(10, 2);
var time = hour + ":" + minutes + " 現在";
$('#lblGettime').html(time);
$('#lblGettime').show();
} else {
$('#lblGettime').hide();
}
if (jst011Maindata.data.updateStopMsgHyojiFlg == "0") {
$('#lblUpdateStopMsg').show();
$('#lblUpdateStopMsg').html(jst011Maindata.data.updateStopMsg);
} else {
$('#lblUpdateStopMsg').hide();
}
if (jst011Maindata.data.guideMsgHyojiFlg == "0") {
$('#lblGuideMsg').show();
$('#lblGuideMsg').html(jst011Maindata.data.guideMsg);
} else {
$('#lblGuideMsg').hide();
}
if (jst011Maindata.data.errorMsg != null) {
$('#lblErrorMsg').show();
var errorMsg = "<br/>" + jst011Maindata.data.errorMsg;
$('#lblErrorMsg').html(errorMsg);
} else {
$('#lblErrorMsg').hide();
}
if (jst011Maindata.data.btnOzzUpdHyojiFlg != "0") {
$('#btnOzzUpd').hide();
} else {
$('#btnOzzUpd').show();
}
var cnt = ozzData.HYOSUM_CNT;
var hyosumCnt = "発売票数：";
if (cnt != null) {
hyosumCnt += o3tView.formatNum(cnt.toString());
$('#lblHatubaiCnt').html(hyosumCnt);
$('#lblHatubaiCnt').show();
}
var out = document.getElementsByName("lblOzzName");
for (var l = 0; l < out.length; l++) {
var wkId = out[l].attributes['id'].value;
var ozz = "";
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, wkId);
if (kesyaFlg == 1) {
ozz = "-----";
} else {
if (kakesikiKbn == "5") {
var dnId = "DN_" + wkId;
var tpId = "TP_" + wkId;
var DN_ozz = ozzData[dnId];
var TP_ozz = ozzData[tpId];
if (DN_ozz == null) {
DN_ozz = "";
} else if (DN_ozz.toString().indexOf(".") < 0) {
DN_ozz = DN_ozz + ".0";
}
if (TP_ozz == null) {
TP_ozz = "";
} else if (TP_ozz.toString().indexOf(".") < 0) {
TP_ozz = TP_ozz + ".0";
}
ozz = DN_ozz + "<br>～<br>" + TP_ozz;
} else {
ozz = ozzData[wkId];
if (ozz == null) {
ozz = "";
} else if (ozz.toString().indexOf(".") < 0) {
ozz = ozz + ".0";
}
}
}
if (jst011Maindata.data.ozzHyojiFlg == "0") {
var wkClass = "nonb";
if (jst011Maindata.data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
wkClass += " red";
}
}
}
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
wkClass += " bold";
}
out[l].innerHTML = '<div class="' + wkClass + '" >' + ozz
+ '</div>';
} else {
var wkBtnId = "btn" + wkId;
var wkClass = "btn onbtn nonb";
if (jst011Maindata.data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
wkClass += " red";
}
}
}
if (kakesikiKbn != "3" && kakesikiKbn != "1") {
wkClass += " btnbold";
}
out[l].innerHTML = '<button class="' + wkClass
+ '" type="button" name="btnOzzName" id=' + wkBtnId
+ '>' + ozz + '</button>';
}
if (kesyaFlg == 1) {
$('#' + wkId).addClass("disabled");
}
}
if (jst011Maindata.data.ozzHyojiFlg == "1") {
var mode = comKaime.kimGetEditMode();
if (mode != 2) {
comOzz.ozzSeigyo();
} else {
var editKaimeGroup = comKaime.kimGetNoSetKaimeGroup();
if (editKaimeGroup != null) {
var newEditKaimeGroup = $.extend(true, {}, editKaimeGroup);
for (var i = 0; i < newEditKaimeGroup.list.length; i++) {
var x2ArrKumiban = newEditKaimeGroup.list[i].kumiban;
var kumibanList = comKaime.kimKumibanX2Arr(x2ArrKumiban);
var kumiban = "";
for (var j = 0; j < kumibanList.length; j++) {
kumiban += kumibanList[j];
}
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, "OZZ"
+ kumiban);
if (kesyaFlg != 1) {
$('#' + "btnOZZ" + kumiban).addClass("active");
} else {
comKaime.kimDelKaime(kumiban);
}
}
}
}
$("#ozz_table button").click(function() {
var id = $(this).attr("id");
var ozz = $(this).html();
if ($(this).hasClass("btn onbtn nonb")) {
if ($(this).hasClass("active")) {
$(this).removeClass("active");
comOzz.ozzClick("1", id, ozz);
} else {
$(this).addClass("active");
comOzz.ozzClick("2", id, ozz);
}
}
return false;
});
}
opView.pullDownHyoji();
return;
},
kesyaCheck : function(kakesikiKbn, wkId) {
if (!jst010Maindata || jst010Maindata.resultCd == -1) {
return 0;
}
var sya1 = wkId.substr(3, 1);
var sya2 = wkId.substr(4, 1);
var sya3 = null;
if (wkId.length == 6) {
sya3 = wkId.substr(5, 1);
}
var sensyuList = jst010Maindata.data.sensyuInfoList;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
var wkArray = new Array();
var wkKesya = new Array();
for (var i = 0; i < sensyuList.length; i++) {
var wkWakuban = sensyuList[i].wakuBan;
if (sensyuList[i].kesyaFlg == "1") {
if (wkKesya[wkWakuban] != null) {
wkKesya[wkWakuban] = wkKesya[wkWakuban] + 1;
} else {
wkKesya[wkWakuban] = 1;
}
}
if (wkArray[wkWakuban] != null) {
wkArray[wkWakuban] = wkArray[wkWakuban] + 1;
} else {
wkArray[wkWakuban] = 1;
}
}
if (wkArray[sya1] == wkKesya[sya1]
|| wkArray[sya2] == wkKesya[sya2]) {
return 1;
}
if (sya1 == sya2 && wkKesya[sya1] != null && wkKesya[sya1] >= 1) {
return 1;
}
} else {
for (var i = 0; i < sensyuList.length; i++) {
if (sensyuList[i].syaban == sya1
|| sensyuList[i].syaban == sya2
|| sensyuList[i].syaban == sya3) {
if (sensyuList[i].kesyaFlg == "1") {
return 1;
}
}
}
}
return 0;
},
formatNum : function(str) {
var newStr = "";
var count = 0;
for (var i = str.length - 1; i >= 0; i--) {
if (count % 3 == 0 && count != 0) {
newStr = str.charAt(i) + "," + newStr;
} else {
newStr = str.charAt(i) + newStr;
}
count++;
}
return newStr;
}
}
var o2tView = {
ozz2SyatanStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data == null
|| jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
o2tView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var sensyuList = jst010Maindata.data.sensyuInfoList;
outStr += "<tr>";
for (var i = 1; i <= syaCnt; i++) {
if (i == 1){
outStr += '<td  align="center" colspan="2" class="nb-l nb-t o2fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}else{
outStr += '<td  align="center" colspan="2" class="nb-t o2fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}
}
outStr += "</tr>";
for (var i = 1; i <= syaCnt - 1; i++) {
outStr += "<tr>";
for (var j = 1; j <= syaCnt; j++) {
var dd = 1;
for (var k = 1; k <= syaCnt; k++) {
if (k != j) {
if (dd == i) {
var wkClass = sensyuList[j-1].syabanColor1;
wkClass += " nb-l";
outStr += '<td class="' + wkClass + '">' + k
+ '</td>';
var kumiban = "OZZ" + j + k;
var ozzColor = sensyuList[j-1].syabanColor2;
if (jst011Maindata.data.ozzHyojiFlg == "1") {
ozzColor += " btn ozzwd";
}
outStr += '<td name="lblOzzName" class="'
+ ozzColor + '" id=' + kumiban + '></td>';
}
dd = dd + 1;
}
}
}
outStr += "</tr>";
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var o3fView = {
ozz3RenhukuStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data == null
|| jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
o3fView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var sensyuList = jst010Maindata.data.sensyuInfoList;
var colCnt = syaCnt - 2;
var wkArray = new Array();
for (var i = 1; i <= syaCnt; i++) {
wkArray[i] = new Array();
}
outStr += "<tr>";
for (var i = 1; i <= colCnt; i++) {
if (i == 1){
outStr += '<td align="center" colspan="3" class="nb-l nb-t o3fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}else{
outStr += '<td align="center" colspan="3" class="nb-t o3fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}
wkArray[i][2] = i;
wkArray[i][3] = syaCnt;
}
outStr += "</tr>";
for (var i = 1; wkArray[1][2] < syaCnt - 1; i++) {
outStr += "<tr>";
var sya2;
var sya3;
for (var j = 1; j <= colCnt; j++) {
if ((wkArray[j][2] == (syaCnt - 1))
&& (wkArray[j][3] == syaCnt)) {
outStr += '<td class="nb-a"></td><td class="nb-a"></td><td class="nb-a"></td>';
} else {
var wkClass = "";
if (wkArray[j][3] == syaCnt) {
sya2 = wkArray[j][2] + 1;
var wkRow = syaCnt - sya2;
wkClass = sensyuList[sya2-1].syabanColor1;
var sya2Class = wkClass;
if (j==1){
sya2Class = wkClass + " nb-l";
}
outStr += '<td rowspan=' + wkRow + ' class="' + sya2Class
+ '">' + sya2 + '</td>';
sya3 = sya2 + 1;
outStr += '<td class=' + wkClass + '>' + sya3 + '</td>';
wkArray[j][2] = sya2;
} else {
sya3 = wkArray[j][3] + 1;
var colorSyaIndex = wkArray[j][2] -1;
wkClass = sensyuList[colorSyaIndex].syabanColor1;
outStr += '<td class=' + wkClass + '>' + sya3 + '</td>';
}
wkArray[j][3] = sya3;
var kumiban = "OZZ" + j + wkArray[j][2] + sya3;
var colorSyaIndex = wkArray[j][2] -1;
var ozzColor = sensyuList[colorSyaIndex].syabanColor2;
if (jst011Maindata.data.ozzHyojiFlg == "1") {
ozzColor += " btn";
}
outStr += '<td name="lblOzzName" class="' + ozzColor
+ '" id=' + kumiban + '></td>';
}
}
outStr += "</tr>";
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var o2fView = {
ozz2SyahukuStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data == null
|| jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
o2fView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var sensyuList = jst010Maindata.data.sensyuInfoList;
outStr += "<tr>";
for (var i = 1; i <= syaCnt; i++) {
if (i == 1){
outStr += '<td align="center" colspan="2" class="nb-t nb-l o2fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}else{
outStr += '<td align="center" colspan="2" class="nb-t o2fheadwd '
+ sensyuList[i-1].syabanColor1 + '">' + i + '</td>';
}
}
outStr += "</tr>";
for (var i = 1; i <= syaCnt - 1; i++) {
outStr += "<tr>";
var sya2;
var sya3;
for (var j = 1; j <= syaCnt; j++) {
var k = i + j;
if (k > syaCnt) {
outStr += '<td colspan="2" class="nb-a"><div class="o2fnob"></div></td>';
} else {
var wkClass = "nb-l o2fsya2wd " + sensyuList[j-1].syabanColor1;
outStr += '<td class="' + wkClass + '">' + k + '</td>';
var kumiban = "OZZ" + j + k;
var ozzColor = "ozzwd2 " + sensyuList[j-1].syabanColor2;
if (jst011Maindata.data.ozzHyojiFlg == "1") {
ozzColor += " btn";
}
outStr += '<td name="lblOzzName" class="' + ozzColor
+ '" id=' + kumiban + '></td>';
}
}
outStr += "</tr>";
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var owtView = {
ozz2WakutanStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data == null
|| jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
owtView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var wkArray = new Array();
var sensyuList = jst010Maindata.data.sensyuInfoList;
var wakubanCnt = sensyuList[sensyuList.length - 1].wakuBan;
for (var i = 0; i < sensyuList.length; i++) {
var wkWakuban = sensyuList[i].wakuBan;
if (wkArray[wkWakuban] != null) {
wkArray[wkWakuban] = wkArray[wkWakuban] + 1;
} else {
wkArray[wkWakuban] = 1;
}
}
var bigRowCnt = Math.ceil(wakubanCnt / 3);
var wk = wakubanCnt;
for (var i = 1; i <= bigRowCnt; i++) {
var wkCol = 3;
if (wk < 3) {
wkCol = wk;
}
wk = wk - 3;
outStr += '<tr>';
for (var j = 1; j <= wkCol; j++) {
var sya1 = (i - 1) * 3 + j;
var wk1Class = "tbl_header bold owtheadwd";
if (i==1){
wk1Class += " nb-t";
}
if (j==1){
wk1Class += " nb-l";
}
outStr += '<td class="' + wk1Class +'">' + sya1
+ '</td>';
}
outStr += '</tr>';
var flg = 0;
var wkCnt = wakubanCnt;
for (var j = 1; j <= wkCol; j++) {
var s1 = (i - 1) * 3 + j
if (wkArray[s1] != 1) {
flg = 1;
}
}
if (flg == 0) {
wkCnt = wkCnt - 1;
}
for (var j = 1; j <= wkCnt; j++) {
outStr += '<tr>';
for (var k = 1; k <= wkCol; k++) {
var sya1 = (i - 1) * 3 + k;
outStr += '<td class="pad nb-l">';
var dd = 1;
for (var l = 1; l <= wakubanCnt; l++) {
if (wkArray[l] != 1 || l != sya1) {
if (dd == j) {
outStr += '<table class="wd_tbl">';
outStr += '<tr>';
outStr += '<td class="tbl_header second nb-t nb-b nb-l bold">'
+ l + '</td>';
var kumiban = "OZZ" + sya1 + l;
var wkClass = "ozu nb-a owtwd";
if (jst011Maindata.data.ozzHyojiFlg == "1") {
wkClass += " btn";
}
outStr += '<td name="lblOzzName" class="'
+ wkClass + '" id=' + kumiban
+ '></td>';
outStr += '</tr>';
outStr += '</table>';
}
dd = dd + 1;
}
}
outStr += '</td>';
}
outStr += '<tr>';
}
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var owfView = {
ozz2WakuhukuStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1
|| !jst011Maindata.data) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data
&& jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
owfView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var wkArray = new Array();
var sensyuList = jst010Maindata.data.sensyuInfoList;
var wakubanCnt = sensyuList[sensyuList.length - 1].wakuBan;
for (var i = 0; i < sensyuList.length; i++) {
var wkWakuban = sensyuList[i].wakuBan;
if (wkArray[wkWakuban] != null) {
wkArray[wkWakuban] = wkArray[wkWakuban] + 1;
} else {
wkArray[wkWakuban] = 1;
}
}
var bigRowCnt = Math.ceil(wakubanCnt / 3);
var wk = wakubanCnt;
for (var i = 1; i <= bigRowCnt; i++) {
var wkCol = 3;
if (wk < 3) {
wkCol = wk;
}
wk = wk - 3;
outStr += '<tr>';
for (var j = 1; j <= wkCol; j++) {
var sya1 = (i - 1) * 3 + j;
var wk1Class = "tbl_header bold owtheadwd";
if (i==1){
wk1Class += " nb-t";
}
if (j==1){
wk1Class += " nb-l";
}
outStr += '<td class="' + wk1Class +'">' + sya1
+ '</td>';
}
outStr += '</tr>';
var flg = 0;
var wkCnt = wakubanCnt;
for (var j = 1; j <= wkCol; j++) {
var s1 = (i - 1) * 3 + j
if (wkArray[s1] != 1) {
flg = 1;
}
}
if (flg == 0) {
wkCnt = wkCnt - 1;
}
for (var j = 1; j <= wkCnt; j++) {
outStr += '<tr>';
for (var k = 1; k <= wkCol; k++) {
var sya1 = (i - 1) * 3 + k;
var dd = 1;
for (var l = sya1; l <= wakubanCnt; l++) {
if (wkArray[l] != 1 || l != sya1) {
if (dd == j) {
outStr += '<td class="pad nb-l">';
outStr += '<table class="wd_tbl">';
outStr += '<tr>';
outStr += '<td class="tbl_header second nb-t nb-b nb-l bold">'
+ l + '</td>';
var kumiban = "OZZ" + sya1 + l;
var wkClass = "ozu nb-a owtwd";
if (jst011Maindata.data.ozzHyojiFlg == "1") {
wkClass += " btn";
}
outStr += '<td name="lblOzzName" class="'
+ wkClass + '" id=' + kumiban
+ '></td>';
outStr += '</tr>';
outStr += '</table>';
outStr += '</td>';
}
dd = dd + 1;
}
}
}
outStr += '<tr>';
}
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var owView = {
ozzWideStart : function() {
if (!jst011Maindata 
|| jst011Maindata.resultCd == -1 
|| !jst011Maindata.data) {
var messageCd = "";
if (jst011Maindata.messageCd != null) {
messageCd = jst011Maindata.messageCd;
}
Com.viewErrorPage(messageCd);
return false;
}
if (jst011Maindata.data 
&& jst011Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst011Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
owView.ozzTableCreate();
o3tView.ozzDataSet();
},
ozzTableCreate : function() {
if (!$('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').addClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var syaCnt = jst010Maindata.data.syaCnt;
var sensyuList = jst010Maindata.data.sensyuInfoList;
outStr += "<tr>";
for (var i = 1; i <= syaCnt; i++) {
if (i==1){
outStr += '<td colspan="2" class="nb-t nb-l o2fheadwd ' + sensyuList[i-1].syabanColor1
+ ' btnhead">' + i + '</td>';
}else{
outStr += '<td colspan="2" class="nb-t o2fheadwd ' + sensyuList[i-1].syabanColor1
+ ' btnhead">' + i + '</td>';
}
}
outStr += "</tr>";
for (var i = 1; i <= syaCnt - 1; i++) {
outStr += "<tr>";
var sya2;
var sya3;
for (var j = 1; j <= syaCnt; j++) {
var k = i + j;
if (k > syaCnt) {
outStr += '<td colspan="2" class="nb-a"><div class="o2fnob"></div></td>';
} else {
var wkClass = "nb-l " + sensyuList[j-1].syabanColor1 + " carno";
outStr += '<td class="' + wkClass + '">' + k + '</td>';
var kumiban = "OZZ" + j + k;
var ozzColor = "ozzwd2 " + sensyuList[j-1].syabanColor2;
if (jst011Maindata.data.ozzHyojiFlg == "1") {
ozzColor += " btn owozz";
outStr += '<td name="lblOzzName" class="' + ozzColor
+ '" id=' + kumiban + '></td>';
} else {
outStr += '<td name="lblOzzName" class="' + ozzColor
+ '" id=' + kumiban + '></td>';
}
}
}
outStr += "</tr>";
}
outStr += "</table>";
out.innerHTML = outStr;
}
};
var opController = {
JSON_012_ID : "JST012",
getNinkiOrderInfo : function() {
var result = null;
var params = {};
if (!jst015Maindata || jst015Maindata.resultCd == -1 
|| !jst010Maindata || jst010Maindata.resultCd == -1) {
if (parentFuncId == "FPT0001") {
$('#ozz_table').html("ただいま、オッズ投票は行えません。");
}else{
$('#ozz_table').html("オッズ情報が受信できませんでした。");
}
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#opPullDown_table').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
commonLoad.loadingImage("false");
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
anaOddsType = "PT0531";
params["kake"] = jst015Maindata.data.kakesikiKbn;
params["mode"] = jst015Maindata.data.mode;
params["encp"] = gPrmParaR;
var dtd = $.Deferred();
var wait = function(dtd) {
o3tController.reqOzzInfo(dtd, opController.JSON_012_ID, params);
return dtd.promise();
};
$.when(wait(dtd)).done(
function(result) {
jst012Maindata = result;
if(parentFuncId == "FPT0001"){
PT0202View.btnControl();
}
if (!jst012Maindata 
|| jst012Maindata.resultCd == -1
|| !jst012Maindata.data) {
if (parentFuncId == "FPT0001") {
$('#ozz_table').html("ただいま、オッズ投票は行えません。");
}else{
$('#ozz_table').html("オッズ情報が受信できませんでした。");
}
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#opPullDown_table').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
commonLoad.loadingImage("false");
return false;
}else {
$('#ozz_table').removeClass("empcolor_red");
}
if (jst012Maindata.data
&& jst012Maindata.data.karaGamenFlg == "1") {
$('#ozz_table').html(
jst012Maindata.data.karaGamenMsg);
$('#ozz_table').addClass("empcolor_red");
$('#btnOzzUpd').hide();
$('#lblUpdateStopMsg').hide();
$('#lblGettime').hide();
$('#lblHatubaiCnt').hide();
$('#lblErrorMsg').hide();
$('#opPullDown_table').hide();
$('#lblGuideMsg').hide();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
commonLoad.loadingImage("false");
return false;
} else {
$('#ozz_table').removeClass("empcolor_red");
}
opView.ninkiOrderStart();
$('#divOzzSearch').removeClass("dispon");
$('#divOzzSearch').addClass("dispoff");
$('#divHyojunNinki').addClass("dispon");
commonLoad.loadingImage("false");
});
}
}
var opView = {
NINKI_ORDER_MUTOHYO : 99999,
ninkiOrderStart : function() {
opView.ninkiOrderHyoji();
},
ninkiOrderHyoji : function() {
var jst012data = jst012Maindata.data;
var date = new Date(Date.parse(jst012data.upDate.replace(".0", "")
.replace(/-/g, "/")));
var dateKey = opView.dateFormat(date);
comKaime.kimChangePrimeKey(jst015Maindata.data.kaisaiDate,
jst015Maindata.data.keirinJyoCd, jst015Maindata.data.raceNo,
jst015Maindata.data.kakesikiKbn, dateKey);
if (date != null) {
var hour = date.getHours() + "";
var minutes = date.getMinutes() + "";
if (minutes.length == 1) {
minutes = "0" + minutes;
}
var time = hour + ":" + minutes + " 現在";
$('#lblGettime').html(time);
$('#lblGettime').show();
} else {
$('#lblGettime').hide();
}
if (jst012data.updateStopMsgHyojiFlg == "0") {
$('#lblUpdateStopMsg').html(jst012data.updateStopMsg);
$('#lblUpdateStopMsg').show();
} else {
$('#lblUpdateStopMsg').hide();
}
if (jst012data.guideMsgHyojiFlg == "0") {
$('#lblGuideMsg').html(jst012data.guideMsg);
$('#lblGuideMsg').show();
} else {
$('#lblGuideMsg').hide();
}
if (jst012data.errorMsg != null) {
var errorMsg = jst012data.errorMsg;
$('#lblErrorMsg').html(errorMsg);
$('#lblErrorMsg').show();
} else {
$('#lblErrorMsg').hide();
}
if (jst012data.btnOzzUpdHyojiFlg != "0") {
$('#btnOzzUpd').hide();
} else {
$('#btnOzzUpd').show();
}
var cnt = jst012data.hyosumCnt;
var hyosumCnt = "発売票数：";
if (cnt != null) {
hyosumCnt += o3tView.formatNum(cnt.toString());
$('#lblHatubaiCnt').html(hyosumCnt);
$('#lblHatubaiCnt').show();
}
var ozzDataList = jst012Maindata.data.ozzDataList;
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var rstOzzData50List = new Array();
RST_OZZDATA_ALL_LIST = new Array();
var maxNinkiOrder = 50;
for (var i = 0; i < ozzDataList.length; i++) {
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, "OZZ"
+ ozzDataList[i].kumiban);
if (kesyaFlg != 1) {
if (ozzDataList[i].ninkiOrder != opView.NINKI_ORDER_MUTOHYO
&& ozzDataList[i].ninkiOrder > maxNinkiOrder) {
RST_OZZDATA_ALL_LIST.push(rstOzzData50List);
rstOzzData50List = new Array();
maxNinkiOrder = maxNinkiOrder + 50;
var karaPageCnt = Math.ceil((ozzDataList[i].ninkiOrder - maxNinkiOrder) / 50);
for (var j = 0; j < karaPageCnt; j++) {
var karaList = new Array();
RST_OZZDATA_ALL_LIST.push(karaList);
maxNinkiOrder = maxNinkiOrder + 50;
}
}
rstOzzData50List.push(ozzDataList[i]);
}
}
if (rstOzzData50List.length > 0) {
RST_OZZDATA_ALL_LIST.push(rstOzzData50List);
}
opView.pullDownHyoji();
opView.ozzTableCreate();
},
ozzTableCreate : function() {
if ($('#ozz_table').hasClass("ozz_tbl_line")){
$('#ozz_table').removeClass("ozz_tbl_line");
}
if (!$('#ozz_table').hasClass("ozz_tbl_srl")){
$('#ozz_table').addClass("ozz_tbl_srl");
}
document.getElementById("ozz_table").scrollTop = 0;
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var jst012data = jst012Maindata.data;
var out = document.getElementById("ozz_table");
var outStr = '<table class="ozu_tbl">';
var wkCol = 4;
var wkRow = Math.ceil(RST_OZZDATA_ALL_LIST[PAGE_CNT].length / wkCol);
var wkCnt = RST_OZZDATA_ALL_LIST[PAGE_CNT].length % wkCol;
if (RST_OZZDATA_ALL_LIST[PAGE_CNT].length == 0) {
outStr += '<div class="ossel_tbl">該当順位のオッズは存在しません。</div>';
}
for (var i = 0; i < wkRow; i++) {
var trClass = "altertable_guusu";
if (i % 2 == 0) {
trClass = "altertable_kisu";
}
outStr += '<tr class="' + trClass + '">';
for (var j = 0; j < wkCol; j++) {
var k = i;
for (var x = 0; x < j; x++) {
if (x < wkCnt || wkCnt == 0) {
k += wkRow;
} else {
k += wkRow - 1;
}
}
if (k < RST_OZZDATA_ALL_LIST[PAGE_CNT].length) {
if (i == (wkRow - 1) && wkCnt != 0 && j >= wkCnt) {
break;
}
var ozz = RST_OZZDATA_ALL_LIST[PAGE_CNT][k].ozz;
if (kakesikiKbn == "5") {
var ozzArrays = ozz.split("-");
var DN_ozz = ozzArrays[0];
var TP_ozz = ozzArrays[1];
if (DN_ozz.indexOf(".") < 0) {
DN_ozz = DN_ozz + ".0";
}
if (TP_ozz.indexOf(".") < 0) {
TP_ozz = TP_ozz + ".0";
}
ozz = DN_ozz + "<br>～<br>" + TP_ozz;
} else {
if (ozz.indexOf(".") < 0) {
ozz = ozz + ".0";
}
}
outStr += '<td  class="ninki_order_color"><div class="al-c op_ninki">'
+ opView
.fmtNinkiOrder(RST_OZZDATA_ALL_LIST[PAGE_CNT][k].ninkiOrder)
+ '</td>';
outStr += '<td ><div class="op_kumiban">'
+ opView
.kumibanFormat(RST_OZZDATA_ALL_LIST[PAGE_CNT][k].kumiban)
+ '</div></td>'
if (jst012data.ozzHyojiFlg == "0") {
var divClass = "bold nonb_nin op_ozz";
if (jst012data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
divClass += " red";
}
}
}
outStr += '<td ><div class="' + divClass + '">' + ozz
+ '</div></td>'
} else {
var btnClass = "btn onbtn nonb_nin";
var tdClass = "btn";
if (kakesikiKbn == "5") {
tdClass += " owozz_nin";
}
if (jst012data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
btnClass += " red";
}
}
}
var kumibanId = "btnOZZ"
+ RST_OZZDATA_ALL_LIST[PAGE_CNT][k].kumiban;
var tdKumibanId = "OZZ" + RST_OZZDATA_ALL_LIST[PAGE_CNT][k].kumiban;
outStr += '<td id ="' + tdKumibanId +'" name="lblOzzName" class="' 
+ tdClass + '"><button class="'
+ btnClass
+ '" type="button" name="btnOzzName" id ="'
+ kumibanId + '">' + ozz + '</button></td>'
}
} else {
}
}
outStr += '</tr>';
}
outStr += "</table>";
out.innerHTML = outStr;
if (jst012data.ozzHyojiFlg == "1") {
var mode = comKaime.kimGetEditMode();
if (mode != 2) {
comOzz.ozzSeigyo();
} else {
var editKaimeGroup = comKaime.kimGetNoSetKaimeGroup();
if (editKaimeGroup != null) {
var newEditKaimeGroup = $.extend(true, {}, editKaimeGroup);
for (var i = 0; i < newEditKaimeGroup.list.length; i++) {
var x2ArrKumiban = newEditKaimeGroup.list[i].kumiban;
var kumibanList = comKaime.kimKumibanX2Arr(x2ArrKumiban);
var kumiban = "";
for (var j = 0; j < kumibanList.length; j++) {
kumiban += kumibanList[j];
}
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, "OZZ"
+ kumiban);
if (kesyaFlg != 1) {
$('#' + "btnOZZ" + kumiban).addClass("active");
} else {
comKaime.kimDelKaime(kumiban);
}
}
}
}
$("#ozz_table button").click(function() {
var id = $(this).attr("id");
var ozz = $(this).html();
if ($(this).hasClass("btn onbtn nonb_nin")) {
if ($(this).hasClass("active")) {
$(this).removeClass("active");
comOzz.ozzClick("1", id, ozz);
} else {
$(this).addClass("active");
comOzz.ozzClick("2", id, ozz);
}
}
return false;
});
}
},
pullDownHyoji : function() {
var dispKbn = jst015Maindata.data.dispKbn;
var out = document.getElementById("opPullDown_table");
var outStr = "";
if (dispKbn == "2") {
outStr += '<table class="op_pulldown"><tr>';
outStr += '<td class="al-l pt-7">人気順 ';
outStr += '<p class="input_color"><select id="opRdoDispRange" onchange="opView.pullDownChange(this)" class="width_140">';
for (var i = 0; i < RST_OZZDATA_ALL_LIST.length; i++) {
var wkStart = 1 + i * 50;
var wkEnd = (i + 1) * 50;
if (i == RST_OZZDATA_ALL_LIST.length - 1) {
var wkIndex = RST_OZZDATA_ALL_LIST[i].length - 1;
for (var j = wkIndex; j >= 0; j--) {
if (RST_OZZDATA_ALL_LIST[i][j].ninkiOrder != opView.NINKI_ORDER_MUTOHYO) {
wkEnd = RST_OZZDATA_ALL_LIST[i][j].ninkiOrder;
break;
}
}
}
var wkStr = wkStart + "位～" + wkEnd + "位";
outStr += '<option value="' + i + '">' + wkStr + '</option>';
}
outStr += '</select></p></td>';
outStr += '<td class="al-r"><button class="btn onbtn al-c pad_width_120" id="opBtnPrev50">前の50位</button></td>';
outStr += '<td class="al-r"><button class="btn onbtn al-c pad_width_120" id="opBtnNext50">次の50位</button></td>';
outStr += '</tr></table>';
outStr += "</table>";
}
out.innerHTML = outStr;
if (dispKbn == "2") {
PAGE_CNT = 0;
opView.btnPrevNext50Display();
}
$('#opBtnPrev50').click(
function() {
PAGE_CNT = PAGE_CNT - 1;
$("#opRdoDispRange option[value='" + PAGE_CNT + "']")
.get(0).selected = true;
opView.btnPrevNext50Display();
opView.ozzTableCreate();
return false;
});
$('#opBtnNext50').click(
function() {
PAGE_CNT = PAGE_CNT + 1;
$("#opRdoDispRange option[value='" + PAGE_CNT + "']")
.get(0).selected = true;
opView.btnPrevNext50Display();
opView.ozzTableCreate();
return false;
});
},
kumibanFormat : function(kumiban) {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var fmKumiban = kumiban.substr(0, 1);
for (var i = 1; i < kumiban.length; i++) {
if (kakesikiKbn == "2" || kakesikiKbn == "3" || kakesikiKbn == "6") {
fmKumiban += "-";
} else {
fmKumiban += "=";
}
fmKumiban += kumiban.substr(i, 1);
}
return fmKumiban;
},
pullDownChange : function(param) {
PAGE_CNT = Number(param.value);
opView.btnPrevNext50Display();
opView.ozzTableCreate();
},
btnPrevNext50Display : function() {
if (PAGE_CNT == 0) {
$('#opBtnPrev50').addClass("disabled");
} else if ($('#opBtnPrev50').hasClass("disabled")) {
$('#opBtnPrev50').removeClass("disabled");
}
if (PAGE_CNT == RST_OZZDATA_ALL_LIST.length - 1) {
$('#opBtnNext50').addClass("disabled");
} else if ($('#opBtnNext50').hasClass("disabled")) {
$('#opBtnNext50').removeClass("disabled");
}
},
fmtNinkiOrder : function(order) {
if (order == opView.NINKI_ORDER_MUTOHYO) {
return "-";
} else {
return order;
}
},
dateFormat : function(date) {
var year = date.getFullYear();
var month = date.getMonth();
if (month < 10) {
month = "0" + month;
}
var day = date.getDay();
if (day < 10) {
day = "0" + day;
}
var hours = date.getHours();
if (hours < 10) {
hours = "0" + hours;
}
var minutes = date.getMinutes();
if (minutes < 10) {
minutes = "0" + minutes;
}
return "" + year + month + day + hours + minutes;
}
}
var OLD_SENSYU_LIST = null;
$(function(){
$('#osBtnHyojiHyojun').click( function() {
if ($('#osBtnHyojiNinOrder').hasClass("active")){
$('#osBtnHyojiNinOrder').removeClass("active");
}
if (!($('#osBtnHyojiHyojun').hasClass("active"))){
$('#osBtnHyojiHyojun').addClass("active");
var searchList = new Array();
if (SEARCH_HYOJUN_LIST != null && SEARCH_HYOJUN_LIST.length != 0){
osView.ozzTblCreater(SEARCH_HYOJUN_LIST);
}
}
return false;
});
$('#osBtnHyojiNinOrder').click( function() {
if ($('#osBtnHyojiHyojun').hasClass("active")){
$('#osBtnHyojiHyojun').removeClass("active");
}
if (!($('#osBtnHyojiNinOrder').hasClass("active"))){
$('#osBtnHyojiNinOrder').addClass("active");
var searchList = new Array();
if (SEARCH_NINKI_LIST != null && SEARCH_NINKI_LIST.length != 0){
osView.ozzTblCreater(SEARCH_NINKI_LIST);
}
}
return false;
});
$('#osBtnClear').click( function() {
osView.displayArea(0);
SEARCH_NINKI_LIST　= null;
SEARCH_HYOJUN_LIST　= null;
if (parentFuncId == "FPT0001" && comKaime.kimGetEditMode() == 2) {
comKaime.kimClearTmp();
PT0202View.btnControl();
PT0202Controller.cPT0202BtnChg(jst061Ret.hyojiKbn);
}
return false;
});
$('#osBtnOzzUpd').click( function() {
doubleClick($(this).attr("id"));
commonLoad.loadingImage("true");
osController.getOzzInfo(2);
return false;
});
})
var osController = {
getOzzInfo : function(initFlg) {
var result = null;
var params = {};
if (!jst015Maindata || jst015Maindata.resultCd == -1
|| !jst010Maindata || jst010Maindata.resultCd == -1) {
if (parentFuncId == "FPT0001") {
$('#osDisplayArea').html("ただいま、オッズ投票は行えません。");
} else {
$('#osDisplayArea').html("オッズ情報が受信できませんでした。");
}
$('#osDisplayArea').addClass("empcolor_red");
$('#osBtnOzzUpd').hide();
$('#osLblUpdateStopMsg').hide();
$('#osLblGettime').hide();
$('#osLblHatubaiCnt').hide();
$('#osLblGuideMsg').hide();
$('#divHyojunNinki').removeClass("dispon");
$('#divHyojunNinki').addClass("dispoff");
$('#divOzzSearch').addClass("dispon");
commonLoad.loadingImage("false");
return false;
} else {
$('#osDisplayArea').removeClass("empcolor_red");
}
anaOddsType = "PT0532";
params["kake"] = jst015Maindata.data.kakesikiKbn;
params["mode"] = jst015Maindata.data.mode;
params["encp"] = gPrmParaR;
var dtd = $.Deferred();
var wait = function(dtd) {
o3tController.reqOzzInfo(dtd, opController.JSON_012_ID, params);
return dtd.promise();
};
$.when(wait(dtd)).done(function(result) {
jst012Maindata = result;
if(parentFuncId == "FPT0001"){
PT0202View.btnControl();
}
if (!jst012Maindata || jst012Maindata.resultCd == -1) {
if (parentFuncId == "FPT0001") {
$('#osDisplayArea').html("ただいま、オッズ投票は行えません。");
} else {
$('#osDisplayArea').html("オッズ情報が受信できませんでした。");
}
$('#osDisplayArea').addClass("empcolor_red");
$('#osBtnOzzUpd').hide();
$('#osLblUpdateStopMsg').hide();
$('#osLblGettime').hide();
$('#osLblHatubaiCnt').hide();
$('#osLblGuideMsg').hide();
$('#divHyojunNinki').removeClass("dispon");
$('#divHyojunNinki').addClass("dispoff");
$('#divOzzSearch').addClass("dispon");
commonLoad.loadingImage("false");
return false;
} else {
$('#osDisplayArea').removeClass("empcolor_red");
}
osView.ozzSearchDisplay(initFlg);
$('#divHyojunNinki').removeClass("dispon");
$('#divHyojunNinki').addClass("dispoff");
$('#divOzzSearch').addClass("dispon");
});
},
getSyusohyoInfo : function(dtd) {
OLD_SENSYU_LIST = jst010Maindata.data.sensyuInfoList
var result = null;
var params = {};
params["encp"] = gPrmParaR;
params["url.media.flg"] = "1";
Com.getRequestGet(otController.JSON_010_ID, params).done(function(result) {
if(!result || result.resultCd == -1){
if(jst010Maindata){
jst010Maindata.resultCd = -1;
}else{
jst010Maindata = {"resultCd":-1};
}
}else{
jst010Maindata = result;
}
dtd.resolve(result);
});
}
}
var osView = {
ozzSearchStart : function() {
osController.getOzzInfo(0);
},
ozzSearchDisplay : function(initFlg) {
var jst012data = jst012Maindata.data;
if (jst012data.karaGamenFlg == "1") {
$('#osDisplayArea').html(jst012data.karaGamenMsg);
$('#osDisplayArea').addClass("empcolor_red");
$('#osBtnOzzUpd').hide();
$('#osLblUpdateStopMsg').hide();
$('#osLblGettime').hide();
$('#osLblHatubaiCnt').hide();
$('#osLblGuideMsg').hide();
} else {
$('#osDisplayArea').removeClass("empcolor_red");
var date = new Date(Date.parse(jst012data.upDate.replace(".0", "")
.replace(/-/g, "/")));
var dateKey = opView.dateFormat(date);
comKaime.kimChangePrimeKey(jst015Maindata.data.kaisaiDate,
jst015Maindata.data.keirinJyoCd, jst015Maindata.data.raceNo,
jst015Maindata.data.kakesikiKbn, dateKey);
if (date != null) {
var hour = date.getHours() + "";
var minutes = date.getMinutes() + "";
if (minutes.length == 1) {
minutes = "0" + minutes;
}
var time = hour + ":" + minutes + " 現在";
$('#osLblGettime').html(time);
$('#osLblGettime').show()
} else {
$('#osLblGettime').hide();
}
if (jst012data.updateStopMsgHyojiFlg == "0") {
$('#osLblUpdateStopMsg').html(jst012data.updateStopMsg);
$('#osLblUpdateStopMsg').show()
} else {
$('#osLblUpdateStopMsg').hide();
}
if (jst012data.btnOzzUpdHyojiFlg != "0") {
$('#osBtnOzzUpd').hide();
} else {
$('#osBtnOzzUpd').show();
}
var cnt = jst012data.hyosumCnt;
var hyosumCnt = "発売票数 ";
if (cnt != null) {
hyosumCnt += o3tView.formatNum(cnt.toString());
$('#osLblHatubaiCnt').html(hyosumCnt);
$('#osLblHatubaiCnt').show();
}
}
var dtd = $.Deferred();
var wait = function(dtd) {
osController.getSyusohyoInfo(dtd);
return dtd.promise();
};
$.when(wait(dtd)).done(function() {
if (jst012data.karaGamenFlg != "1") {
osView.displayArea(initFlg);
}
osView.syusouArea();
if (parentFuncId != "FPT0001") {
if ($('#osArea').addClass("width_75")) {
$('#osArea').removeClass("width_75");
}
if (!$('#osArea').addClass("width_63")) {
$('#osArea').addClass("width_63");
}
osView.searchArea();
} else {
if ($('#osArea').addClass("width_63")) {
$('#osArea').removeClass("width_63");
}
if (!$('#osArea').addClass("width_75")) {
$('#osArea').addClass("width_75");
}
}
commonLoad.loadingImage("false");
});
},
syusouArea : function() {
var jst010Data = jst010Maindata.data;
var out = document.getElementById("osSyusouArea");
var outStr = "";
outStr += '<thead><tr>';
if (jst010Data.wakuKbn == "1") {
outStr += '<td class="width_2"><p><span>枠<br>番</span></p></td>';
}
outStr += '<td class="width_2"><p><span>車<br>番</span></p></td>';
outStr += '<td class="nb-b"><p><span>選手名</span></p>';
outStr += '<p><span>府県</span><span>/</span><span>級班</span><span class="tbl_val14_fsz">前</span><span>現</span><span>/</span><span>脚質</span></p></td>';
outStr += '</tr></thead>';
outStr += '<tbody>';
var outWakuban = new Array();
var sensyuList = jst010Maindata.data.sensyuInfoList;
var wkWakuban = null;
if (jst010Data.wakuKbn == "1") {
var wkSyacnt = 1;
for (var i = 0; i < sensyuList.length; i++) {
if (wkWakuban == sensyuList[i].wakuBan) {
wkSyacnt = wkSyacnt + 1;
} else if (wkWakuban != null) {
outWakuban.push('<td class="wakuban" rowspan="' + wkSyacnt
+ '"><p class="al-c"><span>' + wkWakuban
+ '</span></p></td>');
for (var j = 1; j < wkSyacnt; j++) {
outWakuban.push("");
}
wkSyacnt = 1;
}
wkWakuban = sensyuList[i].wakuBan;
}
if (wkWakuban != null) {
outWakuban.push('<td class="wakuban" rowspan="' + wkSyacnt
+ '"><p class="al-c"><span>' + wkWakuban
+ '</span></p></td>');
for (var j = 1; j < wkSyacnt; j++) {
outWakuban.push("");
}
}
}
for (var i = 0; i < sensyuList.length; i++) {
var syaban = sensyuList[i].syaban;
outStr += '<tr class="' + sensyuList[i].syabanColor2 + '">';
if (jst010Data.wakuKbn == "1") {
outStr += outWakuban[i];
}
outStr += '<td class="' + sensyuList[i].syabanColor1
+ '"><p class="al-c"><span class="al-c">' + syaban
+ '</span></p></td>';
outStr += '<td class="al-l">';
outStr += '<p><span class="bold">' + sensyuList[i].sensyuSei6Char
+ '</span>';
outStr += '<span class="' + sensyuList[i].colorCd + '">'
+ sensyuList[i].kejyoHojyuAdd + '</span>';
outStr += '</p><p>' + sensyuList[i].huken3Char
+ '/<span class="tbl_val14_fsz">'
+ rbEmptyTo3Space(sensyuList[i].MaeKyuhan2Char) + '</span>'
+ '<span class="' + rlDataChecker(sensyuList[i].kyuhanSpecialColor) 
+ '">' + rlDataChecker(sensyuList[i].kyuhan2Char) + '</span>'
+ '/'
+ sensyuList[i].kyasitu1Char;
outStr += '</p></td></tr>';
}
outStr += '</tbody>';
out.innerHTML = outStr;
},
searchArea : function() {
var kimOn1 = "";
var kimOn2 = "";
var kimOn3 = "";
var kimOn4 = "";
var kimOn5 = "";
var kimOn6 = "";
var kimOn7 = "";
var kimOn8 = "";
var kimOn9 = "";
var out = document.getElementById("osSelectArea");
var outStr = "";
outStr += '<table id="kai" class="dispon margin_t15">';
outStr += '<tr><td>';
outStr += '<table id="select_s5" class="width_96">';
outStr += '<tr class="ht30"><td></td>';
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (kakesikiKbn == "6" || kakesikiKbn == "2" || kakesikiKbn == "3") {
outStr += '<td class="f-12 v-al-b pb-5">1<br>着</td>';
outStr += '<td class="f-12 v-al-b pb-5">2<br>着</td>';
if (kakesikiKbn == "6") {
outStr += '<td class="f-12 v-al-b pb-5">3<br>着</td>';
}
} else {
outStr += '<td class="f-12 v-al-b pb-5">組<br>1</td>';
outStr += '<td class="f-12 v-al-b pb-5">組<br>2</td>';
if (kakesikiKbn == "7") {
outStr += '<td class="f-12 v-al-b pb-5">組<br>3</td>';
}
}
outStr += '</tr>';
var sensyuList = jst010Maindata.data.sensyuInfoList;
for (var i = 0; i < sensyuList.length; i++) {
sensyuInfo = sensyuList[i];
if (sensyuInfo.syabanColor1) {
eval('kimOn' + (i + 1) + ' = "' + sensyuInfo.syabanColor1 + '"');
}
}
if (kakesikiKbn != "3" && kakesikiKbn != "1") {
for (var i = 0; i < sensyuList.length; i++) {
var iconClass = "";
var syaClass = "";
if (i % 2 == 0) {
iconClass = "bgc1";
syaClass = "bgc2";
} else {
iconClass = "bgc3";
syaClass = "bgc4";
}
outStr += '<tr class="ht42">';
var syaban = sensyuList[i].syaban;
if (sensyuList[i].kesyaFlg == "1") {
outStr += '<td class="'
+ iconClass
+ '"><span id="" class="btn numbtn pt-0 disabled"><i class="fa fa-caret-right icon-arrow"></i></span></td>';
outStr += '<td class="' + syaClass
+ '"><span id="" class="btn numbtn disabled">'
+ syaban + '</span></td>';
outStr += '<td class="' + syaClass
+ '"><span id="" class="btn numbtn disabled">'
+ syaban + '</span></td>';
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
outStr += '<td class="' + syaClass
+ '"><span id="" class="btn numbtn disabled">'
+ syaban + '</span></td>';
}
} else {
outStr += '<td class="'
+ iconClass
+ '"><span id="osSpanIcon'
+ syaban
+ '" class="btn numbtn pt-0"><i class="fa fa-caret-right icon-arrow"></i></span></td>';
outStr += '<td class="' + syaClass
+ '"><span id="osSpanSya1t' + syaban
+ '" class="btn numbtn">' + syaban + '</span></td>';
outStr += '<td class="' + syaClass
+ '"><span id="osSpanSya2t' + syaban
+ '" class="btn numbtn">' + syaban + '</span></td>';
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
outStr += '<td class="' + syaClass
+ '"><span id="osSpanSya3t' + syaban
+ '" class="btn numbtn">' + syaban
+ '</span></td>';
}
}
outStr += '</tr>';
}
} else {
var outWakuban = new Array();
var wakuGroup = null;
var wkWakuban = null;
var wkSyacnt = 1;
var kesyaFlg = "1";
for (var i = 0; i < sensyuList.length; i++) {
if (wkWakuban == sensyuList[i].wakuBan) {
wkSyacnt = wkSyacnt + 1;
} else if (wkWakuban != null) {
wakuGroup = {
"wakuban" : wkWakuban,
"syaCnt" : wkSyacnt,
"kesyaFlg" : kesyaFlg
}
outWakuban.push(wakuGroup);
wkSyacnt = 1;
kesyaFlg = "1";
}
wkWakuban = sensyuList[i].wakuBan;
if ("0" == sensyuList[i].kesyaFlg) {
kesyaFlg = "0";
}
}
if (wkWakuban != null) {
wakuGroup = {
"wakuban" : wkWakuban,
"syaCnt" : wkSyacnt,
"kesyaFlg" : kesyaFlg
}
outWakuban.push(wakuGroup);
}
for (var i = 0; i < outWakuban.length; i++) {
var iconClass = "";
var syaClass = "";
if (i % 2 == 0) {
iconClass = "bgc1";
syaClass = "bgc2";
} else {
iconClass = "bgc3";
syaClass = "bgc4";
}
var syaban = sensyuList[i].syaban;
if (outWakuban[i].syaCnt > 1){
outStr += '<tr class="h52">';
}else{
outStr += '<tr class="ht42">';
}
if (outWakuban[i].kesyaFlg == "1") {
outStr += '<td rowspan="'
+ outWakuban[i].syaCnt
+ '" class="'
+ iconClass
+ '"><span id="" class="btn numbtn pt-0 disabled"><i class="fa fa-caret-right icon-arrow"></i></span></td>';
outStr += '<td  rowspan="' + outWakuban[i].syaCnt
+ '" class="' + syaClass
+ '"><span id="" class="btn numbtn disabled">'
+ outWakuban[i].wakuban + '</span></td>';
outStr += '<td rowspan="' + outWakuban[i].syaCnt
+ '" class="' + syaClass
+ '"><span id="" class="btn numbtn disabled">'
+ outWakuban[i].wakuban + '</span></td>';
} else {
outStr += '<td rowspan="'
+ outWakuban[i].syaCnt
+ '" class="'
+ iconClass
+ '"><span id="osSpanIcon'
+ syaban
+ '" class="btn numbtn pt-0"><i class="fa fa-caret-right icon-arrow"></i></span></td>';
outStr += '<td  rowspan="' + outWakuban[i].syaCnt
+ '" class="' + syaClass
+ '"><span id="osSpanSya1t' + syaban
+ '" class="btn numbtn">' + outWakuban[i].wakuban
+ '</span></td>';
outStr += '<td rowspan="' + outWakuban[i].syaCnt
+ '" class="' + syaClass
+ '"><span id="osSpanSya2t' + syaban
+ '" class="btn numbtn">' + outWakuban[i].wakuban
+ '</span></td>';
}
outStr += '</tr>';
for (var j = 1; j < outWakuban[i].syaCnt; j++) {
outStr += '<tr class="h52">';
outStr += '</tr>';
}
}
}
outStr += '<tr class="hb">';
outStr += '<td></td>';
outStr += '<td class="f-12"><span id="osSpanAll1" class="btn onbtn os_all_btn">全</span></td>';
outStr += '<td class="f-12"><span id="osSpanAll2" class="btn onbtn os_all_btn">全</span></td>';
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
outStr += '<td class="f-12"><span id="osSpanAll3" class="btn onbtn os_all_btn">全</span></td>';
}
outStr += '</tr><tr class="hb">';
outStr += '<td></td>';
outStr += '<td class="f-12"><span id="osSpanClear1" class="btn numbtn_clr">消</span></td>';
outStr += '<td class="f-12"><span id="osSpanClear2" class="btn numbtn_clr">消</span></td>';
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
outStr += '<td class="f-12"><span id="osSpanClear3" class="btn numbtn_clr">消</span></td>';
}
outStr += '</tr>';
outStr += '</table>';
outStr += '<div class="betset"><button type="button" id="osBtnOzzSearch" class="btn onbtn os_osbtn">オッズ検索</button></div>';
outStr += '</td></tr></table>';
out.innerHTML = outStr;
$("span[id^='osSpanClear']").click(function() {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var id = $(this).attr("id");
var col = id.substr(11, 1);
var syaList = $('span[id^="osSpanSya"]');
for (var l = 0; l < syaList.length; l++) {
var value = syaList[l].innerHTML;
var colorId = value;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
colorId = "1";
}
if ($('#osSpanSya' + col + 't' + value).hasClass(
"on" + colorId)) {
$('#osSpanSya' + col + 't' + value).removeClass(
"on" + colorId);
$('#osSpanSya' + col + 't' + value).removeClass(
eval("kimOn" + colorId));
}
}
});
$("span[id^='osSpanAll']").click(function() {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var id = $(this).attr("id");
var col = id.substr(9, 1);
var syaList = $('span[id^="osSpanSya"]');
for (var l = 0; l < syaList.length; l++) {
var value = syaList[l].innerHTML;
var colorId = value;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
colorId = "1";
}
if (!($('#osSpanSya' + col + 't' + value).hasClass("on"
+ colorId))) {
$('#osSpanSya' + col + 't' + value).addClass(
"on" + colorId);
$('#osSpanSya' + col + 't' + value).addClass(
eval("kimOn" + colorId));
}
}
});
$("span[id^='osSpanIcon']").click(function() {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var id = $(this).attr("id");
var rol = id.substr(10, 1);
var colorId = rol;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
colorId = "1";
}
var syaList = $('span[id^="osSpanSya"]');
var allFlg = 0;
var noFlg = 0;
if ($('#osSpanSya1t' + rol).hasClass("on" + colorId)) {
allFlg = 1;
} else {
noFlg = 1;
}
if ($('#osSpanSya2t' + rol).hasClass("on" + colorId)) {
allFlg = 1;
} else {
noFlg = 1;
}
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
if ($('#osSpanSya3t' + rol).hasClass("on" + colorId)) {
allFlg = 1;
} else {
noFlg = 1;
}
}
if (allFlg == 0) {
$('#osSpanSya1t' + rol).addClass("on" + colorId);
$('#osSpanSya1t' + rol).addClass(eval("kimOn" + colorId));
$('#osSpanSya2t' + rol).addClass("on" + colorId);
$('#osSpanSya2t' + rol).addClass(eval("kimOn" + colorId));
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
$('#osSpanSya3t' + rol).addClass("on" + colorId);
$('#osSpanSya3t' + rol).addClass(eval("kimOn" + colorId));
}
} else if (noFlg == 0) {
$('#osSpanSya1t' + rol).removeClass("on" + colorId);
$('#osSpanSya1t' + rol).removeClass(eval("kimOn" + colorId));
$('#osSpanSya2t' + rol).removeClass("on" + colorId);
$('#osSpanSya2t' + rol).removeClass(eval("kimOn" + colorId));
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
$('#osSpanSya3t' + rol).removeClass("on" + colorId);
$('#osSpanSya3t' + rol).removeClass(eval("kimOn" + colorId));
}
} else {
if (!($('#osSpanSya1t' + rol).hasClass("on" + colorId))) {
$('#osSpanSya1t' + rol).addClass("on" + colorId);
$('#osSpanSya1t' + rol).addClass(eval("kimOn" + colorId));
}
if (!($('#osSpanSya2t' + rol).hasClass("on" + colorId))) {
$('#osSpanSya2t' + rol).addClass("on" + colorId);
$('#osSpanSya2t' + rol).addClass(eval("kimOn" + colorId));
}
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
if (!($('#osSpanSya3t' + rol).hasClass("on" + colorId))) {
$('#osSpanSya3t' + rol).addClass("on" + colorId);
$('#osSpanSya3t' + rol).addClass(eval("kimOn" + colorId));
}
}
}
});
$("span[id^='osSpanSya']").click(function() {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var id = $(this).attr("id");
var value = $(this).html();
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
value = "1";
}
if ($(this).hasClass("on" + value)) {
$(this).removeClass("on" + value);
$(this).removeClass(eval("kimOn" + value));
} else {
$(this).addClass("on" + value);
$(this).addClass(eval("kimOn" + value));
}
});
$('#osBtnOzzSearch').click(function() {
commonLoad.loadingImage("true");
osController.getOzzInfo(1);
});
},
displayArea : function(initFlg) {
if (initFlg == 0) {
var out = document.getElementById("osDisplayArea");
var outStr = "";
if (jst012Maindata.data.guideMsgHyojiFlg == "0") {
$('#osLblGuideMsg').html(jst012Maindata.data.guideMsg);
$('#osLblGuideMsg').removeClass("empcolor_red");
$('#osLblGuideMsg').show();
} else {
$('#osLblGuideMsg').html("");
}
outStr += '<div class="os_dis bold">';
outStr += '検索結果が表示されます。';
outStr += '</div>';
out.innerHTML = outStr;
SEARCH_NINKI_LIST　= null;
SEARCH_HYOJUN_LIST　= null;
} else if (initFlg == 1) {
var sya1tList = new Array();
var sya2tList = new Array();
var sya3tList = new Array();
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (parentFuncId != "FPT0001") {
var list1t = $('span[id^="osSpanSya1t"]');
for (var l = 0; l < list1t.length; l++) {
var value = list1t[l].innerHTML;
var colorId = value;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
colorId = "1";
}
if ($('#osSpanSya1t' + value).hasClass("on" + colorId)) {
sya1tList.push(value);
}
}
var list2t = $('span[id^="osSpanSya2t"]');
for (var l = 0; l < list2t.length; l++) {
var value = list2t[l].innerHTML;
var colorId = value;
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
colorId = "1";
}
if ($('#osSpanSya2t' + value).hasClass("on" + colorId)) {
sya2tList.push(value);
}
}
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
var list3t = $('span[id^="osSpanSya3t"]');
for (var l = 0; l < list3t.length; l++) {
var value = list3t[l].innerHTML;
if ($('#osSpanSya3t' + value).hasClass("on" + value)) {
sya3tList.push(value);
}
}
}
} else {
var list1t = $('p[id^="syabanWakuban1"]');
for (var l = 0; l < list1t.length; l++) {
var value = list1t[l].innerHTML;
if ($('#syabanWakuban1' + value).hasClass("on" + value)) {
sya1tList.push(value);
}
}
var list2t = $('p[id^="syabanWakuban2"]');
for (var l = 0; l < list2t.length; l++) {
var value = list2t[l].innerHTML;
if ($('#syabanWakuban2' + value).hasClass("on" + value)) {
sya2tList.push(value);
}
}
if (kakesikiKbn == "6" || kakesikiKbn == "7") {
var list3t = $('p[id^="syabanWakuban3"]');
for (var l = 0; l < list3t.length; l++) {
var value = list3t[l].innerHTML;
if ($('#syabanWakuban3' + value).hasClass("on" + value)) {
sya3tList.push(value);
}
}
}
 $("p[id^='syabanWakuban']").removeClass("on1 on2 on3 on4 on5 on6 on7 on8 on9 wakuon");
 $("p[id^='syabanWakuban']").removeClass(kimOn1);
 $("p[id^='syabanWakuban']").removeClass(kimOn2);
 $("p[id^='syabanWakuban']").removeClass(kimOn3);
 $("p[id^='syabanWakuban']").removeClass(kimOn4);
 $("p[id^='syabanWakuban']").removeClass(kimOn5);
 $("p[id^='syabanWakuban']").removeClass(kimOn6);
 $("p[id^='syabanWakuban']").removeClass(kimOn7);
 $("p[id^='syabanWakuban']").removeClass(kimOn8);
 $("p[id^='syabanWakuban']").removeClass(kimOn9);
}
osView.ozzSort(sya1tList, sya2tList, sya3tList);
} else {
osView.ozzUpdate();
}
},
ozzSort : function(sya1tList, sya2tList, sya3tList) {
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
var ozzDataList = jst012Maindata.data.ozzDataList;
var searchHyojunList = new Array();
var searchNinkiList = new Array();
for (var i = 0; i < ozzDataList.length; i++) {
if (kakesikiKbn == "3" || kakesikiKbn == "1") {
if (osView.oldKesyaCheck(ozzDataList[i].kumiban)) {
continue;
}
}
if (kakesikiKbn == "6" || kakesikiKbn == "2" || kakesikiKbn == "3") {
if (osView.isSearchTan(ozzDataList[i].kumiban, sya1tList,
sya2tList, sya3tList)) {
searchHyojunList.push(ozzDataList[i]);
searchNinkiList.push(ozzDataList[i]);
}
} else {
if (osView.isSearchHuku(ozzDataList[i].kumiban, sya1tList,
sya2tList, sya3tList)) {
searchHyojunList.push(ozzDataList[i]);
searchNinkiList.push(ozzDataList[i]);
}
}
}
SEARCH_NINKI_LIST = searchNinkiList;
searchHyojunList.sort(function(a, b) {
if (a.kumiban > b.kumiban) {
return 1;
} else if (a.kumiban < b.kumiban) {
return -1;
}
});
SEARCH_HYOJUN_LIST = searchHyojunList;
if ($('#osBtnHyojiHyojun').hasClass("active")) {
osView.ozzTblCreater(SEARCH_HYOJUN_LIST);
} else {
osView.ozzTblCreater(SEARCH_NINKI_LIST);
}
},
ozzUpdate : function() {
if (SEARCH_NINKI_LIST == null) {
return false;
}
var ozzDataList = jst012Maindata.data.ozzDataList;
var searchHyojunList = new Array();
var searchNinkiList = new Array();
for (var i = 0; i < ozzDataList.length; i++) {
for (var j = 0; j < SEARCH_NINKI_LIST.length; j++) {
if (ozzDataList[i].kumiban == SEARCH_NINKI_LIST[j].kumiban) {
searchHyojunList.push(ozzDataList[i]);
searchNinkiList.push(ozzDataList[i]);
break;
}
}
}
SEARCH_NINKI_LIST = searchNinkiList;
searchHyojunList.sort(function(a, b) {
if (a.kumiban > b.kumiban) {
return 1;
} else if (a.kumiban < b.kumiban) {
return -1;
}
});
SEARCH_HYOJUN_LIST = searchHyojunList;
if ($('#osBtnHyojiHyojun').hasClass("active")) {
osView.ozzTblCreater(SEARCH_HYOJUN_LIST);
} else {
osView.ozzTblCreater(SEARCH_NINKI_LIST);
}
},
ozzTblCreater : function(searchList) {
var out = document.getElementById("osDisplayArea");
var outStr = "";
var kakesikiKbn = jst015Maindata.data.kakesikiKbn;
if (searchList.length == 0) {
$(document).off("click", ".ui-widget-overlay");
$('#alert_dialog_p').html("成立する組番を選択してください。");
$('#alert_dialog').dialog('open');
$('#alert_ok_btn').click(function() {
$('#alert_dialog').dialog('close');
return false;
});
outStr += '<div class="os_dis bold">';
outStr += '検索結果が表示されます。';
outStr += '</div>';
} else {
if (jst012Maindata.data.errorMsg != null) {
$('#osLblGuideMsg').html(jst012Maindata.data.errorMsg);
$('#osLblGuideMsg').addClass("empcolor_red");
$('#osLblGuideMsg').show();
} else if (jst012Maindata.data.guideMsgHyojiFlg == "0") {
$('#osLblGuideMsg').html(jst012Maindata.data.guideMsg);
$('#osLblGuideMsg').removeClass("empcolor_red");
$('#osLblGuideMsg').show();
} else {
$('#osLblGuideMsg').html("");
}
var wkCol = 3;
var wkRow = Math.ceil(searchList.length / wkCol);
var wkCnt = searchList.length % wkCol;
for (var i = 0; i < wkCol; i++) {
if (i == 0) {
outStr += '<div class="fl-l width_31">';
} else {
outStr += '<div class="fl-l width_31 margin_l2">';
}
outStr += '<table class="altertable w100pc">';
for (var j = 0; j < wkRow; j++) {
var k = j;
for (var x = 0; x < i; x++) {
if (x < wkCnt || wkCnt == 0) {
k += wkRow;
} else {
k += wkRow - 1;
}
}
if (k < searchList.length) {
if (j == (wkRow - 1) && wkCnt != 0 && i >= wkCnt) {
break;
}
outStr += '<tr>';
outStr += '<td class="ozu_kumi">'
+ opView.kumibanFormat(searchList[k].kumiban)
+ '</td>';
var ozz = searchList[k].ozz;
var ninkiOrder = opView
.fmtNinkiOrder(searchList[k].ninkiOrder);
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, "OZZ"
+ searchList[k].kumiban);
if (kesyaFlg == 1) {
ozz = "-----";
} else {
if (kakesikiKbn == "5") {
var ozzArrays = ozz.split("-");
var DN_ozz = ozzArrays[0];
var TP_ozz = ozzArrays[1];
if (DN_ozz.indexOf(".") < 0) {
DN_ozz = DN_ozz + ".0";
}
if (TP_ozz.indexOf(".") < 0) {
TP_ozz = TP_ozz + ".0";
}
ozz = DN_ozz + "<br>～<br>" + TP_ozz;
} else {
if (ozz.indexOf(".") < 0) {
ozz = ozz + ".0";
}
}
}
if (jst012Maindata.data.ozzHyojiFlg == "1") {
var btnClass = "btn onbtn nonb pd_tr w100pc";
if (jst012Maindata.data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
btnClass += " color_red";
}
}
}
var tdClass = "ozu_num_btn";
if (kesyaFlg == 1) {
tdClass += " disabled";
}
wkBtnId = "osbOZZ" + searchList[k].kumiban;
var tdOzzId = "tdOZZ" + searchList[k].kumiban;
outStr += '<td id = "' + tdOzzId +'" name="lblOzzName" class="' 
+ tdClass +'"><button name="btnOzzName" id='
+ wkBtnId
+ ' class="'
+ btnClass
+ '" type="button">'
+ ozz
+ '</button></td>';
} else {
var divClass = "ozu_num";
if (jst012Maindata.data.endFlg == "0") {
if (kakesikiKbn == "6" || kakesikiKbn == "2"
|| kakesikiKbn == "7") {
if (ozz >= 1 && ozz < 10) {
divClass += " color_red";
}
}
}
outStr += '<td class="' + divClass + '">' + ozz
+ '</td>';
}
outStr += '<td class="ozu_ninki">' + ninkiOrder
+ '</td>';
outStr += '</tr>';
} else {
}
}
outStr += '</table></div>';
}
}
out.innerHTML = outStr;
if (jst012Maindata.data.ozzHyojiFlg == "1") {
var mode = comKaime.kimGetEditMode();
if (mode != 2) {
comOzz.ozzSeigyo();
} else {
var editKaimeGroup = comKaime.kimGetNoSetKaimeGroup();
if (editKaimeGroup != null) {
var newEditKaimeGroup = $.extend(true, {}, editKaimeGroup);
for (var i = 0; i < newEditKaimeGroup.list.length; i++) {
var x2ArrKumiban = newEditKaimeGroup.list[i].kumiban;
var kumibanList = comKaime.kimKumibanX2Arr(x2ArrKumiban);
var kumiban = "";
for (var j = 0; j < kumibanList.length; j++) {
kumiban += kumibanList[j];
}
var kesyaFlg = o3tView.kesyaCheck(kakesikiKbn, "OZZ"
+ kumiban);
if (kesyaFlg != 1) {
$('#' + "osbOZZ" + kumiban).addClass("active");
} else {
comKaime.kimDelKaime(kumiban);
}
}
}
}
$("#osDisplayArea button").click(function() {
var id = $(this).attr("id");
var ozz = $(this).html();
if ($(this).hasClass("btn onbtn nonb")) {
if ($(this).hasClass("active")) {
$(this).removeClass("active");
comOzz.ozzClick("1", id, ozz);
} else {
$(this).addClass("active");
comOzz.ozzClick("2", id, ozz);
}
}
return false;
});
}
},
isSearchTan : function(kumiban, sya1tList, sya2tList, sya3tList) {
var rsFlg = false;
var sya1 = kumiban.substr(0, 1);
var sya2 = kumiban.substr(1, 1);
var sya3 = "";
if (kumiban.length == 3) {
sya3 = kumiban.substr(2, 1);
}
if ((sya1tList.indexOf(sya1) >= 0) && (sya2tList.indexOf(sya2) >= 0)) {
rsFlg = true;
}
if (kumiban.length == 3) {
if (sya3tList.indexOf(sya3) < 0) {
rsFlg = false;
}
}
return rsFlg;
},
isSearchHuku : function(kumiban, sya1tList, sya2tList, sya3tList) {
var rsFlg = false;
var wkKumibanList = new Array();
for (var i = 0; i < sya1tList.length; i++) {
for (var j = 0; j < sya2tList.length; j++) {
if (kumiban.length == 3) {
for (var k = 0; k < sya3tList.length; k++) {
var wkSyabanList = new Array();
wkSyabanList.push(sya1tList[i]);
wkSyabanList.push(sya2tList[j]);
wkSyabanList.push(sya3tList[k]);
wkSyabanList.sort();
var wkKumiban = "";
for (var x = 0; x < wkSyabanList.length; x++) {
wkKumiban += wkSyabanList[x];
}
if (wkKumibanList.indexOf(wkKumiban) < 0) {
wkKumibanList.push(wkKumiban);
}
}
} else {
var wkSyabanList = new Array();
wkSyabanList.push(sya1tList[i]);
wkSyabanList.push(sya2tList[j]);
wkSyabanList.sort();
var wkKumiban = "";
for (var x = 0; x < wkSyabanList.length; x++) {
wkKumiban += wkSyabanList[x];
}
if (wkKumibanList.indexOf(wkKumiban) < 0) {
wkKumibanList.push(wkKumiban);
}
}
}
}
if (wkKumibanList.indexOf(kumiban) >= 0) {
rsFlg = true;
}
return rsFlg;
},
oldKesyaCheck : function(wkId) {
var sya1 = wkId.substr(0, 1);
var sya2 = wkId.substr(1, 1);
var sensyuList = OLD_SENSYU_LIST;
var wkArray = new Array();
var wkKesya = new Array();
for (var i = 0; i < sensyuList.length; i++) {
var wkWakuban = sensyuList[i].wakuBan;
if (sensyuList[i].kesyaFlg == "1") {
if (wkKesya[wkWakuban] != null) {
wkKesya[wkWakuban] = wkKesya[wkWakuban] + 1;
} else {
wkKesya[wkWakuban] = 1;
}
}
if (wkArray[wkWakuban] != null) {
wkArray[wkWakuban] = wkArray[wkWakuban] + 1;
} else {
wkArray[wkWakuban] = 1;
}
}
if (wkArray[sya1] == wkKesya[sya1] || wkArray[sya2] == wkKesya[sya2]) {
return 1;
}
if (sya1 == sya2 && wkKesya[sya1] != null && wkKesya[sya1] >= 1) {
return 1;
}
return 0;
},
}
$(function() {
$('#okrBtnUpdate').click(function() {
doubleClick($(this).attr("id"));
var dtd = $.Deferred();
okrKanrenOzz.loadingImage("true");
okrController.kanrenOzzStart(dtd);
});
});
var okrKanrenOzz = {
loadingImage : function(flag) {
if (flag == "true") {
loaddingflg = true;
var PositionWidth = (wsize - 80) / 2;
var PositionHeight = (hsize - 80) / 2;
$('#kannren_ozu')
.prepend(
'\
           <div id="divfixload">\
            <div id="divrelload">\
                <div id="divabsload" style="left:'
+ PositionWidth
+ 'px;right: '
+ PositionWidth
+ 'px; top: '
+ PositionHeight
+ 'px;  bottom: '
+ PositionHeight
+ 'px;"></div>\
            </div>\
        </div>\
    ');
} else {
$('#divfixload').remove();
loaddingflg = false;
}
},
okrOzzclick : function(kaisaiDate, kaisaiDateMMDD, keirinJyo,
keirinJyoName, raceNo, kakesiki, kumiban) {
okrKaisaiDate = kaisaiDate;
okrKaisaiDateMMDD = kaisaiDateMMDD;
okrKeirinJyo = keirinJyo;
okrKeirinJyoName = keirinJyoName;
okrRace = raceNo;
okrKakesiki = kakesiki;
okrKumiban = kumiban;
var dtd = $.Deferred();
var wait = function(dtd) {
okrController.kanrenOzzStart(dtd);
return dtd.promise();
};
$.when(wait(dtd)).done(function() {
$(document).off("click", ".ui-widget-overlay");
$('#kannren_ozu').dialog('open'); 
});
return false;
}
};
var okrController = {
JSON_016_ID : "JST016",
kanrenOzzStart : function(dtd) {
var result = null;
var params = {};
params["kake"] = okrKakesiki;
params["bkcd"] = okrKeirinJyo;
params["kday"] = okrKaisaiDate;
params["rnum"] = okrRace;
params["kumiban"] = okrKumiban;
Com.getRequestGet(okrController.JSON_016_ID, params).done(
function(result) {
jst016Maindata = result;
okrView.kanrenOzzDisplay();
dtd.resolve(result);
okrKanrenOzz.loadingImage("false");
return false;
});
}
}
var okrView = {
kanrenOzzDisplay : function() {
var kake ="";
if (okrKakesiki == "6") {
kake = "3連単";
} else if (okrKakesiki == "2") {
kake = "2車単";
} else if (okrKakesiki == "7") {
kake = "3連複";
} else if (okrKakesiki == "4") {
kake = "2車複";
} else if (okrKakesiki == "3") {
kake = "2枠単";
} else if (okrKakesiki == "1") {
kake = "2枠複";
} else if (okrKakesiki == "5") {
kake = "ワイド";
}
$('#okrKaisaiDate').html(okrKaisaiDateMMDD);
$('#okrKeirinJyo').html(okrKeirinJyoName);
$('#okrRace').html(okrRace + "R");
$('#okrKakesiki').html(kake);
$('#okrKumiban').html(okrView.kumibanFormat(okrKumiban, okrKakesiki));
if (!jst016Maindata || jst016Maindata.resultCd == -1) {
$('#okrKanrenOzz_table').html("ただいま、関連オッズ情報を取得できません。");
$('#okrKanrenOzz_table').addClass("empcolor_red");
commonLoad.loadingImage("false");
return false;
}else if ($('#okrKanrenOzz_table').hasClass("empcolor_red")){
$('#okrKanrenOzz_table').removeClass("empcolor_red");
}
var date = jst016Maindata.data.upDate;
if (date != null) {
var hour = date.substr(8,2);
var minutes = date.substr(10,2);
var time = hour + ":" + minutes + " 現在オッズ";
$('#okrNowTime').html(time);
$('#okrNowTime').show();
} else {
$('#okrNowTime').hide();
}
if (jst016Maindata.data.updateStopMsgHyojiFlg == "0") {
$('#okrLblUpdateStopMsg').hide().show();
$('#okrLblUpdateStopMsg').html(jst016Maindata.data.updateStopMsg);
} else {
$('#okrLblUpdateStopMsg').hide();
}
var simeTime = jst016Maindata.data.dentoSimeTime;
var simeHenkouTime = jst016Maindata.data.dentoHenkouSimeTime;
var simeTimeFmt = " ";
if (simeTime != null) {
if (simeTime != simeHenkouTime){
simeTimeFmt = "発売締切 " + "<s>" + simeHenkouTime + "</s>" + " → " 
            + "<font class='color_red'>" + simeTime + "</font>";
}else{
simeTimeFmt = "発売締切 " + simeTime;
}
}
$('#okrDentoSimeTime').html(simeTimeFmt);
var out = document.getElementById("okrKanrenOzz_table");
var outStr = "<colgroup>";
for (var i = 1; i <= 13; i++) {
if (i % 2 == 1) {
outStr += '<col class="ork_kum">';
} else {
outStr += '<col class="ork_ozz">';
}
}
outStr += "</colgroup>";
outStr += okrView.kakesikiCommon("6",
jst016Maindata.data.ozz3RentanData, "3連単");
outStr += okrView.kakesikiCommon("2",
jst016Maindata.data.ozz2SyatanData, "2車単");
outStr += okrView.kakesikiCommon("7",
jst016Maindata.data.ozz3RenhukuData, "3連複");
outStr += okrView.kakesikiCommon("4",
jst016Maindata.data.ozz2SyahukuData, "2車複");
outStr += okrView.kakesikiCommon("3",
jst016Maindata.data.ozz2WakutanData, "2枠単");
outStr += okrView.kakesikiCommon("1",
jst016Maindata.data.ozz2WakuhukuData, "2枠複");
outStr += okrView.kakesikiCommon("5", jst016Maindata.data.ozzWideData,
"ワイド");
out.innerHTML = outStr;
},
kakesikiCommon : function(kakesiki, ozzData, kakesikiHead) {
var outStr = "";
var ozzCnt = 0
if (ozzData !=null ){
ozzCnt = ozzData.length;
}
var wkCol = 6;
var wkRow = Math.ceil(ozzCnt / wkCol);
if (wkRow < 2) {
wkRow = 2;
}
for (var i = 0; i < wkRow; i++) {
outStr += "<tr>";
if (i == 0) {
outStr += '<td class="tbl_header" rowspan="' + wkRow + '"><b>'
+ kakesikiHead + '</b></td>';
}
for (var j = 0; j < wkCol; j++) {
var cnt = i * wkCol + j;
var wkClass = "al-r sakaime";
if (cnt < ozzCnt) {
outStr += '<td>' + ozzData[cnt].kumiban + '</td>';
var ozz = ozzData[cnt].ozz;
if (kakesiki == "5") {
var ozzArrays = ozz.split("-");
var DN_ozz = ozzArrays[0];
var TP_ozz = ozzArrays[1];
ozz = DN_ozz + "<br>-" + TP_ozz;
wkClass += " wd_height";
}
if (kakesiki == "6" || kakesiki == "2"
|| kakesiki == "7") {
if (ozz >= 1 && ozz < 10) {
wkClass += " okr_red";
}
}
outStr += '<td class="' + wkClass + '">' + ozz + '</td>';
} else {
outStr += '<td></td>';
outStr += '<td class="' + wkClass + '"></td>';
}
}
outStr += "</tr>";
}
return outStr;
},
kumibanFormat : function(kumiban, kakesikiKbn) {
var fmKumiban = kumiban.substr(0, 1);
for (var i = 1; i < kumiban.length; i++) {
if (kakesikiKbn == "2" || kakesikiKbn == "3" || kakesikiKbn == "6") {
fmKumiban += "-";
} else {
fmKumiban += "=";
}
fmKumiban += kumiban.substr(i, 1);
}
return fmKumiban;
}
}
