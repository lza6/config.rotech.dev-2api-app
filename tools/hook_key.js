Java.perform(function(){
  function hex(b){var s="";for(var i=0;i<b.length;i++){var c=b[i]&0xff;s+=("0"+c.toString(16)).slice(-2);}return s;}
  var SKS = Java.use("javax.crypto.spec.SecretKeySpec");
  SKS.$init.overload("[b","java.lang.String").implementation = function(key, algo){
    if (algo.indexOf("AES") >= 0 && key.length === 16) {
      console.log("##### AESKEY:" + hex(key));
    }
    return this.$init(key, algo);
  };
  var IVPS = Java.use("javax.crypto.spec.IvParameterSpec");
  IVPS.$init.overload("[b").implementation = function(iv){
    console.log("##### AESIV:" + hex(iv));
    return this.$init(iv);
  };
  console.log("[*] key hook ready");
});
