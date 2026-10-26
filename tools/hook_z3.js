// Frida hook: OpenChat (open.chat.gpt.aichat.bot.free.app)
// 目标: Z3.a.b (请求加密) / Z3.a.a (响应解密) — dump 明文协议
// 用法: frida -U -f open.chat.gpt.aichat.bot.free.app -l hook_z3.js --no-pause
Java.perform(function () {
    try {
        var Z3a = Java.use("Z3.a");

        Z3a.a.overload("android.content.Context", "java.lang.String").implementation = function (ctx, s) {
            var out = this.a(ctx, s);
            console.log("\n========== [DECRYPT 响应] ==========");
            console.log("密文: " + (s ? s.substring(0, 100) : "null") + "...");
            console.log("明文: " + out);
            return out;
        };

        Z3a.b.overload("android.content.Context", "java.lang.String").implementation = function (ctx, s) {
            var out = this.b(ctx, s);
            console.log("\n========== [ENCRYPT 请求] ==========");
            console.log("明文: " + s);
            console.log("密文: " + (out ? out.substring(0, 100) + "..." : "null"));
            return out;
        };

        // dump 派生 key
        Z3a.c.overload("android.content.Context").implementation = function (ctx) {
            var sig = this.c(ctx);
            console.log("\n[KEY-SRC] signature.toCharsString() = " + sig);
            return sig;
        };

        console.log("[*] Z3 hooks installed");
    } catch (e) {
        console.log("[!] Z3 hook failed: " + e);
    }

    // 顺带 hook T9.c HTTP 层拿 URL
    try {
        var T9c = Java.use("T9.c");
        T9c.a.overload("android.content.Context", "java.lang.String", "java.util.Map", "T9.b")
          .implementation = function (ctx, url, map, cb) {
            console.log("\n[HTTP] POST " + url);
            var it = map.entrySet().iterator();
            while (it.hasNext()) {
                var e = it.next();
                var v = e.getValue().toString();
                console.log("  " + e.getKey() + " = " + v.substring(0, 120) + (v.length > 120 ? "..." : ""));
            }
            return this.a(ctx, url, map, cb);
        };
        console.log("[*] T9 hooks installed");
    } catch (e) {
        console.log("[!] T9 hook failed: " + e);
    }
});
