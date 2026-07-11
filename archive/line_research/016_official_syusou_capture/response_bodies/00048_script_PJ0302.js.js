$(document).on( 'click', "button[id^='pickup_slide_prev']", function() {
var idx = $(this).attr('id').substr('pickup_slide_prev'.length);
syChangePickup(idx,-1);
});
$(document).on( 'click', "button[id^='pickup_slide_next']", function() {
var idx = $(this).attr('id').substr('pickup_slide_next'.length);
syChangePickup(idx,1);
});
function syChangePickup(idx,move) {
var idName="",
iNum=0;
while(1) {
iNum++;
idName="#pickup"+idx+"_"+iNum;
if( $(idName).hasClass('dispon') ){
$(idName).removeClass('dispon').addClass('dispoff');
break;
}
}
var onId=iNum+move;
idName="pickup"+idx+"_"+onId;
if(document.getElementById(idName) == null) {
if( move == 1 ) {
onId=1;
} else {
idName="pickup"+idx+"_";
onId = $('li[id^='+idName+']').length;
}
}
idName="#pickup"+idx+"_"+onId;
$(idName).removeClass("dispoff").addClass("dispon");
}
function syUnsanitaiz(sanitaizData){
return $("<div>").append(sanitaizData)[0].innerHTML;
}
function syTableHeaderClick() {
$('div[class*="raceInfoSubHelp"] span[class="ui-dialog-title"]').text("調子マーク");
$('#raceInfoSubHelp').dialog('open');
}
