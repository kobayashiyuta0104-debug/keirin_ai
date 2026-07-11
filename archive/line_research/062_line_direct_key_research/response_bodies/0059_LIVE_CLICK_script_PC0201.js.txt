function hhChkOddsBtn() {
return $('#hhflgOddsBtn').val();
}
function hhChkResultBtn() {
return $('#hhflgResultBtn').val();
}
function hhChkDigestBtn() {
return $('#hhflgDigestBtn').val();
}
function hhGetEncSelK() {
var ret = $('#hhEncSelK').val();
return ret;
};
function hhGetEncSelR() {
var ret = $('#hhEncSelR').val();
return ret;
};
function hhGetEncSelRList(raceNo) {
if( raceNo < 1 ) {
return null;
}
return $('#hhRaceBtn'+raceNo).data('encp');
};
function hhGetEncSelKList(idx) {
if( idx < 0
 || idx > $('a[name=hhlnkRaceDate]').length ) {
return null;
}
return $('#hhlnkRaceDate'+idx).data('encp');
};
function hhGetEncFstK() {
var ret = $('#hhEncPrmS').val();
return ret;
};
function hhGetSelK() {
var ret = $('#hhSelK').val();
return ret;
};
function hhGetSelJ() {
var ret = $('#hhSelJ').val();
return ret;
};
function hhCheckPost(fid) {
var prm = hhGetEncSelK(),
urln = location.pathname,
url1 = $('#hhhdnPostUrl1').val(),
url2 = $('#hhhdnPostUrl2').val(),
params = {};
switch (fid) {
case 'PJ0301':
case 'PJ0302':
case 'PJ0304':
prm = hhGetEncFstK();
case 'PJ0305':
case 'PJ0306':
case 'PJ0307':
break;
default:
return;
}
if( (urln == url1 && fid == "PJ0307")
 || (urln == url2 && fid != "PJ0307") ) {
params["encp"] = prm;
params["disp"] = fid;
if( fid == "PJ0307" ) {
btnClickOfFrame(fid);
} else {
update(fid,params);
}
} else {
if( urln == url1 ) {
urln = url2;
} else {
switch(fid) {
case 'PJ0301':
case 'PJ0302':
case 'PJ0304':
case 'PJ0305':
case 'PJ0306':
urln = url2;
break;
default:
urln = url1;
break;
}
}
if (comKaime.kimIfExist() == true || comKaime.kimGetNoSetKaimeGroup() != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
hhPostRace(fid,prm,urln);
return;
}, function(){
return;
});
} else {
hhPostRace(fid,prm,urln);
return;
}
}
};
function hhPostRace(fid,prm,urln) {
var params = {};
params["disp"] = fid;
params["encp"] = prm;
commonSubmit.formPost(urln,params,"_self");
};
function hhChgActiveBtn(kbn) {
switch(kbn) {
case 1:
case 2:
case 3:
hhChgPattern(1);
$('li[id^=hhliRaceDate]').removeClass('active');
$('span[id^=hhspnRaceDate]').addClass('txt_underline');
if( $('body').children('div').hasClass($('#hhMain').attr('data-hhZbg')) ) {
$($(".basewindows")[0]).removeClass($('#hhMain').attr('data-hhZbg'));
}
break;
case 4:
case 5:
case 6:
hhChgPattern(2);
$('[id^=hhRaceBtn]').removeClass('active');
$('#hhDivPlayersList').addClass('dispoff');
break;
}
$('#hhTrTickerH').addClass('dispoff');
$('#hhTrTickerF').removeClass('dispoff');
tickerdisp(
Number($('#hhTickerF_inner').attr('data-v-ptn'))
,'hhTickerF'
,Number($('#hhTickerF_inner').attr('data-innner-width')));
$('#hhbtnRaceProgram').removeClass('active');
$('#hhbtnsyutujyouYoteiSensyu').removeClass('active');
$('#hhbtnKaisaiHatubaiGuidance').removeClass('active');
$('#hhbtnSyusouList').removeClass('active');
$('#hhbtnResultList').removeClass('active');
$('#hhbtnRaceAll').removeClass('active');
switch(kbn) {
case 1: 
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivMessage').addClass('dispoff');
$('#hhbtnRaceProgram').addClass('active');
break;
case 2: 
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivMessage').addClass('dispoff');
$('#hhbtnsyutujyouYoteiSensyu').addClass('active');
break;
case 3: 
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivMessage').addClass('dispoff');
$('#hhbtnKaisaiHatubaiGuidance').addClass('active');
break;
case 4: 
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivMessage').addClass('dispoff');
$('#hhbtnSyusouList').addClass('active');
if( $('body').children('div').hasClass($('#hhMain').attr('data-hhZbg')) ) {
$($(".basewindows")[0]).removeClass($('#hhMain').attr('data-hhZbg'));
$('#hhMain').addClass($('#hhMain').attr('data-hhZbg'));
}
break;
case 5: 
$('#hhDivKaisaiHeadMessage').addClass('dispoff');
$('#hhDivMessage').addClass('dispoff');
$('#hhbtnResultList').addClass('active');
break;
case 6:
if( Number($('#hhDivMessage').attr('data-flg-sc')) ) {
$('#hhDivMessage').addClass('dispoff');
}
$('#hhbtnRaceAll').addClass('active');
break;
}
};
function hhChgPattern(kbn) {
if(kbn == 1) {
$('#hhDivRaceUnder').addClass('dispoff');
} else {
$('#hhDivRaceUnder').removeClass('dispoff');
}
};
function hhbtnRaceNoClick(prm,rno) {
var params = {},
url1 = $('#hhhdnPostUrl1').val(),
url2 = $('#hhhdnPostUrl2').val(),
url3 = $('#hhhdnPostUrl3').val();
$('#hhbtnSyusouList').removeClass('active');
$('#hhbtnResultList').removeClass('active');
params["encp"] = prm;
if( location.pathname == url2 ) {
btnRaceNoClick(rno);
} else {
switch( location.pathname ) {
case url1:
btnRaceNoClick(rno);
break;
case url3:
btnRaceNoClick(rno);
break;
default:
btnRaceNoClick(rno);
break;
}
}
};
function hhlnkRaceDateClick(prm,idx) {
var params = {},
disp = "",
url1 = $('#hhhdnPostUrl1').val(),
url2 = $('#hhhdnPostUrl2').val(),
url3 = $('#hhhdnPostUrl3').val();
params["encp"] = prm;
if( location.pathname == url2  || parentFuncId == 'FPJ0305') {
disp = displayingId;
switch(disp) {
case 'PJ0301':
case 'PJ0302':
case 'PJ0304':
disp = 'PJ0305';
break;
}
update(disp,params);
} else {
disp = displayingId;
switch( location.pathname ) {
case url1:
btnKaisaiDateClick(idx);
break;
case url3:
btnKaisaiDateClick(idx);
break;
default:
    btnKaisaiDateClick(idx);
break;
}
}
}
$(document).on( 'click', "a[id^='hhlnkRaceDate']", function() {
var idx = $(this).data('ktabIdx') + 1;
var encK = hhGetEncSelKList($('a[name=hhlnkRaceDate]').index(this));
if( encK ) {
if (comKaime.kimIfNoSet()) {
comDialog.confirm('選択中の買い目情報は破棄されますが、よろしいでしょうか。', function(){
hhlnkRaceDateClick(encK,idx);
return false;
}, function(){
return false;
});
} else {
hhlnkRaceDateClick(encK,idx);
return false;
}
}
});
$(document).on( 'click', "button[id^='hhRaceBtn']", function() {
var idx = $('button[name=hhRaceBtn]').index(this);
idx = idx + 1;
var encR = hhGetEncSelRList(idx);
if( encR ) {
if (comKaime.kimIfNoSet()) {
comDialog.confirm('選択中の買い目情報は破棄されますが、よろしいでしょうか。', function(){
hhbtnRaceNoClick(encR,idx);
}, function(){
});
} else {
hhbtnRaceNoClick(encR,idx);
}
if ($('#t_syusei').length) {
PT0245Controller.kimBtnVoteContinue(window.sessionStorage.getItem('voteKbn'));
}
}
});
$(document).on( 'click', "button[id='hhbtnRaceProgram']", function() {
hhCheckPost("PJ0301");
});
$(document).on( 'click', "button[id='hhbtnsyutujyouYoteiSensyu']", function() {
hhCheckPost("PJ0302");
});
$(document).on( 'click', "button[id='hhbtnKaisaiHatubaiGuidance']", function() {
hhCheckPost("PJ0304");
});
$(document).on( 'click', "button[id='hhbtnSyusouList']", function() {
hhCheckPost("PJ0305");
});
$(document).on( 'click', "button[id='hhbtnResultList']", function() {
hhCheckPost("PJ0306");
});
$(document).on( 'click', "button[id='hhbtnRaceAll']", function() {
hhCheckPost("PJ0307");
});
$(document).on( 'click', "button[id='hhbtnVote']", function() {
var params = {};
params["encp"] = hhGetEncSelR();
commonSubmit.formPost($(':hidden[id=hhhdnPostUrl3]').val(),params,null);
});
$(document).on( 'click', '#playerPhotos a', function() {
var param = {};
param["snum"] = $(this).data('hhlnkSnum');
commonSubmit.formGet($(':hidden[id=hhhdnPostUrl4]').val(),param,'_blank');
return false;
});
$(document).on( 'click', '#hhDivWinner a', function() {
var IntvUrl = $(':hidden[id=hhhdnPostUrl5]').val();
var param = {};
param["eizo_kbn"] = "04";
param["kday"] = $(this).data('hhintvKday');
param["bkcd"] = $(this).data('hhintvBkcd');
param["tuban"] = $(this).data('hhintvTuban');
commonLink.NewWindow("",1);
commonSubmit.formPost(IntvUrl,param,"subwin");
return false;
});
$(window).on('resize', function() {
if( $('#hhDivTitleArea').outerWidth(true) < $('#hhDivTitle').outerWidth(true) + $('#hhDivWinner').outerWidth(true) ) {
$('#hhDivTitleArea').addClass('hhracetitle_thick');
} else {
$('#hhDivTitleArea').removeClass('hhracetitle_thick');
}
});
