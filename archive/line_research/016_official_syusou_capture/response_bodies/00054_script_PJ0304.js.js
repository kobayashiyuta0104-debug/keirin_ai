function khShowUriba(linkFuncId, uribaCode, kaisaiDate, prm0304) {
var params = {};
if(linkFuncId == "PPJ0704"){
if(uribaCode){
if(uribaCode.length > 2){
params["jocd"] = uribaCode.substr(0,2);
} else {
params["jocd"] = uribaCode;
}
} else {
params["jocd"] = uribaCode;
}
} else {
params["jocd"] = uribaCode;
}
params["kday"] = kaisaiDate;
params["encp"] = prm0304;
var strUrl = "";
if(linkFuncId == "PPJ0704"){
strUrl = $("#khhdnUrl0704").attr("value");
} else {
strUrl = $("#khhdnUrl0708").attr("value");
}
commonSubmit.formPost(strUrl,　params,　null);
}
