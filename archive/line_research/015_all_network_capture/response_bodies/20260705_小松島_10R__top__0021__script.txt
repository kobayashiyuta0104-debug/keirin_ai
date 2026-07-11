var dialog_flag = false;
var wsize = $(window).width();
var hsize = $(window).height();
var lockflg = false;
$(window).on('load resize',function(){
    wsize = $(window).width();
    hsize = $(window).height();
});
$(window).on("scroll wheel onwheel onmousewheel" ,function(e){
if (scrollflg==true){
e.preventDefault();
}
});
if(window.onbeforeprint === null){
    window.onbeforeprint = function(){
        var style="";
        var width="";
        var height="";
        var contextPath = "";
    contextPath = $("script").attr("src").substring(0,$("script").attr("src").indexOf("static"));
        for(var i=0; i < $(".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front").length;i++){
        if($("#"+ $($($($(".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front")[i]).children())[1]).attr("id")).dialog("isOpen")){
        style = $($(".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front")[i]).attr("style");
        width = $($(".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front")[i]).outerWidth();
        height= $($(".ui-dialog.ui-widget.ui-widget-content.ui-corner-all.ui-front")[i]).outerHeight();
        $("body").append($("<img>").attr("id","dialogspacer").attr("src",contextPath +"static/css/img/ui-bg_flat_55_ffffff_40x100.png").attr("style",style).addClass("ui-dialog"));
        $("#dialogspacer").css("z-index","90");
        $("#dialogspacer").css("width",width);
        $("#dialogspacer").css("height",height);
        }
        }
    };
}
if(window.onafterprint === null){
window.onafterprint = function(){
        $("#dialogspacer").remove();
    };
}
var scrollflg = false;
$(function() {
$(".ui-widget-overlay").css("z-index", 999);
$("[id=sub_dlg_Cancel]").click( function() {
$(".ui-dialog-content").dialog("close")
return false;
});
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
$('#y3rentan').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'3連単支持率',
dialogClass: 'y3rentan',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=y3rentan_click]").click( function() {
$( '#y3rentan' ).dialog( 'open' );
return false;
});
$('#over_kyosotokuten').dialog({
autoOpen: false,
height: 'auto',
width: '1000',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'',
dialogClass: 'kimarite',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('.ui-dialog-cancel').after('\
<div class="sub_dlg_title">平均競走得点遷移グラフ　<span class="fred">赤線：直近4ヶ月</span>　<span class="fblue">青線：直近4ヶ月（今期のみ）</span></div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$('.sub_dlg_title').detach();
dialog_flag = false;
}
});
$("[id=over_kyosotokuten_click]").click( function() {
$('#over_kyosotokuten').dialog( 'open' );
return false;
});
$('#kimarite').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'決まり手内訳',
dialogClass: 'kimarite',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=kimarite_click]").click( function() {
$('#kimarite').dialog( 'open' );
return false;
});
$('#B15').dialog({
autoOpen: false,
height: 'auto',
width: '630',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'BHレース一覧',
dialogClass: 'S15',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=B15_click]").click( function() {
$('#B15').dialog( 'open' );
return false;
});
$('#S17').dialog({
autoOpen: false,
height: 'auto',
width: '630',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'Sレース一覧',
dialogClass: 'S17',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=S17_click]").click( function() {
$('#S17').dialog( 'open' );
return false;
});
$('#taisen_seiseki2').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'同時出走レース一覧',
dialogClass: 'taisen_seiseki2',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=taisen_seiseki2_click]").click( function() {
$('#taisen_seiseki2').dialog( 'open' );
return false;
});
$('#chaku').dialog({
autoOpen: false,
height: 'auto',
width: '630',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'',
dialogClass: 'chaku',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$('.sub_dlg_title').detach();
dialog_flag = false;
}
});
$("[id=chaku_click]").click( function() {
$('#chaku').dialog( 'open' );
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
if ( $(this).hasClass("chaku_type1") ) {
$('.ui-dialog-cancel').after('\
<div id="chaku_title" class="sub_dlg_title">1着時のレース一覧</div>\
');
}
if ( $(this).hasClass("chaku_type2") ) {
$('.ui-dialog-cancel').after('\
<div id="chaku_title" class="sub_dlg_title">1～2着時のレース一覧</div>\
');
}
if ( $(this).hasClass("chaku_type3") ) {
$('.ui-dialog-cancel').after('\
<div id="chaku_title" class="sub_dlg_title">1～3着時のレース一覧</div>\
');
}
return false;
});
$('#tejun1').dialog({
autoOpen: false,
height: 'auto',
width: '885',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'１着時の決まり手情報',
dialogClass: 'tejun1',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=tejun1_click]").click( function() {
$('#tejun1').dialog( 'open' );
return false;
});
$('#tejun2').dialog({
autoOpen: false,
height: 'auto',
width: '885',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'２着時の決まり手情報',
dialogClass: 'tejun2',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=tejun2_click]").click( function() {
$('#tejun2').dialog( 'open' );
return false;
});
$('#tanten_ari').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'',        
dialogClass: 'tanten_ari',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#raceInfoSubHelp').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'',
dialogClass: 'raceInfoSubHelp',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PT9101').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'初期金額設定',
dialogClass: 'PT9101',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$(document).off("click", ".ui-widget-overlay");
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=PT9101_click]").click( function() {
$('#PT9101').dialog( 'open' );
return false;
});
$('#PT9102').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'テンキー',
dialogClass: 'PT9102',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$(document).off("click", ".ui-widget-overlay");
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=PT9102_click]").click( function() {
$('#PT9102').dialog( 'open' );
return false;
});
$('#PM0109').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'的中率グラフ　月別(60ヶ月)',
dialogClass: 'PM0109',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-1').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0109_click]").click( function() {
$('#PM0109').dialog( 'open' );
return false;
});
$('#PM0109_44month').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中率グラフ  月別(60ヶ月)',
dialogClass: 'PM0109_44month',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-2').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0109_14month').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'的中率グラフ　月別(14ヶ月)',
dialogClass: 'PM0109_14month',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-3').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0109_14month_click]").click( function() {
$('#PM0109_14month').dialog( 'open' );
return false;
});
$('#PM0109_50ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'的中率グラフ　一押し選手別(50人)',
dialogClass: 'PM0109_50ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-4').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0109_50krj').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0109_50krj',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-5').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0109_50ichioshi_click]").click( function() {
$('#PM0109_50ichioshi').dialog( 'open' );
return false;
});
$('#PM0109_20ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0109_20ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-6').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0109_9ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0109_9ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-7').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0109_9grd').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0109_9grd',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-8').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0109_9kakeshiki').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0109_9kakeshiki',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-9').html(tekityuRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0109_10ichioshi_click]").click( function() {
$('#PM0109_10ichioshi').dialog( 'open' );
return false;
});
$('#PM0110').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-10').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_44month').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109_44month',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-11').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_14month').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109_14month',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-12').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0110_click]").click( function() {
$('#PM0110').dialog( 'open' );
return false;
});
$('#PM0110_50ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109_50ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-13').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_50krj').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0110_50krj',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-14').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0110_50ichioshi_click]").click( function() {
$('#PM0110_50ichioshi').dialog( 'open' );
return false;
});
$('#PM0110_20ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: '1000px',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109_20ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-15').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_9ichioshi').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '回収',
dialogClass: 'PM0109_9ichioshi',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-16').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_9grd').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0110_9grd',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-17').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$('#PM0110_9kake').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title: '的中',
dialogClass: 'PM0110_9kake',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
$('#ui-id-18').html(recoverRateTitle);
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
dialog_flag = false;
}
});
$("[id=PM0110_10ichioshi_click]").click( function() {
$('#PM0110_10ichioshi').dialog( 'open' );
return false;
});
$('#PM0105_omedetou').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'PM0105_omedetou',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".ui-dialog-titlebar").hide();
dialog_flag = true;
},
close: function(event, ui){
dialog_flag = false;
$('body').css('overflow-y', 'auto');
}
});
$("[id=PM0105_omedetou_click]").click( function() {
$('#PM0105_omedetou').dialog( 'open' );
return false;
});
$('#PM0116_omedetou').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'PM0116_omedetou',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".ui-dialog-titlebar").hide();
dialog_flag = true;
},
close: function(event, ui){
dialog_flag = false;
}
});
$("[id=PM0116_omedetou_click]").click( function() {
$('#PM0116_omedetou').dialog( 'open' );
return false;
});
$('#PM0116_tekichu').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'PM0116_tekichu',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".ui-dialog-titlebar").hide();
dialog_flag = true;
},
close: function(event, ui){
dialog_flag = false;
}
});
$("[id=PM0116_tekichu_img]").click( function() {
$('#PM0116_tekichu').dialog( 'close' );
return false;
});
$('#kannren_ozu').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'関連オッズ',
dialogClass: 'kannren_ozu',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(document).off("click", ".ui-widget-overlay");
$('.ui-dialog-titlebar-close').hide();
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=kannren_ozu_click]").click( function() {
$('#kannren_ozu').dialog( 'open' );
return false;
});
$('#conf_cancel').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'conf_cancel',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".conf_cancel .ui-dialog-titlebar").hide();
$(document).off("click", ".ui-widget-overlay");
dialog_flag = true;
},
close: function(event, ui){
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=conf_cancel_click]").click( function() {
$('#conf_cancel').dialog( 'open' );
return false;
});
$('#conf_save').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'conf_save',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".conf_save .ui-dialog-titlebar").hide();
$(document).off("click", ".ui-widget-overlay");
dialog_flag = true;
},
close: function(event, ui){
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=conf_save_click]").click( function() {
$('#conf_save').dialog( 'open' );
return false;
});
$('#set_init').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: true,
resizable: false,
modal: true,
closeOnEscape: true,
title:'初期金額設定',
dialogClass: 'conf_save',
position: {
at: 'left+600 center',
my: 'center center'
},
open: function(event, ui){
$('.ui-dialog-titlebar-close').hide();
$(document).off("click", ".ui-widget-overlay");
$('.ui-dialog-titlebar-close').after('\
<div class="fl-r clear-fix ui-dialog-cancel">\
<div class="cancel_btn" title="Close">\
<a id="sub_dlg_Cancel" class="cancel_btn_fsz" onclick=$(".ui-dialog-content").dialog("close")>&nbsp;&times;&nbsp;</a>\
</div>\
</div>\
');
dialog_flag = true;
},
close: function(event, ui){
$('.ui-dialog-cancel').detach();
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=set_init_click]").click( function() {
$('#set_init').dialog( 'open' );
return false;
});
$('#alert_dialog').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'alert_dialog',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".alert_dialog .ui-dialog-titlebar").hide();
$(document).off("click", ".ui-widget-overlay");
dialog_flag = true;
},
close: function(event, ui){
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
$("[id=conf_alert_dialog]").click( function() {
$('#alert_dialog').dialog( 'open' );
return false;
});
$('#PC0101_kaime_chk').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: false,
closeOnEscape: true,
dialogClass: 'PC0101_kaime_chk',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".PC0101_kaime_chk .ui-dialog-titlebar").hide();
dialog_flag = true;
    scrollflg = true;
displayLock(dialog_flag);
},
close: function(event, ui){
dialog_flag = false;
scrollflg = false;
displayLock(dialog_flag);
}
});
$('#PC0102_kaime_chk').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: false,
closeOnEscape: true,
dialogClass: 'PC0102_kaime_chk',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".PC0102_kaime_chk .ui-dialog-titlebar").hide();
dialog_flag = true;
    scrollflg = true;
displayLock(dialog_flag);
},
close: function(event, ui){
dialog_flag = false;
scrollflg = false;
displayLock(dialog_flag);
}
});
$('#PM0112_tekichu').dialog({
autoOpen: false,
height: '190',
width: '380',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'PM0112_tekichu_hanei',
position: {
at: 'center center',
my: 'center center',
},
open: function(event, ui){
$(".ui-dialog-titlebar").hide();
$(document).off("click", ".ui-widget-overlay");
dialog_flag = true;
},
close: function(event, ui){
dialog_flag = false;
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
}
});
$('#alert_dialog_lock').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: false,
closeOnEscape: true,
dialogClass: 'alert_dialog',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(".alert_dialog .ui-dialog-titlebar").hide();
$(document).off("click", ".ui-widget-overlay");
dialog_flag = true;
    scrollflg = true;
displayLock(dialog_flag);
},
close: function(event, ui){
dialog_flag = false;
scrollflg = false;
displayLock(dialog_flag);
        $(document).on("click", ".ui-widget-overlay", function(){
        $(".ui-dialog-content").dialog("close");
        });
}
});
$("[id=conf_alert_dialog]").click( function() {
$('#alert_dialog_lock').dialog( 'open' );
return false;
});
});
function displayLock(flag) {
if(flag == true){
    if(lockflg != true){
    var PositionWidth  = (wsize-80)/2;
    var PositionHeight = (hsize-80)/2;
    $('body').prepend('\
            <div id="divfixload">\
            <div id="divrelload">\
                <div id="" style="left:' + PositionWidth + 'px;right: ' + PositionWidth + 'px; top: ' + PositionHeight + 'px;  bottom: ' + PositionHeight +'px;"></div>\
            </div>\
        </div>\
    ');        
    lockflg = true;
}
} else {
          $('#divfixload').remove();
    lockflg = false;
}
}
function dialogDispCenter(){
    var sclLeft = document.body.scrollLeft || document.documentElement.scrollLeft;
    var sclTop = document.body.scrollTop || document.documentElement.scrollTop;
    var width = window.innerWidth;
    var height = window.innerHeight;
    var d_w = $("div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all").width();
    var d_h = $("div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all").height();
    var left = (width - d_w) /2;
    var top = (height - d_h) /2;
    left = left + parseInt(sclLeft);
    top = top + parseInt(sclTop);
    $("div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all").css("left",left + "px");
    $("div.ui-dialog.ui-widget.ui-widget-content.ui-corner-all").css("top",top + "px");
}
