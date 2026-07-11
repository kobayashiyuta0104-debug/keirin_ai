var Controller = {
JSON_REQ_ID: "JSJ014",
raceProgramList: function(enprm) {
var result = null;
var params = {};
params["encp"] = enprm;
Com.getRequestGet(Controller.JSON_REQ_ID, params)
.done(function(result) {
PJ0301View.shDrawJSONData(result);
});
}
};
$(document).on("click","#datasetDiv a",function(){
var parent = $(this).parent();
if(!(parent.hasClass("shoukinListtd") || parent.hasClass("gaiteiListtd"))){
var children = $(parent).children();
var action = $(children[1]).attr("value");
var params = {};
params["encp"] = $(children[2]).attr("value");
var dispDI = $(children[3]).attr("value");
if(dispDI == 1){
dispDI="PJ0315";
}else if(dispDI == 2){
dispDI="PJ0326";
}
params["disp"] = dispDI
commonSubmit.formPost(action,params);
}
});
