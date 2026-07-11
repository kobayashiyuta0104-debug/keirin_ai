var kaisaiDateT0001 = '';
var keirinjyoT0001 = '';
var gradeT0001 = '';
var raceNoT0001 = '';
var kakesikiT0001 = '';
var upDateT0001 = '';
var kimOzzInfo = {"1": {}, "2": {}, "3": {}, "4": {}, "5": {}, "6": {}, "7": {}};
var editKaimeGroup = null;
var kimOldEditMode = -1;
var comKaime = {
BINARY_ARRAY: [8,4,2,1],
KIM_CNT_KEY: "KIMCNT",
KIM_KEY_PRE: "KIM",
OZZ_KEY_PRE: "OZZ",
SKN_CNT_KEY: "SKNCNT",
SKN_KEY_PRE: "SKN",
voteEditMode: -1,
initForKimeuti: function() {
comKaime.KIM_CNT_KEY = "KUTCNT";
comKaime.KIM_KEY_PRE = "KUT";
},
initForKaime: function() {
comKaime.KIM_CNT_KEY = 'KIMCNT';
comKaime.KIM_KEY_PRE = 'KIM';
},
getPageType: function() {
if (comKaime.KIM_CNT_KEY == 'KIMCNT') {
return '1'
} else if (comKaime.KIM_CNT_KEY == 'KUTCNT') {
return '2'
} else {
return null;
}
},
kimChangePrimeKey: function(kaisaiDate, keirinjyo, raceNo, kakesiki, upDate, grade) {
if (kaisaiDate) {
kaisaiDateT0001 = kaisaiDate;
}
if (keirinjyo) {
keirinjyoT0001 = keirinjyo;
}
if (raceNo) {
raceNoT0001 = raceNo;
}
if (kakesiki) {
kakesikiT0001 = kakesiki;
}
if (upDate) {
upDateT0001 = upDate;
}
if (grade) {
gradeT0001 = grade;
}
},
kimGetKumibanX: function(data) {
var ret = '';
if (data && (data.length > 0)) {
var tmp2 = '0000000000000000000000000000';
for(var i=0;i<3;i++) {
for(var j=0;j<9 && data[i] && j<data[i].length;j++) {
var chr = data[i].charCodeAt(j) - '0'.charCodeAt(0);
if (chr>=0 && chr<=9) {
var idx = i * 9 + chr - 1;
tmp2 = tmp2.substring(0, idx) + '1' + tmp2.substring(idx + 1);
}
}
}
for (var k=0;k<7;k++) {
var tmp =0;
var tmp4 = tmp2.substring(k*4, k*4+4);
for(var m=0;m<4;m++) {
var chr = tmp4.substring(m, m+1);
if (chr == '1') {
tmp = tmp + comKaime.BINARY_ARRAY[m];
}
}
if (tmp < 10) {
ret = ret + tmp;
}else {
ret = ret + String.fromCharCode('A'.charCodeAt(0) + tmp - 10);
}
}
}
return ret;
},
kimKumibanX2Arr: function(data) {
var ret = [];
if (data && (data.length > 0)) {
var tmp2 = '';
for (var k=0;k<7;k++) {
var tmp =0;
var chr = data.substring(k,k+1);
if (chr >= 'A') {
tmp = chr.charCodeAt(0) - 'A'.charCodeAt(0) + 10;
} else {
tmp = parseInt(chr);
}
var tmp4 = '';
for(var m=0;m<4;m++) {
if (tmp >= comKaime.BINARY_ARRAY[m]) {
tmp4 = tmp4 + '1';
tmp = tmp - comKaime.BINARY_ARRAY[m];
} else {
tmp4 = tmp4 + '0';
}
}
tmp2 = tmp2 + tmp4;
}
for(var i=0;i<3;i++) {
var tmp = '';
for(var j=0;j<9;j++) {
var chr = tmp2.substring(i * 9 + j, i * 9 + j + 1);
if (chr == '1') {
tmp = tmp + (j+1);
}
}
ret[i] = tmp;
}
}
return ret;
},
kimStringfyKumibanX: function(kakesiki ,data, rtFlg) {
var ret = '';
var len = 0;
var retArr = comKaime.kimKumibanX2Arr(data);
if (retArr && (retArr.length > 0)) {
var chr;
if (kakesiki== '1' || kakesiki== '4' || kakesiki== '5' || kakesiki== '7') {
chr = '<span>=</span>';
} else {
chr = '<span>-</span>';
}
for(var i=0;i<retArr.length;i++) {
if (!retArr[i])continue;
if (i==0) {
ret = '<span class="sd' + (i+1) + '">' + retArr[i] + '</span>';
len = retArr[i].length;
} else {
ret = ret + chr + '<span class="sd' + (i+1) + '">' + retArr[i] + '</span>';
len = len + 1 + retArr[i].length;
}
}
if (!rtFlg && len > 10) {
if (kakesiki== '1' || kakesiki== '4' || kakesiki== '5' || kakesiki== '7') {
chr = '<span>=</span><br/>';
} else {
chr = '<span>-</span><br/>';
}
ret = '';
for(var i=0;i<retArr.length;i++) {
if (!retArr[i])continue;
if (i==0) {
ret = '<span class="sd' + (i+1) + '">' + retArr[i] + '</span>';
} else {
ret = ret + chr + '<span class="sd' + (i+1) + '">' + retArr[i] + '</span>';
}
}
ret = ret.substring(0, ret.length - 4);
}
}
return ret;
},
kimGetInitMaisu: function () {
var maisu = 1;
var initMaisu = $('#clblNowSetGaku').html();
if (initMaisu) {
initMaisu = initMaisu.replace(',', '');
try {
maisu = parseInt(initMaisu)/100;
} catch(e){}
}
return maisu;
},
kimAddKaime: function(kakesiki, kumiban, ozz1, ozz2, maisu, result) {
if (!kaisaiDateT0001 || !keirinjyoT0001 || !raceNoT0001 || !upDateT0001) {
comDialog.alert('予期せぬエラーが発生しました。');
return;
}
if (!editKaimeGroup) {
editKaimeGroup = {
"groupId":"Tmp" + comKaime.KIM_KEY_PRE,
"setState":"0",
"kaisaiDate":kaisaiDateT0001,
"keirinjyo": keirinjyoT0001,
"raceNo":raceNoT0001,
"state":"2",
"procedures":"0",
"kakesiki" : kakesiki,
"list" : [],
'upDate' : upDateT0001
};
if (comKaime.getPageType() == '2') {
editKaimeGroup.grade = gradeT0001;
}
}
var tmpMaisu = 0;
if (maisu) {
tmpMaisu = maisu;
} else {
tmpMaisu = comKaime.kimGetInitMaisu();
}
editKaimeGroup.list[editKaimeGroup.list.length] = {
"kumiban" : comKaime.kimGetKumibanX([kumiban.substring(0, 1), 
                                               kumiban.substring(1, 2), 
                                               kumiban.substring(2, 3)]),
"maisu" : tmpMaisu,
"ozz": ozz1
};
if (ozz2) {
editKaimeGroup.list[editKaimeGroup.list.length - 1].ozzMax = ozz2;
}
if (result) {
editKaimeGroup.list[editKaimeGroup.list.length - 1].result = result;
}
var retIfMax = comKaime.kimIfMax();
if (retIfMax > 0) {
errorFlg = true;
if (retIfMax == 1) {
comDialog.alert('投票１回あたりの最大投票可能明細数を超えています。');
} else if (retIfMax == 2) {
comDialog.alert('投票１回あたりの最大投票可能ベット数を超えています。');
}
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
var html = PT0241View.createGroup(editKaimeGroup);
PT0241Controller.initForDispKaime();
if ($('#divTmp' + comKaime.KIM_KEY_PRE).length > 0) {
$('#divTmp' + comKaime.KIM_KEY_PRE).html($(html).html())
} else {
$(html).prependTo($('#kaimeGroupList'));
}
$('#kaimeGroupList').scrollTop(0);
PT0241Controller.kimTotal(editKaimeGroup.groupId);
PT0241Controller.kimSeirituYotei();
PT0241Controller.btnControl();
}
},
kimChangeMaisu: function() {
if (!editKaimeGroup || !editKaimeGroup.list) {
return;
}
var tmpMaisu = comKaime.kimGetInitMaisu();
for (var i=0;i<editKaimeGroup.list.length;i++) {
editKaimeGroup.list[i].maisu = tmpMaisu;
}
if (editKaimeGroup.single) {
editKaimeGroup.single.maisu = tmpMaisu;
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
var html = PT0241View.createGroup(editKaimeGroup);
PT0241Controller.initForDispKaime();
if ($('#divTmp' + comKaime.KIM_KEY_PRE).length > 0) {
$('#divTmp' + comKaime.KIM_KEY_PRE).html($(html).html())
} else {
$(html).prependTo($('#kaimeGroupList'));
}
$('#kaimeGroupList').scrollTop(0);
PT0241Controller.kimTotal(editKaimeGroup.groupId);
PT0241Controller.kimSeirituYotei();
PT0241Controller.btnControl();
}
},
kimAddKaimeFormation: function(kakesiki, kumiban, zenPatternFlg, wakubanStr, maisu) {
if (!kaisaiDateT0001 || !keirinjyoT0001 || !raceNoT0001 || !maisu) {
comDialog.alert('予期せぬエラーが発生しました。');
return false;
}
if(!zenPatternFlg) {
zenPatternFlg = '000';
}
var kumibanList = getListTickets(kakesiki, kumiban, '1', wakubanStr);
if (kumibanList.length == 0) {
if (!editKaimeGroup) {
return false;
}
}
var errorFlg = false;
var upDate = '';
if (kimOzzInfo && kimOzzInfo[kakesiki] && kimOzzInfo[kakesiki]['UP_DATE']) {
upDate = kimOzzInfo[kakesiki]['UP_DATE'];
} else {
upDate = upDateT0001;
}
if (!editKaimeGroup) {
editKaimeGroup = {
"groupId":"Tmp" + comKaime.KIM_KEY_PRE,
"setState":"0",
"kaisaiDate":kaisaiDateT0001,
"keirinjyo": keirinjyoT0001,
"raceNo":raceNoT0001,
"state":"0",
"procedures":"8",
"kakesiki" : kakesiki,
"list" : [],
'upDate' : upDate,
"single" : {
"kumiban":comKaime.kimGetKumibanX(kumiban)
}
};
}
editKaimeGroup.single.maisu = maisu;
editKaimeGroup.single.zenPatternFlg = zenPatternFlg;
if (comKaime.getPageType() == '2') {
editKaimeGroup.grade = gradeT0001;
}
editKaimeGroup.single.kumiban = comKaime.kimGetKumibanX(kumiban);
editKaimeGroup.list =  [];
for (var i=0;i<kumibanList.length;i++) {
if (kakesiki == '5') {
var ozz1 = kimOzzInfo[kakesiki]['DN_OZZ' + kumibanList[i]];
var ozz2 = kimOzzInfo[kakesiki]['TP_OZZ' + kumibanList[i]];
editKaimeGroup.list[editKaimeGroup.list.length] = {
"kumiban" : comKaime.kimGetKumibanX([kumibanList[i].substring(0, 1), 
                                               kumibanList[i].substring(1, 2), 
                                               kumibanList[i].substring(2, 3)]),
"maisu" : maisu,
"ozz": ozz1,
"ozzMax": ozz2
};
if (ozz2) {
editKaimeGroup.list[editKaimeGroup.list.length - 1].ozzMax = ozz2;
}
} else {
var ozz1 = kimOzzInfo[kakesiki]['OZZ' + kumibanList[i]];
editKaimeGroup.list[editKaimeGroup.list.length] = {
"kumiban" : comKaime.kimGetKumibanX([kumibanList[i].substring(0, 1), 
                                               kumibanList[i].substring(1, 2), 
                                               kumibanList[i].substring(2, 3)]),
"maisu" : maisu,
"ozz": ozz1
};
}
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
var groupId = editKaimeGroup.groupId;
if (editKaimeGroup.list.length == 0 && comKaime.kimGetEditMode() != 5) {
editKaimeGroup = null;
if(!comKaime.kimIfExist()) {
PT0241Controller.kimShow();
} else if ($('#div' + groupId).length > 0) {
$('#div' + groupId).remove();
}
} else {
var html = PT0241View.createGroup(editKaimeGroup);
PT0241Controller.initForDispKaime();
if ($('#div' + groupId).length > 0) {
$('#div' + groupId).html($(html).html())
} else {
$(html).prependTo($('#kaimeGroupList'));
}
}
if ($('#div' + groupId).length > 0) {
$('#kaimeGroupList').scrollTop($('#div' + groupId).offset().top - $('#kaimeGroupList').offset().top + $('#kaimeGroupList').scrollTop());
}
PT0241Controller.kimTotal(groupId);
PT0241Controller.kimSeirituYotei();
PT0241Controller.btnControl();
}
var retIfMax = comKaime.kimIfMax();
if (retIfMax > 0) {
errorFlg = true;
if (retIfMax == 1) {
comDialog.alert('投票１回あたりの最大投票可能明細数を超えています。');
} else if (retIfMax == 2) {
comDialog.alert('投票１回あたりの最大投票可能ベット数を超えています。');
}
}
if (!errorFlg && editKaimeGroup && editKaimeGroup.list && editKaimeGroup.list.length > 0) {
return true;
} else {
return false;
}
},
kimDelKaime: function(kumiban) {
if (editKaimeGroup && editKaimeGroup.list && editKaimeGroup.list.length > 0) {
var kumibanX = comKaime.kimGetKumibanX([kumiban.substring(0,1), kumiban.substring(1,2), kumiban.substring(2,3)])
for (var i=0;i<editKaimeGroup.list.length;i++) {
if (kumibanX == editKaimeGroup.list[i].kumiban) {
editKaimeGroup.list.splice(i, 1);
i--;
}
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
var groupId = editKaimeGroup.groupId;
if (editKaimeGroup.list.length == 0) {
editKaimeGroup = null;
if(!comKaime.kimIfExist()) {
PT0241Controller.kimShow();
} else if ($('#divTmp' + comKaime.KIM_KEY_PRE).length > 0) {
$('#divTmp' + comKaime.KIM_KEY_PRE).remove();
}
} else {
var html = PT0241View.createGroup(editKaimeGroup);
if ($('#divTmpKIM').length > 0) {
$('#divTmpKIM').html($(html).html())
} else {
$(html).prependTo($('#kaimeGroupList'));
}
}
PT0241Controller.kimTotal(groupId);
PT0241Controller.kimSeirituYotei();
PT0241Controller.btnControl();
}
}
},
kimIfMax : function() {
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
var betCnt = 0;
if (kimcnt) {
kimcnt = parseInt(kimcnt);
if (kimcnt > 999) {
return 1;
} else {
if (editKaimeGroup) {
if ((kimcnt + 1) > 999) {
return 1;
}
}
var count = 0;
for(var i=0;i<kimcnt;i++) {
var group = comKaime.getGroup(comKaime.KIM_KEY_PRE + i);
if (group && (!editKaimeGroup || group.groupId != editKaimeGroup.groupId)) {
if (group.state == 2) { 
count = count + group.list.length;
} else {
count = count + 1;
}
betCnt = betCnt + group.list.length;
}
}
if (editKaimeGroup) {
if (editKaimeGroup.state == 2) { 
count = count + editKaimeGroup.list.length;
} else {
count = count + 1;
}
betCnt = betCnt + editKaimeGroup.list.length;
}
if (count > 999) {
return 1;
}
if (betCnt > 999) {
return 2;
}
}
}
return 0;
},
kimClear : function(kaisaiDate) {
if (!comKaime.kimIfSessionStorage()) {
return;
}
if (kaisaiDate) {
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
if (kimcnt) {
kimcnt = parseInt(kimcnt);
if (kimcnt == 0) {
return;
} else {
var count = 0;
for(var i=0;i<kimcnt;i++) {
var group = comKaime.getGroup(comKaime.KIM_KEY_PRE + i);
if (group) {
if (group.kaisaiDate < kaisaiDate) {
window.sessionStorage.removeItem(comKaime.KIM_KEY_PRE + i);
} else {
if (count != i) {
group.groupId = comKaime.KIM_KEY_PRE + count;
comKaime.setGroup(group);
window.sessionStorage.removeItem(comKaime.KIM_KEY_PRE + i);
}
count = count + 1;
}
}
}
window.sessionStorage.setItem(comKaime.KIM_CNT_KEY, count);
}
}
} else {
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
if (kimcnt) {
kimcnt = parseInt(kimcnt);
if (kimcnt == 0) {
return;
} else {
for(var i=0;i<kimcnt;i++) {
window.sessionStorage.removeItem(comKaime.KIM_KEY_PRE + i);
}
window.sessionStorage.setItem(comKaime.KIM_CNT_KEY, '0');
}
}
}
},
kimIfExist : function() {
if (!comKaime.kimIfSessionStorage()) {
return false;
}
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
if (!kimcnt) {
return false;
} else {
kimcnt = parseInt(kimcnt);
if (kimcnt > 0) {
return true;
} else {
return false;
}
}
},
kimClearTmp : function() {
if (editKaimeGroup) {
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
if (comKaime.kimGetEditMode() == 5) {
var group = comKaime.getGroup(editKaimeGroup.groupId);
comKaime.kimSetEditMode(kimOldEditMode, '1');
var html = PT0241View.createGroup(group);
$('#div' + editKaimeGroup.groupId).replaceWith(html);
} else {
if ($('#divTmp' + comKaime.KIM_KEY_PRE).length > 0) {
$('#divTmp' + comKaime.KIM_KEY_PRE).remove();
}
}
PT0241Controller.kimTotal(editKaimeGroup.groupId);
editKaimeGroup = null;
if(!comKaime.kimIfExist()) {
PT0241Controller.kimShow();
}
PT0241Controller.kimSeirituYotei();
PT0241Controller.btnControl();
}
}
},
kimGetLastGroup : function() {
if (editKaimeGroup) {
return editKaimeGroup;
}
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
if (!kimcnt) {
return null;
} else {
kimcnt = parseInt(kimcnt);
return comKaime.getGroup(comKaime.KIM_KEY_PRE + (kimcnt - 1));
};
},
kimGetEditMode : function() {
return comKaime.voteEditMode;
},
kimSetEditMode : function(voteEditMode, flg) {
var tmp = comKaime.voteEditMode;
if ((tmp == '9' || tmp == '5' && voteEditMode != '3' || tmp == '3' && voteEditMode != '5') && !flg) {
if (voteEditMode != tmp) {
kimOldEditMode = voteEditMode;
}
return;
}
comKaime.voteEditMode = voteEditMode;
switch (comKaime.voteEditMode) {
case 1 :
PT0202View.cPPT0202BtnFalse()
comOzz.ozzSeigyo();
if(!comKaime.kimIfExist()) {
PT0241Controller.kimShow();
}
PT0241Controller.btnControl();
break;
case 2 :
PT0202View.cPPT0202BtnTrue();
comOzz.ozzSeigyoClear();
if(!comKaime.kimIfExist()) {
PT0241Controller.kimShow();
}
PT0241Controller.btnControl();
break;
case 3 :
if (tmp != 5) {
kimOldEditMode = tmp;
}
PT0202View.cPPT0202BtnTrue();
$('.btn_set').addClass('disabled');
comOzz.ozzSeigyo();
PT0241Controller.btnControl();
$('.kimBtnModify').removeClass('disabled');
$('.kimBtnModify').removeAttr('disabled');
break;
case 5 :
PT0202View.cPPT0202BtnFalse();
$('.btn_set').removeClass('disabled');
comOzz.ozzSeigyo();
PT0241Controller.btnControl();
$('.kimBtnModify').addClass('disabled');
$('.kimBtnModify').attr('disabled', 'disabled');
break;
case 9:
comOzz.ozzSeigyo();
kimOldEditMode = tmp;
break;
default:
break;
}
comKaime.kimHint();
},
kimHint : function() {
if (editKaimeGroup) {
$('.kimHintTd').addClass('dispoff');
if (comKaime.kimGetEditMode() == '3') {
$('#div' + editKaimeGroup.groupId + ' .kimHintTd.dispoff').removeClass('dispoff');
}
} else {
$('.kimHintTd.dispoff').removeClass('dispoff');
}
},
kimIfNoSet : function() {
if (editKaimeGroup && (editKaimeGroup.setState == '0' || editKaimeGroup.setState == '5')) {
return true;
} else {
return false;
}
},
kimSet : function() {
if (editKaimeGroup) {
if (comKaime.kimGetEditMode() != 5) {
editKaimeGroup.setState = '1';
} else {
editKaimeGroup.setState = '2';
}
if (comKaime.kimGetEditMode() != 5) {
comKaime.setGroup(editKaimeGroup);
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
var html = PT0241View.createGroup(editKaimeGroup);
}
if (typeof(PT0241Controller) == 'object' && typeof(PT0241View) == 'object') {
if ($('#div' + editKaimeGroup.groupId).length > 0) {
$('#div' + editKaimeGroup.groupId).replaceWith(html);
} else {
$(html).prependTo($('#kaimeGroupList'));
}
$('.kimBtnModify').removeClass("disabled");
PT0241Controller.btnControl();
}
if (comKaime.kimGetEditMode() == 5) {
PT0241Controller.kimBtnModify($('#div' + editKaimeGroup.groupId).find('.kimBtnModify'));
} else if ($('.ozz_tbl .btn .active').length > 0) {
$('.ozz_tbl .btn .active').removeClass('active');
}
if (comKaime.kimGetEditMode() != 5 && comKaime.kimGetEditMode() != 3) {
if ($('#divTmp' + comKaime.KIM_KEY_PRE).length > 0) {
$('#divTmp' + comKaime.KIM_KEY_PRE).remove();
}
editKaimeGroup = null;
}
}
if (comKaime.kimGetEditMode() != 3) {
$('.kimHintTd.dispoff').removeClass('dispoff');
}
},
kimGetNoSetKaimeGroup : function() {
if (!comKaime.kimIfSessionStorage()) {
return null;
}
return editKaimeGroup;
},
getGroup : function (groupId) {
if (!groupId) {
return editKaimeGroup;
}
var kaime = window.sessionStorage.getItem(groupId);
var group = {};
var index = 0;
group.groupId = groupId; 
group.setState = kaime.substring(index, index+=1);
group.state = kaime.substring(index, index+=1);
group.kaisaiDate = kaime.substring(index, index+=8);
group.keirinjyo = kaime.substring(index, index+=2);
if (comKaime.getPageType() == '2') {
group.grade = kaime.substring(index, index+=1);
}
group.raceNo = parseInt(kaime.substring(index, index+=2), 10) + '';
group.kakesiki = kaime.substring(index, index+=1);
group.procedures = kaime.substring(index, index+=1);
group.upDate = kaime.substring(index, index+=12);
group.single = {};
var single = kaime.substring(index, index+=15);
if (group.state != '2') {
group.single.kumiban = single.substring(0, 7);
group.single.zenPatternFlg = single.substring(7, 10);
group.single.maisu = single.substring(10, 13).trim();
group.single.result = single.substring(13, 15);
}
group.list = []; 
var meisaiCnt = kaime.substring(index).length / 24;
for (var i=0;i<meisaiCnt;i++) {
var meisai = kaime.substring(index, index+=24);
var tmp = {};
tmp.kumiban = meisai.substring(0, 7);
tmp.maisu =  meisai.substring(7, 10).trim();
tmp.result = meisai.substring(10, 12);
tmp.ozz = parseFloat(meisai.substring(12, 18));
tmp.ozzMax = parseFloat(meisai.substring(18, 24));
group.list[group.list.length] = tmp;
}
return group;
},
setGroup : function (group) {
var kimcnt = window.sessionStorage.getItem(comKaime.KIM_CNT_KEY);
if (!kimcnt || isNaN(kimcnt)) {
kimcnt = 0;
}
var addFlg = false;
if (group.groupId == "Tmp" + comKaime.KIM_KEY_PRE) {
group.groupId = comKaime.KIM_KEY_PRE + kimcnt;
addFlg = true;
}
var kaime = '';
kaime = kaime + group.setState;
kaime = kaime + group.state;
kaime = kaime + group.kaisaiDate;
kaime = kaime + group.keirinjyo;
if (comKaime.getPageType() == '2') {
kaime = kaime + comKaime.getFixedStr(' ' + group.grade, '2', 1);
}
kaime = kaime + comKaime.getFixedStr('00' + group.raceNo, '2', 2);
kaime = kaime + group.kakesiki;
kaime = kaime + group.procedures;
if (group.upDate) {
kaime = kaime + group.upDate;
} else {
kaime = kaime + comKaime.getFixedStr('            ', '1', 12);
}
if (group.state == '2') {
kaime = kaime + comKaime.getFixedStr('               ', '1', 15);
} else {
kaime = kaime + group.single.kumiban;
kaime = kaime + comKaime.getFixedStr('000' + group.single.zenPatternFlg, '2', 3);
kaime = kaime + comKaime.getFixedStr('   ' + group.single.maisu, '2', 3);
if (group.single.result) {
kaime = kaime + comKaime.getFixedStr(group.single.result + '  ', '1', 2);
} else {
kaime = kaime + '  ';
}
}
for (var i=0;i<group.list.length;i++) {
var meisai = group.list[i];
kaime = kaime + meisai.kumiban;
kaime = kaime + comKaime.getFixedStr('   ' + meisai.maisu, '2', 3);
if (meisai.result) {
kaime = kaime + comKaime.getFixedStr(meisai.result + '  ', '1', 2);
} else {
kaime = kaime + '  ';
}
var ozz = '';
if (meisai.ozz) {
ozz = meisai.ozz;
}
kaime = kaime + comKaime.getFixedStr('000000' + ozz, '2', 6);
if (meisai.ozzMax) {
kaime = kaime + comKaime.getFixedStr('000000' + meisai.ozzMax, '2', 6);
} else {
kaime = kaime + '000000';
}
}
window.sessionStorage.setItem(group.groupId, kaime);
if (addFlg) {
window.sessionStorage.setItem(comKaime.KIM_CNT_KEY, parseInt(kimcnt) + 1);
}
},
getFixedStr: function(object, fixdFlg, len) {
var ret = '';
if (fixdFlg == '1') {
ret = object.substring(0, len);
} else if (fixdFlg == '2') {
if (object.length > len) {
ret = object.substring(object.length - len);
} else {
ret = object;
}
}
return ret;
},
kimSaveTmpForSkn: function(kaimeGroupList) {
for (var i=0;i<kaimeGroupList.length;i++) {
var group = kaimeGroupList[i];
var sikin = '';
sikin = comKaime.getFixedStr(group.groupId + '  ', '1', 6);
for (var j=0;j<group.list.length;j++) {
sikin = sikin + comKaime.getFixedStr('000' + group.list[j].itemId, '2', 3);
sikin = sikin + comKaime.getFixedStr('000' + group.list[j].modifyMaisu, '2', 3);
sikin = sikin + group.list[j].cancel;
}
window.sessionStorage.setItem(comKaime.SKN_KEY_PRE + i, sikin);
}
window.sessionStorage.setItem(comKaime.SKN_CNT_KEY, kaimeGroupList.length);
},
kimGetGroupListWithTmpInfo : function(){
var groupListWithTmpInfo = {};
var sknCnt = parseInt(window.sessionStorage.getItem(comKaime.SKN_CNT_KEY));
for (var i=0;i<sknCnt;i++) {
var sikin = window.sessionStorage.getItem(comKaime.SKN_KEY_PRE + i);
var sknGroup = {"list": []};
var index = 0;
sknGroup.groupId = sikin.substring(index, index+=6).trim(); 
var meisaiCnt = sikin.substring(index).length / 7;
var kimGroup = comKaime.getGroup(sknGroup.groupId);
for (var j=0;j<meisaiCnt;j++) {
var meisai = sikin.substring(index, index+=7);
var tmp = {};
tmp.itemId = parseInt(meisai.substring(0, 3), 10);
tmp.modifyMaisu =  parseInt(meisai.substring(3, 6), 10);
tmp.cancel =  meisai.substring(6, 7);
sknGroup.list[sknGroup.list.length] = tmp;
}
for (var j=0;j<meisaiCnt;j++) {
var kumiInfo = kimGroup.list[sknGroup.list[j].itemId];
var tmpKumiInfo = sknGroup.list[j];
kumiInfo.cancel = tmpKumiInfo.cancel;
if (tmpKumiInfo.modifyMaisu != -1) {
kumiInfo.maisu = tmpKumiInfo.modifyMaisu;
}
}
groupListWithTmpInfo[sknGroup.groupId] = kimGroup;
}
comKaime.kimCancelTmpForSkn();
return groupListWithTmpInfo;
},
kimCommitForSkn: function() {
var groupListWithTmpInfo = comKaime.kimGetGroupListWithTmpInfo();
var dels = [];
for (var groupId in groupListWithTmpInfo) {
var kimGroup = groupListWithTmpInfo[groupId];
var itemDels = [];
for (var j=0;j<kimGroup.list.length;j++) {
if (kimGroup.list[j].cancel == '1') {
itemDels.push(j);
}
}
for (var j=0;j<itemDels.length;j++) {
kimGroup.list.splice(itemDels[j] - j, 1);
}
if (kimGroup.list.length == 0) {
window.sessionStorage.removeItem(kimGroup.groupId);
dels.push(kimGroup.groupId);
} else {
kimGroup.state = '2';
kimGroup.procedures = '0';
kimGroup.single = null;
comKaime.setGroup(kimGroup);
}
}
if (dels.length > 0) {
var kimCnt = parseInt(window.sessionStorage.getItem(comKaime.KIM_CNT_KEY));
var index = 0;
for(var i=0;i<kimCnt;i++) {
var item = window.sessionStorage.getItem(comKaime.KIM_KEY_PRE + i);
if (item) {
if (i != index) {
window.sessionStorage.setItem(comKaime.KIM_KEY_PRE + index, item);
}
index++;
}
}
window.sessionStorage.setItem(comKaime.KIM_CNT_KEY, index);
for (var i=index;i<kimCnt;i++) {
window.sessionStorage.removeItem(comKaime.KIM_KEY_PRE + i);
} 
}
comKaime.kimCancelTmpForSkn();
},
kimCancelTmpForSkn: function() {
var sknCnt = window.sessionStorage.getItem(comKaime.SKN_CNT_KEY);
if (!sknCnt || isNaN(sknCnt)) {
sknCnt = 0;
}
for (var i=0;i<sknCnt;i++) {
window.sessionStorage.removeItem(comKaime.SKN_KEY_PRE + i);
}
window.sessionStorage.removeItem(comKaime.SKN_CNT_KEY);
},
kimUpdOzzForSkn: function(jst003Ret) {
if (!jst003Ret) {
var kaimeCnt = parseInt(window.sessionStorage.getItem(comKaime.KIM_CNT_KEY));
for (var i=0;i<kaimeCnt;i++) {
var group = comKaime.getGroup(comKaime.KIM_KEY_PRE + i);
for(var j=0;j<group.list.length;j++) {
var kumibanArr = comKaime.kimKumibanX2Arr(group.list[j].kumiban);
var kumiban = kumibanArr[0] + kumibanArr[1] + kumibanArr[2];
if (group.kakesiki == '5') { 
group.list[j].ozz = null;
group.list[j].ozzMax = null;
} else {
group.list[j].ozz = null;
}
}
comKaime.setGroup(group);
}
return;
}
if (jst003Ret.updateStopMessage) {
$('#kimLblUpdateStopMsg').html(jst003Ret.updateStopMessage);
} else {
$('#kimLblUpdateStopMsg').html('');
}
if (jst003Ret.resultCd == '-1') {
return;
}
var kaimeOzzInfoList = jst003Ret.kaimeOzzInfoList;
for (var i=0;i<kaimeOzzInfoList.length;i++) {
var groupId = kaimeOzzInfoList[i].groupId;
var ozzInfoList = kaimeOzzInfoList[i].ozzInfoList;
if (groupId != "Tmp" + comKaime.KIM_KEY_PRE) {
var group = comKaime.getGroup(groupId);
for(var j=0;j<group.list.length;j++) {
if (group.list.length * 2 == ozzInfoList.length) { 
var ozz1 = ozzInfoList[j * 2];
var ozz2 = ozzInfoList[j * 2 + 1];
group.list[j].ozz =  ozz1;
group.list[j].ozzMax = ozz2;
} else {
var ozz1 = ozzInfoList[j];
group.list[j].ozz =  ozz1;
}
}
group.upDate = kaimeOzzInfoList[i].upDate;
comKaime.setGroup(group);
}
if (editKaimeGroup && editKaimeGroup.groupId == groupId) {
for(var j=0;j<editKaimeGroup.list.length;j++) {
if (editKaimeGroup.list.length * 2 == ozzInfoList.length) { 
var ozz1 = ozzInfoList[j * 2];
var ozz2 = ozzInfoList[j * 2 + 1];
editKaimeGroup.list[j].ozz =  ozz1;
editKaimeGroup.list[j].ozzMax = ozz2;
} else {
var ozz1 = ozzInfoList[j];
editKaimeGroup.list[j].ozz =  ozz1;
}
}
editKaimeGroup.upDate = kaimeOzzInfoList[i].upDate;
}
}
},
kimIfSessionStorage : function(){
    var flg = false;
    try{
        if(('sessionStorage' in window) && window.sessionStorage != null){
        window.sessionStorage.setItem('_k', '_v');
        window.sessionStorage.removeItem('_k');
        flg = true;
        }
    }catch(e){}
    return flg;
}
};
var comDialog = {
okFun: null,
cancelFun:null,
confirm: function(message, okFun, cancelFun, width) {
if ($('#kim_conf_dialog').length > 0) {
$('#kim_conf_dialog').remove();
}
$(document.body).append(comDialog.createConfirmDialog(width));
$('#kimConfirmMsg').html(message);
$('#kim_conf_dialog').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'kim_conf_dialog',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(document).off("click", ".ui-widget-overlay");
$(".kim_conf_dialog .ui-dialog-titlebar").hide();
dialog_flag = true;
},
close: function(event, ui){
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
comDialog.okFun = okFun;
comDialog.cancelFun = cancelFun;
    $('#kim_conf_dialog').dialog('open');
},
alert: function(message, okFun) {
if ($('#kim_alert_dialog').length > 0) {
$('#kim_alert_dialog').remove();
}
$(document.body).append(comDialog.createAlertDialog());
$('#kimAlertMsg').html(message);
$('#kim_alert_dialog').dialog({
autoOpen: false,
height: 'auto',
width: 'auto',
draggable: false,
resizable: false,
modal: true,
closeOnEscape: true,
dialogClass: 'kim_alert_dialog',
position: {
at: 'center center',
my: 'center center'
},
open: function(event, ui){
$(document).off("click", ".ui-widget-overlay");
$(".kim_alert_dialog .ui-dialog-titlebar").hide();
dialog_flag = true;
},
close: function(event, ui){
$(document).on("click", ".ui-widget-overlay", function(){
$(".ui-dialog-content").dialog("close");
});
dialog_flag = false;
}
});
comDialog.okFun = okFun;
    $('#kim_alert_dialog').dialog('open');
},
createAlertDialog: function() {
var html = '<div id="kim_alert_dialog" class="kim_alert_dialog">' + 
'<div class="">' + 
    '<div style="margin:10px; width:260px;">' + 
    '<p class="al-c" id="kimAlertMsg"></p>' + 
    '<div class="al-c" style="padding-top:10px">' + 
    '<button id="kim_alert_ok_btn" onclick="comDialog.okForAlert();" type="button" class="btn onbtn" style="width:100px;">OK</button>' + 
    '</div>' + 
    '</div>' + 
    '</div>' + 
    '</div>' + 
    '<style type="text/css">' + 
    '#kim_alert_dialog {' + 
    'background-color: #F5F4F2 !important;' + 
    'box-shadow: 3px 3px 4px rgba(0,0,0,0.60);' + 
    'padding: 5px 10px 15px 10px;' + 
    'border: 2px solid #0670b1;' + 
    '-moz-border-radius: 6px;' + 
    '-webkit-border-radius: 6px;' + 
    '-o-border-radius: 6px;' + 
    '-ms-border-radius: 6px;' + 
    'border-radius: 6px;' + 
    'margin: 0 auto;' + 
    '}' + 
    '.ui-widget-overlay {' + 
    'z-index: 10000 !important;' + 
    '}' + 
    '.ui-dialog {' + 
    'z-index: 10001 !important;' + 
    '}' + 
    '</style>';
return html;
},
createConfirmDialog: function(width) {
var widthHtml = '';
if (width) {
widthHtml = 'width:' + width + 'px;';
} else {
widthHtml = 'width:260px;';
}
var html = '<div id="kim_conf_dialog" class="kim_conf_dialog">' + 
    '<div class="">' + 
    '<div  class="al-c" style="margin:10px;' + widthHtml + '">' + 
    '<span id="kimConfirmMsg"></span>' + 
    '<div class="al-c" style="padding-top:10px">' + 
    '<button id="kim_confirm_cancel_btn" onclick="comDialog.cancelForConfirm();" type="button" class="btn onbtn" style="width:100px;">キャンセル</button>' + 
    '<button id="kim_confirm_ok_btn" onclick="comDialog.okForConfirm();" type="button" class="btn onbtn kim_confirm_ok_btn" style="width:100px;">OK</button>' + 
    '</div>' + 
    '</div>' + 
    '</div>' + 
    '</div>' + 
    '<style type="text/css">' + 
    '#kim_conf_dialog {' + 
    'background-color: #F5F4F2 !important;' + 
    'box-shadow: 3px 3px 4px rgba(0,0,0,0.60);' + 
    'padding: 5px 10px 15px 10px;' + 
    'border: 2px solid #0670b1;' + 
    '-moz-border-radius: 6px;' + 
    '-webkit-border-radius: 6px;' + 
    '-o-border-radius: 6px;' + 
    '-ms-border-radius: 6px;' + 
    'border-radius: 6px;' + 
    'margin: 0 auto;' + 
    '}' + 
    '.ui-widget-overlay {' + 
    'z-index: 10000 !important;' + 
    '}' + 
    '.ui-dialog {' + 
    'z-index: 10001 !important;' + 
    '}' + 
    '.kim_confirm_ok_btn {' + 
    'margin-left: 5px;' + 
    '}' + 
    '</style>';
return html;
},
    okForAlert: function () {
$('#kim_alert_dialog').dialog('close');
if (comDialog.okFun) {
comDialog.okFun();
}
    },
cancelForConfirm: function () {
$('#kim_conf_dialog').dialog('close');
if (comDialog.cancelFun) {
comDialog.cancelFun();
}
    },
    okForConfirm: function () {
$('#kim_conf_dialog').dialog('close');
if (comDialog.okFun) {
comDialog.okFun();
}
    }
}