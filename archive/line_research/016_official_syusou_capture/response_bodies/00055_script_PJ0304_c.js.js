var khController = {
    JSON_REQ_ID: "JSJ016",
    khCreateList: function( params) {
        Com.getRequestGet(khController.JSON_REQ_ID, params)
            .done(function(result) {
            khView.khDrawJSONData(result, params);
            });
    }
};
