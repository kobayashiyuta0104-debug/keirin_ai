var syRankingTableC1 = ["no1","no2","no3","no","no"];
var syRankingTableC2 = ["class_color_A3_light","class_color_A3","class_color_A3_dark","",""];
var syTableBgcolor = ["altertable_kisu","altertable_guusu"];
var syView = {
HDNKEY_ID: 'JSJ015',
syDrawJSONData: function(maindata, _reqParam) {
if ( !maindata ) {
Com.viewErrorPage(null);
} else if ( maindata.resultCd == -1 ) {
var messageCd = "";
if( maindata.messageCd != undefined ) {
messageCd = maindata.messageCd;
}
Com.viewErrorPage(messageCd);
} else {
$('#cdivGaiteiList').empty();
$('#cdivYoteiSensyu').empty();
if( maindata.J0302data.J0302gaitei == null
 || maindata.J0302data.J0302gaitei == undefined
 || maindata.J0302data.J0302gaitei.length < 1 ) {
return;
}
var $tbody = $('<tbody />');
for( var ilop=0; ilop<maindata.J0302data.J0302gaitei.length; ilop++ ) {
var kikan = maindata.J0302data.J0302gaitei[ilop].kikanFirstDay+maindata.J0302data.J0302gaitei[ilop].nitijiFirstDay;
if((maindata.J0302data.J0302gaitei[ilop].kikanLastDay != undefined
 && maindata.J0302data.J0302gaitei[ilop].kikanLastDay.length > 0)
 ||(maindata.J0302data.J0302gaitei[ilop].nitijiLastDay != null
 && maindata.J0302data.J0302gaitei[ilop].nitijiLastDay.length > 0)) {
kikan = kikan + "～" + maindata.J0302data.J0302gaitei[ilop].kikanLastDay + maindata.J0302data.J0302gaitei[ilop].nitijiLastDay;
}
var udate = '';
if(ilop==0) {
udate = maindata.J0302data.updateDateTime;
}
$tbody.append($('<tr />')
.append($('<td />').addClass('pl0 gkikan').append($('<p />').addClass('al-l').append(kikan)))
.append($('<td />').addClass('gsicon')
.append($('<div />').addClass('al-c v-al-m')
.append($('<img />').addClass('gsicon').attr('src',maindata.J0302data.J0302gaitei[ilop].imgSyuyouIconSrc).attr('alt',maindata.J0302data.J0302gaitei[ilop].imgSyuyouIconAlt))))
.append($('<td />').addClass('gbname')
.append($('<p />').addClass('al-l')
.append($('<a />').attr('onclick',"shLocalJump('b" + Number(ilop+1)  + "')")
.append($('<span />').addClass('btn onbtn al-c gbname')
.append(maindata.J0302data.J0302gaitei[ilop].bangumiName)))))
.append($('<td />').addClass('gblank').append($('<p />')))
.append($('<td />').addClass('gudate').append($('<p />').addClass('al-r').append(udate)))
);
}
$('#cdivGaiteiList').append($('<table />').addClass('nonbd w100pc').append($tbody));
var dOnOff = "";
var $divZ1 = $('<div />').addClass('plLoginIcon'),
$divZ2 = $('<div />').addClass('plGuideMsg'),
$spnZ1 = $('<span />'),
$spnZ2 = $('<span />');
;
if( !maindata.J0302data.flgEndState
 && maindata.J0302data.flgRelease
 && maindata.J0302data.flgLogin ) {
var $imgZ1 = $('<div />').addClass('dispib'),
$imgZ2 = $('<div />').addClass('dispib');
$imgZ1
.append($('<img />')
.addClass('dispon')
.attr('src',maindata.J0302data.imgPushSrc)
.attr('alt',syUnsanitaiz(maindata.J0302data.imgPushAlt)));
$imgZ2
.append($('<img />')
.addClass('dispon')
.attr('src',maindata.J0302data.imgCongenialSrc)
.attr('alt',syUnsanitaiz(maindata.J0302data.imgCongenialAlt)));
$spnZ1.append($imgZ1).append('一押し').append('&nbsp;&nbsp;&nbsp;').append($imgZ2).append('好相性');
 dOnOff = "dispib";
}
if( maindata.J0302data.flgRelease ) {
$spnZ2.append('成績上位5位を赤字で表示');
 dOnOff = "dispib";
}
$divZ1.addClass(dOnOff).append($spnZ1);
$divZ2.addClass(dOnOff).append($spnZ2);
for( var ilop=0; ilop<maindata.J0302data.J0302gaitei.length; ilop++ ) {
var $gtitle = $('<div />').addClass('sbname'),
$prpufa = $('<div />').addClass('sbname'),
$sslist = $('<div />').addClass('sbname');
var bName = '';
if( maindata.J0302data.J0302gaitei[ilop].bangumiName != undefined
 && maindata.J0302data.J0302gaitei[ilop].bangumiName.length > 0 ) {
bName = maindata.J0302data.J0302gaitei[ilop].bangumiName;
if( maindata.J0302data.J0302gaitei[ilop].nitijiLastDay == undefined
 || maindata.J0302data.J0302gaitei[ilop].nitijiLastDay.length == 0 ) {
 bName = bName + maindata.J0302data.J0302gaitei[ilop].nitijiFirstDay;
}
}
$gtitle.addClass('sbname')
.append($('<a />').attr('id','b'+(ilop+1)))
.append($('<table />').addClass('nonbd')
.append($('<tbody />')
.append($('<tr />')
.append($('<td />').addClass('pl0 ssicon')
.append($('<div />').addClass('al-c v-al-m')
.append($('<img />').addClass('ssicon').attr('src',maindata.J0302data.J0302gaitei[ilop].imgSyuyouIconSrc).attr('alt',maindata.J0302data.J0302gaitei[ilop].imgSyuyouIconAlt))))
.append($('<td />').addClass('sbname').append($('<p />').addClass('sbname').append(bName)))
)));
var $divEndPoint = $('<div />').addClass('h20pt');
var $ranking = $('<td />').addClass('rtitle v-al-t'),
$pickups = $('<td />').addClass('ptitle v-al-t'),
$failadd = $('<td />').addClass('ftitle v-al-t');
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu != undefined ) {
if( !maindata.J0302data.flgEndState ) {
$ranking.append($('<p />').addClass('midasi2_fsz ml15').text('競走得点ランキング'));
if( maindata.J0302data.J0302gaitei[ilop].J0302ranking == undefined ) {
} else if ( maindata.J0302data.J0302gaitei[ilop].J0302ranking.length > 0 ) {
var $prdiv = $('<div />').addClass('mt5'),
$prtbl = $('<table />').addClass('tokuten_ranking al-c'),
$prtbd = $('<tbody />');
for( var jlop=0; jlop<maindata.J0302data.J0302gaitei[ilop].J0302ranking.length; jlop++ ) {
if( jlop > 4 ) {
break;
}
var emNum = maindata.J0302data.J0302gaitei[ilop].J0302ranking[jlop].emNumber;
var pName = maindata.J0302data.J0302gaitei[ilop].J0302sensyu[emNum].playerNm,
txtUrl = $(':hidden[id=chdnPostUrl1]').val()+"?snum="+maindata.J0302data.J0302gaitei[ilop].J0302sensyu[emNum].playerNo;
$prtbd.append($('<tr />')
.append($('<td />').addClass(syRankingTableC1[jlop]).addClass(syRankingTableC2[jlop]).append(jlop+1))
.append($('<td />').addClass(syRankingTableC1[jlop]).addClass(syRankingTableC2[jlop]).addClass('name')
.append($('<a />').attr('href',txtUrl).append(pName)))
);
}
$prtbl.append($prtbd);
$prdiv.append($prtbl);
$ranking.append($prdiv);
}
$pickups.append($('<p />').addClass('dispib midasi2_fsz ml15').text('ピックアップ選手'));
if( maindata.J0302data.J0302gaitei[ilop].J0302pickup == undefined ) {
} else if ( maindata.J0302data.J0302gaitei[ilop].J0302pickup.length > 0 ) {
var iddPick = "pickup_type"+(ilop+1);
var $dPick = $('<div />').addClass('tab-pane1 active').attr('id',iddPick),
$uPick = $('<ul />').addClass('al-l pickup');
for( var jlop=0; jlop<maindata.J0302data.J0302gaitei[ilop].J0302pickup.length; jlop++ ) {
var iduPick = "pickup"+(ilop+1)+"_"+(jlop+1);
var $lPick = $('<li />').attr('id',iduPick).addClass('pickupRace pickup');
if( jlop == 0 ) {
$lPick.addClass('dispon');
} else {
$lPick.addClass('dispoff');
}
var $divLst = $('<div />').addClass('pickupRaceText clear-fix');
var $pKijun = $('<p />').attr('id','pPickKjn'+ilop+'_'+jlop);
if( maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].pickupBlink ) {
$pKijun.addClass('win6over');
}
var $imgPly = $('<img />').addClass('face_pickup');
if( maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].imgPlayerPict != undefined
 && maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].imgPlayerPict.length > 0 ) {
$imgPly
.attr('src',maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].imgPlayerPict)
.attr('alt',syUnsanitaiz(maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].playerName));
} else {
$imgPly.addClass('face_pickup_deffw');
}
$divLst
.append($pKijun.append($('<b />').append(maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].pickupKijun)))
.append($('<div />').addClass('fl-l').append($('<div />').addClass('face_pickup_mxw').append($imgPly)))
.append($('<p />').addClass('pt5').append($('<b />').append(maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].playerName)).append('　選手'))
.append($('<p />').addClass('player_class')
.append("("+maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].hukenName+maindata.J0302data.J0302gaitei[ilop].J0302pickup[jlop].kyuhanName+")"));
$lPick.append($divLst);
$uPick.append($lPick);
}
var oneMoreClass = '';
if( maindata.J0302data.J0302gaitei[ilop].J0302pickup.length <= 1 ) {
oneMoreClass = 'disabled';
}
$uPick.append($('<div />').addClass('clear-fix')
.append($('<div />').addClass('myHR'))
.append($('<p />').addClass('fl-l m-lf').append($('<button />').attr('id','pickup_slide_prev'+(ilop+1)).attr('name','pickup_slide_prev').attr('type','button').addClass('btn onbtn w60pt '+oneMoreClass).append('&lt;')))
.append($('<p />').addClass('fl-r m-rt').append($('<button />').attr('id','pickup_slide_next'+(ilop+1)).attr('name','pickup_slide_next').attr('type','button').addClass('btn onbtn w60pt '+oneMoreClass).append('&gt;')))
);
$pickups.append($('<div />').addClass('mt5')
.append($('<div />').addClass('contentsUtility clear-fix').attr('style','border: 1px solid rgb(136, 136, 136); border-image: none; width: 250px;')
.append($('<div />').addClass('clear-fix').attr('style','margin-bottom: 0px;')
.append($('<div />').addClass('tab-content1').attr('id','my-tab-content')
.append($dPick.append($uPick))
))));
$pickups.append($('<div />').addClass('al-r').append($('<p />').addClass('updtm').append('情報更新日時：'+maindata.J0302data.J0302gaitei[ilop].pickupUpdDateTime)));
}
}
}
$failadd.append($('<p />').addClass('dispib midasi2_fsz ml15').text('欠場・追加・補充'));
if( maindata.J0302data.J0302gaitei[ilop].txtDisqualification != null
 && maindata.J0302data.J0302gaitei[ilop].txtDisqualification != undefined ) {
$failadd.append($('<span />').addClass('ml15').append(maindata.J0302data.J0302gaitei[ilop].txtDisqualification));
}
if( maindata.J0302data.J0302gaitei[ilop].J0302failadd == undefined ) {
} else if ( maindata.J0302data.J0302gaitei[ilop].J0302failadd.length > 0 ) {
var $fatbl = $('<table />').addClass('tbl_1 altertable mt5 w100pc'),
$fatbd = $('<tbody />');
$fatbd.append($('<tr />')
.append($('<th />').addClass('title al-c').attr('colspan','2').text('欠場・不参加情報'))
.append($('<th />').addClass('title al-c').attr('colspan','2').text('追加・補充情報')) );
$fatbd.append($('<tr />')
.append($('<th />').addClass('title al-c w10pc').text('選手名'))
.append($('<th />').addClass('title al-c w10pc').text('変更状況'))
.append($('<th />').addClass('title al-c w10pc').text('選手名'))
.append($('<th />').addClass('title al-c w10pc').text('変更状況')) );
for( var jlop=0; jlop<maindata.J0302data.J0302gaitei[ilop].J0302failadd.length; jlop++ ) {
$fatbd.append($('<tr />')
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302failadd[jlop].failPlayerName))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302failadd[jlop].failPlayerState))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302failadd[jlop].addPlayerName))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302failadd[jlop].addPlayerState)) );
}
$fatbl.append($fatbd);
$failadd.append($fatbl);
}
$prpufa.append($('<table />').addClass('w100pc')
.append($('<tbody />')
.append($('<tr />')
.append($ranking)
.append($pickups)
.append($failadd) )));
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu != undefined ) {
var $divX0 = $('<div />'),
$divX1 = $('<div />').addClass('dispib w60pt'),
$divX2 = $('<span />'),
$divX3 = $('<div />').addClass('dispib w200pt'),
$divS0 = $('<div />').addClass('clear-fix'),
$divT1 = $divZ1.clone(),
$divT2 = $divZ2.clone(),
$divS1 = $('<div />').addClass('fl-l w30pc'),
$tblS1 = $('<table />').addClass('race_member').append($('<thead />')
.append($('<tr />')
.append($('<td />').attr('rowspan','2').addClass('hdkh').text('級班'))
.append($('<td />').attr('rowspan','2').addClass('hdtk').text('地区'))
.append($('<td />').attr('rowspan','2').addClass('w52pc nb-b')
.append($('<p />').text('選手名'))
.append($('<p />').text('府県/級班').append($('<span />').addClass('tbl_val11_fsz').text('前')).append('現/脚質')))
.append($('<td />').addClass('hdkb').text('期別')))
.append($('<tr />')
.append($('<td />').text('年齢')))),
$tbdS1 = $('<tbody />');
$divS2 = $('<div />').addClass('fl-l w70pc'),
$tblS2 = $('<table />').addClass('race_member1').append($('<thead />')
.append($('<tr />')
.append($('<td />').attr('colspan','12').append($('<p />').text('直近4ヶ月成績')))
.append($('<td />').attr('rowspan','3').addClass('hdts').attr('data-toggle','modal').attr('data-target','#choushi_konkyo').text('調').append($('<br />')).append('子')) )
.append($('<tr />')
.append($('<td />').attr('rowspan','2').addClass('hdkt').text('競走得点'))
.append($('<td />').attr('colspan','4').addClass('row2 b-b nb-t nb-l').text('決まり手'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w4pc').text('B'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w4pc').text('H'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w4pc').text('S'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w9pc').text('勝率'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w9pc').text('２連対率'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c wb-r w9pc').text('３連対率'))
.append($('<td />').attr('rowspan','2').addClass('decisive al-c w4pc').text('優勝').append($('<br />')).append('回数')))
.append($('<tr />')
.append($('<td />').addClass('row3 w4pc').text('逃'))
.append($('<td />').addClass('w4pc').text('捲'))
.append($('<td />').addClass('w4pc').text('差'))
.append($('<td />').addClass('w4pc').text('マ')))
);
$tbdS2 = $('<tbody />').addClass('altertable');
for( var jlop=0; jlop<maindata.J0302data.J0302gaitei[ilop].J0302sensyu.length; jlop++ ) {
var huken = "　　　",
prvKH = "&nbsp;&nbsp;&nbsp;",
nowKH = "&nbsp;&nbsp;&nbsp;",
kyaku = "　",
txtUrl = $(':hidden[id=chdnPostUrl1]').val()+"?snum="+maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].playerNo,
$imgIti = '',
$imgKou = '';
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].hukenName != undefined 
 && maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].hukenName.length > 0 ) {
huken = maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].hukenName;
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].prevKyuhan != undefined
 && maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].prevKyuhan.length > 0 ) {
prvKH = maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].prevKyuhan;
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].nowKyuhan != undefined
 && maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].nowKyuhan.length > 0 ) {
nowKH = maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].nowKyuhan;
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kyakushitsu != undefined
 && maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kyakushitsu.length > 0 ) {
kyaku = maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kyakushitsu;
}
var $divItiKou = $('<div />').addClass('fl-l');
if( maindata.J0302data.flgRelease && maindata.J0302data.flgLogin ) {
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].flgPush ) {
$imgIti = $('<img />').attr('src',maindata.J0302data.imgPushSrc).attr('alf',maindata.J0302data.imgPushAlt);
$divItiKou.append($imgIti).append('&nbsp;');
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].flgCongenial ) {
$imgKou = $('<img />').attr('src',maindata.J0302data.imgCongenialSrc).attr('alt',maindata.J0302data.imgCongenialAlt);
$divItiKou.append($imgKou);
}
}
var $spnNowKH = $('<span />').append(nowKH);
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].flgTokusyo ) {
$spnNowKH.addClass(maindata.J0302data.cidTokusyo);
}
$tbdS1
.append($('<tr />').addClass(syTableBgcolor[jlop%2])
.append($('<td />').attr('rowspan','2').addClass('al-c')
.addClass(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cidKyuhanBg)
.append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].nowKyuhan))
.append($('<td />').attr('rowspan','2').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].tikuName))
.append($('<td />').attr('rowspan','2').addClass('al-l')
.append($('<div />').addClass('clear-fix')
.append($('<div />').addClass('fl-r w38pt')
.append($divItiKou))
.append($('<div />').addClass('fl-l')
.append($('<div />').addClass('pad5').append($('<a />').attr('href',txtUrl).addClass('bold txt_underline').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].playerNm)).append('&nbsp;').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].playerState))
.append($('<div />').addClass('pad5').append(huken+"/").append($('<span />').addClass('tbl_val11_fsz').append(prvKH)).append($spnNowKH).append("/"+kyaku)))
))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kibetsu))
)
.append($('<tr />').addClass(syTableBgcolor[jlop%2])
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].playerAge))
)
;
if( maindata.J0302data.flgRelease ) {
var cidPts = '',
cidWin = '',
$imgCud = '';
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].flgTop5 ) {
cidPts = 'bold ' + maindata.J0302data.cidRanking;
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].flgHigherWinner ) {
cidWin = 'bold ' + maindata.J0302data.cidRanking;
}
if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kbnCondition == "1" ) {
$imgCud = $('<img />').attr('src',maindata.J0302data.imgConditionUpSrc).attr('alt',maindata.J0302data.imgConditionUpAlt);
} else if( maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].kbnCondition == "2" ) {
$imgCud = $('<img />').attr('src',maindata.J0302data.imgConditionDnSrc).attr('alt',maindata.J0302data.imgConditionDnAlt);
}
$tbdS2.append($('<tr />')
.append($('<td />').addClass('al-c h58pt').addClass(cidPts).append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].racePoint))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntNige))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntMaki))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntSa))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntMark))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntBack))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntHome))
.append($('<td />').addClass('al-c').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntStand))
.append($('<td />').addClass('al-c chaku_type1').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].perWin1))
.append($('<td />').addClass('al-c chaku_type2').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].perWin2))
.append($('<td />').addClass('al-c wb-r chaku_type3').append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].perWin3))
.append($('<td />').addClass('al-c').addClass(cidWin).append(maindata.J0302data.J0302gaitei[ilop].J0302sensyu[jlop].cntWin))
.append($('<td />').addClass('al-c').append($imgCud))
);
} else {
$tbdS2.append($('<tr />')
.append($('<td />').addClass('al-c h58pt'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c chaku_type1'))
.append($('<td />').addClass('al-c chaku_type2'))
.append($('<td />').addClass('al-c wb-r chaku_type3'))
.append($('<td />').addClass('al-c'))
.append($('<td />').addClass('al-c'))
);
}
}
$divS0.append($divS1.append($divT1).append($tblS1.append($tbdS1)));
if( maindata.J0302data.flgRelease ) {
$divS0.append($divS2.append($divT2).append($tblS2.append($tbdS2)));
$divEndPoint.addClass('al-r').append('調子：').append($('<a />').attr('onclick','syTableHeaderClick();').addClass('txt_underline').append('データ集計結果'));
} else {
$divS0.append($divS2);
}
$sslist.append($divS0);
}
$('#cdivYoteiSensyu').append($gtitle).append($prpufa).append($sslist).append($divEndPoint);
}
}
$(".win6over").each(function() {
syBlink( $(this).attr("id") );
});
return;
}
};
function syBlink(idName) {
setInterval(function(){
$("[id="+idName+"]").animate({ opacity: "0.0"}, 250).animate({ opacity: "1.0"}, 250);
},500);
};
