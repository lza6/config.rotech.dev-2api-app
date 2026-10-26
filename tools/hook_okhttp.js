Java.perform(function(){
  // hook RealCall 拿 response body string 的路径太深; 直接 hook Z3.a.a 的调用者 T9$c$a.onResponse 拿 strQ
  var Callback = Java.use("T9.c$a");
  Callback.onResponse.implementation = function(call, response){
    var body = response.f27333g; // ResponseBody (jadx name) — runtime name may differ
    try {
      var rb = response.body ? response.body() : null;
      if (rb) console.log("##### RESP-BODY:" + rb.string());
    } catch(e){ console.log("##### body-err:" + e); }
    return this.onResponse(call, response);
  };
  console.log("[*] okhttp hook ready");
});
