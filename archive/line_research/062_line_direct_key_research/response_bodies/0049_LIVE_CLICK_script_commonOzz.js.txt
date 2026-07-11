function doubleClick(id){
var stopTime=5000;
if(id) $("[id='"+id+"']").prop("disabled",true);
$("[ozzuDoubleClickStop='1']").prop("disabled",true);
if(id) window.setTimeout('$("[id=\'' +id +'\']").prop("disabled",false)',stopTime);
window.setTimeout('$("[ozzuDoubleClickStop]").prop("disabled",false)',stopTime);
}