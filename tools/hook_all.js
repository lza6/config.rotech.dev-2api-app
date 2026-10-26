Java.perform(function(){
  var Z3a = Java.use("Z3.a");
  var methods = Z3a.class.getDeclaredMethods();
  methods.forEach(function(m){
    var name = m.getName();
    try {
      var overloads = Z3a[name].overloads;
      overloads.forEach(function(ov){
        ov.implementation = function(){
          var args = Array.prototype.slice.call(arguments);
          var ret = ov.apply(this, args);
          console.log("##### M:" + name + " argc=" + args.length +
            " arg0=" + (typeof args[0]==='string'? args[0].substring(0,60): typeof args[0]) +
            " ret=" + (typeof ret==='string'? ret.substring(0,120) : String(ret).substring(0,60)));
          return ret;
        };
      });
    } catch(e){}
  });
  console.log("[*] all-method hook ready");
});
