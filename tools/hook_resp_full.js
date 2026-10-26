Java.perform(function(){
  function hex(b){var s="";for(var i=0;i<b.length;i++){var c=b[i]&0xff;s+=("0"+c.toString(16)).slice(-2);}return s;}
  var Cipher = Java.use("javax.crypto.Cipher");
  Cipher.doFinal.overloads.forEach(function(ov){
    ov.implementation = function(){
      var out = ov.apply(this, arguments);
      try {
        var algo = this.getAlgorithm();
        if (algo === "AES/CBC/PKCS5Padding") {
          var input = arguments[0];
          var enc = Java.use("android.util.Base64").encodeToString(input, 2);
          var dec = Java.use("android.util.Base64").encodeToString(out, 2);
          var f = Java.use("java.io.File").$new("/data/local/tmp/z3dump.txt");
          var fw = Java.use("java.io.FileWriter").$new(f, true);
          fw.write("===MODE:" + algo + "\nIN:" + enc + "\nOUT:" + dec + "\n");
          fw.close();
        }
      } catch(e){}
      return out;
    };
  });
  console.log("[*] full dump ready");
});
