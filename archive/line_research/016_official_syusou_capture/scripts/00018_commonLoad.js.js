var wsize = $(window).width();
var hsize = $(window).height();
var loaddingflg = false;
$(window).keydown(function(event){
if(loaddingflg == true) {
event.keyCode = null;
return false;
}
});
$(window).on('load',function(){
commonLoad.changeWindowSize();
});
$(window).on('resize',function(){
if(loaddingflg == true) {
commonLoad.changeWindowSize();
var PositionWidth  = (wsize-80)/2;
var PositionHeight = (hsize-80)/2;
$("#divabsload").css(
{
"right":PositionWidth,
"left":PositionWidth,
"top":PositionHeight,
"bottom":PositionHeight
}
);
}
});
$(window).on('beforeunload pagebeforehide',function(){
});
$(window).on("dialogclose",function(){
$('.wchkstp').removeClass('wchkstp');
});
$(window).on('unload pagehide',function(){
commonLoad.loadingImage("false");
$('.wchkstp').removeClass('wchkstp');
});
$(window).on('load pageshow',function(){
if( $('#divfixload').length > 0 ) {
$('#divfixload').remove();
loaddingflg = false;
}
});
var commonLoad = {
wclkchk: function (e) {
if( $(e.target).hasClass('wchkstp') ) {
return false;
}
$(e.target).addClass('wchkstp');
return true;
},
loadingImage: function (flag) {
if(flag == "true"){
if(loaddingflg != true){
loaddingflg = true;
var PositionWidth  = (wsize-80)/2;
var PositionHeight = (hsize-80)/2;
$('body').prepend('\
<div id="divfixload">\
<div id="divrelload">\
<div id="divabsload" style="left:' + PositionWidth + 'px;right: ' + PositionWidth + 'px; top: ' + PositionHeight + 'px;  bottom: ' + PositionHeight +'px;"></div>\
</div>\
</div>\
');
}
} else {
if(loaddingflg == true){
$('#divfixload').remove();
loaddingflg = false;
}
}
},
changeWindowSize: function () {
wsize = $(window).width();
hsize = $(window).height();
}
};
