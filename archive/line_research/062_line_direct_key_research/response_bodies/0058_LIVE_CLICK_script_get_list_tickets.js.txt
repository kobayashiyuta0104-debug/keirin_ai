function getListTickets(kakesikiCd, selectSyaWakubanList,proceduresKubun,syaban2WakubanStr) {
var returnSyaWakubanList = new Array();
var tyakuSyaWakubanStr1;
var tyakuSyaWakubanStr2;
var tyakuSyaWakubanStr3;
var sl1;
var sl2;
var sl3;
var slwk;
if(kakesikiCd == '6' || kakesikiCd == '7'){
tyakuSyaWakubanStr1 = selectSyaWakubanList[0];
tyakuSyaWakubanStr2 = selectSyaWakubanList[1];
tyakuSyaWakubanStr3 = selectSyaWakubanList[2];
sl1 = tyakuSyaWakubanStr1.length;
sl2 = tyakuSyaWakubanStr2.length;
sl3 = tyakuSyaWakubanStr3.length;
}else{
tyakuSyaWakubanStr1 = selectSyaWakubanList[0];
tyakuSyaWakubanStr2 = selectSyaWakubanList[1];
sl1 = tyakuSyaWakubanStr1.length;
sl2 = tyakuSyaWakubanStr2.length;
}
if(kakesikiCd == '3' || kakesikiCd == '1'){
slwk = syaban2WakubanStr.length;
}else{
}
if(kakesikiCd == '6'){
for( i1=0; i1<sl1; i1++ ){
for( i2=0; i2<sl2; i2++ ){
for( i3=0; i3<sl3; i3++ ){
if( tyakuSyaWakubanStr1.charAt(i1)!=tyakuSyaWakubanStr2.charAt(i2) && tyakuSyaWakubanStr1.charAt(i1)!=tyakuSyaWakubanStr3.charAt(i3) && tyakuSyaWakubanStr2.charAt(i2)!=tyakuSyaWakubanStr3.charAt(i3)){
returnSyaWakubanList.push(tyakuSyaWakubanStr1.charAt(i1)+tyakuSyaWakubanStr2.charAt(i2)+tyakuSyaWakubanStr3.charAt(i3));
}else{
continue;
}
}
}
}
}else if(kakesikiCd == '7'){
var sp = new Array();
var cnt = 0;
for( i1=0; i1<sl1; i1++ ){
for( i2=0; i2<sl2; i2++ ){
for( i3=0; i3<sl3; i3++ ){
if( tyakuSyaWakubanStr1.charAt(i1)==tyakuSyaWakubanStr2.charAt(i2) || tyakuSyaWakubanStr1.charAt(i1)==tyakuSyaWakubanStr3.charAt(i3) || tyakuSyaWakubanStr2.charAt(i2)==tyakuSyaWakubanStr3.charAt(i3) ){
continue;
} else {
var t = new Array();
t[0] = tyakuSyaWakubanStr1.charAt(i1);
t[1] = tyakuSyaWakubanStr2.charAt(i2);
t[2] = tyakuSyaWakubanStr3.charAt(i3);
t.sort();
var t1 = t[0]+t[1]+t[2];
var flag=0;
for( i=0; i<sp.length; i++ ){
if(t1==sp[i]) {
flag=1;
break;
}
}
if( flag==0 ){
returnSyaWakubanList.push(t1);
sp[cnt]=t1;
cnt++;
}
}
}
}
}
}else if(kakesikiCd == '4' || kakesikiCd == '5' || kakesikiCd == '1'){
var sp = new Array();
var cnt=0;
for( i1=0; i1<sl1; i1++ ){
for( i2=0; i2<sl2; i2++ ){
if( tyakuSyaWakubanStr1.charAt(i1)==tyakuSyaWakubanStr2.charAt(i2) ){
continue;
}else{
var t = new Array();
t[0] = tyakuSyaWakubanStr1.charAt(i1);
t[1] = tyakuSyaWakubanStr2.charAt(i2);
t.sort();
var t1 = t[0]+t[1];
var flag=0;
for( i=0; i<sp.length; i++ ){
if(t1==sp[i]) {
flag=1; 
break; 
}
}
if( flag==0 ){
returnSyaWakubanList.push(t1);
sp[cnt]=t1;
cnt++;
}
}
}
}
}else if(kakesikiCd == '2' || kakesikiCd == '3'){
for( i1=0; i1<sl1; i1++ ){
for( i2=0; i2<sl2; i2++ ){
if( tyakuSyaWakubanStr1.charAt(i1)!=tyakuSyaWakubanStr2.charAt(i2) ){
returnSyaWakubanList.push(tyakuSyaWakubanStr1.charAt(i1)+tyakuSyaWakubanStr2.charAt(i2));
}else{
continue;
}
}
}
}
if(proceduresKubun == '1'){
if(kakesikiCd == '3' || kakesikiCd == '1'){
for( iw=0; iw<slwk; iw++ ){
for( i1=0; i1<sl1; i1++ ){
for( i2=0; i2<sl2; i2++ ){
if( tyakuSyaWakubanStr1.charAt(i1)==syaban2WakubanStr.charAt(iw) && tyakuSyaWakubanStr2.charAt(i2)==syaban2WakubanStr.charAt(iw) ){
returnSyaWakubanList.push(tyakuSyaWakubanStr1.charAt(i1)+tyakuSyaWakubanStr2.charAt(i2));
}else{
continue;
}
}
}
}
}
}
return(returnSyaWakubanList.sort());
}
