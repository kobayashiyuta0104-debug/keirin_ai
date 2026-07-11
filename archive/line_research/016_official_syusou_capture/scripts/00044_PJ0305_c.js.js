var slController = {
JSON_REQ_ID: "JSJ017",
reqSyusoList: function(prm) {
var result = null;
var params = {};
params[Com.COM_CONST.ENCRYPTION] = prm;
Com.getRequestGet(slController.JSON_REQ_ID, params)
.done(function(result) {
slView.slDrawJSONData(result);
});
}
};
