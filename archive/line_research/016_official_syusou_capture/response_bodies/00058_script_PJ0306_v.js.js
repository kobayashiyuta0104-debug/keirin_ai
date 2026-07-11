var klView = {
    HDNKEY_ID: 'JSJ018',
    klDrawJSONData: function(PJ0306JSONData) {
    try{
var result = $("#raceresult");
    if( PJ0306JSONData == "exception" ) {
Com.viewErrorPage(null);
    } else if( !PJ0306JSONData ) {
Com.viewErrorPage(null);
    } else if( PJ0306JSONData.resultCd == -1 ) {
Com.viewErrorPage(null);
    } else if( PJ0306JSONData.resultCd == -2 ) {
Com.viewErrorPage(null);
    } else {
    result.empty();
var tmpHtml = "";
var tmpFlg = "";
result.append($("<table>").attr("id","bctblTitle").addClass("w100pc").append($("<tbody>").append($("<tr>").append($("<th>").append("結果一覧").addClass("midasi1_fsz v-al-t").attr("colspan","5")))));
if(PJ0306JSONData.ctlblScreenMegFlg == 1){
tmpHtml = $("<div>").addClass(PJ0306JSONData.screenMegColor + " msg_table")
  .append($("<div>").addClass("al-c msg_cell").append(PJ0306JSONData.ctlblScreenMeg));
result.append(tmpHtml);
if(PJ0306JSONData.ctlblPostMeg){
tmpHtml = $("<div>").addClass("al-c bold").append(PJ0306JSONData.ctlblPostMeg);
result.append(tmpHtml);
}
result.append($("<br />"));
}
tmpFlg = 0;
if(PJ0306JSONData.resultList.length != 0 ){
if(PJ0306JSONData.resultList.length == 1){
if(PJ0306JSONData.resultList[0].rclblRaceNo){
tmpFlg = 1;
}
} else {
tmpFlg = 1;
}
if(tmpFlg == 1){
    $("#bctblTitle tr").append($("<td>").addClass("al-r").attr("colspan","14")
    .append($("<div>").append("連続再生にチェックを入れて「ダイジェスト連続」ボタン(画面下部)を押してください。"))
    .append($("<div>").append(PJ0306JSONData.ctlblResultUpdate))
    );
    result.append(bcCreatebctblResule(PJ0306JSONData));
}
if(PJ0306JSONData.kessyaFlg == 1){
result.append(bcCreatebctblKessya(PJ0306JSONData,0));
}
var DokantoData = PJ0306JSONData.dokantoList;
    if(0 < DokantoData.dispDokantoFlg){
    tmpHtml = $("<table>");
    tmpHtml.addClass("dokanto spacerm").append($("<tbody>")
    .append($("<tr>")
    .append($("<td>").addClass("midasi2_fsz al-l v-al-t").append("Dokanto!レース結果"))
    .append($("<td>").addClass("al-r").append($("<a>").attr("href",DokantoData.oldDokantoUrl)
    .append($("<button>").addClass("btn onbtn").attr({
    id:"oldDokanto",
    type:"button"
    }).append("過去のDokanto!結果一覧"))
    )
    ))
    .append($("<tr>")
    .append($("<td>").addClass("al-r").attr("colspan","2").append(DokantoData.cblblDokantoUpdate))
    )
    );
    result.append(tmpHtml);
    if(PJ0306JSONData.dokantoList.dokantoMsgFlg == 1){
    tmpHtml = $("<div>").addClass(PJ0306JSONData.screenMegColor + " msg_table")
      .append($("<div>").addClass("al-c msg_cell").append(DokantoData.dokantomsg));
    result.append(tmpHtml);
    }
    result.append(bcCreatetblRaceResuleDokanto(DokantoData));
    if(DokantoData.dispBetFlg == 1){
    result.append("<br />")
        result.append($("<div>").addClass("clear-fix pt1")
        .append(bcCreatetblRaceBetDokanto(DokantoData))
        .append(bcCreatetblDokantoTotalmoney(DokantoData))
        ); 
    }
    if(DokantoData.dispDokantoFlg == 2){   
    if(DokantoData.dokanto7NokorimeList && DokantoData.dokanto7NokorimeList.length != 0){
    if(DokantoData.dokanto7NokorimeList.length == 1){
    result.append("<br />");
    result.append(bcCreatetblNokorimeDokanto(DokantoData.dokanto7NokorimeList[0],DokantoData.dokanto7Color,0,0));
    } else {
    for(var i= 0;i < DokantoData.dokanto7NokorimeList.length;i++){
    result.append("<br />");
    result.append(bcCreatetblNokorimeDokanto(DokantoData.dokanto7NokorimeList[i],DokantoData.dokanto7Color,0,1));
    }
    }
    }
    if(DokantoData.dokanto4NokorimeList && DokantoData.dokanto4NokorimeList.length != 0){
      if(DokantoData.dokanto4NokorimeList.length == 1){
    result.append("<br />");
    result.append(bcCreatetblNokorimeDokanto(DokantoData.dokanto4NokorimeList[0],DokantoData.dokanto4twoColor,1,0));
    } else {
    for(var i= 0;i < DokantoData.dokanto4NokorimeList.length;i++){
    result.append("<br />");
    result.append(bcCreatetblNokorimeDokanto(DokantoData.dokanto4NokorimeList[i],DokantoData.dokanto4twoColor,1,1));
    }
    }
    }
    }
    if(DokantoData.dispDokantoFlg == 3){
    if(DokantoData.dispDokanto7Flg == 1 || DokantoData.dispDokanto4Flg == 1){
    result.append("<br />")
    }
    if(DokantoData.dispDokanto7Flg == 1 && DokantoData.dispDokanto4Flg == 1){
        result.append($("<table>").addClass("wsize_90p").append($("<tr>")
            .append($("<td>").addClass("wsize_45p v-al-t").append(bcCreatetblResuleDokanto(DokantoData.dokanto7ResulteList,DokantoData.dokanto7Color,0)))
            .append($("<td>").append("&nbsp;"))
            .append($("<td>").addClass("wsize_45p v-al-t").append(bcCreatetblResuleDokanto(DokantoData.dokanto4ResulteList,DokantoData.dokanto4twoColor,1)))
            ));
    } else if(DokantoData.dispDokanto7Flg == 0 && DokantoData.dispDokanto4Flg == 1){
        result.append($("<table>").addClass("wsize_90p").append($("<tr>")
            .append($("<td>").addClass("wsize_45p v-al-t").append(bcCreatetblResuleDokanto(DokantoData.dokanto4ResulteList,DokantoData.dokanto4twoColor,1)))
            .append($("<td>").append("&nbsp;"))
            .append($("<td>").addClass("wsize_45p v-al-t").append("&nbsp;"))
            ));
    } else if(DokantoData.dispDokanto7Flg == 1 && DokantoData.dispDokanto4Flg == 0){
        result.append($("<table>").addClass("wsize_90p").append($("<tr>")
            .append($("<td>").addClass("wsize_45p v-al-t").append(bcCreatetblResuleDokanto(DokantoData.dokanto7ResulteList,DokantoData.dokanto7Color,0)))
            .append($("<td>").append("&nbsp;"))
            .append($("<td>").addClass("wsize_45p v-al-t").append("&nbsp;"))
            ));
    }
    }
    if(PJ0306JSONData.kessyaDokantoFlg == 1){
    result.append(bcCreatebctblKessya(PJ0306JSONData,1));
    }
    }
    result.append($("<input>").attr({
    type: "hidden",
    id: "hdnRaceRVURL",
    value:PJ0306JSONData.raceRVURL
    }));
    result.append($("<input>").attr({
    type: "hidden",
    id: "hdnRacedigestURL",
    value:PJ0306JSONData.raceDigestURL
    }));
    result.append($("<input>").attr({
    type: "hidden",
    id: "hdnklKday",
    value:PJ0306JSONData.kday
    }));
    result.append($("<input>").attr({
    type: "hidden",
    id: "hdnklBkcd",
    value:PJ0306JSONData.bkcd
    }));
    }
    }
    $('#FPJ0305_dlg_msg').empty();
$('#FPJ0305_dlg_msg').append($('<span />').append(PJ0306JSONData.dialogMsg));
    $("html").trigger("JsonEndEvent");
        }catch(e){
        $("html").trigger("JsonEndEvent");
        }
    }
};
function bcCreatebctblResule(JsonData){
var tblHtml = $("<table>");
var theadHtml = $("<tr>");
var tbodyHtml = $("<tbody>").addClass("altertable");
var tbodytrHtml = $("<tr>");
var tmpHtml = "";
var RaceResult ="";
var tempList ="";
var DigestFlg = false;
var DigestPath = JsonData.digestPath;
var DigestName = unsanitaiz(JsonData.digestName);
tblHtml.attr("id","bctblResul").addClass("w100pc");
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdRaceHead").append("レース"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdSyumokuHead").append("種目"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdFristHead").append("1着"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdScondHead").append("2着"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdThirdHead").append("3着"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctd2syaHead").append("2車単"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctd3renHead").append("3連単"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdResultHead").append("結果"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdReproHead")
.append($("<div>").append("連続<br/>再生"))
.append($("<button>").attr({
id:"bcbtnAllCheck",
type:"button"
}).addClass("btn onbtn v-al-b").append("全"))
);
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").attr("id","bctdDigestHead").append("ダイジェスト"));
tblHtml.append($("<thead>").append(theadHtml));
tbodyHtml.addClass("altertable");
for(var i = 0; i < JsonData.resultList.length; i++){
tbodytrHtml = $("<tr>");
RaceResult = $(JsonData.resultList)[i];
tmpHtml = "";
if(RaceResult.raceTanpyoPrm){
tmpHtml = $("<input>");
tmpHtml.attr({
type: "hidden",
id: "csub" + RaceResult.rclblRaceNo + "Prm",
value: RaceResult.raceTanpyoPrm
});
}
tbodytrHtml.append($("<td>").addClass("b-a al-c bold clc").attr("id","csub"+ RaceResult.rclblRaceNo)
.append(RaceResult.rclblRaceNo)
.append(tmpHtml)
);
tbodytrHtml.append($("<td>").addClass("b-a al-c").append(RaceResult.rclblSyumokuName));
tmpHtml = $("<tbody>");
for(var j = 0; j < RaceResult.tyakui1List.length; j++){
tempList = $(RaceResult.tyakui1List)[j];
tmpHtml.append($("<tr>")
.append($("<td>").addClass("al-c nb-r syaban")
.append($("<div>").addClass("lnum "+ tempList.rclblSyabanClass).append(tempList.rclblSyaban)))
.append($("<td>").addClass("al-l nb-r nb-l bold sensyuName").append(tempList.rclblSensyuName))
.append($("<td>").addClass("al-r nb-l").append(tempList.rclblKimari))
);
}
tbodytrHtml.append($("<td>").addClass("v-al-m b-a").append($("<table>").addClass("w100pc").append(tmpHtml)));
tmpHtml = $("<tbody>");
for(var j = 0; j < RaceResult.tyakui2List.length; j++){
tempList = $(RaceResult.tyakui2List)[j];
tmpHtml.append($("<tr>")
.append($("<td>").addClass("al-c nb-r syaban")
.append($("<div>").addClass("lnum "+ tempList.rclblSyabanClass).append(tempList.rclblSyaban)))
.append($("<td>").addClass("al-l nb-r nb-l bold sensyuName").append(tempList.rclblSensyuName))
.append($("<td>").addClass("al-r nb-l").append(tempList.rclblKimari))
);
}
tbodytrHtml.append($("<td>").addClass("v-al-m").addClass("b-a").append($("<table>").addClass("w100pc").append(tmpHtml)));
tmpHtml = $("<tbody>");
for(var j = 0; j < RaceResult.tyakui3List.length; j++){
tempList = $(RaceResult.tyakui3List)[j];
tmpHtml.append($("<tr>")
.append($("<td>").addClass("al-c nb-r syaban")
.append($("<div>").addClass("lnum "+ tempList.rclblSyabanClass).append(tempList.rclblSyaban)))
.append($("<td>").addClass("al-l nb-r nb-l bold sensyuName").append(tempList.rclblSensyuName))
);
}
tbodytrHtml.append($("<td>").addClass("v-al-m").addClass("b-a").append($("<table>").addClass("w100pc").append(tmpHtml)));
tmpHtml = $("<tbody>");
for(var j = 0; j < RaceResult.harai2syaList.length; j++){
tempList = $(RaceResult.harai2syaList)[j];
tmpHtml.append($("<tr>")
.append($("<td>").addClass("al-l nb-r 2syakumi").append(tempList.kumi))
.append($("<td>").addClass("al-r nb-r nb-l").append(tempList.kingaku))
.append($("<td>").addClass("al-r nb-l ninki").append(tempList.ninki))
);
}
tbodytrHtml.append($("<td>").addClass("v-al-m b-a kingaku").append($("<table>").addClass("w100pc").append(tmpHtml)));
tmpHtml = $("<tbody>");
for(var j = 0; j < RaceResult.harai3renList.length; j++){
tempList = $(RaceResult.harai3renList)[j]
tmpHtml.append($("<tr>")
.append($("<td>").addClass("al-l nb-r kumi").append(tempList.kumi))
.append($("<td>").addClass("al-r nb-r nb-l").append(tempList.kingaku))
.append($("<td>").addClass("al-r nb-l ninki").append(tempList.ninki))
);
}
tbodytrHtml.append($("<td>").addClass("v-al-m b-a kingaku").append($("<table>").addClass("w100pc").append(tmpHtml)));
if(RaceResult.raceRVPrm){
tbodytrHtml.append($("<td>").addClass("b-a al-c")
.append($("<button>").addClass("btn btn_fsz onbtn mini resultbtn").attr({
id:"bcbtnResult"+RaceResult.rclblRaceNo,
type:"button"
}).append("結果"))
    .append($("<input>").attr({
    type: "hidden",
    id: "btnracuRVPrm"+RaceResult.rclblRaceNo,
    name: "btnracuRVPrm"+RaceResult.rclblRaceNo,
    value:RaceResult.raceRVPrm
    }))
    );
}else{
tbodytrHtml.append($("<td>").addClass("b-a al-c")
.append($("<button>").addClass("btn btn_fsz onbtn mini disabled").append("結果").attr({
id: "bcbtnResult"+RaceResult.rclblRaceNo,
type:"button",
disabled:"disabled"
}))
);
}
if(RaceResult.cheackFLG == 1){
tbodytrHtml.append($("<td>").addClass("input_bkColor b-a al-c")
    .append($("<input>").addClass("check_size").attr({
    type: "checkbox",
    id: "chk"+RaceResult.rclblRaceNo,
    name: "chk"+RaceResult.rclblRaceNo,
    }))
    );
tbodytrHtml.append($("<td>").addClass("b-a al-c")
.append($("<button>").addClass("btn onbtn fl-l digestbtn").attr({
type:"button",
id:"btndigest"+RaceResult.rclblRaceNo
}).append($("<img>").addClass("digesticon").attr({
height: "16",
alt: DigestName,
src: DigestPath
}))
.append("ダイジェスト")
)
);
DigestFlg = true
}else{
tbodytrHtml.append($("<td>").addClass("b-a al-c").append("&nbsp;"));
tbodytrHtml.append($("<td>").addClass("b-a al-c")
.append($("<button>").addClass("btn onbtn fl-l digestbtn").attr({
disabled:"disabled",
type:"button"
})
.append($("<img>").addClass("digesticon").attr({
height: "16",
alt: DigestName,
src: DigestPath
}))
.append("ダイジェスト")
)
);
}
tbodyHtml.append(tbodytrHtml);
}
if(DigestFlg == true){
tbodyHtml.append($("<tr>").append($("<td>").addClass("al-r spacer white_bg_color").attr("colspan","19")
.append($("<button>").addClass("btn onbtn fl-r rendigestbtn").attr("type","button")
.append($("<img>").addClass("digesticon").attr({
height: "16",
alt: DigestName,
src: DigestPath
}))
.append("ダイジェスト連続")
)
));
} else {
tbodyHtml.append($("<tr>").append($("<td>").addClass("al-r spacer white_bg_color").attr("colspan","19")
.append($("<button>").addClass("btn onbtn fl-r rendigestbtn").attr("type","button").attr("disabled","disabled")
.append($("<img>").addClass("digesticon").attr({
height: "16",
alt: DigestName,
src: DigestPath,
}))
.append("ダイジェスト連続")
)
));
}
tblHtml.append(tbodyHtml);
return tblHtml;
};
function bcCreatebctblKessya(JsonData,Kbn){
var tblHtml = $("<table>");
var titleHtml = $("<tr>");
var theadHtml = $("<tr>");
var tbodyHtml = $("<tbody>").addClass("altertable");
var tbodytrHtml = $("<tr>");
var tmpHtml = "";
var kessyaList="";
if(Kbn == 0){
tblHtml.attr("id","bctblKessya");
}else{
tblHtml.attr("id","bctblKessyaDokanto");
}
tblHtml.addClass("tblKessya spacerm");
titleHtml.append($("<td>").addClass("nb-a midasi2_fsz").append("欠車情報"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c tdkessyaRace").append("レース番号"));
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").append("欠車車番"));
tblHtml.append($("<thead>").append(titleHtml).append(theadHtml));
for(var i = 0; i < JsonData.resultList.length; i++){
RaceResult = $(JsonData.resultList)[i];
if(RaceResult){
    if(Kbn == 0){
    kessyaList = $(RaceResult.kessyaList);
    }else{
    kessyaList = $(RaceResult.kessyaDokantoList);
    }
    if(kessyaList != null && kessyaList.length != 0){
    tbodytrHtml = $("<tr>");
    tmpHtml = $("<td>");
    tbodytrHtml.append($("<td>").addClass("b-a al-c").append(RaceResult.rclblRaceNo));
    for(var j=0; j< kessyaList.length;j++){
    tmpHtml.append($("<div>").addClass("lnum "+kessyaList[j].syabanClass).append(kessyaList[j].syaban));
    }
    tbodytrHtml.append(tmpHtml.addClass("b-a al-l"));
    tbodyHtml.append(tbodytrHtml);
    }
        }
}
tblHtml.append(tbodyHtml);
return tblHtml;
}
function bcCreatetblRaceResuleDokanto(JsonData){
var tblHtml = $("<table>");
var theadHtml = $("<tr>");
var tbodyHtml = $("<tbody>");
var dokanto7tr = $("<tr>");
var dokanto4twotr = $("<tr>");
var dokanto7tmp = "";
var dokanto4twotmp = "";
var firstSyaban = "";
var secondSyaban = "";
var tempList ="";
var count = 0;
var startCount = 0;
var endCount = 0;
tblHtml.addClass("dokanto tblpadding");
theadHtml.append($("<td>").addClass("tbl_header b-a al-c dokantoTitle").append("レース"));
if((JsonData.dokanto7StartRace <  JsonData.dokanto4twoStartRace && JsonData.dokanto7StartRace != 0) || JsonData.dokanto4twoStartRace == 0){
startCount = JsonData.dokanto7StartRace;
} else {
startCount = JsonData.dokanto4twoStartRace;
}
if(JsonData.dokanto7EndRace <=  JsonData.dokanto4twoEndRace){
endCount = JsonData.dokanto4twoEndRace;
} else {
endCount = JsonData.dokanto7EndRace;
}
count = endCount-startCount;
for(i = startCount;i <= endCount;i++){
if((JsonData.dokanto7StartRace <= i &&  i <= JsonData.dokanto7EndRace) || (JsonData.dokanto4twoStartRace <= i &&  i <= JsonData.dokanto4twoEndRace )){
theadHtml.append($("<td>").addClass("tbl_header b-a al-c").append(i+"R"));
}
}
tblHtml.append($("<thead>").append(theadHtml));
dokanto7tr.append($("<td>").addClass("b-a dokantoTitle").append("レース結果<br />1着"));
if(JsonData.dispDokanto4Flg == 1){
dokanto4twotr.append($("<td>").addClass("b-a dokantoTitle ").append("レース結果<br />2着"));
}
for(var i = 0; i <= count; i++){
dokanto7tmp = $("<td>").addClass("b-a al-c dokantoData");
dokanto4twotmp = $("<td>").addClass("b-a al-c dokantoData");
if($(JsonData.dokantoRaceList)[i]){
dokantoList = $(JsonData.dokantoRaceList)[i];
for(var j= 0;j < dokantoList.dokantoFirst.length;j++){
firstSyaban = dokantoList.dokantoFirst[j]
if(firstSyaban.syaban){
if(firstSyaban.syaban == "?" || firstSyaban.syaban == "" || firstSyaban.syaban == "-" ||  firstSyaban.syaban.indexOf("<br />") != -1){
dokanto7tmp.addClass(firstSyaban.syabanClass).append($("<div>").append(firstSyaban.syaban));
} else {
dokanto7tmp.append($("<div>").append(firstSyaban.syaban).addClass("lnum " + firstSyaban.syabanClass));
if(j != dokantoList.dokantoFirst.length-1){
dokanto7tmp.append($("<br />"));
}
}
dokanto7tr.append(dokanto7tmp);
if(firstSyaban.syaban.indexOf("<br />") != -1){
break;
}
}else{
dokanto7tmp.append($("<div>").append("?"));
dokanto7tr.append(dokanto7tmp);
}
}
if(JsonData.dispDokanto4Flg == 1){
if(JsonData.dokanto4twoStartRace <= dokantoList.dokantoRaceNo && dokantoList.dokantoRaceNo <= JsonData.dokanto4twoEndRace){
for(var j= 0;j < dokantoList.dokantoSecond.length;j++){
secondSyaban = dokantoList.dokantoSecond[j];
        if(secondSyaban.syaban){
if(secondSyaban.syaban == "?" || secondSyaban.syaban == "" || secondSyaban.syaban == "-" ||  secondSyaban.syaban.indexOf("<br />") != -1){
dokanto4twotmp.addClass(secondSyaban.syabanClass).append($("<div>").append(secondSyaban.syaban));
} else {
dokanto4twotmp.append($("<div>").append(secondSyaban.syaban).addClass("lnum " + secondSyaban.syabanClass));
if(j != secondSyaban.length-1){
dokanto4twotmp.append($("<br />"));
}
}
dokanto4twotr.append(dokanto4twotmp);
if(secondSyaban.syaban.indexOf("<br />") != -1){
break;
}
        }else{
        dokanto4twotmp.append($("<div>").append("?"));
        dokanto4twotr.append(dokanto4twotmp);
        }
}
}else{
dokanto4twotmp.addClass(JsonData.dokanto4twonodataColor).append($("<div>").append(""));
dokanto4twotr.append(dokanto4twotmp);
}
}
} else {
if(JsonData.dokanto7StartRace <= count + i &&  count + i <= JsonData.dokanto7EndRace){
dokanto7tmp.append($("<div>").append("?"));
}else{
dokanto7tmp.addClass(JsonData.dokanto4twonodataColor).append($("<div>").append(""));
}
if(JsonData.dispDokanto4Flg == 1){
if(JsonData.dokanto4twoStartRace <= count + i &&  count + i <= JsonData.dokanto4twoEndRace){
dokanto4twotmp.append($("<div>").append("?"));
}else{
dokanto4twotmp.addClass(JsonData.dokanto4twonodataColor).append($("<div>").append(""));
}
dokanto4twotr.append(dokanto4twotmp);
}
dokanto7tr.append(dokanto7tmp);
}
}
tbodyHtml.append(dokanto7tr);
if(JsonData.dispDokanto4Flg == 1){
tbodyHtml.append(dokanto4twotr);
}
tblHtml.append(tbodyHtml);
return tblHtml;
}
function bcCreatetblRaceBetDokanto(JsonData){
var tblHtml = $("<table>");
var tbodyHtml = $("<tbody>");
var dokanto7tr = $("<tr>");
var dokanto4twotr = $("<tr>");
var tmp = "";
var count = 0;
var startCount = 0;
var endCount = 0;
if((JsonData.dokanto7StartRace <  JsonData.dokanto4twoStartRace && JsonData.dokanto7StartRace != 0) || JsonData.dokanto4twoStartRace == 0){
startCount = JsonData.dokanto7StartRace;
} else {
startCount = JsonData.dokanto4twoStartRace;
}
if(JsonData.dokanto7EndRace <=  JsonData.dokanto4twoEndRace){
endCount = JsonData.dokanto4twoEndRace;
} else {
endCount = JsonData.dokanto7EndRace;
}
count = endCount-startCount;
tblHtml.addClass("dokanto tblpadding fl-l");
if(JsonData.dispDokanto7Flg == 1){
dokanto7tr = $("<tr>").addClass(JsonData.dokanto7Color);
dokanto7tr.append($("<td>").addClass("b-a dokantoTitle h55").append("Dokanto!7<br />的中継続ベット数"));
}
if(JsonData.dispDokanto4Flg == 1){
dokanto4twotr = $("<tr>").addClass(JsonData.dokanto4twoColor);
dokanto4twotr.append($("<td>").addClass("b-a dokantoTitle h55").append("Dokanto!4two<br />的中継続ベット数"));
}
for(var i = 0; i <= count; i++){
if($(JsonData.dokantoRaceList)[i]){
dokantoList = $(JsonData.dokantoRaceList)[i];
if(JsonData.dispDokanto7Flg == 1){
if(JsonData.dokanto7StartRace <= dokantoList.dokantoRaceNo && dokantoList.dokantoRaceNo <= JsonData.dokanto7EndRace){
if(dokantoList.dokant7zanBet){
dokanto7tr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append(dokantoList.dokant7zanBet).addClass("al-c")));
}else{
dokanto7tr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append("").addClass("al-c")));
}
} else {
dokanto7tr.append($("<td>").addClass("b-a al-c dokantoData h55 " + JsonData.dokanto4twonodataColor).append($("<div>").append("").addClass("al-c")));
}
}
if(JsonData.dispDokanto4Flg == 1){
if(JsonData.dokanto4twoStartRace <= dokantoList.dokantoRaceNo && dokantoList.dokantoRaceNo<= JsonData.dokanto4twoEndRace){
if(dokantoList.dokant4twozanBet){
dokanto4twotr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append(dokantoList.dokant4twozanBet).addClass("al-c")));
}else{
dokanto4twotr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append("").addClass("al-c")));
}
} else {
dokanto4twotr.append($("<td>").addClass("b-a al-c dokantoData h55 " + JsonData.dokanto4twonodataColor).append($("<div>").append("").addClass("al-c")));
}
}
} else {
if(JsonData.dispDokanto7Flg == 1){
if(JsonData.dokanto7StartRace <= count + i && count + i<= JsonData.dokanto7EndRace){
dokanto7tr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append("").addClass("al-c")));
}else{
dokanto7tr.append($("<td>").addClass("b-a al-c dokantoData h55 " + JsonData.dokanto4twonodataColor).append($("<div>").append("").addClass("al-c")));
}
}
if(JsonData.dispDokanto4Flg == 1){
if(JsonData.dokanto4twoStartRace <= count + i && count + i<= JsonData.dokanto4twoEndRace){
dokanto4twotr.append($("<td>").addClass("b-a al-c dokantoData h55").append($("<div>").append("").addClass("al-c")));
}else{
dokanto4twotr.append($("<td>").addClass("b-a al-c dokantoData h55 " + JsonData.dokanto4twonodataColor).append($("<div>").append("").addClass("al-c")));
}
}
}
}
if(JsonData.dispDokanto7Flg == 1){
tbodyHtml.append(dokanto7tr);
}
if(JsonData.dispDokanto4Flg == 1){
tbodyHtml.append(dokanto4twotr);
}
tblHtml.append(tbodyHtml);
return tblHtml;
}
function bcCreatetblDokantoTotalmoney(JsonData){
var tblHtml = "";
if(JsonData.dispDokantoFlg < 3){
tblHtml = $("<table>");
var tbodyHtml = $("<tbody>");
var tbodytrHtml = $("<tr>");
var tmp = "";
tblHtml.addClass("tblpadding wsize_29p fl-r");
if(JsonData.dispDokanto7Flg == 1){
tbodytrHtml.append($("<td>").addClass(JsonData.dokanto7Color+ " b-a h55")
.append("Dokanto!7<br />払戻対象総額"));
tbodytrHtml.append($("<td>").addClass("b-a al-r " + JsonData.dokanto7Color).append(JsonData.dokanto7Totalmoney));
tblHtml.append(tbodyHtml.append(tbodytrHtml));
}
if(JsonData.dispDokanto4Flg == 1){
tbodytrHtml = $("<tr>");
tbodytrHtml.append($("<td>").addClass(JsonData.dokanto4twoColor + " b-a h55")
.append("Dokanto!4two<br />払戻対象総額"));
tbodytrHtml.append($("<td>").addClass("b-a al-r "+JsonData.dokanto4twoColor).append(JsonData.dokanto4twoTotalmoney));
}
tblHtml.append(tbodyHtml.append(tbodytrHtml));
}
return tblHtml;
}
function bcCreatetblNokorimeDokanto(JsonData,classColor,dokantoflg,doutyakuFlg){
var tblHtml = $("<table>").addClass("wsize_49p");
var chiltblHtml = $("<table>").addClass("w100pc tblpadding");
var chiltheadHtml = $("<tr>");
var chiltbodyHtml = $("<tbody>");
var tmp = "";
var souteiHarai = "";
var kumibantd = $("<td>");
var titleName = "";
var kumibanName = ""
if(dokantoflg == 0){
titleName = "Dokanto!7残り目";
} else if(dokantoflg == 1){
titleName = "Dokanto!4two残り目";
}
if(doutyakuFlg == 0){
kumibanName = "";
} else if(doutyakuFlg == 1){
kumibanName = $("<br />") + "的中組番：" + $("<br />") + JsonData.nokorimeKumiban;
}
chiltheadHtml.append($("<td>").append("組番").addClass(classColor + " al-c b-a"));
chiltheadHtml.append($("<td>").append("残りベット数").addClass(classColor + " al-c b-a"));
chiltheadHtml.append($("<td>").append("的中時払戻額").addClass(classColor + " al-c b-a"));
chiltblHtml.append($("<thead>").append(chiltheadHtml));
if(dokantoflg == 0){
for(var i= 0; i < JsonData.SouteiHarai.length;i++){
souteiHarai = JsonData.SouteiHarai[i];
chiltbodyHtml.append($("<tr>")
.append($("<td>").addClass("b-a wsize_30p al-c").append($("<div>").append(souteiHarai.nokorimeFirstSyaban.syaban).addClass("lnum " + souteiHarai.nokorimeFirstSyaban.syabanClass)))
.append($("<td>").addClass("b-a wsize_30p al-c").append(souteiHarai.nokorimeBet))
.append($("<td>").addClass("b-a wsize_40p al-r").append(souteiHarai.nokorimeSouteiHarai))
);
}
} else if(dokantoflg == 1){
for(var i= 0; i < JsonData.SouteiHarai.length;i++){
souteiHarai = JsonData.SouteiHarai[i];
chiltbodyHtml.append($("<tr>")
.append($("<td>").addClass("b-a wsize_30p al-c")
.append($("<div>").append(souteiHarai.nokorimeFirstSyaban.syaban).addClass("lnum " + souteiHarai.nokorimeFirstSyaban.syabanClass))
.append("&nbsp;")
.append($("<div>").append(souteiHarai.nokorimeSecondSyaban.syaban).addClass("lnum " + souteiHarai.nokorimeSecondSyaban.syabanClass))
)
.append($("<td>").addClass("b-a wsize_30p al-c").append(souteiHarai.nokorimeBet).addClass("al-c"))
.append($("<td>").addClass("b-a wsize_40p al-r").append(souteiHarai.nokorimeSouteiHarai).addClass("al-r"))
);
}
}
chiltblHtml.append(chiltbodyHtml);
tblHtml.append($("<tbody>").append($("<tr>")
.append($("<td>").addClass("wsize_27p v-al-t")
.append(titleName)
.append(kumibanName)
)
.append($("<td>").append(chiltblHtml))
));
return tblHtml;
}
function bcCreatetblResuleDokanto(JsonData,classColor,dokantoflg){
var tblHtml = $("<table>").addClass("w100pc tblpadding");
var theadHtml = $("<tr>");
var tbodyHtml = $("<tbody>").addClass("altertable");
var tmp = "";
var syaban = "";
var kumibanntd = $("<td>");
var titleName = "";
var entmp = "";
if(dokantoflg == 0){
titleName = "Dokanto!7";
} else if(dokantoflg == 1){
titleName = "Dokanto!4two";
}
theadHtml.append($("<td>").addClass(classColor + " b-a").attr("colspan","3").append(titleName));
tblHtml.append($("<thead>").append(theadHtml));
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " wsize_40p b-a").append("前回からのキャリーオーバー額"))
.append($("<td>").addClass("wsize_56p b-t b-l b-b al-r padr0").append(JsonData.carryOver))
.append($("<td>").addClass("wsize_4p b-t b-r b-b al-r padl0").append("円"))
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("発売ベット数"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.hatubaiBet))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("&nbsp;"))
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("総発売金額"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.souHatubaiGaku))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("円"))
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("返還ベット数"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.henkanBet))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("&nbsp;"))
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("返還金額"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.souHenkanGaku))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("円"))
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("総的中ベット数"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.souTekityuBet))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("&nbsp;"))
);
if(JsonData.ResultTekityu.length <= 1){
if(JsonData.ResultTekityu[0].tekityuKingaku == "-"){
entmp = "";
} else {
entmp = "円";
}
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a ").append("払戻金額(１ベットあたり)"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.ResultTekityu[0].tekityuKingaku))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append(entmp))
);
} else {
for(var i=0; i < JsonData.ResultTekityu.length;i++){
kumibanntd = $("<td>").addClass("b-a al-r").attr("colspan","2");
for(var j = 0;j < JsonData.ResultTekityu[i].DokantotekityuList.length;j++){
syaabnList = JsonData.ResultTekityu[i].DokantotekityuList[j];
tmp = $("<div>");
tmp.append(syaabnList.syaban).addClass("lnum " + syaabnList.syabanClass);
kumibanntd.append(tmp);
if(j != JsonData.ResultTekityu[i].DokantotekityuList.length-1){
if(dokantoflg == 0){
kumibanntd.append("-");
}else if(dokantoflg == 1){
if(j%2 != 0){
kumibanntd.append("-");
}
}
}
}
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("的中組番"))
.append(kumibanntd)
);
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("払戻金額(１ベットあたり)"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.ResultTekityu[i].tekityuKingaku))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append("円"))
);
}
}
if(JsonData.nextCarryOver == "-"){
entmp = "";
} else {
entmp = "円";
}
tbodyHtml.append($("<tr>")
.append($("<td>").addClass(classColor + " b-a").append("次回へのキャリーオーバー額"))
.append($("<td>").addClass("b-t b-l b-b al-r padr0").append(JsonData.nextCarryOver))
.append($("<td>").addClass("b-t b-r b-b al-r padl0").append(entmp))
);
tblHtml.append(tbodyHtml);
return tblHtml;
}
function unsanitaiz(sanitaizData){
return $("<div>").append(sanitaizData)[0].innerHTML;
}
