var PC0101View = {
HDNKEY_ID: 'ppc0101',
shDrawJSONData: function(jsondata,param) {
var outHtml=[];
var outHtml2=[];
var outHtml_tc=[];
var outHtml_bl=[];
var stroutHtml;
var stroutTcHtml = "";
var stroutBlHtml = "";
var $result = $('#hcomRaceDiv'), n=3000;
var $noRaceresult = $('#hcomnoRaceMsg'), n=3000;
var $tc_result = $('#hcomTcDiv'), n=3000;
var $bl_result = $('#hcomBlDiv'), n=3000;
var current;
var outHtml_gSearch=[];
var $gSearchArea = $('#shGSearch'), n=3000;
if( !jsondata ) {
} else if( jsondata.resultCd != 0 ) {
} else {
var msg =jsondata.noRaceMessage;
if(jsondata.tickerFlg){
$('#ticker_area').removeClass('dispoff').addClass('dispon');
PC0101View.makeTickerArea(jsondata);
} else {
$('#ticker_area').removeClass('dispon').addClass('dispoff');
}
if(!jsondata.kanyusyaFlgJSON){
$bl_result.empty();
var breadName;
var psFlg;
var breadlbl;
outHtml_bl.push('<div id="bread_area_id" jname="パンくずリスト" name="lnkBreadcrumb" class="list-inline">');
for (var b_loop = 0; b_loop < jsondata.breadCrumbData.length ;b_loop++){
if(b_loop != 0){
outHtml_bl.push('<span>'+ " > " +'');
}
psFlg = jsondata.breadCrumbData[b_loop].postgetFlg;
breadlbl = jsondata.breadCrumbData[b_loop].breadCrumbName;
if( psFlg == 2) {
outHtml_bl.push('<span>'+breadlbl+'');
} else {
outHtml_bl.push('<a class="pankuzu_link" onclick="shClickBreadCrumb('+b_loop+')" style="cursor:pointer" >'+breadlbl+'</a>');
outHtml_bl.push('<h:inputHidden id="shBreadCrumbLnkPath_'+b_loop+'" value="'+jsondata.breadCrumbData[b_loop].breadCrumbPath+'"></h:inputHidden>');
outHtml_bl.push('<h:inputHidden id="shBreadCrumb_PGFlg_'+b_loop+'" value="'+psFlg+'"></h:inputHidden>');
outHtml_bl.push('<h:inputHidden id="shBreadCrumbDspId_'+b_loop+'" value="'+jsondata.breadCrumbData[b_loop].breadCrumbDspID+'"></h:inputHidden>');
}
}
outHtml_bl.push('</div>');
$bl_result[0].innerHTML = outHtml_bl.join("");
$gSearchArea.empty();
if (window.location.protocol == "https:"){
outHtml_gSearch.push('<form method="get" action="https://www.google.co.jp/search" id="siteSearch" name="find">');
outHtml_gSearch.push('<input type="hidden" name="ie" value="UTF-8" />');
outHtml_gSearch.push('<input type="hidden" name="oe" value="UTF-8" />');
outHtml_gSearch.push('<input type="hidden" name="hl" value="ja" />');
outHtml_gSearch.push('<input type="hidden" name="domains" value="https://keirin.jp/" />');
outHtml_gSearch.push('<input type="hidden" name="sitesearch" value="https://keirin.jp/" checked="checked" />');
outHtml_gSearch.push('<button class="fl-r google_search_btn" onclick="document.find.submit();return false;"></button>');
outHtml_gSearch.push('<input type="text" name="q" maxlength="255" value="" class="fl-r google_search" style="width: 148px; font-size: 12px;" placeholder="Google™ カスタム検索" />');
outHtml_gSearch.push('</form>');
} else {
outHtml_gSearch.push('<form method="get" action="http://www.google.co.jp/search" id="siteSearch" name="find">');
outHtml_gSearch.push('<input type="hidden" name="ie" value="UTF-8" />');
outHtml_gSearch.push('<input type="hidden" name="oe" value="UTF-8" />');
outHtml_gSearch.push('<input type="hidden" name="hl" value="ja" />');
outHtml_gSearch.push('<input type="hidden" name="domains" value="http://keirin.jp/" />');
outHtml_gSearch.push('<input type="hidden" name="sitesearch" value="http://keirin.jp/" checked="checked" />');
outHtml_gSearch.push('<button class="fl-r google_search_btn" onclick="document.find.submit();return false;"></button>');
outHtml_gSearch.push('<input type="text" name="q" maxlength="255" value="" class="fl-r google_search" style="width: 148px; font-size: 12px;" placeholder="Google™ カスタム検索" />');
outHtml_gSearch.push('</form>');
}
$gSearchArea[0].innerHTML = outHtml_gSearch.join("");
outHtml.push('<ul class="list-inline">');
outHtml.push('<h:inputHidden id="sh_hidden2" value="'+jsondata.kaisaiDateKbn+'"></h:inputHidden>');
outHtml.push('<h:inputHidden id="shTouhyouLnkPath" value="'+jsondata.touhyouLnkPath+'"></h:inputHidden>');
outHtml.push('<h:inputHidden id="shLiveLinkPath" value="'+jsondata.liveLinkPath+'"></h:inputHidden>');
outHtml.push('<h:inputHidden id="shParentDisp" value="'+jsondata.parentDspId+'"></h:inputHidden>');
outHtml.push('<h:inputHidden id="shCurrentDisp" value="'+jsondata.currentDspId+'"></h:inputHidden>');
outHtml.push('<h:inputHidden id="shCcp" value="'+jsondata.forceProtcolParam+'"></h:inputHidden>');
for(var ilop = 0; ilop < jsondata.RaceList.length; ilop++ ){
stroutHtml='<li class="kyotuHeader '+jsondata.RaceList[ilop].gradeBackColor+'">';
stroutHtml +='<div class="fl-l"><p class="place">'+jsondata.RaceList[ilop].keirinjoName+'</p>';
if (jsondata.RaceList[ilop].tyusiKbn == 1) {
stroutHtml += '<p id="lblTyusi" class="place color_red">中止</p>';
} else {
if (jsondata.RaceList[ilop].denColorFlg != 1) {
stroutHtml += '<p id="denRaceInfo" class="place" style="width: 145px;">' + jsondata.RaceList[ilop].raceNum
+ ' <span style="font-size: 12px;">' + jsondata.RaceList[ilop].denTitle + '</span> '
+ jsondata.RaceList[ilop].denTime + '</p>';
} else {
stroutHtml += '<p id="denRaceInfo" class="place color_red" style="width: 145px;">' + jsondata.RaceList[ilop].raceNum
+ ' <span style="font-size: 12px;">' + jsondata.RaceList[ilop].denTitle + '</span> '
+ jsondata.RaceList[ilop].denTime + '</p>';
}
}
stroutHtml += '<img alt="'+jsondata.RaceList[ilop].gradeIconName+'" class="gradeIconSize" src="'+jsondata.RaceList[ilop].gradeIconPath+'"/>';
stroutHtml += '<img alt="'+jsondata.RaceList[ilop].nichijiIconName+'"  src="'+jsondata.RaceList[ilop].nichijiIconPath+'"/>';
stroutHtml += '<img alt="'+jsondata.RaceList[ilop].kubunIconName+'"  class="HoldingIconSize" src="'+jsondata.RaceList[ilop].KubunIconPath+'"/>';
stroutHtml += '</div>';
stroutHtml += '<div class="fl-r" style="margin-bottom: 1px;">';
stroutHtml += '<input type="hidden" id=hcomHdnTouhyouLive'+ilop+' value="'+jsondata.RaceList[ilop].touhyouLivePara+'" >';
if(jsondata.RaceList[ilop].liveFlg == 1){
stroutHtml += '<button  id=hcombtnLive'+ilop+'  class="btn onbtn btn_fsz top" style="width: 80px; height: 35px;" onclick="pc0101_checkKaimeLive(\''+ilop+'\')" >LIVE</button></div>';
} else {
stroutHtml += '<button  id=hcombtnLive'+ilop+'  class="btn onbtn btn_fsz top" style="width: 80px; height: 35px;" disabled >LIVE</button></div>';
}
stroutHtml += '<div class="fl-r" style="margin-top: 1px;">';
stroutHtml += '<input type="hidden" id=hcomHdnTouhyouLive'+ilop+' value="'+jsondata.RaceList[ilop].touhyouLivePara+'" >';
if(jsondata.RaceList[ilop].touhyouFlg == 1){
if (jsondata.RaceList[ilop].loginState){
stroutHtml += '<button  id=hcombtnTouhyou'+ilop+'  class="btn onbtn btn_fsz top orange" style="width: 80px; height: 35px;" onclick="pc0101_checkKaimeTouhyou(\'1\',\''+ilop+'\')" >投票</button>';
} else {
stroutHtml += '<button  id=hcombtnTouhyou'+ilop+'  class="btn onbtn btn_fsz top orange" style="width: 80px; height: 35px;" onclick="pc0101_checkKaimeTouhyou(\'0\',\''+ilop+'\')">投票</button>';
}
} else {
stroutHtml += '<button  id=hcombtnTouhyou'+ilop+'  class="btn onbtn btn_fsz top orange" style="width: 80px; height: 35px;" disabled  >投票</button>';
}
stroutHtml += '</div>';
stroutHtml += '</li>';
outHtml.push(stroutHtml);
}
outHtml.push('</ul>');
if (jsondata.kaisaiDateKbn == 1){
$("#shTodayRace").removeClass("active");
$("#shTomorrowRace").addClass("active");
} else {
$("#shTodayRace").addClass("active");
$("#shTomorrowRace").removeClass("active");
}
if(jsondata.RaceList.length == 0){
outHtml2.push('<p class="place">'+jsondata.noRaceMessage+'</p>');
$noRaceresult[0].innerHTML = outHtml2.join("");
 $('#hcomRaceDiv').removeClass('dispon');
 $('#hcomRaceDiv').addClass('dispoff');
 $('#hcomnoRaceMsg').removeClass('dispoff');
 $('#hcomnoRaceMsg').addClass('dispon');
 $('#hcomBtngroup').addClass('fl-l');
} else {
 $('#hcomRaceDiv').removeClass('dispoff');
 $('#hcomRaceDiv').addClass('dispon');
 $('#hcomnoRaceMsg').removeClass('dispon');
 $('#hcomnoRaceMsg').addClass('dispoff');
 $('#hcomBtngroup').removeClass('fl-l');
}
 $('#sh_err_div').removeClass('dispon');
 $('#sh_err_div').addClass('dispoff');
 $('#sh_suc_div').removeClass('dispoff');
 $('#sh_suc_div').addClass('dispon');
$result[0].innerHTML = outHtml.join(" ");
}
}
commonLoad.loadingImage("false");
return;
},
makeTickerArea: function(maindata) {
$('#ticker').empty();
$('#ticker').append($('<div />').attr('id','ticker_inner'));
if( maindata.tickerData.length > 0 ) {
var widthTckH =  $('#ticker_area').width();
var vPtn = maindata.tickerFlashFlg;
$('#ticker_inner').attr('data-v-ptn',vPtn);
if( vPtn == 0 ) {
$('#ticker_area').css('height','32px');
$('#ticker_inner').append($('<div />').attr('id','shTickerHsep').width(widthTckH).addClass('dispib').append($('<span />').addClass('ticker').css('height','32px').append('&nbsp;')));
    } else {
    $('#ticker_area').css('height','auto');    
    }
for( var ilop=0; ilop<maindata.tickerData.length; ilop++ ) {
$('#ticker_inner')
.append($('<span />').addClass('ticker '+maindata.tickerData[ilop].tickerColorData)
.append(maindata.tickerData[ilop].tickerTextData));
}
tickerdisp(vPtn,'ticker',widthTckH);
$('#shTickerHsep').width(widthTckH);
}
return;
}
};
