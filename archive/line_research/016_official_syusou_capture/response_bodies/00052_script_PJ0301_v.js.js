var PJ0301View = {
HDNKEY_ID: 'pPJ0301',
shDrawJSONData: function(jsondata) {
var outHtml=[];
var outHtml2=[];
var stroutHtml;
var $result = $('#hcomRaceDiv'), n=3000;
var $noRaceresult = $('#hcomnoRaceMsg'), n=3000;
var current;
if ( !jsondata ) {
Com.viewErrorPage(null);
} else if ( jsondata.resultCd == -1 ) {
var messageCd = "";
if( jsondata.messageCd != undefined ) {
messageCd = jsondata.messageCd;
}
Com.viewErrorPage(messageCd);
} else {
var setDataDiv = $('#datasetDiv');
var makediv = "";
var makeTable = "";
var makeRaceNoTr = "";
var makeEventTr = "";
var makeTb = "";
    var colcount = 0;
setDataDiv.empty();
setDataDiv.append(
$('<div>').addClass("mardivtop").append(
$('<p>').addClass("midasi1_fsz").append("レースプログラム")
).append(
$('<p>').addClass("al-r").append(jsondata.strUPDATE)
)
);
for(var loopDay = 0; loopDay < jsondata.raceDayDataList.length; loopDay++){
makediv = $('<div>');
makeTable = $('<table>');
makeTbody = $('<tbody>');
makeRaceNoTr = $('<tr>');
makeEventTr = $('<tr>');
colcount = 0;
var raceDayData = jsondata.raceDayDataList[loopDay];
if(raceDayData.strKaisaiFlg == 8){
makediv = $('<div>');
makediv.append(
$('<table>').addClass("mardivtop tablhei al-c nodata w100pc").append(
$('<tbody>').append(
$('<tr>').append(
$('<td>').addClass("v-al-m nb-a").append(
raceDayData.strMes)
)
)
)
);
setDataDiv.append(makediv);
} else {
makediv.addClass("mardivtop").append(
$('<p>').addClass("dispib midasi2_fsz").append(raceDayData.strRaceNitiji)
);
makeRaceNoTr.addClass("tbl_header");
for(var loopRaceNo = 0; loopRaceNo < raceDayData.raceNoDataList.length; loopRaceNo++){
makeTb = $('<td>');
if(raceDayData.raceNoDataList[loopRaceNo].strRaceNoLnk == ""){
makeTb.append(
raceDayData.raceNoDataList[loopRaceNo].strRaceNo);
}else{
makeTb.append(
$('<a>').addClass("txt_underline bold").append(
raceDayData.raceNoDataList[loopRaceNo].strRaceNo
)
);
makeTb.append(
$('<input>').attr("type","hidden").attr("value",raceDayData.raceNoDataList[loopRaceNo].strRaceNoLnk)
);
makeTb.append(
$('<input>').attr("type","hidden").attr("value",raceDayData.raceNoDataList[loopRaceNo].strLnkPrm)
);
makeTb.append(
$('<input>').attr("type","hidden").attr("value",raceDayData.raceNoDataList[loopRaceNo].strLnkKBn)
);
}
makeRaceNoTr.append(makeTb);
}
for(var loopRaceEvent = 0; loopRaceEvent < raceDayData.raceEventDataList.length; loopRaceEvent++){
makeTb = $('<td>');
makeTb.addClass(raceDayData.raceEventDataList[loopRaceEvent].strRaceEventColor)
.attr("colspan",raceDayData.raceEventDataList[loopRaceEvent].strColspan)
.append(
$('<span>').append(
raceDayData.raceEventDataList[loopRaceEvent].strRaceEvent
)
);
makeEventTr.append(makeTb);
colcount = colcount + Number(raceDayData.raceEventDataList[loopRaceEvent].strColspan);
}
if(colcount < raceDayData.raceNoDataList.length){
for(var i = colcount;i <= raceDayData.raceNoDataList.length;i++){
makeEventTr.append($('<td>').append('&nbsp;'));
}
}
makeTable.addClass("w100pc al-c tablhei").append(
makeTbody.append(makeRaceNoTr)
.append(makeEventTr)
);
makediv.append(makeTable);
setDataDiv.append(makediv);
if(raceDayData.strKaisaiFlg == 1){
makediv = $('<div>');
makediv.append(
$('<table>').addClass("mardivtop tablhei al-c nodata w100pc").append(
$('<tbody>').append(
$('<tr>').append(
$('<td>').addClass("v-al-m nb-a").append(
raceDayData.strMes)
)
)
)
);
setDataDiv.append(makediv);
}
}
}
var makeGaiteitbody = $('<tbody>');
var makeGaiteiNameTb = "";
var makeSyokinTb = "";
var makeGaiteiListTb = "";
var makeAtag = "";
var makebtn = "";
if(jsondata.strgaiteiDispFlg != 1){
for(var loopGaitei = 0; loopGaitei < jsondata.gaiteiInfoList.length; loopGaitei++){
var gaiteData = jsondata.gaiteiInfoList[loopGaitei];
makeGaiteiNameTb = $('<td>');
makeGaiteiNameTb.addClass("gaiteiNametd").append(gaiteData.strGaiteiName)
makebtn = $('<button>');
makebtn.addClass("w100pc btn btn_fsz onbtn shoukinbtn").attr("type","button").append(gaiteData.strPDFName1);
makeSyokinTb = $('<td>');
makeSyokinTb.addClass("shoukinListtd")
if(gaiteData.strdispClass1 == ""){
makeAtag = $('<a>');
makeAtag.attr({
href:gaiteData.strPDFPath1,
target:"_blank"
}).append(makebtn);
makeSyokinTb.append(makeAtag);
}else{
makeSyokinTb.addClass(gaiteData.strdispClass1);
makeSyokinTb.append(makebtn);
}
makebtn = $('<button>');
makebtn.addClass("w100pc btn btn_fsz onbtn gaitebangumi").attr("type","button").append(gaiteData.strPDFName2)
makeGaiteiListTb = $('<td>');
makeGaiteiListTb.addClass("gaiteiListtd")
if(gaiteData.strdispClass2 == ""){
makeAtag = $('<a>');
makeAtag.attr({
href:gaiteData.strPDFPath2,
target:"_blank"
}).append(makebtn);
makeGaiteiListTb.append(makeAtag);
}else{
makeGaiteiListTb.addClass(gaiteData.strdispClass2);
makeGaiteiListTb.append(makebtn);
}
makeGaiteitbody.append(
$('<tr>').append(
makeGaiteiNameTb).append(
makeSyokinTb).append(
makeGaiteiListTb)
);
}
setDataDiv.append(
$('<div>').addClass("gaiteidiv").append(
$('<table>').addClass("w100pc").append(
makeGaiteitbody)
).append('<div class="al-r mesdiv">上記情報はPDFで表示されます。</div>')
);
}
}
return;
}
};
