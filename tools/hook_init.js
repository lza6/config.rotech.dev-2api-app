Java.perform(function(){
  function hex(b){var s="";for(var i=0;i<b.length;i++){var c=b[i]&0xff;s+=("0"+c.toString(16)).slice(-2);}return s;}
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.init.overloads.forEach(function(ov){
    var paramTypes = ov.argumentTypes.map(function(t){return t.className;}).join(",");
    if (paramTypes.indexOf("java.security.Key") >= 0) {
      ov.implementation = function(){
        try {
          var key = arguments[1];
          var enc = key.getEncoded();
          if (enc) console.log("##### KEYINIT algo=" + this.getAlgorithm() + " key=" + hex(enc));
        } catch(e){ console.log("##### keyinit-err:" + e); }
        return ov.apply(this, arguments);
      };
    }
  });
  console.log("[*] init hook ready");
});
