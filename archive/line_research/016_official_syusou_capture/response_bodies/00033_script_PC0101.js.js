function shLinkClick(id){
pc0101_checkKaime(id);
}
function shClickBreadCrumb(index){
var retKimIfExist;
var objKimGetNoSetKaimeGroup;
var ctrlId= "[id=shBreadCrumbLnkPath_"+index+"]";
var url = $(ctrlId).attr("value");
var params = {};
ctrlId= "[id=shBreadCrumb_PGFlg_"+index+"]";
var pgFlg = $(ctrlId).attr("value");
ctrlId= "[id=shBreadCrumbDspId_"+index+"]";
var dspId = $(ctrlId).attr("value");
var prm;
if (dspId == "FPJ0305") {
prm = hhGetEncFstK();
params["disp"] = "PJ0301";
params["encp"] = prm;
}
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
if (pgFlg == 0){
commonSubmit.formPost(url, params, "_self");
} else {
commonSubmit.formGet(url, params, "_self");
}
return;
},function(){
});
} else {
comKaime.kimClear();
if (pgFlg == 0){
commonSubmit.formPost(url, params, "_self");
} else {
commonSubmit.formGet(url, params, "_self");
}
}
return false;
}
function pc0101_checkKaime(id){
var retKimIfExist;
var objKimGetNoSetKaimeGroup;
var fwurl;
var clrl;
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
pc0101_ok_normal(0,id);
comKaime.kimClear();
return;
},function(){
});
} else {
comKaime.kimClear();
pc0101_ok_normal(0,id);
return;
}
return false;
}
function pc0101_checkKaimeLive(index){
var retKimIfExist;
var objKimGetNoSetKaimeGroup;
var ctrlId= "[id=hcomHdnTouhyouLive"+index+"]";
var encPrm =$(ctrlId).attr("value");
ctrlId = "[id=shParentDisp]";
var dspId = $(ctrlId).attr("value");
var url = $(shLiveLinkPath).attr("value");
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
pc0101_okLive(index);
return;
},function(){
});
} else {
comKaime.kimClear();
if (dspId == "FPJ0315"){
btnLiveVoteClick("1", encPrm);
} else {
commonSubmit.formPost(url, { "encp" : encPrm }, "_self");
}
}
return false;
}
function pc0101_checkKaimeTouhyou(mode,index){
var retKimIfExist;
var objKimGetNoSetKaimeGroup;
var ctrlId= "[id=hcomHdnTouhyouLive"+index+"]";
var encPrm =$(ctrlId).attr("value");
ctrlId = "[id=shParentDisp]";
var dspId = $(ctrlId).attr("value");
var url = $(shTouhyouLnkPath).attr("value");
if (dspId == "FPT0001"){
if (comKaime.kimIfNoSet()) {
comDialog.confirm('選択中の買い目情報は破棄されますが、よろしいでしょうか。', function(){
btnLiveVoteClick("1", encPrm);
}, function(){
});
} else {
btnLiveVoteClick("1", encPrm);
}
} else {
commonSubmit.formPost(url, { "encp" : encPrm }, "_self");
}
return false;
}
function pc0101_ok_normal(mode,id){
var fwurl;
var clrl;
if (mode ==1){
ctrlId= "[id=hcomHdnTouhyouLive"+id+"]";
fwurl =$(ctrlId).attr("value");
} else {
clrl = "[id=shHdnLink_"+id+"]"
fwurl =$(clrl).attr("value");
}
window.location.href = fwurl;
return false;
}
function pc0101_okLive(id){
var ctrlId = "[id=hcomHdnTouhyouLive"+id+"]";
var para =$(ctrlId).attr("value");
ctrlId = "[id=shParentDisp]";
var dspId = $(ctrlId).attr("value");
var url = $(shLiveLinkPath).attr("value");
if (dspId == "FPJ0315"){
btnLiveVoteClick("1", para);
} else {
commonSubmit.formPost(url, { "encp" : para }, "_self");
}
return false;
}
function shChgRaceListBtn(flg){
var pc0101_json0 = $("#sh_hidden1").attr("value");
var dispid = $("#shCurrentDisp").attr("value");
var shccp = $("#shCcp").attr("value");
if (flg==0){
$("#shTodayRace").addClass("active");
$("#shTomorrowRace").removeClass("active");
$("#sh_hidden2").attr("value","0");
PC0101Controller.chgRaceList("0",pc0101_json0, dispid, shccp);
} else {
$("#shTodayRace").removeClass("active");
$("#shTomorrowRace").addClass("active");
$("#sh_hidden2").attr("value","1");
PC0101Controller.chgRaceList("1", pc0101_json0, dispid, shccp);
}
}
var comheadDisp = 1;
var jpFlg = 0;
var beforeId ="";
var spos = 0;
var tmOutFlg = false;
var beforpos = 0;
function shLocalJump(jumpTag){
var serchTag;
var element;
var rect;
var posY;
var elementHeight = 0;
var newPos = 0;
var newHeadDisp=0;
var currentPos = 0;
if (jumpTag == "" || jumpTag == undefined){
var hash = location.hash; 
if (hash != "" || (hash != "#top" && hash.length > 1 ) ){
jumpTag = hash.substring(1,(hash.length));
}
}
serchTag= jumpTag;
element = document.getElementById(serchTag);
if (beforeId == jumpTag){
return false;
}
beforeId = jumpTag;
if (element == null) {
return false;
} else {
rect = element.getBoundingClientRect();
elementHeight =Math.floor(rect.height);
posY = Math.floor(rect.top + window.pageYOffset);
}
if (posY === spos ) {
return false;
} else {
jpFlg = 1;
var upflg= 0;
if (posY < spos) {
upflg = 0;
} else if (posY > spos) {
upflg = 1;
}
var breadEle;
var breRect;
breadEle = document.getElementById('breads');
breRect = breadEle.getBoundingClientRect();
var breaElementHeight =Math.floor(breRect.height);
if(posY > 70) {
$("#breads").hide();
$("#menu").removeClass("navbar-fixed-top");
if(upflg===1){
$("#topfix").removeClass("navbar-fixed-top");
$("#ticker_area").addClass("navbar-fixed-top");
$("#main").css("margin-top","7px");
newHeadDisp = 0;
}else{
$("#ticker_area").removeClass("navbar-fixed-top");
$("#menu").addClass("navbar-fixed-top");
$("#nav_menus").show().css("margin-top","-19px");
$("#main").css("margin-top","91px");
newHeadDisp = 2;
}
} else {
if (posY > 19 || posY ===0){
$("#breads").show();
$("#ticker_area").removeClass("navbar-fixed-top");
$("#menu").removeClass("navbar-fixed-top");
$("#topfix").removeClass("navbar-fixed-top");
$("#nav_menus").css("margin-top","0");
$("#main").css("margin-top","0");
newHeadDisp = 1;
}
}
var navmenuArea;
if (element == null) {
return false;
} else {
rect = element.getBoundingClientRect();
elementHeight =Math.floor(rect.height);
posY = Math.floor(rect.top + window.pageYOffset);
}
var tickerele;
tickerele = document.getElementById("ticker_area");
var tickrect = tickerele.getBoundingClientRect();
var tickerArea =Math.floor(tickrect.height);
currentPos = posY-tickerArea;
if (comheadDisp === 0){
if (newHeadDisp === 0){
} else if (newHeadDisp === 1){
currentPos = currentPos -($("#menu").height());
} else if (newHeadDisp === 2){
currentPos = currentPos - ($("#menu").height());
}
} else if (comheadDisp === 1){
if (newHeadDisp === 0){
} else if (newHeadDisp === 1){
currentPos = currentPos -($("#menu").height());
} else if (newHeadDisp === 2){
currentPos = currentPos - ($("#menu").height());
}
} else if (comheadDisp === 2) {
if (newHeadDisp === 0){
} else if (newHeadDisp === 1){
currentPos = currentPos - ($("#menu").height());
} else if (newHeadDisp === 2){
currentPos = currentPos - ($("#menu").height());
}
}
currentPos = currentPos;
window.scrollTo(0,currentPos);
comheadDisp = newHeadDisp;
spos = currentPos;
}
}
$(window).on("scroll", function() {
var m = 71;
var updownflg = 0;
var sflg;
var sbottom;
var stop = Math.floor($(this).scrollTop());
var scrollHeight = Math.floor($(document).height());
var scrollPosition =Math.floor( $(window).height() + $(window).scrollTop());
var scrollTop = Math.floor($(window).scrollTop());
var disoHight = Math.floor($(window).height());
if (jpFlg == 0){
if (scrollHeight == scrollPosition){
if(beforpos == scrollPosition){
return false;
}
}
var testpos = 0;
beforpos = scrollPosition;
if(stop>=spos || scrollPosition > scrollHeight){
sflg = true;
}else{
sflg = false;
}
if ((stop - spos) >= -1 &&  (stop - spos)<= 1){
testpos = 1;
}
spos = stop;
if ((scrollHeight - scrollPosition) / scrollHeight === 0) {
sbottom = true;
}else{
sbottom = false;
}
if (tmOutFlg == false){
tmOutFlg = true;
if(stop > 70) {
$("#breads").hide();
$("#menu").removeClass("navbar-fixed-top");
if(sflg || sbottom){
$("#topfix").removeClass("navbar-fixed-top");
$("#ticker_area").addClass("navbar-fixed-top");
$("#main").css("margin-top","7px");
if(testpos !=1){
updownflg = -1;
}
comheadDisp = 0;
}else{
$("#ticker_area").removeClass("navbar-fixed-top");
$("#menu").addClass("navbar-fixed-top");
$("#nav_menus").show().css("margin-top","-19px");
$("#main").css("margin-top","91px");
if(testpos !=1){
updownflg = 1;
}
comheadDisp = 2;
}
} else {
if (stop > 19 || stop ===0){
$("#breads").show();
$("#ticker_area").removeClass("navbar-fixed-top");
$("#menu").removeClass("navbar-fixed-top");
$("#topfix").removeClass("navbar-fixed-top");
$("#nav_menus").css("margin-top","0");
$("#main").css("margin-top","0");
comheadDisp = 1;
}
}
setTimeout(function(){
tmOutFlg = false;
stop = Math.floor($(this).scrollTop());
if ((stop < 32 && !sbottom)||(stop ===0)){
$("#breads").show();
$("#ticker_area").removeClass("navbar-fixed-top");
$("#menu").removeClass("navbar-fixed-top");
$("#topfix").removeClass("navbar-fixed-top");
$("#nav_menus").css("margin-top","0");
$("#main").css("margin-top","0");
comheadDisp = 1;
}
spos =stop+updownflg;
if (spos < 0){
spos = 0;
}
},100);
}
beforeId ="";
} else {
if (jpFlg === 2){
jpFlg = 1;
} else {
jpFlg = 0;
}
}
});
var basehash;
var initHashFlg = 0;
$(function(){
$(window).on("load", function() {
spos = 0;
comheadDisp = 1;
beforeId ="";
beforpos = 0;
var hash = basehash; 
var jumpTag; 
if (hash != undefined){
if ( hash != "" || (hash != "#top" && hash.length > 1 ) ){
jumpTag = hash.substring(1,(hash.length));
}
}
});
$(window).on("hashchange", function() {
var hash = basehash; 
var jumpTag; 
if (hash != undefined && initHashFlg===1){
if ( hash != "" || (hash != "#top" && hash.length > 1 ) ){
jumpTag = hash.substring(1,(hash.length));
shLocalJump(jumpTag);
initHashFlg=0;
}
}
});
});
function shJump(){
var hash = location.hash; 
var jumpTag; 
if (hash != "" || (hash != "#top" && hash.length > 1 ) ){
beforeId = "";
jumpTag = hash.substring(1,(hash.length));
shLocalJump(jumpTag);
}
}
$(document).ready( function() {
var hash = location.hash; 
if (hash != "" || (hash != "#top" && hash.length > 1 ) ){
basehash = location.hash; 
window.location.hash ="";
initHashFlg = 1;
}
});
