var hhView = {
HDNKEY_ID: 'JSJ001',
hhDrawJSONData: function(maindata, _reqParam) {
if ( !maindata ) {
Com.makePcUpdatePage("hhDivErrArea","",_reqParam,function(arg0){hhController.hhJSONretry(arg0);});
$('#hhDivSucArea').addClass('dispoff');
$('#hhDivErrArea').removeClass('dispoff');
} else if ( maindata.resultCd == -1 ) {
var reqPrm = [];
if( !_reqParam && maindata.reqprm.encp != null && ("encp" in maindata.reqprm) ) {
reqPrm["encp"] = maindata.reqprm.encp;
} else if( _reqParam && _reqParam.encp != null && ("encp" in _reqParam) ) {
reqPrm["encp"] = _reqParam.encp;
}
Com.makePcUpdatePage("hhDivErrArea",maindata.message,reqPrm,function(arg0){hhController.hhJSONretry(arg0);});
$('#hhDivSucArea').addClass('dispoff');
$('#hhDivErrArea').removeClass('dispoff');
} else {
$('#hhDivErrArea').addClass('dispoff');
$('#hhDivSucArea').removeClass('dispoff');
$('#hhDivKaisaiHeadMessage').empty();
$('#hhLblMessage').empty();
$('#hhDivMessage').attr('data-flg-sc',Number(maindata.C0201data.flgSectionCancel));
if( maindata.C0201data.flgRaceCancel ) {
$('#hhDivKaisaiHeadMessage')
.append($('<table />').addClass('al-m al-c underr-inner')
.append($('<tbody />').append($('<tr />').append($('<td />')
.append(maindata.C0201data.hhMessage)))));
$('#hhDivPlayersList').addClass('dispoff');
$('#hhDivRaceDtl').addClass('dispoff');
$('#hhTdRaceDtl').addClass('dispoff');
$('#hhDivKaisaiHeadMessage').removeClass('dispoff');
} else {
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivPlayersList').removeClass('dispoff');
$('#hhDivRaceDtl').removeClass('dispoff');
$('#hhTdRaceDtl').removeClass('dispoff');
if( maindata.C0201data.hhMessage ) {
$('#hhLblMessage').append(maindata.C0201data.hhMessage);
$('#hhDivMessage').removeClass('dispoff');
$('#hhDivVote').addClass('dispoff');
} else {
$('#hhDivMessage').addClass('dispoff');
$('#hhDivVote').removeClass('dispoff');
}
}
hhView.makeTitleArea(maindata);
if( maindata.C0201data.flgActvKekkaList ) {
$('#hhbtnResultList').removeClass('disabled').prop('disabled',false);
} else {
$('#hhbtnResultList').addClass('disabled').prop('disabled',true);
}
if( maindata.C0201data.flgActvSyutujyo ) {
$('#hhbtnsyutujyouYoteiSensyu').removeClass('disabled').prop('disabled',false);
} else {
$('#hhbtnsyutujyouYoteiSensyu').addClass('disabled').prop('disabled',true);
}
hhView.makeTickerArea(maindata);
$('#hhMain').removeClass(maindata.C0201data.cidPrevBetBgcolor);
$('#hhMain').attr('data-hhZbg',maindata.C0201data.cidPrevBetBgcolor);
if( maindata.C0201data.flgPrevBet == true ) {
$($(".basewindows")[0]).addClass(maindata.C0201data.cidPrevBetBgcolor);
} else {
$($(".basewindows")[0]).removeClass(maindata.C0201data.cidPrevBetBgcolor);
}
}
return;
},
makeTitleArea: function(maindata) {
var addflg = false;
$('#hhLblJo').empty();
$('#hhLblJo').append(maindata.C0201data.joName);
$('#hhDivIconField').empty();
$('#hhDivIconField').append('&nbsp;').append($('<img />').attr('width','10').attr('height','16').attr('src',jshhSpacer).attr('alt','')).append('&nbsp;');
$('#hhDivIconField').append($('<img />').addClass('gradeIconSize').attr('src',maindata.C0201data.imgGradeSrc).attr('alt',maindata.C0201data.imgGradeAlt));
$('#hhDivIconField').append('&nbsp;').append($('<img />').attr('width','5').attr('height','16').attr('src',jshhSpacer).attr('alt','')).append('&nbsp;');
if( maindata.C0201data.imgKkbnSrc ) {
if( maindata.C0201data.imgKkbnAlt ) {
$('#hhDivIconField').append($('<img />').addClass('HoldingIconSize').attr('src',maindata.C0201data.imgKkbnSrc).attr('alt',maindata.C0201data.imgKkbnAlt)).append('&nbsp;');
addflg = true;
}
}
if( maindata.C0201data.imgFuka1Src ) {
$('#hhDivIconField').append($('<img />').addClass('inforIconSize').attr('src',maindata.C0201data.imgFuka1Src).attr('alt',maindata.C0201data.imgFuka1Alt)).append('&nbsp;');
addflg = true;
}
if( maindata.C0201data.imgFuka2Src ) {
$('#hhDivIconField').append($('<img />').addClass('inforIconSize').attr('src',maindata.C0201data.imgFuka2Src).attr('alt',maindata.C0201data.imgFuka2Alt)).append('&nbsp;');
addflg = true;
}
if( addflg ) {
$('#hhDivIconField').append($('<img />').attr('width','5').attr('height','16').attr('src',jshhSpacer).attr('alt','')).append('&nbsp;');
}
$('#hhLblRaceName').empty();
$('#hhLblRaceName').append(maindata.C0201data.raceName);
hhView.makeWinner(maindata);
if( $('#hhDivTitleArea').outerWidth(true) < $('#hhDivTitle').outerWidth(true) + $('#hhDivWinner').outerWidth(true) ) {
$('#hhDivTitleArea').addClass('hhracetitle_thick');
} else {
$('#hhDivTitleArea').removeClass('hhracetitle_thick');
}
$('#hhJoinfo').empty();
if( maindata.C0201data.joInfo ) {
var strInfoHtml =[];
var brSetText = $("<span>");
brSetText.append(maindata.C0201data.joInfo);
strInfoHtml.push(brSetText[0].innerText);
$('#hhJoinfo').addClass('race_place hhjoinfo').html(strInfoHtml.join(""));
}
var mode = 0;
if( maindata.C0201data.C0201kaisai.length > 6 ) {
mode = 1;
}
hhView.makeTabButton(mode,maindata);
hhView.makeRace(mode,maindata);
hhView.makeRaceDtl(maindata);
$('#hhDivGuideIcon').empty();
if( maindata.C0201data.flgLogin ) {
$('#hhDivGuideIcon')
.append($('<table />').addClass('ichitbl')
.append($('<tbody />')
.append($('<tr />')
.append($('<td />').addClass('ichitd')
.append($('<img />').addClass('ichi1').attr('alt',maindata.C0201data.imgPushAlt).attr('src',maindata.C0201data.imgPushSrc)))
.append($('<td />').addClass('al-l').append(maindata.C0201data.imgPushAlt)))
.append($('<tr />')
.append($('<td />').addClass('ichitd')
.append($('<img />').addClass('ichi2').attr('alt',maindata.C0201data.imgCongenialAlt).attr('src',maindata.C0201data.imgCongenialSrc)))
.append($('<td />').addClass('al-l').append(maindata.C0201data.imgCongenialAlt)))
 ));
$('#hhDivGuideIcon').removeClass('disphidden');
} else {
$('#hhDivGuideIcon').addClass('disphidden');
}
if( location.pathname == $('#hhhdnPostUrl3').val() ) {
$('#hhDivVote').addClass('disphidden');
} else {
$('#hhDivVote').removeClass('disphidden');
}
return;
},
makeRace: function(mode, maindata) {
$('#hhDivRaceNum').empty();
if( !maindata.C0201data.C0201race ) {
$('#hhDivRaceUnder').addClass('dispoff');
} else {
$('#hhDivRaceNum').append($('<img />').attr('width','25').attr('height','16').attr('src',jshhSpacer)).append(' ');
for( var ilop = 0; ilop < maindata.C0201data.C0201race.length; ilop++ ) {
var rno = (ilop+1)+"R",
$racebtn = $('<button />');
$racebtn.attr('type','button').attr('name','hhRaceBtn').attr('id','hhRaceBtn'+(ilop+1))
.attr('data-encp',maindata.C0201data.C0201race[ilop].encParaR)
.addClass('btn btn_fsz onbtn race_btn hhracebtn').append(rno);
if(maindata.C0201data.C0201race[ilop].flgRaceEnd) {
$racebtn.addClass('fin')
}
if(maindata.C0201data.C0201race[ilop].flgActvRaceBtn) {
$racebtn.removeClass('disabled').prop('disabled',false);
} else {
$racebtn.addClass('disabled').prop('disabled',true);
}
if(maindata.C0201data.selRaceNo==ilop+1) {
$racebtn.addClass('active')
}
$('#hhDivRaceNum').append($racebtn).append(' ');
}
var $racebtn = $('<button />');
$racebtn.attr('type','button').attr('id','hhbtnRaceAll').addClass('btn btn_fsz onbtn race_btn hhracebtn').append('全R');
if( maindata.C0201data.flgActvKekkaList ) {
$('#hhbtnResultList').removeClass('disabled').prop('disabled',false);
} else {
$('#hhbtnResultList').addClass('disabled').prop('disabled',true);
}
$('#hhDivRaceNum').append($racebtn);
$('#hhDivRaceUnder').removeClass('dispoff');
}
return;
},
makeRaceDtl: function(maindata) {
var $imgIchi = $('<img />').addClass('ichi1').attr('src',maindata.C0201data.imgPushSrc).attr('alt',maindata.C0201data.imgPushAlt),
$imgKoai = $('<img />').addClass('ichi2').attr('src',maindata.C0201data.imgCongenialSrc).attr('lt',maindata.C0201data.imgCongenialAlt);
$('#players').empty();
if( !maindata.C0201data.C0201racedtl ) {
} else {
if( maindata.C0201data.C0201racedtl.flgViewPut ) {
$('#hhbtnVote').removeClass('disabled').prop('disabled',false);
} else {
$('#hhbtnVote').addClass('disabled').prop('disabled',true);
}
if( !maindata.C0201data.C0201racedtl.C0201sensyu ) {
} else {
for( var ilop = 0; ilop < maindata.C0201data.C0201racedtl.C0201sensyu.length; ilop++ ) {
var $divIchi_org = $('<div />').addClass('rtv'),
$divKoai_org = $('<div />').addClass('rtv');
if(!maindata.C0201data.C0201racedtl.C0201sensyu[ilop].flgPush) {
$divIchi_org.addClass('dispoff');
} else {
$divIchi_org.removeClass('dispoff');
}
$divIchi_org.append($imgIchi);
if(!maindata.C0201data.C0201racedtl.C0201sensyu[ilop].flgCongenial) {
$divKoai_org.addClass('dispoff');
} else {
$divKoai_org.removeClass('dispoff');
}
$divKoai_org.append($imgKoai);
var divIchi = $divIchi_org.clone(),
divKoai = $divKoai_org.clone();
var $imgPly = $('<img />').addClass('face');
if( maindata.C0201data.C0201racedtl.C0201sensyu[ilop].imgPlayerPictSrc != undefined
 && maindata.C0201data.C0201racedtl.C0201sensyu[ilop].imgPlayerPictSrc.length > 0 ) {
$imgPly
.attr('src',maindata.C0201data.C0201racedtl.C0201sensyu[ilop].imgPlayerPictSrc)
.attr('alt',maindata.C0201data.C0201racedtl.C0201sensyu[ilop].imgPlayerPictAlt);
} else {
$imgPly.addClass('deffw')
}
$('#players')
.append($('<li />')
.append($('<div />').addClass('mxw').append($('<a />')
.attr('href','javascript:void(0);')
.attr('data-hhlnk-snum',maindata.C0201data.C0201racedtl.C0201sensyu[ilop].numPlayer)
.append($imgPly)
)).append(' ')
.append(divIchi).append(divKoai).append(' ')
.append($('<div />').addClass('w110pt')
.append($('<div />')
.addClass('lnum')
.addClass(maindata.C0201data.C0201racedtl.C0201sensyu[ilop].cidCarNum).append(maindata.C0201data.C0201racedtl.C0201sensyu[ilop].carNum)).append(' ')
.append($('<div />').addClass('dispib').append(maindata.C0201data.C0201racedtl.C0201sensyu[ilop].namePlayerSei)).append(' ')
).append(' ')
).append(' ');
}
for( ilop = maindata.C0201data.C0201racedtl.C0201sensyu.length; ilop < 9; ilop++ ) {
$('#players')
.append($('<li />')
).append(' ');
}
}
var txtDtl = maindata.C0201data.selRaceNo+"R "+maindata.C0201data.C0201racedtl.syumoku+"　"+maindata.C0201data.C0201racedtl.kyori+"m（"+maindata.C0201data.C0201racedtl.syukai+"周）"+maindata.C0201data.C0201racedtl.nameKyosou;
$('#hhLblRaceDtl').empty();
$('#hhLblShimeTime').empty();
$('#hhLblShimeHenTime').empty();
$('#hhLblHassoTime').empty();
$('#hhLblHassoHenTime').empty();
$('#hhLblRaceDtl').append(txtDtl);
$('#hhLblShimeTime').append(maindata.C0201data.C0201racedtl.bfrBetTime);
if(maindata.C0201data.C0201racedtl.aftBetTime == maindata.C0201data.C0201racedtl.bfrBetTime) {
$('#hhLblShimeTime').removeClass('lineth');
$('#hhLblShimeArrow').addClass('dispoff');
$('#hhLblShimeHenTime').addClass('dispoff');
} else {
$('#hhLblShimeTime').addClass('lineth');
$('#hhLblShimeArrow').removeClass('dispoff');
$('#hhLblShimeHenTime').removeClass('dispoff');
$('#hhLblShimeHenTime').append(maindata.C0201data.C0201racedtl.aftBetTime);
}
$('#hhLblHassoTime').append(maindata.C0201data.C0201racedtl.bfrStartTime);
if(maindata.C0201data.C0201racedtl.aftStartTime == maindata.C0201data.C0201racedtl.bfrStartTime) {
$('#hhLblHassoTime').removeClass('lineth');
$('#hhLblHassoArrow').addClass('dispoff');
$('#hhLblHassoHenTime').addClass('dispoff');
} else {
$('#hhLblHassoTime').addClass('lineth');
$('#hhLblHassoArrow').removeClass('dispoff');
$('#hhLblHassoHenTime').removeClass('dispoff');
$('#hhLblHassoHenTime').append(maindata.C0201data.C0201racedtl.aftStartTime);
}
}
return;
},
makeTabButton: function(mode, maindata) {
var $outer = $('<div id="hhDivTabButton" />'),
$tabUl = $('<ul />'),
$tabDiv = $('<div />'),
$btnDiv = hhView.makeUpperButton(mode),
$hdnprm = $('<div />');
$tabUl.addClass('nav nav-tabs').append($('<li />').append($('<img />').attr('width','25').attr('height','16').attr('src',jshhSpacer)));
for( var ilop = 0; ilop < maindata.C0201data.C0201kaisai.length; ilop++ ) {
var $liTag = $('<li />'),
$aTag = $('<a />').addClass('hh-nav'),
$spnTg = $('<span />');
$liTag.attr('role','race_data').attr('id','hhliRaceDate'+ilop);
if( maindata.C0201data.C0201kaisai[ilop].encParaK == maindata.C0201data.encSelParaK ) {
$liTag.addClass('active');
} else {
$spnTg.addClass('txt_underline');
}
if( maindata.C0201data.C0201kaisai[ilop].flgSelect == true ) {
$liTag.removeClass('disabled').prop('disabled',false);
} else {
$liTag.addClass('disabled').prop('disabled',true);
}
if( mode == 1 ) {
$aTag.addClass('nav-7over');
$spnTg.addClass('nav-7over');
}
var idName = 'hhlnkRaceDate'+ilop;
$liTag.append($aTag.attr('id',idName).attr('data-ktab-idx',ilop).attr('name','hhlnkRaceDate').attr('href','javascript:void(0);')
.attr('data-encp',maindata.C0201data.C0201kaisai[ilop].encParaK)
.append($spnTg.attr('id','hhspnRaceDate'+ilop).append(maindata.C0201data.C0201kaisai[ilop].txtEventDate+maindata.C0201data.C0201kaisai[ilop].txtDaily)));
$liTag.append(' ');
$tabUl.append($liTag);
var prmid = "hhKtabPrm" + ilop;
$hdnprm.append($('<input />').attr('type','hidden').attr('id',prmid).attr('name','hhKtabPrm').attr('value',maindata.C0201data.C0201kaisai[ilop].encParaK));
}
$hdnprm.append($('<input />').attr('type','hidden').attr('id','hhEncSelK').attr('name','hhEncSelK').attr('value',maindata.C0201data.encSelParaK));
$hdnprm.append($('<input />').attr('type','hidden').attr('id','hhEncSelR').attr('name','hhEncSelR').attr('value',maindata.C0201data.encSelParaR));
$hdnprm.append($('<input />').attr('type','hidden').attr('id','hhEncPrmS').attr('name','hhEncPrmS').attr('value',maindata.C0201data.encParaS));
$hdnprm.append($('<input />').attr('type','hidden').attr('id','hhSelK').attr('name','hhSelK').attr('value',maindata.C0201data.selKaisai));
$hdnprm.append($('<input />').attr('type','hidden').attr('id','hhSelJ').attr('name','hhSelJ').attr('value',maindata.C0201data.selKjyoCd));
if( mode == 0 ) {
$tabUl.addClass('nav-6less');
$outer.append($tabDiv.append($tabUl)).append($btnDiv);
}
else {
$tabUl.addClass('nav-7over');
$outer.append($btnDiv).append($tabDiv.addClass('race_days clear-fix').append($tabUl));
}
$outer.append($hdnprm);
$('#hhDivKaisaibi').empty();
$('#hhDivKaisaibi').append($outer);
return;
},
makeUpperButton: function(mode) {
var $outer = $('<div />');
var modeClassName = "upbtn-6less";
if( mode == 1 ) {
modeClassName = "upbtn-7over";
}
$outer.addClass('fl-r').addClass(modeClassName);
$outer.append($('<button />').attr('type','button').attr('id','hhbtnRaceProgram').addClass('btn btn_fsz onbtn btn_sz_hh').text('レースプログラム')).append(' ');
$outer.append($('<button />').attr('type','button').attr('id','hhbtnsyutujyouYoteiSensyu').addClass('btn btn_fsz onbtn btn_sz_hh').text('出場予定選手')).append(' ');
$outer.append($('<button />').attr('type','button').attr('id','hhbtnKaisaiHatubaiGuidance').addClass('btn btn_fsz onbtn btn_sz_hh').text('発売案内'));
return $outer;
},
makeWinner: function(maindata) {
$('#hhDivWinner').empty();
if( maindata.C0201data.C0201interview.length > 0 ) {
var $outer = $('<table />').addClass('w100pc').append('<tbody />');
var $tabTr = $('<tr />');
for(var ilop=0; ilop<maindata.C0201data.C0201interview.length; ilop++) {
$tabTr.append($('<td />').addClass('al-l hh_interview')
.append($('<a />').addClass('txt_underline').attr('href','javascript:void(0);')
.attr('data-hhintv-tuban',maindata.C0201data.C0201interview[ilop].serialNumber)
.attr('data-hhintv-niti',maindata.C0201data.C0201interview[ilop].daily)
.attr('data-hhintv-enum',maindata.C0201data.C0201interview[ilop].dailyBrunch)
.attr('data-hhintv-kday',maindata.C0201data.C0201interview[ilop].kDate)
.attr('data-hhintv-bkcd',maindata.C0201data.C0201interview[ilop].kJoCd)
.append($('<img />').attr('height','16').attr('alt',maindata.C0201data.imgInterviewAlt).attr('src',maindata.C0201data.imgInterviewSrc).addClass('hh_interview'))
.append(maindata.C0201data.C0201interview[ilop].interviewTitle)));
}
$outer.append($tabTr);
$('#hhDivWinner').append($outer);
}
return;
},
makeTickerArea: function(maindata) {
$('#hhTicker').empty();
$('#hhTickerF').empty();
$('#hhTicker').append($('<div />').attr('id','hhTicker_inner'));
$('#hhTickerF').append($('<div />').attr('id','hhTickerF_inner'));
$('#hhDivRaceDtlFrame').removeClass('race_detail_height');
$('#hhTrTickerF').addClass('dispoff');
$('#hhTrTickerH').removeClass('dispoff');
if( maindata.C0201data.C0201ticker.length > 0 ) {
var widthTckH = $('#hhDivRaceDtlFrame').width() - $('#hhTdRaceDtl').width();
var widthTckF = $('#hhDivRaceDtlFrame').width();
var vPtn = maindata.C0201data.C0201ticker[0].vPattern;
$('#hhTickerF_inner').attr('data-v-ptn',vPtn);
$('#hhTickerF_inner').attr('data-innner-width',widthTckF);
if( vPtn == 0 ) {
$('#hhDivRaceDtlFrame').addClass('race_detail_height');
$('#hhTicker_inner').append($('<div />').attr('id','hhTickerHsep').width(widthTckH).addClass('dispib').append($('<span />').addClass('hhTicker').append('&nbsp;')));
$('#hhTickerF_inner').append($('<div />').attr('id','hhTickerFsep').width(widthTckF).addClass('dispib').append($('<span />').addClass('hhTicker').append('&nbsp;')));
}
for( var ilop=0; ilop<maindata.C0201data.C0201ticker.length; ilop++ ) {
$('#hhTicker_inner')
.append($('<span />').addClass('hhTicker '+maindata.C0201data.C0201ticker[ilop].cidFontColor)
.append(maindata.C0201data.C0201ticker[ilop].tickText)).append('&nbsp;');
$('#hhTickerF_inner')
.append($('<span />').addClass('hhTicker '+maindata.C0201data.C0201ticker[ilop].cidFontColor)
.append(maindata.C0201data.C0201ticker[ilop].tickText)).append('&nbsp;');
}
tickerdisp(vPtn,'hhTicker',widthTckH);
$('#hhTickerHsep').width(widthTckH);
$('#hhTickerFsep').width(widthTckF);
} else {
$('#hhDivRaceDtlFrame').addClass('race_detail_height');
}
return;
}
};
