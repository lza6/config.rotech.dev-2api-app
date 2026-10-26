Java.perform(function(){
  var Z3a = Java.use("Z3.a");
  var f = Z3a.class.getDeclaredField("f9215a");
  f.setAccessible(true);
  console.log("SIG_FIELD:" + f.get(null));
  // 同时静态调用 c() 重新取
  var ActivityThread = Java.use("android.app.ActivityThread");
  var ctx = ActivityThread.currentApplication().getApplicationContext();
  console.log("SIG_CALL:" + Z3a.c(ctx));
});
