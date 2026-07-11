var ptView = {
HDNKEY_ID: 'ppj9102',
ptDrawJSONData: function(jsondata, params) {
var outHtml=[];
if(!jsondata) {
$('#ptErrmsgArea').removeClass('dispoff');
$('#ptGraphArea').addClass('dispoff');
$('#ptHyoArea').addClass('dispoff');
Com.makePcUpdatePage(
"ptErrmsgArea"
, ""
, params
, function(arg0){
ptController.ptCreateList(arg0);
}
);
}
else if (jsondata.resultCd == -1){
$('#ptErrmsgArea').removeClass('dispoff');
$('#ptGraphArea').addClass('dispoff');
$('#ptHyoArea').addClass('dispoff');
var msg = "";
if(jsondata.message != undefined){
msg = jsondata.message;
}
Com.makePcUpdatePage(
"ptErrmsgArea"
, msg
, params
, function(arg0){
ptController.ptCreateList(arg0);
}
);
}
else{
if(!jsondata.tokutenList || jsondata.dataGetFlg == "false"){
outHtml.push('<div class="midasi1_fsz" style="margin: 10px; padding: 0px; text-align: center;">');
 outHtml.push('<p class="place list-inline">'+jsondata.message+'</p>');
 outHtml.push('</div>');
$('#ptErrmsgArea').html(outHtml.join(""));
$('#ptErrmsgArea').removeClass('dispoff').addClass(jsondata.firstNotFoundColor);
$('#ptGraphArea').addClass('dispoff');
$('#ptHyoArea').addClass('dispoff');
}
else{
var sdate = [];
var joname = [];
var grade = [];
var chokin = [];
var konki = [];
for(var ilop = 0; ilop < jsondata.tokutenList.length; ilop++ ){
sdate.push(jsondata.tokutenList[ilop].kStartDate);
joname.push(jsondata.tokutenList[ilop].keirinjoName);
grade.push(jsondata.tokutenList[ilop].gradeName);
chokin.push(jsondata.tokutenList[ilop].chokinTokuten);
konki.push(jsondata.tokutenList[ilop].konkiTokuten);
}
outHtml.push('<table class="over_kyosotokuten_tbl">');
outHtml.push('<tr>');
outHtml.push('<th style="width:70px">開催初日</th>');
var icount = 0;
for(var ilop = 0; ilop < 10; ilop++ ){
if( ilop < jsondata.tokutenList.length){
var right_line = "";
if ( ilop == 9)
right_line = ' border-right-width: 1px;';
outHtml.push('<th style="width:90px;' + right_line + '">' + sdate[ilop] + '</th>');
} else {
if( icount == 0 ){
outHtml.push('<th class="blank1" style="width:90px">' + '</th>');
icount ++;
} else {
outHtml.push('<th class="blank2" style="width:90px">' + '</th>');
}
}
}
icount = 0;
outHtml.push('</tr><tr>');
outHtml.push('<th>競輪場<br>グレード</th>')
for(var ilop = 0; ilop < 10; ilop++ ){
if( ilop < jsondata.tokutenList.length){
var right_line = "";
if ( ilop == 9)
right_line = ' style = "border-right-width: 1px;"';
outHtml.push('<td class="kn"' + right_line + '>' + joname[ilop] + '<br>' + grade[ilop] + '</td>');
} else {
if( icount == 0 ){
outHtml.push('<td class="blank1">' + '</td>');
icount ++;
} else {
outHtml.push('<td class="blank2">' + '</td>');
}
}
}
icount = 0;
outHtml.push('</tr><tr>');
outHtml.push('<th>直近4ヶ月</th>')
for(var ilop = 0; ilop < 10; ilop++ ){
if( ilop < jsondata.tokutenList.length){
var right_line = "";
if ( ilop == 9)
right_line = ' style = "border-right-width: 1px;"';
outHtml.push('<td class="bold"' + right_line + '>' + chokin[ilop] + '</td>');
} else {
if( icount == 0 ){
outHtml.push('<td class="blank1">' + '</td>');
icount ++;
} else {
outHtml.push('<td class="blank2">' + '</td>');
}
}
}
icount = 0;
outHtml.push('</tr><tr>');
outHtml.push('<th class="bbw1">今期のみ</th>')
for(var ilop = 0; ilop < 10; ilop++ ){
if( ilop < jsondata.tokutenList.length){
var right_line = "";
if ( ilop == 9)
right_line = ' style = "border-right-width: 1px;"';
outHtml.push('<td class="bold bbw1"' + right_line + '>' + konki[ilop] + '</td>');
} else {
if( icount == 0 ){
outHtml.push('<td class="blank1">' + '</td>');
icount ++;
} else {
outHtml.push('<td class="blank2">' + '</td>');
}
}
}
outHtml.push('</tr>');
outHtml.push('</table>');
outHtml.push('<div class="al-r">※ 開催終了時点の平均競走得点を表示しています。</div>');
$('#ptHyoArea').html(outHtml.join(""));
var label=[];
for(var ilop = 0; ilop < 12; ilop++ ){
if(ilop == 0 || ilop == 11){
label[ilop] = "";
}
else{
if(jsondata.tokutenList.length > ilop - 1){
label[ilop] = "";  
}
else{
label[ilop] = "";
}
}
}
var chokinti=[];
for(var ilop = 0; ilop < 12; ilop++ ){
if(ilop == 0 || ilop == 11){
chokinti[ilop] = null;
}
else{
if(jsondata.tokutenList.length > ilop - 1){
if(chokin[ilop - 1] == "-" || chokin[ilop - 1] == "0.0"){
chokinti[ilop] = null;
}
else{
chokinti[ilop] = parseInt(chokin[ilop - 1] * 100.0);
}
}
else{
chokinti[ilop] = null;
}
}
}
var konkiti=[];
for(var ilop = 0; ilop < 12; ilop++ ){
if(ilop == 0 || ilop == 11){
konkiti[ilop] = null;
}
else{
if(jsondata.tokutenList.length > ilop - 1){
if(konki[ilop - 1] == "-" || konki[ilop - 1] == "0.0"){
konkiti[ilop] = null;
}
else{
konkiti[ilop] = parseInt(konki[ilop - 1] * 100.0);
}
}
else{
konkiti[ilop] = null;
}
}
}
var data = {
labels: label,
    datasets: [
        {
            label: "chokin dataset",
            showBaseLineX : false,
            fillColor: "rgba(205,0,0,0)",
            strokeColor: "rgba(205,0,0,1)",
            pointColor: "rgba(205,0,0,1)",
            pointStrokeColor: "rgba(205,0,0,1)",
            pointChangeRect: true,
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: chokinti
        },
        {
            label: "konki dataset",
            showBaseLineX : false,
            fillColor: "rgba(0,125,187,0)",
            strokeColor: "rgba(0,125,187,1)",
            pointColor: "rgba(0,125,187,1)",
            pointStrokeColor: "rgba(0,125,187,1)",
            pointChangeRect: false,
            pointHighlightFill: "#fff",
            pointHighlightStroke: "rgba(220,220,220,1)",
            data: konkiti
        }
    ]
};
var min = 99999;
var max = 0;
for (var i=0; i<2; i++){
for (var j=0; j<data.datasets[i].data.length; j++){
if(data.datasets[i].data[j] != null && data.datasets[i].data[j] > max){
max = data.datasets[i].data[j];
}
}
}
for (var i=0; i<2; i++){
for (var j=0; j<data.datasets[i].data.length; j++){
if(data.datasets[i].data[j] != null && data.datasets[i].data[j] < min){
min = data.datasets[i].data[j];
}
}
}
if( min > max ){ min = 0; max =0; }
var scalemin = Math.floor(min) - Math.floor(min)%500;
var scalemax = Math.floor(max) - Math.floor(max)%500 + 500;
var haba = (scalemax - scalemin)/5;
var options = {
         showTooltips : false,
    scaleOverlay : true,
    scaleOverride : true,
    scaleSteps : 5,
    scaleStepWidth : haba,
    scaleStartValue : scalemin,
    scaleLineColor : "rgba(0, 0, 0, 1)",
    scaleLineWidth : 1,
    scaleShowLabels : true,
    scaleLabel : "<%=parseInt(value/100)%>.00",
    scaleFontFamily : "'メイリオ'",
    scaleFontSize : 16,
    scaleFontStyle : "normal",
    scaleFontColor : "#666",    
    scaleShowGridLines : true,
    scaleGridLineColor : "rgba(0, 0, 0, .5)",
    scaleGridLineWidth : 1,
    scaleShowVerticalLines : false,
    bezierCurve : false,
    pointDot : true,
    pointDotRadius : 5,
    pointDotStrokeWidth : 1,
    datasetStroke : true,
    datasetStrokeWidth : 3,
    datasetFill : false,
    animation : false,
    animationSteps : 60,
    animationEasing : "easeOutQuad",
}
document.getElementById("canvas_tokuten").width = 970;
document.getElementById("canvas_tokuten").height = 455;
document.getElementById("canvas_tokuten").getContext("2d").clearRect(0, 0, 970, 455);
var myLineChart = new Chart(document.getElementById("canvas_tokuten").getContext("2d"));
myLineChart.Line(data, options);
$('#ptErrmsgArea').addClass('dispoff');
$('#ptGraphArea').removeClass('dispoff');
$('#ptHyoArea').removeClass('dispoff');
}
}
}
};
