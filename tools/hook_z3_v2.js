// Frida hook v2: OpenChat — 完整 dump 请求/响应明文 + key 派生 + HTTP URL
Java.perform(function () {
    var Z3a = Java.use("Z3.a");

    // 响应解密
    Z3a.a.overload("android.content.Context", "java.lang.String").implementation = function (ctx, s) {
        var out = this.a(ctx, s);
        console.log("\n##### DECRYPT-RESP #####");
        console.log("CIPHER_B64:" + s);
        console.log("PLAIN:" + out);
        return out;
    };

    // 请求加密
    Z3a.b.overload("android.content.Context", "java.lang.String").implementation = function (ctx, s) {
        var out = this.b(ctx, s);
        console.log("\n##### ENCRYPT-REQ #####");
        console.log("PLAIN:" + s);
        console.log("CIPHER_B64:" + out);
        return out;
    };

    // key 源
    Z3a.c.overload("android.content.Context").implementation = function (ctx) {
        var sig = this.c(ctx);
        console.log("##### SIG-HEX:" + sig);
        return sig;
    };

    // HTTP 层: URL + form + 响应原文
    var T9c = Java.use("T9.c");
    T9c.a.overload("android.content.Context", "java.lang.String", "java.util.Map", "T9.b")
      .implementation = function (ctx, url, map, cb) {
        console.log("\n##### HTTP-REQ:" + url);
        return this.a(ctx, url, map, cb);
    };

    // OkHttp Response body 已在 T9$c$a onResponse 里读到 strQ, hook Z3.a.a 即可覆盖
    console.log("[*] hooks v2 installed");
});
