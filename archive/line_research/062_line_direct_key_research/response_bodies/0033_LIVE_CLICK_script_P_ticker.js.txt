var ccTimerId = 0;
var hhTimerId = 0;
var hhTimerId2 = 0;
function tickerdisp(flg,idnm,wdsz){
var iWidth = 1500;
var idName = idnm;
if( idnm == undefined ) {
idName = 'ticker';
}
if(flg == 0){
if( wdsz != undefined ) {
iWidth = wdsz;
}
var _scroll = {
delay: 1000,
easing: 'linear',
items: 1,
duration: 0.05,
timeoutDuration: 0
};
$('#'+idName+'_inner').carouFredSel({
width: iWidth,
align: false,
items: {
width: 'variable',
height: 32,
visible: 1
},
scroll: _scroll
});
}
var tickerTimerId = 0;
if( idName.substr(0,2) == "hh" ) {
if( idName == "hhTickerF" ) {
tickerTimerId = hhTimerId2;
} else {
tickerTimerId = hhTimerId;
}
} else {
tickerTimerId = ccTimerId;
}
if( tickerTimerId != 0 ) {
clearInterval(tickerTimerId);
}
if(flg==2) {
tickerTimerId = setInterval(function(){
$("span."+idName).animate({ opacity: "0.0"}, 100).animate({ opacity: "1.0"}, 100);
},2000);
if( idName.substr(0,2) == "hh" ) {
if( idName == "hhTickerF" ) {
hhTimerId2 = tickerTimerId;
} else {
hhTimerId = tickerTimerId;
}
} else {
ccTimerId = tickerTimerId;
}
}
};
