var PJ0101View = {
cDrawJSONData: function(jsondata, reqPrm) {
div_KaisaiSuccess = '#kaisaiInfo_div'; 
div_KaisaiError = '#kaisaiInfo_err_div'; 
prm_div_KaisaiError = 'kaisaiInfo_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_KaisaiSuccess).addClass('dispoff');
$(div_KaisaiError).removeClass('dispoff');
$('#ctabYesterday').removeClass("active");
$('#ctabTomorrow').removeClass("active");
$('#ctabToday').addClass("active");
Com.makePcUpdatePage(prm_div_KaisaiError, null, setPrm, function(arg0){PJ0101Controller.reqKaisaiInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_KaisaiSuccess).addClass('dispoff');
$(div_KaisaiError).removeClass('dispoff');
$('#ctabYesterday').removeClass("active");
$('#ctabTomorrow').removeClass("active");
$('#ctabToday').addClass("active");
Com.makePcUpdatePage(prm_div_KaisaiError, null, setPrm, function(arg0){PJ0101Controller.reqKaisaiInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_KaisaiSuccess).addClass('dispoff');
$(div_KaisaiError).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_KaisaiError, message, setPrm, function(arg0){PJ0101Controller.reqKaisaiInfo(arg0);});
} else {
$(div_KaisaiSuccess).removeClass('dispoff');
$(div_KaisaiError).addClass('dispoff');
var tabKaisaiList = $('#kaisaiInfoTable');
tabKaisaiList.empty();
if( jsondata.kResultCd == 0 ) {
$(div_KaisaiSuccess).addClass('dispoff');
$(div_KaisaiError).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_KaisaiError, message, setPrm, function(arg0){PJ0101Controller.reqKaisaiInfo(arg0);});
}else if(jsondata.kInfo){
for(var i = 0; i < jsondata.kInfo.length; i++ ){
var tr = $('<tr class="' + jsondata.kInfo[i].bgColor + '" />');
var tdHead = $('<td class="col1 ' + jsondata.kInfo[i].bgColor + '" />');
var kJyokyo = "";
if(jsondata.kInfo[i].kJyokyo){
kJyokyo = jsondata.kInfo[i].kJyokyo;
}else if(jsondata.kInfo[i].zenjituFlg == 1 && $('#ctabKaisai li[class~="active"]').attr('id') == 'ctabTomorrow'){
kJyokyo = '<img src="' + CONTEXT_PATH + '/static/img/icon/Himoku/ico_yday.png" alt="前日発売">'
}
tdHead.append('<div><div class="kaisaichi bold" style="font-size:18px;">' + jsondata.kInfo[i].jyoName + '</div>' +
  '<div class="cyuusi">' + kJyokyo + '</div></div>');
var divIcon = $('<div class="icon" />');
divIcon.append('<img class="rsp" src="' + jsondata.kInfo[i].gradeIcon + '" alt="' + jsondata.kInfo[i].gradeIconChar + '"/>');
divIcon.append('<img src="' + jsondata.kInfo[i].nitijiIcon + '" alt="' + jsondata.kInfo[i].nitijiIconChar + '"/>\n');
divIcon.append('<img class="rsp" src="' + jsondata.kInfo[i].kaisaiIcon + '" alt="' + jsondata.kInfo[i].kaisaiIconChar + '"/>');
if(jsondata.kInfo[i].huka1Icon){
divIcon.append('<img class="rsp" src="' + jsondata.kInfo[i].huka1Icon + '" alt="' + jsondata.kInfo[i].huka1IconChar + '"/>');
}else{
divIcon.append('<img class="rsp" src="' + CONTEXT_PATH + '/static/img/icon/ico_white.png"/>');
}
if(jsondata.kInfo[i].huka2Icon){
divIcon.append('<img class="rsp" src="' + jsondata.kInfo[i].huka2Icon + '" alt="' + jsondata.kInfo[i].huka2IconChar + '"/>');
}else{
divIcon.append('<img class="rsp" src="' + CONTEXT_PATH + '/static/img/icon/ico_white.png"/>');
}
if(jsondata.kInfo[i].itioshiIcon){
divIcon.append('<img src="' + jsondata.kInfo[i].itioshiIcon + '" alt="' + jsondata.kInfo[i].itioshiIconChar + '"/>');
}else{
divIcon.append('<img src="' + CONTEXT_PATH + '/static/img/icon/ico_white.png"/>');
}
tdHead.append(divIcon);
tr.append(tdHead);
var tdSyuyo = $('<td class="col2 ' + jsondata.kInfo[i].bgColor + '" />');
if(jsondata.kInfo[i].sensyuList){
for(var j = 0; j < jsondata.kInfo[i].sensyuList.length; j++ ){
var sensyu = jsondata.kInfo[i].sensyuList[j];
tdSyuyo.append('<span class="kaisaiInfo-syuyo"><a onclick="syuyoSensyuClick(\'' + sensyu.sensyuNo + '\'); return false;" href=\"\">' + 
       '<img class="classTeamIconSize" src="' + sensyu.sensyuIcon + '" alt="' + sensyu.sensyuIconChar + '">' + sensyu.sensyuName + '</a></span>');
if(j == 2){
tdSyuyo.append('<br/>');
}
}
}
tr.append(tdSyuyo);
var disabled = ""; 
if(jsondata.kInfo[i].btnFlgLive == 1){
disabled = "";
}else{
disabled = "disabled";
}
tr.append('<td class="btd pd_l0 ' + jsondata.kInfo[i].bgColor + '">' + 
  '<button type="button" class="btn onbtn live ' + disabled + '" onclick="btnLiveVoteClick(\'' + jsondata.kInfo[i].encPrm + '\')">LIVE&amp;<br>投票</button></td>');
tr.append('<td class="btd ' + jsondata.kInfo[i].bgColor + '">' + 
  '<button type="button" class="btn onbtn slist rsp ' + disabled + '" onclick="btnSyusouListClick(\'' + jsondata.kInfo[i].encPrm + '\')">出走表<br>一覧</button></td>');
if(jsondata.kInfo[i].btnFlgOdds == 1){
disabled = "";
}else{
disabled = "disabled";
}
tr.append('<td class="btd pd_l0 ' + jsondata.kInfo[i].bgColor + '">' + 
  '<button type="button" class="btn onbtn ozu rsp ' + disabled + '" onclick="btnOddsClick(\'' + jsondata.kInfo[i].encPrm + '\')">オッズ</button></td>');
if(jsondata.kInfo[i].btnFlgResult == 1){
disabled = "";
}else{
disabled = "disabled";
}
tr.append('<td class="btd ' + jsondata.kInfo[i].bgColor + '">' + 
  '<button type="button" class="btn onbtn klist ' + disabled + '" onclick="btnResultClick(\'' + jsondata.kInfo[i].encPrm + '\')">結果<br>一覧</button></td>');
tr.append('<td class="btd pd_r0 ' + jsondata.kInfo[i].bgColor + '">' + 
  '<button type="button" class="btn onbtn sisetu " onclick="btnSisetuClick(\'' + jsondata.kInfo[i].bKeirinCd + '\')">施設<br>案内</button></td>');
tabKaisaiList.append(tr);
}
}else{
if(jsondata.msgNone){
tabKaisaiList.append('<div class="none-msg">' + jsondata.msgNone + '</div>');
}
}
}
commonLoad.loadingImage("false");
return;
},
tlDrawJSONData: function(jsondata, reqPrm) {
div_DokantoSuccess = '#DokantoInfo_div'; 
div_DokantoError = '#DokantoInfo_err_div'; 
prm_div_DokantoError = 'DokantoInfo_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_DokantoSuccess).addClass('dispoff');
$(div_DokantoError).removeClass('dispoff');
$('#divimgHatubaiIcon').addClass('dispoff');
$('#tldivDokantobtn').addClass('dispoff');
$('#cbtnDokanto').attr('disabled', 'disabled'); 
Com.makePcUpdatePage(prm_div_DokantoError, null, setPrm, function(arg0){PJ0101Controller.reqDokantoInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_DokantoSuccess).addClass('dispoff');
$(div_DokantoError).removeClass('dispoff');
$('#divimgHatubaiIcon').addClass('dispoff');
$('#tldivDokantobtn').addClass('dispoff');
$('#cbtnDokanto').attr('disabled', 'disabled'); 
Com.makePcUpdatePage(prm_div_DokantoError, null, setPrm, function(arg0){PJ0101Controller.reqDokantoInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_DokantoSuccess).addClass('dispoff');
$(div_DokantoError).removeClass('dispoff');
$('#divimgHatubaiIcon').addClass('dispoff');
$('#tldivDokantobtn').addClass('dispoff');
$('#cbtnDokanto').attr('disabled', 'disabled'); 
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_DokantoError, null, setPrm, function(arg0){PJ0101Controller.reqDokantoInfo(arg0);});
} else {
$(div_DokantoSuccess).removeClass('dispoff');
$(div_DokantoError).addClass('dispoff');
if( jsondata.dResultCd == 0 ) {
$(div_DokantoSuccess).addClass('dispoff');
$(div_DokantoError).removeClass('dispoff');
$('#divimgHatubaiIcon').addClass('dispoff');
$('#tldivDokantobtn').addClass('dispoff');
$('#cbtnDokanto').attr('disabled', 'disabled'); 
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_DokantoError, message, setPrm, function(arg0){PJ0101Controller.reqDokantoInfo(arg0);});
}else if(jsondata.dInfo){
$('#divimgHatubaiIcon').removeClass('dispoff');
$('#tldivDokantobtn').removeClass('dispoff');
prmDokantoKeirinCD = jsondata.dInfo.prmKeirinCd;
prmDokantoKaisaiDate = jsondata.dInfo.prmKaisaiDate;
prmDokantoEnc = jsondata.dInfo.prmEnc;
if(jsondata.dInfo.hatubaicyuFlg == 2){
$('#tldenStopMsg').removeClass('dispoff');
$('#divimgHatubaiIcon').hide();
$('#cimgDokantoOnSale').hide();
}else if(jsondata.dInfo.hatubaicyuFlg == 1){
$('#tldenStopMsg').addClass('dispoff');
$('#divimgHatubaiIcon').show();
$('#cimgDokantoOnSale').show();
}else{
$('#tldenStopMsg').addClass('dispoff');
$('#divimgHatubaiIcon').hide();
$('#cimgDokantoOnSale').hide();
}
if(jsondata.dInfo.kaisai != undefined){
if(jsondata.dInfo.nextDspFlg == 1){
$('#tlDokantoKaisaihi').html('次回開催 ' + jsondata.dInfo.kaisai);
}else{
$('#tlDokantoKaisaihi').html(jsondata.dInfo.kaisai);
}
if(jsondata.dInfo.saleTime){
$('#divlblHatubaiKaisi').show(); 
$('#tllblHatubaiKaisi').html(jsondata.dInfo.saleTime);
}else{
$('#divlblHatubaiKaisi').hide(); 
}
$('#tlDokantoKaisaijyo').html(jsondata.dInfo.jyoName);
$('#tlimgKaisaiGrade').attr('src', jsondata.dInfo.gradeIcon);
$('#tlimgKaisaiGrade').attr('alt', jsondata.dInfo.gradeIconChar);
$('#jyoName').removeClass('dispoff');
}else{
$('#jyoName').addClass('dispoff');
}
if(jsondata.dInfo.reachFlg == 1){
$('#tlimgCoverReach').show();
$('#tlimgCoverReach').removeClass('kyari_over');
$('#tlimgCoverReach').addClass('dokanto_ri-chi');
}else if (jsondata.dInfo.carryOverFlg == 1){
$('#tlimgCoverReach').show();
$('#tlimgCoverReach').removeClass('dokanto_ri-chi');
$('#tlimgCoverReach').addClass('kyari_over');
}else{
$('#tlimgCoverReach').hide();
}
switch (jsondata.dInfo.d7iconKbn) {
case 1: 
$('#tlimgD7IconHatubaicyuu').show();
$('#tlimgD7Icon').hide();
break;
case 2: 
$('#tlimgD7IconHatubaicyuu').hide();
$('#tlimgD7Icon').show();
$('#tlimgD7Icon').removeClass('ri-chi-s');
$('#tlimgD7Icon').addClass('simekiri');
break;
case 3: 
$('#tlimgD7IconHatubaicyuu').hide();
$('#tlimgD7Icon').show();
$('#tlimgD7Icon').removeClass('simekiri');
$('#tlimgD7Icon').addClass('ri-chi-s');
break;
default: 
$('#tlimgD7IconHatubaicyuu').hide();
$('#tlimgD7Icon').hide();
break;
}
$('#tldivD7Info').empty();
$('#tldivD7Info').append('<div id="tllblD7Info" class="dokanto7_t1"/>');
if(jsondata.dInfo.d7info){
$('#tldivD7Info').show();
$('#tllblD7Info').append('<span> ' + jsondata.dInfo.d7info + '</span>');
if(getWidth($('#tllblD7Info'), 1) >= 200){
$('#tllblD7Info').prepend('<div class="dispib" style="width:210px;">&nbsp;</div>');
setTicker('#tllblD7Info', 25);
}
}else if(jsondata.dInfo.d7zankutiInfo){
$('#tldivD7Info').show();
var d7span = $('<span />');
for(var i = 0; i < jsondata.dInfo.d7zankutiInfo.length; i++ ){
var syaban = jsondata.dInfo.d7zankutiInfo[i].kumi.substr(0, 1);
var bet = jsondata.dInfo.d7zankutiInfo[i].bet;
$('#tllblD7Info').append('<span><span class="snum16 base_color_' + syaban + '">' + syaban + '</span> ' + bet + 'ベット　</span>');
d7span.append('<span><span class="snum16 base_color_' + syaban + '">' + syaban + '</span> ' + bet + 'ベット　</span>');
}
if(getWidth(d7span, 2) >= 200){
$('#tllblD7Info').prepend('<div class="dispib" style="width:210px;">&nbsp;</div>');
setTicker('#tllblD7Info', 33);
}
}else{
$('#tldivD7Info').hide();
}
$('#tllblD7Carry').html(jsondata.dInfo.d7carryOver);
switch (jsondata.dInfo.d4iconKbn) {
case 1: 
$('#tlimgD4IconHatubaicyuu').show();
$('#tlimgD4Icon').hide();
$('#tlimgD4Icon').removeClass('simekiri');
$('#tlimgD4Icon').removeClass('ri-chi-s');
break;
case 2: 
$('#tlimgD4IconHatubaicyuu').hide();
$('#tlimgD4Icon').show();
$('#tlimgD4Icon').removeClass('ri-chi-s');
$('#tlimgD4Icon').addClass('simekiri');
break;
case 3: 
$('#tlimgD4IconHatubaicyuu').hide();
$('#tlimgD4Icon').show();
$('#tlimgD4Icon').removeClass('simekiri');
$('#tlimgD4Icon').addClass('ri-chi-s');
break;
default: 
$('#tlimgD4IconHatubaicyuu').hide();
$('#tlimgD4Icon').hide();
break;
}
$('#tldivD4Info').empty();
$('#tldivD4Info').append('<div id="tllblD4Info" class="dokanto4_t1"/>');
if(jsondata.dInfo.d4info){
$('#tldivD4Info').show();
$('#tllblD4Info').append('<span> ' + jsondata.dInfo.d4info + '</span>');
if(getWidth($('#tllblD4Info'), 1) >= 200){
$('#tllblD4Info').prepend('<div class="dispib" style="width:210px;">&nbsp;</div>');
setTicker('#tllblD4Info', 25);
}
}else if(jsondata.dInfo.d4zankutiInfo){
$('#tldivD4Info').show();
var d4span = $('<span />');
for(var i = 0; i < jsondata.dInfo.d4zankutiInfo.length; i++ ){
var syaban1 = jsondata.dInfo.d4zankutiInfo[i].kumi.substr(0, 1);
var syaban2 = jsondata.dInfo.d4zankutiInfo[i].kumi.substr(1, 1); 
var bet = jsondata.dInfo.d4zankutiInfo[i].bet;
$('#tllblD4Info').append('<span><span class="snum16 base_color_' + syaban1 + '">' + syaban1 + '</span>-' +
                 '<span class="snum16 base_color_' + syaban2 + '">' + syaban2 + '</span> ' + bet + 'ベット　</span>');
d4span.append('<span><span class="snum16 base_color_' + syaban1 + '">' + syaban1 + '</span>-' +
                 '<span class="snum16 base_color_' + syaban2 + '">' + syaban2 + '</span> ' + bet + 'ベット　</span>');
}
if(getWidth(d4span, 2) >= 200){
$('#tllblD4Info').prepend('<div class="dispib" style="width:210px;">&nbsp;</div>');
setTicker('#tllblD4Info', 33);
}
}else{
$('#tldivD4Info').hide();
}
$('#tllblD4Carry').html(jsondata.dInfo.d4carryOver);
if(jsondata.dInfo.btnVoteFlg == 1 && jsondata.dInfo.hatubaicyuFlg != 2){
$('#btnDokantoVote').removeAttr('disabled', 'disabled'); 
$('#cbtnDokanto').removeAttr('disabled', 'disabled'); 
}else{
$('#btnDokantoVote').attr('disabled', 'disabled'); 
$('#cbtnDokanto').attr('disabled', 'disabled'); 
}
}
}
commonLoad.loadingImage("false");
return;
},
bclDrawJSONData: function(jsondata, reqPrm) {
div_success = '#topics_div'; 
div_error = '#topics_err_div'; 
prm_div_error = 'topics_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqTopicsInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqTopicsInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_error, message, setPrm, function(arg0){PJ0101Controller.reqTopicsInfo(arg0);});
} else {
$(div_success).removeClass('dispoff');
$(div_error).addClass('dispoff');
var divTopicsList = $('#bcdivTopicsList');
divTopicsList.empty();
$("#ktopic_list").css('height', '');
$("#kosirase_list").css('height', '');
if(jsondata.tList){
var ul = $('<ul />');
var topic = null;
for(var i = 0; i < jsondata.tList.length; i++ ){
topic = '<li><div class="clear-fix"><p class="fl-l">' +
        '<span class="date">' + jsondata.tList[i].sDate + '</span>';
if(jsondata.tList[i].newFlg == 1){
topic += '<span style="vertical-align:top;margin-top:4px" class="icon-color new">New</span>';
}
topic += '</p><div class="icon-color fl-r ' + jsondata.tList[i].ctgyCls + '">' + jsondata.tList[i].ctgyName + '</div></div>';
var target = "_self";
if (jsondata.tList[i].winKbn == 1){
target = "_blank";
}
topic += '<p class="listTitle"><a href="' + jsondata.tList[i].lnkURL + '" target="' + target + '">';
topic += jsondata.tList[i].title + '</a></p></li>';
ul.append(topic);
}
divTopicsList.append(ul);
}else{
if(jsondata.msgNone){
divTopicsList.append('<div class="none-msg">' + jsondata.msgNone + '</div>');
}
if(!jsondata.reqprm || Object.keys(jsondata.reqprm).length == 0 || jsondata.reqprm['ctgy'] == null || jsondata.reqprm['ctgy'] == '') {
$('#bccmbCategory').attr('disabled', 'disabled');
}
}
}
newsHeightAdjust();
commonLoad.loadingImage("false");
return;
},
bcrDrawJSONData: function(jsondata, reqPrm) {
div_success = '#oshirase_div'; 
div_error = '#oshirase_err_div'; 
prm_div_error = 'oshirase_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqOshiraseInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqOshiraseInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_error, message, setPrm, function(arg0){PJ0101Controller.reqOshiraseInfo(arg0);});
} else {
$(div_success).removeClass('dispoff');
$(div_error).addClass('dispoff');
var divOshiraseList = $('#bcdivNoticeList');
divOshiraseList.empty();
$("#ktopic_list").css('height', '');
$("#kosirase_list").css('height', '');
if(jsondata.oList){
var ul = $('<ul />');
var ochirase = null;
for(var i = 0; i < jsondata.oList.length; i++ ){
ochirase = '<li><div class="clear-fix"><p class="fl-l">' +
        '<span class="date">' + jsondata.oList[i].sDate + '</span>';
if(jsondata.oList[i].newFlg == 1){
ochirase += '<span style="vertical-align:top;margin-top:4px" class="icon-color new">New</span>';
}
ochirase += '</p><div class="icon-color fl-r ' + jsondata.oList[i].tikuCls + '">' + jsondata.oList[i].tikuName + '</div>';
ochirase += '<div class="icon-color fl-r ' + jsondata.oList[i].shisetuCls + '">' + jsondata.oList[i].shisetuName + '</div></div>';
var target = "_self";
if (jsondata.oList[i].winKbn == 1){
target = "_blank";
}
ochirase += '<p class="listTitle"><a href="' + jsondata.oList[i].lnkURL + '" target="' + target + '">';
ochirase += jsondata.oList[i].title + '</a></p></li>';
ul.append(ochirase);
}
divOshiraseList.append(ul);
}else{
if(jsondata.msgNone){
divOshiraseList.append('<div class="none-msg">' + jsondata.msgNone + '</div>');
}
if(!jsondata.reqprm || Object.keys(jsondata.reqprm).length == 0 || jsondata.reqprm['tiku'] == null || jsondata.reqprm['tiku'] == '') {
$('#bccmbTiku').attr('disabled', 'disabled');
}
}
}
newsHeightAdjust();
commonLoad.loadingImage("false");
return;
},
clDrawJSONData: function(jsondata, reqPrm) {
div_success = '#pickup_today'; 
div_error = '#pickup_err_div'; 
prm_div_error = 'pickup_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
$('#cltabTomorrow').removeClass("active");
$('#cltabToday').addClass("active");
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqPickupInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
$('#cltabTomorrow').removeClass("active");
$('#cltabToday').addClass("active");
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqPickupInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_error, message, setPrm, function(arg0){PJ0101Controller.reqPickupInfo(arg0);});
} else {
$(div_success).removeClass('dispoff');
$(div_error).addClass('dispoff');
var divPickupList = $('#pickup_today');
divPickupList.empty();
if(jsondata.oList && jsondata.oList.length > 0 ){
var ul = $('<ul class="al-l" style="margin-bottom: 0; padding: 5px;">');
var pickup = null;
for(var i = 0; i < jsondata.oList.length; i++ ){
pickup = '<li id="pickup_' + (i + 1 ) + '" class="pickupRace';
if( jsondata.oList[i].zenColor != null && jsondata.oList[i].zenColor != ""){
pickup += ' ' + jsondata.oList[i].zenColor;
}
var attr = "";
if(jsondata.oList[i].lnkPara){
attr = 'class="memlink" onclick="btnItiosiClick(\''+ jsondata.oList[i].lnkPara + '\'); return false;" href=\"\"';
}else{
attr = 'class="memlink2"';
}
if( i == 0) pickup += ' dispon';
else pickup += ' dispoff';
pickup += '">' +
'<a target="_self" ' + attr + '>' +
'<div class="pickupRaceText clear-fix">';
if( jsondata.oList[i].pickupTenmetsu == true)
pickup += '<p id="blink_win6" class="midasi1_fsz">' + jsondata.oList[i].pickupKijyun + '</p>';
else
pickup += '<p class="midasi1_fsz">' + jsondata.oList[i].pickupKijyun + '</p>';
var nameCnt = $('<u/>').html(jsondata.oList[i].nameSeiMei).text().length;
var strSensyu = '　選手';
if(nameCnt > 6){
strSensyu = '選手';
}
var senshuGazouFile = ''; 
var addNoImageClass = ''; 
if (jsondata.oList[i].senshuGazouFile != null && jsondata.oList[i].senshuGazouFile != "") {
senshuGazouFile = ' src="' + CMS_PATH + jsondata.oList[i].senshuGazouFile + '"'
 +' alt="' + jsondata.oList[i].nameSeiMei + '　選手 (' + jsondata.oList[i].kuniMei + jsondata.oList[i].kyuhanMei + ') "';
} else {
addNoImageClass = ' face_pickup_deffw';
}
pickup += '<div class="fl-l"><div class="face_pickup_mxw"><img class="face_pickup' + addNoImageClass + '"' + senshuGazouFile + ' /></div></div>';
pickup += '<p style="padding-top:5px; line-height:1.8;"><span class="midasi2_fsz">' + jsondata.oList[i].nameSeiMei + '</span>' + strSensyu + '</p>';
pickup += '<p class="player_class">(' + jsondata.oList[i].kuniMei + jsondata.oList[i].kyuhanMei + ')</p>';
pickup += '<br/>';
pickup += '<p>';
pickup += '<span class="bet_info">' + jsondata.oList[i].keirinMei + '</span>';
pickup += '<img src="' + jsondata.oList[i].gradeIconFile + '" alt="' + 
jsondata.oList[i].kuniMei + jsondata.oList[i].gradeIconName + '" />';
pickup += '<img src="' + jsondata.oList[i].nichijiIconFile + '" alt="' + jsondata.oList[i].nichijiIconName + '" />';
pickup += '<img src="' + CONTEXT_PATH + '/static/img/icon/ico_white.png" alt="" width="2" />';
pickup += '<img src="' + jsondata.oList[i].kaisaiIconFile + '" alt="' + jsondata.oList[i].kaisaiIconName + '" />';
if( jsondata.oList[i].huka1File == null || jsondata.oList[i].huka1File ==""){
jsondata.oList[i].huka1Name = "";
jsondata.oList[i].huka1File = CONTEXT_PATH + "/static/img/icon/ico_white.png";
}
pickup += '<img src="' + jsondata.oList[i].huka1File + '" alt="' + jsondata.oList[i].huka1Name + '" />';
if( jsondata.oList[i].huka2File == null || jsondata.oList[i].huka2File ==""){
jsondata.oList[i].huka2Name = "";
jsondata.oList[i].huka2File = CONTEXT_PATH + "/static/img/icon/ico_white.png";
}
pickup += '<img src="' + jsondata.oList[i].huka2File + '" alt="' + jsondata.oList[i].huka2Name + '" />';
pickup += '</p>';
pickup += '<p>';
if(jsondata.oList[i].saleStatus != null && jsondata.oList[i].saleStatus != ""){
pickup += '<span class="bet_info ' + jsondata.oList[i].saleStatusColor + '">' + jsondata.oList[i].saleStatus + '</span>';
}
pickup += '<span class="bet_info">' + jsondata.oList[i].race + '</span>';
pickup += '</p>';
pickup += '<p>';
if(jsondata.oList[i].denTime){
pickup += '<span class="bet_info">発売締切</span>';
pickup += '<span class="bet_info">' + jsondata.oList[i].denTime + '</span>';
} else {
pickup += '<span class="bet_info"></span>';
pickup += '<span class="bet_info"></span>';
}
pickup += '</p>';
pickup += '</div>';
if(jsondata.oList[i].lnkPara){
pickup += '<p class="raceListLink"><img src="' + CONTEXT_PATH + '/static/img/icon/ico_arrow03.png" alt=""></p>';
}else{
pickup += '<p class="raceListLink"><img src="' + CONTEXT_PATH + '/static/img/icon/ico_arrow03_w.png" alt=""></p>';
}
pickup += '</a></li>';
ul.append(pickup);
}
pickup = '<div class="clear-fix" style="margin-top: 5px;">';
var disable = '';
if( jsondata.oList[0].pickupBtnDisp == "1" )
disable = 'disabled=true';
pickup += '<p class="fl-l" style="margin: 5px 0 5px 5px;"><button id="pickup_slide_prev" type="button" class="btn onbtn" style="width: 60px;" onclick="pickup_slide(2);" ' + disable + '>&lt;</button></p>';
pickup += '<p class="fl-r" style="margin: 5px 5px 5px 0;"><button id="pickup_slide_next" type="button" class="btn onbtn" style="width: 60px;" onclick="pickup_slide(1);" ' + disable + '>&gt;</button></p>';
pickup += '</div>';
ul.append(pickup);
divPickupList.append(ul);
qnum=1;
picktimer();
}else{
divPickupList.append('<div class="al-c" style="margin-bottom: 16px;">' + jsondata.msgNone + '</div>');
}
}
commonLoad.loadingImage("false");
return;
},
brDrawJSONData: function(jsondata, reqPrm) {
div_success = '#push_today'; 
div_error = '#push_err_div'; 
prm_div_error = 'push_err_div'; 
var setPrm = null;
if(jsondata && jsondata.reqprm) {
setPrm = jsondata.reqprm;
}else{
setPrm = reqPrm;
}
if( !jsondata) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
$('#brtabTomorrow').removeClass("active");
$('#brtabToday').addClass("active");
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqItiosiInfo(arg0);});
} else if(Object.keys(jsondata).length == 0) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
$('#brtabTomorrow').removeClass("active");
$('#brtabToday').addClass("active");
Com.makePcUpdatePage(prm_div_error, null, setPrm, function(arg0){PJ0101Controller.reqItiosiInfo(arg0);});
} else if( jsondata.resultCd == -1 ) {
$(div_success).addClass('dispoff');
$(div_error).removeClass('dispoff');
var message = "";
if( jsondata.message != undefined ) {
message = jsondata.message;
}
Com.makePcUpdatePage(prm_div_error, message, setPrm, function(arg0){PJ0101Controller.reqItiosiInfo(arg0);});
} else {
$(div_success).removeClass('dispoff');
$(div_error).addClass('dispoff');
var divPushList = $('#push_today');
divPushList.removeClass('dispoff');
$('#no_push').addClass('dispoff');
divPushList.empty();
if(jsondata.oList && jsondata.oList.length > 0 ){
$('#brpIchioshiListLink').removeClass('dispoff');
var ul = $('<ul class="al-l" style="padding-left: 0px;">');
var push = null;
for(var i = 0; i < jsondata.oList.length; i++ ){
push = '<li id="push_' + (i + 1 ) + '" class="pushPlayer';
if( jsondata.oList[i].zenColor != null && jsondata.oList[i].zenColor != ""){
push += ' ' + jsondata.oList[i].zenColor;
}
var attr = "";
if(jsondata.oList[i].lnkPara){
attr = 'class="memlink" onclick="btnItiosiClick(\''+ jsondata.oList[i].lnkPara + '\'); return false;" href=\"\"';
}else{
attr = 'class="memlink2"';
}
push += '">' +
'<a target="_self" ' + attr + '>' +
'<div class="pickupRaceText" style="display: block; margin-top: -15px;">';
var senshuGazouFile = ''; 
var addNoImageClass = ''; 
if (jsondata.oList[i].senshuGazouFile != null && jsondata.oList[i].senshuGazouFile != "") {
senshuGazouFile = ' src="' + CMS_PATH + jsondata.oList[i].senshuGazouFile + '"'
 +' alt="' + jsondata.oList[i].nameSeiMei + '　選手 (' + jsondata.oList[i].kuniMei + jsondata.oList[i].kyuhanMei + ') "';
} else {
addNoImageClass = ' face_pickup_deffw';
}
push += '<table class="ichiosi_tbl"><tr><td>';
push += '<table class="ichiosi_left_tbl">';
push += '<tr>';
push += '<td class="pict"><div class="face_pickup_mxw"><img class="face_pickup' + addNoImageClass + '"' + senshuGazouFile + ' /></div></td>';
push += '<td>';
push += '<div><b>' + jsondata.oList[i].nameSeiMei + '</b>　選手</div>';
push += '<div>(' + jsondata.oList[i].kuniMei + jsondata.oList[i].kyuhanMei + ')</div>';
push += '</td>';
push += '</tr>';
push += '<tr>';
push += '<td colspan="2" class="icon">';
push += '<div class="nobr" style="width: 66px;">' + jsondata.oList[i].keirinMei + '</div>';
push += '<img src="' + jsondata.oList[i].gradeIconFile + '" alt="' + jsondata.oList[i].nichijiIconName + '" />';
push += '<img src="' + jsondata.oList[i].nichijiIconFile + '" alt="' + jsondata.oList[i].nichijiIconName + '" />';
push += '<img src="' + CONTEXT_PATH + '/static/img/icon/ico_white.png" alt="" width="2" />';
push += '<img src="' + jsondata.oList[i].kaisaiIconFile + '" alt="' + jsondata.oList[i].kaisaiIconName + '" />';
if( jsondata.oList[i].huka1File == null || jsondata.oList[i].huka1File ==""){
jsondata.oList[i].huka1Name = "";
jsondata.oList[i].huka1File = CONTEXT_PATH + "/static/img/icon/ico_white.png";
}
push += '<img src="' + jsondata.oList[i].huka1File + '" alt="' + jsondata.oList[i].huka1Name + '" />';
if( jsondata.oList[i].huka2File == null || jsondata.oList[i].huka2File ==""){
jsondata.oList[i].huka2Name = "";
jsondata.oList[i].huka2File = CONTEXT_PATH + "/static/img/icon/ico_white.png";
}
push += '<img src="' + jsondata.oList[i].huka2File + '" alt="' + jsondata.oList[i].huka2Name + '" />';
push += '</td>';
push += '</tr>';
push += '<tr>';
push += '<td colspan="2">';
if(jsondata.oList[i].saleStatus != null && jsondata.oList[i].saleStatus != ""){
push += '<span class="bet_info ' + jsondata.oList[i].saleStatusColor + '">' + jsondata.oList[i].saleStatus + '</span>&nbsp;';
}
push += '<span class="bet_info">' + jsondata.oList[i].race + '</span>';
push += '</td>';
push += '</tr>';
push += '<tr>';
push += '<td colspan="2">';
if(jsondata.oList[i].denTime){
push += '<span class="bet_info">発売締切</span>';
push += '<span class="bet_info">' + jsondata.oList[i].denTime + '</span>';
} else {
push += '<span class="bet_info"></span>';
push += '<span class="bet_info"></span>';
}
push += '</td>';
push += '</tr>';
push += '</table>';
push += '</td><td>';
if(jsondata.oList[i].lnkPara){
push += '<img src="' + CONTEXT_PATH + '/static/img/icon/ico_arrow03.png" alt="">';
}else{
push += '<img src="' + CONTEXT_PATH + '/static/img/icon/ico_arrow03_w.png" alt="">';
}
push += '</td><tr></table>';
push += '</div>';
push += '</a>';
push += '</li>';
ul.append(push);
}
if (jsondata.blnDispNextFlg == true){
push = '<div class="clear-fix" style="margin: 10px;">';
push += '<p class="al-c"><button id="pickup_slide_prev1" type="button" class="btn onbtn" style="width: 100px;" onclick="tabPushClick(' + jsondata.kaisaiDate + ',1);">もっと見る</button></p>';
push += '</div>';
ul.append(push);
}
divPushList.append(ul);
$('#brpIchioshiListLink').removeClass('dispoff');
}else{
if (jsondata.blnIchioshiFlg == false){
var divNoPush = $('#no_push');
divNoPush.empty();
divNoPush.append('<li class="dispon nonMember no_bbottom">' +
'<p style="padding: 10px;">一押し選手を登録すると、その選手が出場する今日、明日のレースが表示されます。</p>' +
'<p class="al-c" style="padding: 10px;">選手検索は<a href="' + $('#sensyuserchURL').val() + '" class="txt_underline">こちら</a></p>' +
'<p style="padding: 10px;">一押し選手は、選手検索から登録できます。</p></li>');
$('#push_today').addClass('dispoff');
$('#no_push').removeClass('dispoff');
$('#brpIchioshiListLink').addClass('dispoff');
} else {
divPushList.append('<div class="al-c" style="margin-bottom: 16px;">' + jsondata.msgNone + '</div>');
$('#brpIchioshiListLink').removeClass('dispoff');
}
}
}
commonLoad.loadingImage("false");
return;
},
};
function getWidth($txt, mode){
var body = $(document.body);
var dummyWrapper = $('<div class="dokanto7_t1" />')
var dummy = $('<span />');
var ret = 0;
dummyWrapper.css({
position: 'absolute',
top: 0,
left: 0,
width: 9999,
'z-index': -1,
});
if(mode && mode == 1){
dummy.append($txt.text());
}else{
dummy.append($txt);
}
dummy.css({
color: 'transparent',
'letter-spacing': $txt.css('letter-spacing'),
});
body.append(dummyWrapper.append(dummy));
ret = dummy.width();
setTimeout(function(){
dummyWrapper.remove();
}, 0);
return ret;
}
function setTicker(id, areaHeight){
var _scroll = {
delay: 1000,
easing: 'linear',
items: 1,
duration: 0.05,
timeoutDuration: 0
};
$(id).carouFredSel({
width: 210,
align: false,
items: {
width: 'variable',
height: areaHeight,
visible: 1
},
scroll: _scroll
});
}
