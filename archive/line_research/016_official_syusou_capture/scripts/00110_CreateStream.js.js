var liveStreamPalyer = null;
function CreateStream(aLiveUrl){
try {
liveStreamPalyer = dashjs.MediaPlayer().create();
liveStreamPalyer.initialize(document.querySelector("#videoPlayer"), aLiveUrl, false);
liveStreamPalyer.setVolume(0.0);
} catch (e) {
DestroyStream();
}
}
function DestroyStream(){
if (liveStreamPalyer != null) {
try {
liveStreamPalyer.reset();
} catch (e) {
;
}
liveStreamPalyer = null;
}
}
