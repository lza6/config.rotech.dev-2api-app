Java.perform(function(){
  function bytesToStr(b){ var s=""; for(var i=0;i<b.length&&i<8000;i++){var c=b[i]&0xff; if(c>=32&&c<127)s+=String.fromCharCode(c); else if(c===10||c===13)s+="\n"; else s+=".";} return s; }
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.doFinal.overloads.forEach(function(ov){
    ov.implementation = function(){
      var out = ov.apply(this, arguments);
      try {
        var algo = this.getAlgorithm();
        if (algo.indexOf("AES") >= 0) {
          var input = arguments[0];
          if (input && input.length !== undefined) {
            var enc = Java.use("android.util.Base64").encodeToString(input, 2);
            console.log("##### C[" + algo + "]");
            console.log("IN:" + enc.substring(0, 5000));
            console.log("OUT:" + bytesToStr(out));
          }
        }
      } catch(e){}
      return out;
    };
  });
  console.log("[*] cipher2 ready");
});
