function chkInputEmp(p_val)
{
var strTarget = ''+p_val;
if (strTarget && (strTarget.match(/\S/g)))
{
return true;
}
else
{
    return false;
}
}
function chkInputNum(p_val)
{
var strTarget = ''+p_val;
if (!strTarget)
{
return false;
}
if (strTarget.match(/^([1-9]\d*|0)$/))
{
return true;
}
else
{
return false;
}
}
function chkNumPass(p_val)
{
var strTarget = ''+p_val;
if (strTarget.match(/^\d*$/))
{
return true;
}
else
{
return false;
}
}
function chkNumRange(p_val,p_min,p_max)
{
var strTarget = p_val;
if (p_min <= strTarget && strTarget <= p_max)
{
return true;
}
else
{
return false;
}
}
function chkNumLength(p_val,p_min_length,p_max_length){
var strTarget = ''+p_val;
var nTargetLength = strTarget.length;
if (Number(p_min_length) <= nTargetLength && nTargetLength<= Number(p_max_length))
{
return true;
}
else
{
return false;
}
}