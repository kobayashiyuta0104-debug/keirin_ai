var _config = {
ajaxCfg: {
url: location.protocol + '//' + location.host + '/' + $($('script[src$="commonJSON.js"]')[0]).attr('src').split('/')[1] + '/json',
crossDomain: true
}
};
function createAnalyzeInfo(jsonType) {
var targetJsonType = jsonType;
var targetAnaUri = window.location.href;
if("anaOddsType" in window) {
if(anaOddsType != "") {
targetJsonType = anaOddsType;
}
}
if("anaUri" in window) {
targetAnaUri = anaUri;
}
return {
"X-KEIRINJP-ANA-SCREEN"    : screen.width+"x"+screen.height,
"X-KEIRINJP-ANA-URI"       : targetAnaUri,
"X-KEIRINJP-ANA-JSONTYPE"  : targetJsonType
};
};
(function($, config, undefined) {
'use strict';
var _self = this;
var options = {
fireTapThreshold: 850,
touchMovingThreshold: 9,
cookiePath: '/',
cookieExpires: 60 * 60 * 24 * 365,
cssHide: 'mfp-hide',
cssActive: 'active',
cssDisabled: 'disabled',
ajaxCfg: {
timeout: 10000,
url: location.protocol + '//' + location.host + '/' + $($('script[src$="commonJSON.js"]')[0]).attr('src').split('/')[1] + '/json',
type: 'post',
async: true,
statusCode: {
},
beforeSend: function(xhr) {
xhr.setRequestHeader("If-Modified-Since", "Thu, 01 Jun 1970 00:00:00 GMT");
}
},
ajaxCfgG: {
timeout: 10000,
url: location.protocol + '//' + location.host + '/' + $($('script[src$="commonJSON.js"]')[0]).attr('src').split('/')[1] + '/json',
type: 'get',
async: true,
statusCode: {
},
beforeSend: function(xhr) {
}
},
ajaxCfgAna: {
timeout: 10000,
url: location.protocol + '//' + location.host + '/' + $($('script[src$="commonJSON.js"]')[0]).attr('src').split('/')[1] + '/ana',
type: 'get',
async: true,
statusCode: {
},
beforeSend: function(xhr) {
}
}
};
var prmSet = {};
var isProcessed = false;
var isConnected = false;
var cfg = $.extend(true, {}, options, config);
$.ajaxSetup(cfg.ajaxCfg);
$.extend($.support, {
touch: "ontouchend" in document,
androidVersion: navigator.userAgent.indexOf('Android') > 0
? parseFloat(navigator.userAgent.slice(navigator.userAgent.indexOf('Android') + 8))
: 999
});
var com = {
emptyErrMsg: '情報を取得できませんでした。',
pcErrUrl: '/pc/pc/error',
spErrUrl: '/pc/sp/error',
EVENTS: {
REQUEST_START: 'communicate_on',
REQUEST_SUCCESS: 'communicate_success',
REQUEST_FAIL: 'communicate_fail',
REQUEST_END: 'communicate_off'
},
getRequest: function(reqType, para) {
return com.getRequestMain(reqType, para,false);
},
getRequestGet: function(reqType, para) {
return com.getRequestMain(reqType, para,true);
},
getRequestMain: function(reqType, para, flgType) {
if(flgType) {
$.ajaxSetup(cfg.ajaxCfgG);
} else {
$.ajaxSetup(cfg.ajaxCfg);
}
var $html = $('html'),
params = para;
isConnected = true;
$html.trigger(com.EVENTS.REQUEST_START);
params.type = reqType;
return $.Deferred(function(defer) {
$.ajax({ data: params, dataType: 'json' })
.done(function(result, status, xhr) {
if( result.resultCd == -2 ) {
com.viewErrorPage(null);
} else {
defer.resolve(result);
if(result.writeANA) {
$.ajaxSetup(cfg.ajaxCfgAna);
$.ajax({headers: createAnalyzeInfo(reqType)});
if("anaOddsType" in window) {
anaOddsType = "";
}
}
$html.trigger(com.EVENTS.REQUEST_SUCCESS, result);
}
}).fail(function(xhr, status, error) {
if (status == 'timeout') {
defer.resolve(null);
} else {
defer.reject(null, status, error, xhr.responseText);
}
$html.trigger(com.EVENTS.REQUEST_FAIL, xhr);
}).always(function() {
isConnected = false;
isProcessed = false;
$html.trigger(com.EVENTS.REQUEST_END);
});
defer.fail(com.requestErrorView);
}).promise();
},
viewErrorPage: function(errprm) {
var pnm = location.pathname,
errpath = com.pcErrUrl,
errurl = location.protocol + '//' + location.host;
if( pnm.indexOf("/sp/") != -1 ) {
errpath = com.spErrUrl;
}
if( errpath.split('/')[1] == errpath.split('/')[2] ) {
errpath = errpath.slice(('/'+errpath.split('/')[1]).length);
}
errurl = errurl + errpath;
if( errprm ) {
errurl = errurl + "?PRM=" + errprm;
}
location.href = errurl;
},
makePcUpdatePage: function(errDivId, errmsg, reqprm, cbfunc) {
var btnid=errDivId+"RetryBtn";
prmSet[btnid] = reqprm;
$('#'+errDivId).empty();
$('#'+errDivId).addClass('al-c')
.append($('<span />').addClass('error_msg_fsz').append(!errmsg ? com.emptyErrMsg : errmsg))
.append($('<br />'))
.append($('<button />').addClass('btn onbtn jupdbtn').attr('id',btnid).append('更　新'));
$('button[id='+btnid+']').on('click',function(arg){cbfunc(prmSet[(this.id)]);});
},
makeSpUpdatePage: function(errDivId, errmsg, reqprm, cbfunc) {
var btnid=errDivId+"RetryBtn";
prmSet[btnid] = reqprm;
$('#'+errDivId).empty();
$('#'+errDivId).addClass('al-c')
.append($('<span />').addClass('error_msg_fsz').append(!errmsg ? com.emptyErrMsg : errmsg))
.append($('<br />'))
.append($('<button />').addClass('btn onbtn jupdbtn').attr('id',btnid).append('更　新'));
$('button[id='+btnid+']').on('click',function(arg){cbfunc(prmSet[(this.id)]);});
},
requestErrorView: function(result, status, error, responseText) {
setTimeout(function() {
$(window).off();
$(document).off();
$('html,body').off();
try {
Com = jQuery = $ = null;
delete window.Com;
delete window.$;
delete window.jQuery;
} catch(e){}
var newDoc = document.open('text/html', 'replace');
newDoc.write(responseText);
newDoc.close();
}, 100);
}
};
$(function() {
var $html = $('html'),
$body = $('body');
$html.on(com.EVENTS.REQUEST_END, function() {
});
$html.on(com.EVENTS.REQUEST_SUCCESS, function(event, result) {
});
});
_self.Com = com;
}).call(this, jQuery, _config);
