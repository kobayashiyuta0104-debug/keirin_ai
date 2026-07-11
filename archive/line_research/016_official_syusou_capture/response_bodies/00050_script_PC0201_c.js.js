var hhController = {
JSON_REQ_ID: "JSJ001",
init: function() {
},
hhJSONRequest: function(encp) {
var result = null;
var params = {};
params["encp"] = encp;
Com.getRequestGet(hhController.JSON_REQ_ID, params)
.done(function(result) {
hhView.hhDrawJSONData(result, params);
});
},
hhJSONretry: function(cbPrm) {
var result = null;
Com.getRequestGet(hhController.JSON_REQ_ID, cbPrm)
.done(function(result) {
hhView.hhDrawJSONData(result, cbPrm);
});
}
};
