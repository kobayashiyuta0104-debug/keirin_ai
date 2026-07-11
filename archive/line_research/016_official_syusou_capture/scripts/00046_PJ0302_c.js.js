var syController = {
JSON_REQ_ID: "JSJ015",
init: function() {
},
syJSONRequest: function(encp) {
var result = null;
var params = {};
params["encp"] = encp;
Com.getRequestGet(cController.JSON_REQ_ID, params)
.done(function(result) {
syView.syDrawJSONData(result, params);
});
},
syJSONretry: function(cbPrm) {
var result = null;
Com.getRequestGet(cController.JSON_REQ_ID, cbPrm)
.done(function(result) {
syView.syDrawJSONData(result, cbPrm);
});
}
};
