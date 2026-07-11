var PJ9110Controller = {
JSON_REQ_ID: "JSJ075",
reqTanpyoTenkai: function(prm, thinFlg) {
var result = null;
var params = {};
if(typeof(prm) == 'object'){
params = prm;
}else{
params['encp'] = prm;
if (thinFlg != undefined){
params['thin'] = thinFlg;
}
}
commonLoad.loadingImage("true"); 
Com.getRequestGet(PJ9110Controller.JSON_REQ_ID, params)
.done(function(result) {
PJ9110View.piDrawJSONData(result, prm);
commonLoad.loadingImage("false");
$('#tanten_ari').dialog( 'open' );
});
},
};
