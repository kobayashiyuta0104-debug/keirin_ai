var reActDispID = "";
var reActParam = "";
var gReqDispID = "";
function switchDisplay(){
var dispIDs = ['PJ0301', 'PJ0302', 'PJ0304', 'PJ0305', 'PJ0306' ]; 
var dispDivIDs = ['#PJ0301', '#PJ0302', '#PJ0304', '#PJ0305', '#PJ0306']; 
for (var i = 0; i < dispIDs.length; i++) {
if (dispIDs[i] == displayingId){
$(dispDivIDs[i]).removeClass('dispoff');
$(dispDivIDs[i]).addClass('dispon');
}else{
$(dispDivIDs[i]).removeClass('dispon');
$(dispDivIDs[i]).addClass('dispoff');
}
}
}
function buttonMarker(){
var kbn=0;
switch (displayingId) {
case 'PJ0301': kbn=1; break;
case 'PJ0302': kbn=2; break;
case 'PJ0304': kbn=3; break;
case 'PJ0305': kbn=4; break;
case 'PJ0306': kbn=5; break;
default: return;
}
hhChgActiveBtn(kbn);
}
function dateReflection(){
callDrawFunction('PC0201');
callDrawFunction(displayingId);
callDrawFunction('PC0101');
delete jsonData['PC0201'];
delete jsonData[displayingId];
delete jsonData['PC0101'];
buttonMarker();
}
function update(dispID, param){
gReqDispID = dispID;
commonLoad.loadingImage('true');
var reqPrms = {};
reqPrms['PC0101'] = PC0101Controller.shGetJsonRequestParameter(dispID);
reqPrms['PC0201'] = param;
if (dispID != 'PJ0306'){
reqPrms[dispID] = param;
}
$.when(jsonRequest(reqPrms))
.done(function(){
if (dispID == 'PJ0306'){
if (jsonData['PC0201'].C0201data.flgActvKekkaList){
update_main('PJ0306',param);
} else {
update_main('PJ0305',param);
}
 } else {
if(gReqDispID != displayingId){
displayingId = gReqDispID;
switchDisplay();
}
dateReflection();
commonLoad.loadingImage('false');
}
})
.fail(function(){
commonLoad.loadingImage('false');
});
} 
function update_main(dispId,param){
var reqPrms = {};
gReqDispID = dispId;
reqPrms[dispId] = param;
$.when(jsonRequest(reqPrms))
.done(function(){
if(gReqDispID != displayingId){
displayingId = gReqDispID;
switchDisplay();
}
dateReflection();
})
.always(function(){
commonLoad.loadingImage('false');
});
} 
function btnClickOfFrame(dispID, param){
reActDispID = dispID;
reActParam = param;
update(reActDispID, reActParam);
}
function btnKaisaiDateClick(){
reActDispID = displayingId;
reActParam = ""; 
update(reActDispID, reActParam);
}
function btnRaceNoClick(raceno){
commonLoad.loadingImage(true);
commonSubmit.formPost($('#slRaceBasicInfoURL').val(), { 'disp' : 'PJ0315', 'encp' : hhGetEncSelRList(raceno) }, "_self");
}
function jsonRequest(params){
var dispIDs = []; 
var reqPromises = []; 
for (var key in params) {
dispIDs.push(key);
var reqID = getReqID(key);
reqPromises.push(Com.getRequestGet(reqID, params[key]));
}
var d = new $.Deferred();
$.when.apply(null, reqPromises)
.done(function () {
for (var i = 0; i < arguments.length; i++) {
jsonData[dispIDs[i]] = arguments[i];
}
d.resolve();
})
.fail(function(){
d.reject();
});
    return d.promise();
}
function callDrawFunction(funcID){
var helpUrl;
switch (funcID) {
case 'PJ0301':
PJ0301View.shDrawJSONData(jsonData[funcID]);
helpUrl = $('#slHelpUrlPj0301').attr("value");
$('#sfHdnLink_0').attr("value",helpUrl);
$('#slBreadCrumbID').attr("value","PJ0301");
break;
case 'PJ0302':
syView.syDrawJSONData(jsonData[funcID],jsonData[funcID].reqprm);
helpUrl = $('#slHelpUrlPj0302').attr("value");
$('#sfHdnLink_0').attr("value",helpUrl);
$('#slBreadCrumbID').attr("value","PJ0302");
break;
case 'PJ0304':
khView.khDrawJSONData(jsonData[funcID]);
helpUrl = $('#slHelpUrlPj0304').attr("value");
$('#sfHdnLink_0').attr("value",helpUrl);
$('#slBreadCrumbID').attr("value","PJ0304");
break;
case 'PJ0305':
slView.slDrawJSONData(jsonData[funcID]);
helpUrl = $('#slHelpUrlPj0305').attr("value");
$('#sfHdnLink_0').attr("value",helpUrl);
$('#slBreadCrumbID').attr("value","PJ0305");
break;
case 'PJ0306':
klView.klDrawJSONData(jsonData[funcID]);
helpUrl = $('#slHelpUrlPj0306').attr("value");
$('#sfHdnLink_0').attr("value",helpUrl);
$('#slBreadCrumbID').attr("value","PJ0306");
break;
case 'PC0201':
hhView.hhDrawJSONData(jsonData[funcID],jsonData[funcID].reqprm);
break;
case 'PC0101':
PC0101View.shDrawJSONData(jsonData[funcID]);
break;
default:
break;
}
}
function getReqID(dispID){
switch (dispID) {
case 'PJ0301':
return 'JSJ014';
break;
case 'PJ0302':
return syController.JSON_REQ_ID;
break;
case 'PJ0304':
return khController.JSON_REQ_ID;
break;
case 'PJ0305':
return slController.JSON_REQ_ID;
break;
case 'PJ0306':
return klController.JSON_REQ_ID;
break;
case 'PC0201':
return hhController.JSON_REQ_ID;
break;
case 'PC0101':
return PC0101Controller.JSON_REQ_ID;
break;
default:
return '';
break;
}
}
$(document).ready(function() {
switchDisplay();
switch (displayingId) {
case 'PJ0301':
case 'PJ0302':
case 'PJ0304':
hhChgPattern(1);
break;
default:
hhChgPattern(2);
break;
}
dateReflection();
buttonMarker();
});
