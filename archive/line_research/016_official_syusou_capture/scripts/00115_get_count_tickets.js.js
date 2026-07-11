function getCountTickets(kakesikiCd, selectSyaWakubanList, proceduresKubun, syaban2WakubanStr) {
var returnCount;
var returnSyaWakubanList = new Array();
returnSyaWakubanList = getListTickets(kakesikiCd, selectSyaWakubanList, proceduresKubun, syaban2WakubanStr);
returnCount = returnSyaWakubanList.length
return(returnCount);
}
