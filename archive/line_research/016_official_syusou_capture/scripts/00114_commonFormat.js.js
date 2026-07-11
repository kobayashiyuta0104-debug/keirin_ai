//
var escapeHTML = function (val){
return $("<div/>").text(val).html();
}
function formatDate(val, kbn , opt)
{
var opt = opt||"0";
var optUpd = "1";
var optNow = "2";
var YYYYMMDD = "5"
var MMDD = "7";
var strReturn = "";
if(val.length==8){
if(kbn==MMDD){
var tmp = val.slice(-4);
strReturn = tmp.replace(/(\d\d)(\d\d)/,"$1/$2");
}else if(kbn==YYYYMMDD){
strReturn = val.replace(/(\d{4})(\d\d)(\d\d)/,"$1/$2/$3");
}
if(opt == optUpd){
strReturn += "更新";
}else if (opt == optNow){
strReturn += "現在";
}
}
return strReturn;
}
function formatTime(val, kbn , opt)
{
var kbn = kbn||"9";
var opt = opt||"0";
var optUpd = "1";
var optNow = "2";
var HHMM = "9"
var strReturn = "";
if(kbn==HHMM){
strReturn = val.replace(/.*(\d\d).?(\d\d).?$/,"$1:$2");
}
if(opt == optUpd){
strReturn += "更新";
}else if (opt == optNow){
strReturn += "現在";
}
return strReturn;
}
function formatNum(val)
{
var strReturn = "";
strReturn = (val + '').replace(/(\d)(?=(\d{3})+$)/g,"$1,");
return strReturn;
}
function getNum(strMoney) {
return parseInt(strMoney.replace(/,/g,""), 10);;
}
function formatOzz(val)
{
var strReturn = val + "";
if (strReturn.indexOf(".") == -1){
strReturn = strReturn + '.0';
}
return strReturn;
}
