$(window).load(function() {
    $("a").click(function(){
    if($(this).hasClass("notlink")){
    return false;
    }
    });
});
var commonLink = {
    NewWindow: function (url,WinFlag,prm){
        if(WinFlag == 0){
            window.open(url,"_blank");
        } else if(WinFlag == 1) {
            var actn = "";
            var key = "";
            var val = "";
            var lprm = {};
            var indexcount = url.indexOf("?")+1;
            if(url.indexOf("?") == -1){
                actn = url;
                if(prm){
                    lprm = prm;
                }
            }else{
                actn = url.substring(0,url.indexOf("?"));
                while(true){   
                    key = "";
                    val = "";
                    key = url.substring(indexcount,url.indexOf("=",indexcount));
                    val = url.substring(url.indexOf("=",indexcount+key.length)+1,url.indexOf("&"));
                    if(url.indexOf("&",indexcount) == -1){
                        indexcount = url.indexOf("=",indexcount+key.length)+1;
                        val = url.substring(indexcount);
                        lprm[key] = val;
                        break;
                    }else{
                        lprm[key] = val;
                        indexcount = url.indexOf("&",indexcount)+1;
                    }
                }
            }
            window.open("about:blank","subwin","width=480,height=535");   
            commonSubmit.formGet(actn,lprm,"subwin");
        }
    }
};
