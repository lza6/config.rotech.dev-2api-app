package S9;

import A0.f;
import A1.B;
import H8.h;
import H8.o;
import M8.d;
import M8.g;
import O8.e;
import O8.i;
import Qa.x;
import W8.p;
import Ya.C0956a;
import Ya.Z;
import android.content.Context;
import android.util.Log;
import com.google.ads.mediation.facebook.FacebookMediationAdapter;
import com.inmobi.media.core.config.models.AdConfig;
import java.util.HashMap;
import java.util.Locale;
import kotlin.jvm.internal.l;
import org.json.JSONException;
import org.json.JSONObject;
import p091h9.G;
import p091h9.G0;
import p091h9.H;
import p091h9.K;
import p091h9.X;
import p147m9.C1977c;

/* JADX INFO: loaded from: classes3.dex */
public final class b {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public static final C1977c f7847a;

    @e(c = "open.chat.gpt.aichat.bot.free.app.net.app.ChatGPTNetUtil$doRequest$1", f = "ChatGPTNetUtil.kt", l = {AdConfig.DEFAULT_AD_QUALITY_RESIZE_PERCENTAGE}, m = "invokeSuspend")
    public static final class a extends i implements p<G, d<? super o>, Object> {

        /* JADX INFO: renamed from: r, reason: collision with root package name */
        public int f7848r;

        /* JADX INFO: renamed from: s, reason: collision with root package name */
        public final /* synthetic */ Context f7849s;

        /* JADX INFO: renamed from: t, reason: collision with root package name */
        public final /* synthetic */ String f7850t;

        /* JADX INFO: renamed from: u, reason: collision with root package name */
        public final /* synthetic */ String f7851u;

        /* JADX INFO: renamed from: v, reason: collision with root package name */
        public final /* synthetic */ String f7852v;

        /* JADX INFO: renamed from: w, reason: collision with root package name */
        public final /* synthetic */ Integer f7853w;

        /* JADX INFO: renamed from: x, reason: collision with root package name */
        public final /* synthetic */ String f7854x;

        /* JADX INFO: renamed from: y, reason: collision with root package name */
        public final /* synthetic */ M9.c f7855y;

        /* JADX INFO: renamed from: z, reason: collision with root package name */
        public final /* synthetic */ S9.a f7856z;

        /* JADX INFO: renamed from: S9.b$a$a, reason: collision with other inner class name */
        public static final class C0093a implements T9.b {

            /* JADX INFO: renamed from: a, reason: collision with root package name */
            public final /* synthetic */ Integer f7857a;

            /* JADX INFO: renamed from: b, reason: collision with root package name */
            public final /* synthetic */ Context f7858b;

            /* JADX INFO: renamed from: c, reason: collision with root package name */
            public final /* synthetic */ S9.a f7859c;

            public C0093a(Integer num, Context context, S9.a aVar) {
                this.f7857a = num;
                this.f7858b = context;
                this.f7859c = aVar;
            }

            @Override // T9.b
            public final void d(String str) {
                Object objA;
                S9.a aVar = this.f7859c;
                Context context = this.f7858b;
                C6.a.h("jsonString = ".concat(str));
                Integer num = this.f7857a;
                if (num == null || num.intValue() == 0) {
                    W9.a.f8706a.getClass();
                    W9.a.f("chat");
                }
                try {
                    JSONObject jSONObject = new JSONObject(str);
                    JSONObject jSONObjectOptJSONObject = jSONObject.optJSONObject("data");
                    String strOptString = jSONObjectOptJSONObject != null ? jSONObjectOptJSONObject.optString("content") : null;
                    Integer numValueOf = jSONObjectOptJSONObject != null ? Integer.valueOf(jSONObjectOptJSONObject.optInt(FacebookMediationAdapter.KEY_ID, -1)) : null;
                    Integer numValueOf2 = jSONObjectOptJSONObject != null ? Integer.valueOf(jSONObjectOptJSONObject.optInt("code", -1)) : null;
                    l.e(context, "context");
                    if (numValueOf2 != null && numValueOf2.intValue() == 0) {
                        Boolean bool = C0956a.f9074a;
                        C0956a.k("chat_api", "result_0");
                        o oVar = o.f3683a;
                    } else if (numValueOf2 != null && numValueOf2.intValue() == 1) {
                        Boolean bool2 = C0956a.f9074a;
                        C0956a.k("chat_api", "result_1");
                        q9.c cVar = U2.b.f8182a;
                        U2.b.d(context, "chat_api(answerId=" + numValueOf + "): result_1");
                    } else if (numValueOf2 != null && numValueOf2.intValue() == 2) {
                        Boolean bool3 = C0956a.f9074a;
                        C0956a.k("chat_api", "result_2");
                        q9.c cVar2 = U2.b.f8182a;
                        U2.b.d(context, "chat_api(answerId=" + numValueOf + "): result_2");
                    } else {
                        q9.c cVar3 = U2.b.f8182a;
                        U2.b.d(context, "Error, chat_api(answerId=" + numValueOf + ")");
                    }
                    if (strOptString == null || strOptString.length() == 0 || numValueOf == null || numValueOf.intValue() == -1) {
                        aVar.a("error ".concat(str), null);
                    } else {
                        aVar.c(numValueOf.intValue(), strOptString);
                    }
                    if (num == null || num.intValue() == 0) {
                        W9.a.f8706a.getClass();
                        W9.a.i(jSONObject, "chat");
                    }
                    objA = o.f3683a;
                } catch (Throwable th) {
                    objA = H8.i.a(th);
                }
                Throwable thA = h.a(objA);
                if (thA != null) {
                    aVar.a("parse error: " + thA, null);
                    q9.c cVar4 = U2.b.f8182a;
                    U2.b.d(context, "doRequest parse error: \n" + Log.getStackTraceString(thA));
                    if (num == null || num.intValue() == 0) {
                        W9.a.f8706a.getClass();
                        W9.a.c(str, "chat");
                    }
                }
            }

            @Override // T9.b
            public final void onFailure(Exception exc) {
                String error = exc.toString();
                Context context = this.f7858b;
                l.e(context, "context");
                l.e(error, "error");
                this.f7859c.a("e = " + exc, exc);
                q9.c cVar = U2.b.f8182a;
                U2.b.d(context, "doRequest onFailure: \n" + Log.getStackTraceString(exc));
                Integer num = this.f7857a;
                if (num == null || num.intValue() == 0) {
                    W9.a.f8706a.getClass();
                    W9.a.d("chat", exc);
                }
            }
        }

        /* JADX WARN: 'super' call moved to the top of the method (can break code semantics) */
        public a(Context context, String str, String str2, String str3, Integer num, String str4, M9.c cVar, S9.a aVar, d dVar) {
            super(2, dVar);
            this.f7849s = context;
            this.f7850t = str;
            this.f7851u = str2;
            this.f7852v = str3;
            this.f7853w = num;
            this.f7854x = str4;
            this.f7855y = cVar;
            this.f7856z = aVar;
        }

        @Override // O8.a
        public final d<o> create(Object obj, d<?> dVar) {
            return new a(this.f7849s, this.f7850t, this.f7851u, this.f7852v, this.f7853w, this.f7854x, this.f7855y, this.f7856z, dVar);
        }

        @Override // W8.p
        public final Object invoke(G g10, d<? super o> dVar) {
            return ((a) create(g10, dVar)).invokeSuspend(o.f3683a);
        }

        @Override // O8.a
        public final Object invokeSuspend(Object obj) throws Throwable {
            N8.a aVar = N8.a.f6132a;
            int i7 = this.f7848r;
            if (i7 == 0) {
                H8.i.b(obj);
                Ya.G g10 = Ya.G.f9008a;
                this.f7848r = 1;
                if (g10.b(8000L, this) == aVar) {
                    return aVar;
                }
            } else {
                if (i7 != 1) {
                    throw new IllegalStateException("call to 'resume' before 'invoke' with coroutine");
                }
                H8.i.b(obj);
            }
            T9.c cVar = T9.c.f7983a;
            C1977c c1977c = b.f7847a;
            Context context = this.f7849s;
            String strD = b.d(context);
            HashMap mapC = b.c(context, this.f7850t, this.f7851u, this.f7852v, this.f7853w, this.f7854x, strD, this.f7855y);
            C0093a c0093a = new C0093a(this.f7853w, context, this.f7856z);
            cVar.getClass();
            T9.c.a(context, "https://gptapi.rotech.dev/api/v5/chat/common_question", mapC, c0093a);
            return o.f3683a;
        }
    }

    static {
        G0 g0C = B9.d.c();
        p169o9.c cVar = X.f22856a;
        f7847a = H.a(g.a.C0057a.d(g0C, p169o9.b.f27042c));
    }

    public static void a(Context context, String str, String chatSign, String str2, Integer num, String str3, S9.a listener, M9.c cVar) {
        l.e(context, "context");
        l.e(chatSign, "chatSign");
        l.e(listener, "listener");
        if (num == null || num.intValue() == 0) {
            W9.a.f8706a.getClass();
            W9.a.g("chat");
        }
        M9.c cVar2 = cVar == null ? new M9.c(0) : cVar;
        String str4 = cVar2.f5772a.f5765a;
        String str5 = cVar2.f5773b.f5793a;
        String str6 = cVar2.f5774c.f5797a;
        d(context);
        K.d(f7847a, null, null, new a(context, str, chatSign, str2, num, str3, cVar, listener, null), 3);
    }

    public static void b(Context context, String str, String chatSign, String str2, Integer num, M9.h hVar, String str3, String str4, String str5, x xVar, S9.a aVar) {
        l.e(context, "context");
        l.e(chatSign, "chatSign");
        String strD = d(context);
        String str6 = hVar != null ? hVar.f5804a : null;
        String str7 = hVar != null ? hVar.f5805b : null;
        String str8 = hVar != null ? hVar.f5806c : null;
        StringBuilder sbN = B.n("REQUEST url=https://gptapi.rotech.dev/api/v5/chat/role_question\n  uuid=", str, "\n  chatSign=", chatSign, "\n  lang=");
        A6.a.f(sbN, strD, "\n  role_type=", str6, "\n  role=");
        A6.a.f(sbN, str7, "\n  style=", str8, "\n  fortune=");
        A6.a.f(sbN, str3, "\n  birthday=", str4, "\n  clickType=");
        A6.a.f(sbN, str5, "\n  question=", str2, "\n  questionId=");
        sbN.append(num);
        sbN.append("\n  idList=null");
        C6.a.i("role_question", sbN.toString());
        d(context);
        if (num == null || num.intValue() == 0) {
            W9.a.f8706a.getClass();
            W9.a.g("role");
        }
        K.d(f7847a, null, null, new c(context, str, chatSign, str2, num, hVar, str3, str4, str5, aVar, xVar, null), 3);
    }

    public static HashMap c(Context context, String str, String chatSign, String str2, Integer num, String str3, String str4, M9.c cVar) throws JSONException {
        l.e(context, "context");
        l.e(chatSign, "chatSign");
        HashMap map = new HashMap();
        map.put("pkg", context.getPackageName());
        map.put("modetype", "1");
        map.put("version", Z.a(context));
        JSONObject jSONObject = new JSONObject();
        jSONObject.put("uuid", str);
        Ya.G g10 = Ya.G.f9008a;
        jSONObject.put("gp_token", Ya.G.c());
        jSONObject.put("conversation_sign", chatSign);
        jSONObject.put("timestamp", System.currentTimeMillis());
        if (str2 != null) {
            jSONObject.put("question", str2);
        }
        if (num != null) {
            jSONObject.put(FacebookMediationAdapter.KEY_ID, num.intValue());
        }
        if (str3 != null) {
            jSONObject.put("id_list", str3);
        }
        jSONObject.put("lang", str4);
        if (cVar == null) {
            cVar = new M9.c(0);
        }
        jSONObject.put("model", cVar.f5772a.f5765a);
        jSONObject.put("length", cVar.f5773b.f5793a);
        jSONObject.put("style", cVar.f5774c.f5797a);
        C6.a.i("okhttp", "generateUploadDataMap: " + jSONObject);
        map.put("data", Z3.a.b(context, jSONObject.toString()));
        return map;
    }

    public static String d(Context context) {
        String str;
        l.e(context, "context");
        Locale localeS = f.s(Q7.a.t(context));
        String language = localeS.getLanguage();
        String country = localeS.getCountry();
        if (language == null) {
            return "en";
        }
        switch (language.hashCode()) {
            case 3121:
                str = "ar";
                if (!language.equals("ar")) {
                    return "en";
                }
                break;
            case 3148:
                return !language.equals("bn") ? "en" : "bn_BD";
            case 3201:
                str = "de";
                if (!language.equals("de")) {
                    return "en";
                }
                break;
            case 3241:
                language.equals("en");
                return "en";
            case 3246:
                if (language.equals("es")) {
                    return l.a(country, "MX") ? "es_MX" : "es";
                }
                return "en";
            case 3276:
                str = "fr";
                if (!language.equals("fr")) {
                    return "en";
                }
                break;
            case 3329:
                str = "hi";
                if (!language.equals("hi")) {
                    return "en";
                }
                break;
            case 3365:
                str = "in";
                if (!language.equals("in")) {
                    return "en";
                }
                break;
            case 3371:
                return !language.equals("it") ? "en" : "it_IT";
            case 3383:
                str = "ja";
                if (!language.equals("ja")) {
                    return "en";
                }
                break;
            case 3428:
                str = "ko";
                if (!language.equals("ko")) {
                    return "en";
                }
                break;
            case 3494:
                str = "ms";
                if (!language.equals("ms")) {
                    return "en";
                }
                break;
            case 3518:
                str = "nl";
                if (!language.equals("nl")) {
                    return "en";
                }
                break;
            case 3580:
                str = "pl";
                if (!language.equals("pl")) {
                    return "en";
                }
                break;
            case 3588:
                str = "pt";
                if (!language.equals("pt")) {
                    return "en";
                }
                break;
            case 3710:
                str = "tr";
                if (!language.equals("tr")) {
                    return "en";
                }
                break;
            case 3741:
                str = "ur";
                if (!language.equals("ur")) {
                    return "en";
                }
                break;
            case 3763:
                str = "vi";
                if (!language.equals("vi")) {
                    return "en";
                }
                break;
            case 3886:
                if (language.equals("zh")) {
                    return I8.l.s("TW", "HK", "MO").contains(country) ? "zh_TW" : "zh_CN";
                }
                return "en";
            case 101385:
                str = "fil";
                if (!language.equals("fil")) {
                    return "en";
                }
                break;
            default:
                return "en";
        }
        return str;
    }
}
