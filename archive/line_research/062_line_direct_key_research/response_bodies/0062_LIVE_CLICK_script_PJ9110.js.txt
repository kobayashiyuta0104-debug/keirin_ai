function piInitialize(prm, thinFlg){
PJ9110Controller.reqTanpyoTenkai(prm, thinFlg);
}
function pibtnResultClick(url, prm){
commonSubmit.formPost(url, { "disp" : "PJ0326", 'encp' : prm }, "_blank");
}
function pibtnDigestClick(url, jyoCd, kaisaihi, raceNo){
piDigestPrm(url, jyoCd, kaisaihi, raceNo);
}
function piDigestPrm(url, jyoCd, kaisaihi, raceNo){
var digestParams = new Array();
var prm = {};
prm.bkcd = jyoCd;
prm.kday = kaisaihi;
prm.rnum = raceNo;
digestParams.push(prm);
commonSubmit.formPost(url, { 'prmsDigestList' : JSON.stringify(digestParams) }, "_blank");
}
