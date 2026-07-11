var ptController = {
JSON_REQ_ID: "JSJ067",
ptCreateList: function(params) {
commonLoad.loadingImage("true");
        Com.getRequestGet(ptController.JSON_REQ_ID, params)
            .done(function(result) {
                ptView.ptDrawJSONData(result, params);
commonLoad.loadingImage("false");
$('#over_kyosotokuten').dialog( 'open' );
            });
    }
};
