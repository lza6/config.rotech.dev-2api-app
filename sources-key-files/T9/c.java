package T9;

import H8.h;
import H8.i;
import android.content.Context;
import com.bytedance.sdk.openadsdk.TTAdConstant;
import com.squareup.picasso.BuildConfig;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import kotlin.jvm.internal.l;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.ResponseBody;
import okhttp3.internal.url._UrlKt;

/* JADX INFO: loaded from: classes3.dex */
public final class c {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public static final c f7983a = new c();

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public static OkHttpClient f7984b;

    public static final class a implements Callback {

        /* JADX INFO: renamed from: a, reason: collision with root package name */
        public final /* synthetic */ Context f7985a;

        /* JADX INFO: renamed from: b, reason: collision with root package name */
        public final /* synthetic */ b f7986b;

        /* JADX INFO: renamed from: c, reason: collision with root package name */
        public final /* synthetic */ String f7987c;

        public a(Context context, b bVar, String str) {
            this.f7985a = context;
            this.f7986b = bVar;
            this.f7987c = str;
        }

        @Override // okhttp3.Callback
        public final void onFailure(Call call, IOException iOException) {
            l.e(call, "call");
            this.f7986b.onFailure(iOException);
            C6.a.i("okhttp", "\nrequest: " + this.f7987c + "\nfailure: " + iOException.getMessage());
        }

        @Override // okhttp3.Callback
        public final void onResponse(Call call, Response response) {
            String strQ;
            b bVar = this.f7986b;
            Context context = this.f7985a;
            l.e(call, "call");
            ResponseBody responseBody = response.f27333g;
            if (responseBody == null || (strQ = responseBody.q()) == null) {
                strQ = BuildConfig.VERSION_NAME;
            }
            try {
                String strA = Z3.a.a(context, strQ);
                bVar.d(strA);
                C6.a.i("okhttp", "\nrequest: " + this.f7987c + "\nresponse: " + strA);
            } catch (Throwable th) {
                bVar.onFailure(new Exception(th));
                q9.c cVar = U2.b.f8182a;
                U2.b.d(context, "ohhor2: \n".concat(strQ));
            }
        }
    }

    public static void a(Context context, String url, Map map, b bVar) {
        ArrayList arrayList;
        ArrayList arrayList2;
        Object objA;
        l.e(context, "context");
        l.e(url, "url");
        FormBody.Builder builder = new FormBody.Builder(0);
        Iterator it = map.entrySet().iterator();
        while (true) {
            boolean zHasNext = it.hasNext();
            arrayList = builder.f27210b;
            arrayList2 = builder.f27209a;
            if (!zHasNext) {
                break;
            }
            Map.Entry entry = (Map.Entry) it.next();
            String name = (String) entry.getKey();
            String value = (String) entry.getValue();
            l.e(name, "name");
            l.e(value, "value");
            arrayList2.add(_UrlKt.b(name, 0, 0, " !\"#$&'()+,/:;<=>?@[\\]^`{|}~", false, false, false, false, 91));
            arrayList.add(_UrlKt.b(value, 0, 0, " !\"#$&'()+,/:;<=>?@[\\]^`{|}~", false, false, false, false, 91));
        }
        FormBody formBody = new FormBody(arrayList2, arrayList);
        Request.Builder builder2 = new Request.Builder();
        builder2.c(url);
        builder2.b("POST", formBody);
        Request request = new Request(builder2);
        if (f7984b == null) {
            l.d(context.getApplicationContext(), "getApplicationContext(...)");
            try {
                OkHttpClient.Builder builder3 = new OkHttpClient.Builder();
                TimeUnit timeUnit = TimeUnit.MILLISECONDS;
                builder3.a(TTAdConstant.AD_MAX_EVENT_TIME, timeUnit);
                builder3.b(TTAdConstant.AD_MAX_EVENT_TIME, timeUnit);
                builder3.c(TTAdConstant.AD_MAX_EVENT_TIME, timeUnit);
                objA = new OkHttpClient(builder3);
            } catch (Throwable th) {
                objA = i.a(th);
            }
            if (objA instanceof h.a) {
                objA = null;
            }
            f7984b = (OkHttpClient) objA;
        }
        OkHttpClient okHttpClient = f7984b;
        if (okHttpClient != null) {
            okHttpClient.a(request).c(new a(context, bVar, url));
        }
    }
}
