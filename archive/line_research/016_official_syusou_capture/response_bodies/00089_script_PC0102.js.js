$(window).on('load resize',function() {
pc0102_DspTopPageIcon();
});
function sfLinkClick(id){
pc0102_checkKaime(id);
return false;
}
function pc0102_checkKaime(id){
var retKimIfExist;
var objKimGetNoSetKaimeGroup;
var fwurl;
var clrl;
retKimIfExist = comKaime.kimIfExist();
objKimGetNoSetKaimeGroup = comKaime.kimGetNoSetKaimeGroup();
clrl = "[id=sfHdnLink_"+id+"]"
fwurl =$(clrl).attr("value");
if (id == 0){
window.open(fwurl);
} else {
if (retKimIfExist == true || objKimGetNoSetKaimeGroup != null){
comDialog.confirm('編集中の買い目は破棄されますがよろしいですか。', function(){
comKaime.kimClear();
pc0102_ok(id);
return;
},function(){
});
} else {
comKaime.kimClear();
window.location.href = fwurl;
}
}
return false;
}
function pc0102_ok(id){
var clrl = "[id=sfHdnLink_"+id+"]"
var url =$(clrl).attr("value");
window.location.href = url;
return false;
}
function pc0102_DspTopPageIcon(){
var windowsize = $(window).height();
var bodysize = $('body').height();
if (windowsize >= bodysize) {
$("#shbtnTop").addClass("dispoff");
    $("#shbtnTopoff").removeClass("dispoff");
$("#shbtnTopoff").addClass("dispon");
}
else {
if ($("#shbtnTop").hasClass("dispoff")) {
$("#shbtnTop").removeClass("dispoff");
    $("#shbtnTopoff").removeClass("dispon");
$("#shbtnTopoff").addClass("dispoff");
}
}
};
function sfLoadingFinalize(){
var url =$("#sfHelpLink").attr("value");
$("#sfHdnLink_0").attr("value",url);
return false;
}
