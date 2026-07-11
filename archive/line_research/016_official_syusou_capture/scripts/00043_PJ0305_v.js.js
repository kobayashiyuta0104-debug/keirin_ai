var slView = {
HDNKEY_ID: 'ppj0305',
slKeirinCd: '',
slKaisaihi: '',
slDrawJSONData: function(json) {
var edtNarabiYoso = (function(raceNo, nInfo, line, lineColor, seriFlag, narabiYCnt){
var tr = $('<tr />')
tr.append('<td class="sltitle">並び予想</td>');
var lineCls = '';
var lineName = '&nbsp;';
if (line){
lineCls = lineColor;
lineName = line;
}
var seri = "";
var seriCls = "";
if (seriFlag == "1"){
seri = '競';
seriCls = 'seri'
}else{
seri = '&nbsp;';
}
var arrow = '&nbsp;';
if(nInfo && nInfo.length > 0){
arrow = '<img class="slyajirusi_left" src="' + CONTEXT_PATH + '/static/img/member_left.png"/>&nbsp;</td>';
}
tr.append('<td class="slbtype" valign="top">' +
   '<table class="sltb_04" style="border: 0;"><tr style="height: 23px;">' +
   '<td class="sltx-c ' + lineCls + '" style="width: 78px;">' + lineName + '</td>' +
   '<td class="sltx-c" style="width: 8px;">&nbsp;</td>' +
   '<td class="sltx-c ' + seriCls + '" style="width: 36px;">' + seri  + '</td>' +
   '<td class="sltx-r" style="width: 160px;">' +
   arrow +
   '</tr></table></td>');
tr.append($('<td class="slsno_all" align="left" valign="top" />').append($('<table style="width:100%; table-layout:fixed;" />').append(makeYosoTable(raceNo, narabiYCnt))));
return $('<table class="slnara_all_tbl" />').append(tr);
});
var makeYosoTable = (function(raceNo, narabiYCnt){
var retBodyHtml = "";
for(var yLoop = 1 ; yLoop <= narabiYCnt; yLoop++){
retBodyHtml += '<tr>';
for(var xLoop = 1 ; xLoop <= 14; xLoop++){
retBodyHtml += '<td id="slyoso_td_'+ raceNo +'_'+ xLoop +'_'+ yLoop +'" class="al-c">&nbsp;</td>';
}
retBodyHtml += '</tr>';
}
return retBodyHtml;
});
var edtNarabi = (function(raceNo, nInfo){
if(!nInfo){
return;
}
for(var i = 0; i < nInfo.length; i++){
var syaban = '<span class="slsnum16 base_color_' + nInfo[i].syaban + '">' + nInfo[i].syaban + '</span>';
$('#slyoso_td_'+ raceNo +'_'+ nInfo[i].narabiX +'_'+ nInfo[i].narabiY).html(syaban);
}
});
var edtSyabetu = (function(sInfo, ichiIconURL, kouIconURL){
var table = $('<table class="sltb_03 slma-0" style="width: 100%;" />');
for(var i = 0; i < Math.ceil(sInfo.length / 3); i++){
var tr = $('<tr />');
var cols = 3;
if((sInfo.length - (i * 3)) / 3 < 1){
cols = sInfo.length - (i * 3);
}
var btFlag = 0; 
if(i == 0){
btFlag = 1;
}
for(var j = 0; j < cols; j++){
var blFlag = 0; 
if(j == 0){
blFlag = 1;
}
tr.append(edtSensyu(sInfo[i * 3 + j], blFlag, btFlag, ichiIconURL, kouIconURL));
}
table.append(tr);
}
return $('<td class="slva-top" />').append(table);
});
var edtSensyu = (function(sensyu, borderLeftFlag, borderTopFlag, ichiIconURL, kouIconURL){
var mark = "&nbsp;";
if(sensyu.Yosoin != null){
mark = sensyu.Yosoin;
}
var kyakuColor = "";
if (sensyu.kyakuColor != null){
kyakuColor = sensyu.kyakuColor;
}
var ichiKouIcon = "";
if(sensyu.itiosiFlag != null && ichiIconURL != null && sensyu.itiosiFlag == 1){
ichiKouIcon += "<div class='slichi_icon' style='background-image:url(\"" + ichiIconURL + "\");'></div>";
}
if(sensyu.aisyoFlag != null && kouIconURL != null && sensyu.aisyoFlag == 1){
ichiKouIcon += "<div class='slkou_icon' style='background-image:url(\"" + kouIconURL + "\");'></div>";
}
borderLeft = "";
if(borderLeftFlag == 1){
borderLeft = " slbd_l";
}
borderTop = "";
if(borderTopFlag == 1){
borderTop = " slbd_t";
}
var ret = '<td class="sltb-no' + sensyu.syaban + ' ' + sensyu.syabanColor + ' ' + borderTop + borderLeft + '">' + sensyu.syaban + '</td>' +
      '<td class="sltb-mark'      + borderTop + '" style="font-size:20px">' + mark + '</td>' +
      '<td class="sltbl_no11_6B'  + borderTop + '" ><a class="sllink_name" href="" onclick="slSensyuClick(\'' + sensyu.senNo + '\');return false;">' + sensyu.senName + '</a></td>' +
      '<td class="sltbl_no11B_sp' + borderTop + '" >&nbsp;</td>' +
      '<td class="sltbl_no11_3B'  + borderTop + '" >' + sensyu.huken + '</td>' +
      '<td class="sltbl_no11B_sp' + borderTop + '" >&nbsp;</td>' +
      '<td class="sltbl_no11_1B'  + borderTop + ' ' + kyakuColor + '">' + sensyu.kyaku + '</td>' +
      '<td class="sltbl_no11B_sp' + borderTop + '" >&nbsp;</td>';
if(sensyu.assen != null){
ret += '<td class="sltbl_col_end ' + sensyu.assenColor + ' ' + borderTop + '">' + sensyu.assen + '</td>';
}else{
ret += '<td class="sltbl_col_end ' + borderTop + '">' + ichiKouIcon + '</td>';
}
return ret;
});
if( !json ) {
Com.viewErrorPage(null);
} else if( json.resultCd == -1 ) {
var messageCd = "";
if( json.messageCd != undefined ) {
messageCd = json.messageCd;
}
Com.viewErrorPage(messageCd);
} else {
$("#sllblLastUpdateTime1").empty();
if(json.kaisaiMsg){
var msgArea = $('#sllblMsg');
msgArea.empty();
msgArea.append(json.kaisaiMsg);
$('#sltrMsg').removeClass('dispoff');
$('#sltrUpdateTime1').removeClass('dispoff'); 
$('#sllblLastUpdateTime2').addClass('dispoff'); 
}else{
$('#sltrMsg').addClass('dispoff');
$('#sltrUpdateTime1').addClass('dispoff'); 
$('#sllblLastUpdateTime2').removeClass('dispoff'); 
}
if(json.syusouDispFlag == 0){
$('#sldivLegend').addClass('dispoff'); 
$('#sldivbtnPrint').addClass('dispoff'); 
$('#sllblDigestGuide').addClass('dispoff'); 
$('#sldivDigestButton').addClass('dispoff'); 
$('#sldivSyusouList').empty();
return;
}else{
$('#sldivLegend').removeClass('dispoff'); 
$('#sldivbtnPrint').removeClass('dispoff'); 
$('#sllblDigestGuide').removeClass('dispoff'); 
$('#sldivDigestButton').removeClass('dispoff'); 
}
slView.slKeirinCd = json.keirinCd;
slView.slKaisaihi = json.kaisaihi;
$('#sllblLastUpdateTime1').html(json.lastUpdateTime);
$('#sllblLastUpdateTime2').html(json.lastUpdateTime);
if(json.legendDspFlag == 1){
$('#sldivLegend').removeClass('dispoff');
}else{
$('#sldivLegend').addClass('dispoff');
}
var divSyusouList = $('#sldivSyusouList');
divSyusouList.empty();
var narabiTyuiFlg = false;
for(var i = 0; i < json.rInfo.length; i++ ){
var raceBgColor = "";
if(json.rInfo[i].zenBgColor){
raceBgColor = json.rInfo[i].zenBgColor;
}else if(i % 2 == 1){
raceBgColor = 'altertable_guusu';
}
var raceTable;
if(i == 0){
raceTable = $('<table class="sltbl_02 slma-0 ' + raceBgColor + '" />'); 
}else{
raceTable = $('<table class="sltbl_02-2 slma-0 ' + raceBgColor + '" />'); 
}
var tdRaceTable = $('<td class="slma-0" />'); 
var trRaceTop = $('<tr />'); 
var trNarabiDigest = $('<tr />'); 
trRaceTop.append('<td class="slva-top sltx-l" style="width: 160px;">' +
        '<div class="slinline slmgn-l-5 sltx-l bold" style="width: 26px; font-size: 17px;">' + json.rInfo[i].raceNo + 'R</div>' +
         '<div class="slinline" style="width: 10px;">&nbsp;</div>' +
         '<div class="slinline">' + json.rInfo[i].syumoku + '</div></td>');
if(json.rInfo[i].narabiFlg == 1){
trNarabiDigest.append($('<td class="sltx-l" style="width: 748px;" />').append(edtNarabiYoso(json.rInfo[i].raceNo, json.rInfo[i].nInfo, json.rInfo[i].line, json.rInfo[i].lineColor, json.rInfo[i].seri, json.rInfo[i].narabiYCnt)));
narabiTyuiFlg = true;
}else if(json.rInfo[i].narabiMsg){
trNarabiDigest.append('<td class="sltx-l" style="width: 748px;"><table class="slnara_all_tbl"><tr>' +
       '<td class="sltitle">並び予想</td>' +
       '<td align="center" valign="top">' + json.rInfo[i].narabiMsg + '</td></tr></table></td>');
}else{
trNarabiDigest.append('<td class="sltx-l" style="width: 748px;" />');
}
var disabled = "";
if(json.rInfo[i].digetFlag != 1){
disabled = "disabled";
}
trNarabiDigest.append('<td class="sltx-c slva-mid" style="width: 118px;"><button id="slbtnContinuationReplay' + json.rInfo[i].raceNo + '" type="button" ' + disabled + ' class="slbtn onbtn saisei btn_fsz" style="width: 100px;" onclick="slContinuationReplayClick(this)";><input class="slchk" name="slchkContinuationReplay" value="' + json.rInfo[i].raceNo + '" type="checkbox">連続再生</button></td>');
trNarabiDigest.append('<td class="sltx-c slva-mid" style="width: 138px;"><button id="slbtnDigest' + json.rInfo[i].raceNo + '" type="button" ' + disabled + ' class="slbtn onbtn saisei btn_fsz" style="width: 130px;" onclick="slDigestClick(' + json.rInfo[i].raceNo + ');"><img height="16" style="margin-right: 6px;" alt="film" src="' + CONTEXT_PATH + '/static/img/icon/ico_film.png">ダイジェスト</button></td>');
trRaceTop.append($('<td class="sltxr-va-top" style="width: 1028px;" />')
         .append($('<table class="sltbl_01" style="width: 100%;" />')
          .append(trNarabiDigest)));
        tdRaceTable.append($('<table id="" class="sltbl_01 slma-0" style="width: 100%;" />')
                          .append(trRaceTop));
var trRaceBottom = $('<tr />');
var trSensyu = $('<tr />');
trSensyu.append('<td style="width: 81px;">' +
           '<div class="slmgn-l-5 sltx-l">発売締切:<br><span class="' + json.rInfo[i].denTimeColor + '">' + json.rInfo[i].denTime + '</span></div>' +
           '<div class="slmgn-l-5 sltx-l">発走予定:<br><span class="' + json.rInfo[i].stTimeColor + '">' + json.rInfo[i].stTime + '</span></div></td>');
trSensyu.append(edtSyabetu(json.rInfo[i].sInfo, json.itiosiURL, json.aisyoURL));
trRaceBottom.append($('<td colspan="2" class="slva-top">').append($('<table style="width: 100%;" />').append(trSensyu)));
var tdButtons = $('<td class="sltx-c" style="width: 244px;" />');
tdButtons.append('<div class="slinlineBtnBox"><button id="slbtnLiveVote' + json.rInfo[i].raceNo + '" type="button" class="slbtn onbtn btn_fsz sltx-c on" style="width: 60px; height: 60px; padding: 0px; margin-left: 6px; margin-right: 0px;" onclick="slLiveVoteClick(' + json.rInfo[i].raceNo + ');">LIVE&amp;<br>投票</button></div>');
if(json.rInfo[i].ozzFlg == 1){
disabled = "";
}else{
disabled = "disabled";
}
tdButtons.append('<div class="slinlineBtnBox"><button id="slbtnOzz' + json.rInfo[i].raceNo + '" type="button" ' + disabled + ' class="slbtn onbtn btn_fsz sltx-c on" style="width: 60px; height: 60px; padding: 0px; margin-left: 6px; margin-right: 0px;" onclick="slOzzClick(' + json.rInfo[i].raceNo + ');">オッズ</button></div>');
if(json.rInfo[i].resultFlg == 1){
disabled = "";
}else{
disabled = "disabled";
}
tdButtons.append('<div class="slinlineBtnBox"><button id="slbtnResult' + json.rInfo[i].raceNo + '" type="button" ' + disabled + ' class="slbtn onbtn btn_fsz sltx-c" style="width: 60px; height: 60px; padding: 0px; margin-left: 6px; margin-right: 6px;" onclick="slResultClick(' + json.rInfo[i].raceNo + ');">結　果</button></div>');
trRaceBottom.append(tdButtons);
        tdRaceTable.append($('<table id="" class="sltbl_01 slma-0" style="width: 100%;" />')
            .append(trRaceBottom));
        divSyusouList.append(raceTable.append($('<tr />').append(tdRaceTable)));
}
for(var i = 0; i < json.rInfo.length; i++ ){
if(json.rInfo[i].narabiFlg == 1){
edtNarabi(json.rInfo[i].raceNo, json.rInfo[i].nInfo);
}
}
$("#sllblNarabiMei").remove();
if(json.narabiMei != null){
var sllblNarabiMei = '<div id="sllblNarabiMei" class="w100pc"><table class="w100pc"><tbody><tr>';
if(narabiTyuiFlg){
sllblNarabiMei = sllblNarabiMei + '<td id="brlblNarabiTyui" class="al-l">※この並びはあくまで予想の為、実際の並びとは異なることがあります。</td>';
}
sllblNarabiMei = sllblNarabiMei + '<td class="al-r">並び予想　情報提供：' + json.narabiMei + '</td></tr></tbody></table></div>';
$("#slDivBottom").before(sllblNarabiMei);
}
$("#sllblYosoinMei").remove();
if(json.YosoinMei != null){
$("#slDivBottom").before('<div id="sllblYosoinMei" class="al-r">予想印　情報提供：' + json.YosoinMei + '</div>');
}
$('#FPJ0305_dlg_msg').empty();
$('#FPJ0305_dlg_msg').append($('<span />').append(json.dlgMsg));
if($("#sltrUpdateTime1").hasClass("dispoff")){
    $("#timeArea .slt1-1").addClass("dispoff");
}
return;
}
}
};
