Java.perform(function(){
  var PM = Java.use("android.app.ApplicationPackageManager");
  PM.getPackageInfo.overload("java.lang.String","int").implementation = function(pkg, flags){
    var pi = this.getPackageInfo(pkg, flags);
    if ((flags & 64) == 64 || (flags & 0x08000000) == 0x08000000) {
      console.log("##### GETPKG pkg=" + pkg + " flags=" + flags);
      if (pi.signatures.value) {
        for (var i=0;i<pi.signatures.value.length;i++){
          var s = pi.signatures.value[i];
          console.log("##### SIG-TCHARS:" + s.toCharsString());
          console.log("##### SIG-BYTES-LEN:" + s.toByteArray().length);
        }
      }
      if (pi.signingInfo.value) {
        var si = pi.signingInfo.value;
        var sc = si.getSigningCertificateHistory();
        for (var i=0;i<sc.length;i++){
          console.log("##### V3-CERT:" + Java.use("android.util.Base64").encodeToString(sc[i].toBytes?sc[i].toBytes():sc[i], 2));
        }
      }
    }
    return pi;
  };
  console.log("[*] sig hook ready");
});
