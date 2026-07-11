var commonSubmit = {
formPost: function(actn, lprm, target) {
var $form = $('<form />');
$form.attr("action", actn).attr("method", "post");
if(target != null){
$form.attr("target",target);
}
var kynm = Object.keys(lprm);
for( var ilop = 0; ilop < kynm.length; ilop++ ) {
$form.append($('<input />').attr("type", "hidden").attr("name", kynm[ilop]).attr("value", lprm[kynm[ilop]]));
}
$form.appendTo("body").submit().remove();
return;
},
formGet: function(actn, lprm, target) {
var $form = $('<form />');
$form.attr("action", actn).attr("method", "get");
if(target != null){
$form.attr("target",target);
}
var kynm = Object.keys(lprm);
for( var ilop = 0; ilop < kynm.length; ilop++ ) {
$form.append($('<input />').attr("type", "hidden").attr("name", kynm[ilop]).attr("value", lprm[kynm[ilop]]));
}
$form.appendTo("body").submit().remove();
return;
}
};
