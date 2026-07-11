var PC0101Controller = {
JSON_REQ_ID: "JSJ048",
init: function() {
},
shGetJsonRequestParameter: function(dispID){
var params = {};
params["kaisaibikbn"] = $("[id=sh_hidden2]").attr("value");
params["kanyusyaflg"] = $("[id=sh_hidden1]").attr("value");
params["shccp"] = $("[id=shCcp]").attr("value");
if (dispID == undefined){
params["dispid"] =$("[id=shCurrentDisp]").attr("value");
} else {
params["dispid"] = dispID;
}
return params;
},
chgCommonHeader:function(dispid){
var pc0101_json0 =$("[id=sh_hidden2]").attr("value");
var pc0101_json1 =$("[id=sh_hidden1]").attr("value");
var shccp = $("[id=shCcp]").attr("value");
PC0101Controller.jsj048JSONRequest(pc0101_json0,pc0101_json1, dispid, shccp);
},
chgRaceList: function(kaisabikbn, kanyusyaflg, dispid, shccp) {
commonLoad.loadingImage("true");
PC0101Controller.jsj048JSONRequest(kaisabikbn,kanyusyaflg,dispid,shccp);
},
jsj048JSONRequest: function(kaisabikbn, kanyusyaflg, dspid, shccp){
var result = null;
var params = {};
params["kaisaibikbn"] = kaisabikbn;
params["kanyusyaflg"] = kanyusyaflg;
params["dispid"] = dspid;
params["shccp"] = shccp;
Com.getRequestGet(PC0101Controller.JSON_REQ_ID, params)
.done(function(result) {
PC0101View.shDrawJSONData(result,params);
}).fail(function() {
PC0101View.shDrawJSONData(null,params);
});
}
};
