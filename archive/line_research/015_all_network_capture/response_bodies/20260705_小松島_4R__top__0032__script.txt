var PJ0101Controller = {
JSON_REQ_ID_KAISAI: "JSJ057",
JSON_REQ_ID_TOPICS: "JSJ078",
JSON_REQ_ID_OSHIRASE: "JSJ079",
JSON_REQ_ID_PICKUP: "JSJ080",
JSON_REQ_ID_ITIOSHI: "JSJ081",
JSON_REQ_ID_DOKANTO: "JSJ082",
reqKaisaiInfo: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['kday'] = prm;
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_KAISAI, params)
.done(function(result) {
PJ0101View.cDrawJSONData(result, prm);
}).always(function() {
PJ0101Controller.reqDokantoInfo(prm);
});
},
reqTopicsInfo: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['ctgy'] = prm;
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_TOPICS, params)
.done(function(result) {
PJ0101View.bclDrawJSONData(result, prm);
});
},
reqOshiraseInfo: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['tiku'] = prm;
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_OSHIRASE, params)
.done(function(result) {
PJ0101View.bcrDrawJSONData(result, prm);
});
},
reqPickupInfo: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['kday'] = prm;
params['mkbn'] = 1; 
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_PICKUP, params)
.done(function(result) {
PJ0101View.clDrawJSONData(result, prm);
});
},
reqItiosiInfo: function(prm,more) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['kday'] = prm;
params['more'] = more;
params['mkbn'] = 1; 
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_ITIOSHI, params)
.done(function(result) {
PJ0101View.brDrawJSONData(result, prm);
});
},
reqDokantoInfo: function(prm) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['kday'] = prm;
}
Com.getRequestGet(PJ0101Controller.JSON_REQ_ID_DOKANTO, params)
.done(function(result) {
PJ0101View.tlDrawJSONData(result, prm);
});
}
};
