Java.perform(function(){
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.doFinal.overload("[b").implementation = function(input){
    var out = this.doFinal(input);
    var algo = this.getAlgorithm();
    if (algo.indexOf("AES") >= 0) {
      var enc = Java.use("android.util.Base64").encodeToString(input, 2);
      var dec = Java.use("android.util.Base64").encodeToString(out, 2);
      // 只要短的(聊天响应对话) — 打印全部但截断
      console.log("##### CIPHER[" + algo + "] mode=" + opmode_str(this));
      console.log("IN_B64:" + enc.substring(0, 300));
      console.log("OUT_STR:" + bytesToStr(out).substring(0, 500));
    }
    return out;
  };
  function opmode_str(c){ return ""; }
  function bytesToStr(b){
    var s=""; for(var i=0;i<b.length && i<500;i++){ var c=b[i]; if(c>=32&&c<127) s+=String.fromCharCode(c); else if(c==10||c==13) s+="\n"; else s+="."; } return s;
  }
  console.log("[*] cipher hook ready");
});
