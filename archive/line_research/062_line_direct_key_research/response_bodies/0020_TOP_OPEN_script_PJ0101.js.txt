var prmDokantoKeirinCD; 
var prmDokantoKaisaiDate; 
var prmDokantoEnc; 
$(document).ready(function() {
if(isUnSupported()){
$('#ttUsrEnvMsg').removeClass('dispoff');
}else{
$('#ttUsrEnvMsg').addClass('dispoff');
}
PJ0101View.cDrawJSONData(jsonData['JSJ057'], null);
PJ0101View.bclDrawJSONData(jsonData['JSJ078'], null);
PJ0101View.bcrDrawJSONData(jsonData['JSJ079'], null);
PJ0101View.clDrawJSONData(jsonData['JSJ080'], null);
PJ0101View.brDrawJSONData(jsonData['JSJ081'], null);
PJ0101View.tlDrawJSONData(jsonData['JSJ082'], null);
$('#bccmbCategory').change(function(){
PJ0101Controller.reqTopicsInfo($(this).val());
});
$('#bccmbTiku').change(function(){
PJ0101Controller.reqOshiraseInfo($(this).val());
});
if(document.getElementById('slides') == null){
$('#tcdivSpace').addClass('dispoff');
$('#top_raceinfo').css('margin-top', '22px');
$('#link_block').css('position', 'static');
}
if(document.getElementById('dspBtnG3BannerFlag').value == "false") {
$('#top_r_banner1').prop("disabled", true);
$('#top_r_banner2').prop("disabled", true);
}
if(document.getElementById('warnticker') != null){
var widthTckH = document.getElementById("warnticker").getBoundingClientRect().width;
$('#warnticker_inner').append($('<div />').width(widthTckH).addClass('dispib').append($('<span />').addClass('ticker').css('height','32px').append('&nbsp;')));
$('#warnticker_inner').append($('<span />').append('↓車券は 20 歳になってから↓ ↓のめり込みが不安な方はこちら（購入限度額の設定）↓'));
tickerdisp(0,'warnticker',widthTckH);
}
});
function btnDokantoVoteClick(){
commonSubmit.formPost($('#dokantoVoteURL').val(), { "bkcd" : prmDokantoKeirinCD,
"kday" : prmDokantoKaisaiDate }, "_self");
}
function btnDokantoResultClick(){
commonSubmit.formPost($('#syusoListURL').val(), { "disp" : "PJ0306", 
  "encp" : prmDokantoEnc}, "_self");
}
function gradeRaceClick(prm){
commonSubmit.formPost($('#syusoListURL').val(), { "encp" : prm, "disp" : "PJ0302" }, "_self");
}
function syuyoSensyuClick(prm){
commonSubmit.formGet($('#profileURL').val(), { "snum" : prm }, "_self");
}
function btnLiveVoteClick(prm){
commonSubmit.formPost($('#raceBasicInfoURL').val(), { "encp" : prm, "disp" : "PJ0315" }, "_self");
}
function btnSyusouListClick(prm){
commonSubmit.formPost($('#syusoListURL').val(), { "encp" : prm, "disp" : "PJ0305" }, "_self");
}
function btnOddsClick(prm){
commonSubmit.formPost($('#raceBasicInfoURL').val(), { "encp" : prm, "disp" : "PT0511" }, "_self");
}
function btnResultClick(prm){
commonSubmit.formPost($('#syusoListURL').val(), { "encp" : prm, "disp" : "PJ0306" }, "_self");
}
function btnSisetuClick(prm){
commonSubmit.formGet($('#sisetuURL').val(), { "jocd" : prm }, "_self");
}
function btnPickupClick(prm){
commonSubmit.formPost($('#raceBasicInfoURL').val(), { "encp" : prm, "disp" : "PJ0315" }, "_self");
}
function btnItiosiClick(prm){
commonSubmit.formPost($('#raceBasicInfoURL').val(), { "encp" : prm, "disp" : "PJ0315" }, "_self");
}
function btnLoginClick(){
if( !commonLoad.wclkchk(event) ) {
return false;
}
if(($('#trtxtBallotID').val() == '' && $('#trtxtBallotPW').val() == '') || 
   ($('#trtxtBallotID').val() != '' && $('#trtxtBallotPW').val() != '')){
return true;
} else {
$('#alert_dialog').dialog( 'open' );
return false;
}
}
function tabKaisaiClick(kbn){
switch (kbn) {
case 1:
PJ0101Controller.reqKaisaiInfo($('#prevDate').val());
$('#trLegendNextDay').addClass("dispoff");
$('#trLegend').removeClass("dispoff");
break;
case 2:
PJ0101Controller.reqKaisaiInfo($('#todayDate').val());
$('#trLegendNextDay').addClass("dispoff");
$('#trLegend').removeClass("dispoff");
break;
case 3:
PJ0101Controller.reqKaisaiInfo($('#nextDate').val());
$('#trLegend').addClass("dispoff");
$('#trLegendNextDay').removeClass("dispoff");
break;
default:
break;
}
}
function tabPickupClick(kbn){
switch (kbn) {
case 2:
PJ0101Controller.reqPickupInfo($('#todayDate').val());
break;
case 3:
PJ0101Controller.reqPickupInfo($('#nextDate').val());
break;
default:
break;
}
}
function tabPushClick(kbn,more){
switch (kbn) {
case 2:
PJ0101Controller.reqItiosiInfo($('#todayDate').val(),more);
break;
case 3:
PJ0101Controller.reqItiosiInfo($('#nextDate').val(),more);
break;
default:
break;
}
}
var qnum=1;
var pickupTimer;
picktimer();
function picktimer(){
clearInterval(pickupTimer);
pickupTimer = setInterval(function(){
if(document.getElementById("pickup_2") == null){
return;
}
pickoff();
qnum++;
if(document.getElementById("pickup_"+qnum) == null){
qnum=1;
}
$("#pickup_"+qnum).removeClass("dispoff").addClass("dispon").animate({"margin-left":"-250px" }, 10).animate({"margin-left":"0" }, 300);
},5000);
}
function pickoff(){
var len = $("li[id ^='pickup_']").length;
for(var i=1;i<=len;i++){
$("#pickup_"+i).removeClass("dispon").addClass("dispoff");
}
}
function pickup_slide(mode){
$("li#pickup_" + qnum).removeClass("dispon").addClass("dispoff");
if( mode == 1){
qnum++;
if(document.getElementById("pickup_"+qnum) == null){
qnum=1;
}
} else {
qnum--;
if(document.getElementById("pickup_"+qnum) == null){
qnum = $("li[id ^='pickup_']").length;
}
}
$("li#pickup_" + qnum).removeClass("dispoff").addClass("dispon").animate({"margin-left":"0"}, 300);
picktimer();
}
function newsHeightAdjust(){
if($("#ktopic_list").height() > $("#kosirase_list").height()) {
$("#kosirase_list").height( $("#ktopic_list").height() );
$("#ktopic_list").height( $("#kosirase_list").height() );
}
else {
$("#ktopic_list").height( $("#kosirase_list").height() );
$("#kosirase_list").height( $("#ktopic_list").height() );
}
}
function isUnSupported(){
var ret = false;
var userAgent = navigator.userAgent;
if((userAgent.toLowerCase()).indexOf("msie") != -1){
BrowserVer  = userAgent.substr((userAgent.toLowerCase()).indexOf("msie")+5,(userAgent.toLowerCase()).indexOf(";",(userAgent.toLowerCase()).indexOf("msie"))-(userAgent.toLowerCase()).indexOf("msie")-5);
if(BrowserVer == "8.0" || BrowserVer == "9.0"){
ret = true;
}
}
if(!comKaime.kimIfSessionStorage()){
ret = true;
}
return ret;
}
$(function () {
$('.slide-items').slick({
arrows: false,
dots: false,
autoplay: true,
autoplaySpeed: 4000,
infinite: true,
swipe: true,
touchMove: true
});
$(".slide-items3").on('init', function(event,slick){
changeThumbsFrame(0);
});
$(".slide-items3").slick({
slidesToShow: 7
});
$(".slide-items").on('afterChange', function(event,slick,currentSlide){
changeThumbsFrame(currentSlide);
});
function changeThumbsFrame(index) {
$("#slide3 .slick-slide").removeClass("current-frame");
$("#slide3 .slick-slide").eq(index).addClass("current-frame");
}
$('.slide-items2').slick({
slidesToShow: 1,
slidesToScroll: 1,
vertical: true,
arrows: false,
dots: false,
autoplay: true,
autoplaySpeed: 8000,
infinite: true
});
$('#top_r_banner1').on('click', function(){
$('.slide-items2').slick('slickPrev');
});
$('#top_r_banner2').on('click', function(){
$('.slide-items2').slick('slickNext');
});
setInterval(function(){
$("[id=blink_win6]").animate({ opacity: "0.0"}, 250).animate({ opacity: "1.0"}, 250);
},500);
$('.slide-items4').slick({
slidesToShow: 6,
speed: 450,
arrows: true,
prevArrow: $('#slick-prev'),
nextArrow: $('#slick-next'),
dots: false,
autoplay: true,
autoplaySpeed: 2700,
infinite: true,
swipe: false,
touchMove: false
});
});
function slide3_click(index) {
$('.slide-items').slick('slickGoTo', index);
}
var rankup_text_cnt=0;
var rankup_text_type=0;
$(window).load(function() {
setInterval(function(){
var nowdate = new Date();
if((nowdate.getSeconds()%2) != 0 ) {
$("[id=rank_up]").css("background-color","#FD3838");
}
else {
$("[id=rank_up]").css("background-color","#FF9000");
}
},1000);
setInterval(function(){
rankup_text_cnt++;
if(rankup_text_cnt >=1 ) {
rankup_text_cnt=0;
if(rankup_text_type==0) {
rankup_text_type=1;
$("[id=rank_up_text]").html("お め で と う");
}
else {
rankup_text_type=0;
$("[id=rank_up_text]").html("ラ ン ク ア ッ プ");
}
}
},2000);
setInterval(function(){
$("[id=tlimgHatubaiIcon]").animate({ opacity: "0.0"}, 200).animate({ opacity: "1.0"}, 200);
$(".dokantbg_border").css({outline: "2px solid #e72222"}).animate({outlineColor: "#e72222",outlineWidth: "0"}, 200).animate({outlineColor: "#fff",outlineWidth: "2px"}, 200).animate({outlineColor: "#e72222",outlineWidth: "2px"}, 200);
$("[id=hatubaicyuu7]").animate({ opacity: "0.0"}, 200).animate({ opacity: "1.0"}, 200);
$("[id=hatubaicyuu4]").animate({ opacity: "0.0"}, 200).animate({ opacity: "1.0"}, 200);
},4000);
if($('.slide-items4 .slick-track div:not(".slick-cloned")').length <= 6){
$('.flex-nav-prev').addClass('disabled');
$('.flex-nav-next').addClass('disabled');
}
newsHeightAdjust();
});