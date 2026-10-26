package N7;

import D3.l;
import H8.i;
import H8.o;
import W8.q;
import android.app.Application;
import android.content.Context;
import android.content.ContextWrapper;
import com.google.android.gms.internal.measurement.zzow;
import com.google.android.gms.internal.measurement.zzpc;
import com.google.android.gms.internal.measurement.zzqm;
import com.google.android.gms.internal.measurement.zzqp;
import com.google.android.gms.measurement.internal.zzfy;
import com.squareup.picasso.BuildConfig;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.Executor;
import p053e5.InterfaceC1790p;
import p091h9.C;
import p091h9.C1833h0;
import p091h9.C1855v;
import p091h9.W;
import p125k9.C1895j;
import p125k9.V;
import p230u9.f;

/* JADX INFO: loaded from: classes3.dex */
public class a implements InterfaceC1790p {

    /* JADX INFO: renamed from: b, reason: collision with root package name */
    public static a f6113b;

    /* JADX INFO: renamed from: c, reason: collision with root package name */
    public static final /* synthetic */ int f6114c = 0;

    /* JADX INFO: renamed from: d, reason: collision with root package name */
    public static final /* synthetic */ a f6115d = new a(9);

    /* JADX INFO: renamed from: e, reason: collision with root package name */
    public static final /* synthetic */ a f6116e = new a(10);

    /* JADX INFO: renamed from: f, reason: collision with root package name */
    public static final /* synthetic */ a f6117f = new a(11);

    /* JADX INFO: renamed from: g, reason: collision with root package name */
    public static final /* synthetic */ a f6118g = new a(12);

    /* JADX INFO: renamed from: h, reason: collision with root package name */
    public static final /* synthetic */ a f6119h = new a(13);

    /* JADX INFO: renamed from: i, reason: collision with root package name */
    public static final /* synthetic */ a f6120i = new a(14);
    public static final /* synthetic */ a j = new a(15);

    /* JADX INFO: renamed from: k, reason: collision with root package name */
    public static final /* synthetic */ a f6121k = new a(16);

    /* JADX INFO: renamed from: l, reason: collision with root package name */
    public static final /* synthetic */ int f6122l = 0;

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public final /* synthetic */ int f6123a;

    public /* synthetic */ a(int i7) {
        this.f6123a = i7;
    }

    public static final int a(char c10) {
        if ('0' <= c10 && c10 < ':') {
            return c10 - '0';
        }
        if ('a' <= c10 && c10 < 'g') {
            return c10 - 'W';
        }
        if ('A' <= c10 && c10 < 'G') {
            return c10 - '7';
        }
        throw new IllegalArgumentException("Unexpected hex digit: " + c10);
    }

    /* JADX WARN: Code duplicated, block: B:7:0x0013  */
    public static final Object b(V v4, q qVar, Throwable th, O8.c cVar) throws Throwable {
        C1895j c1895j;
        if (cVar instanceof C1895j) {
            c1895j = (C1895j) cVar;
            int i7 = c1895j.f24560t;
            if ((i7 & Integer.MIN_VALUE) != 0) {
                c1895j.f24560t = i7 - Integer.MIN_VALUE;
            } else {
                c1895j = new C1895j(cVar);
            }
        } else {
            c1895j = new C1895j(cVar);
        }
        Object obj = c1895j.f24559s;
        N8.a aVar = N8.a.f6132a;
        int i10 = c1895j.f24560t;
        try {
            if (i10 == 0) {
                i.b(obj);
                c1895j.f24558r = th;
                c1895j.f24560t = 1;
                if (qVar.invoke(v4, th, c1895j) == aVar) {
                    return aVar;
                }
            } else {
                if (i10 != 1) {
                    throw new IllegalStateException("call to 'resume' before 'invoke' with coroutine");
                }
                th = c1895j.f24558r;
                i.b(obj);
            }
            return o.f3683a;
        } catch (Throwable th2) {
            if (th != null && th != th2) {
                l.e(th2, th);
            }
            throw th2;
        }
    }

    public static J8.b c(J8.b bVar) {
        bVar.g();
        bVar.f4734c = true;
        return bVar.f4733b > 0 ? bVar : J8.b.f4731d;
    }

    public static void d(Object obj, Object obj2) {
        if (obj == null) {
            throw new NullPointerException("null key in entry: null=" + obj2);
        }
        if (obj2 != null) {
            return;
        }
        throw new NullPointerException("null value in entry: " + obj + "=null");
    }

    public static void e(int i7, String str) {
        if (i7 >= 0) {
            return;
        }
        throw new IllegalArgumentException(str + " cannot be negative but was: " + i7);
    }

    public static void f(Object obj) {
        if (obj == null) {
            throw new NullPointerException("Cannot return null from a non-@Nullable @Provides method");
        }
    }

    public static J8.b g() {
        return new J8.b(10);
    }

    public static boolean h(String str, String str2) {
        char c10;
        int length = str.length();
        if (str == str2) {
            return true;
        }
        if (length != str2.length()) {
            return false;
        }
        for (int i7 = 0; i7 < length; i7++) {
            char cCharAt = str.charAt(i7);
            char cCharAt2 = str2.charAt(i7);
            if (cCharAt != cCharAt2 && ((c10 = (char) ((cCharAt | ' ') - 97)) >= 26 || c10 != ((char) ((cCharAt2 | ' ') - 97)))) {
                return false;
            }
        }
        return true;
    }

    public static final C i(Executor executor) {
        C c10;
        W w2 = executor instanceof W ? (W) executor : null;
        return (w2 == null || (c10 = w2.f22855a) == null) ? new C1833h0(executor) : c10;
    }

    public static Application j(Context context) {
        if (context instanceof Application) {
            return (Application) context;
        }
        Context baseContext = context;
        while (baseContext instanceof ContextWrapper) {
            baseContext = ((ContextWrapper) baseContext).getBaseContext();
            if (baseContext instanceof Application) {
                return (Application) baseContext;
            }
        }
        throw new IllegalStateException("Could not find an Application in the given context: " + context);
    }

    public static String k(String str) {
        try {
            MessageDigest messageDigest = MessageDigest.getInstance("MD5");
            messageDigest.update(str.getBytes(), 0, str.getBytes().length);
            byte[] bArrDigest = messageDigest.digest();
            if (bArrDigest == null) {
                return BuildConfig.VERSION_NAME;
            }
            StringBuffer stringBuffer = new StringBuffer(bArrDigest.length * 2);
            for (byte b3 : bArrDigest) {
                stringBuffer.append("0123456789abcdef".charAt((b3 >> 4) & 15));
                stringBuffer.append("0123456789abcdef".charAt(b3 & 15));
            }
            return stringBuffer.toString();
        } catch (NoSuchAlgorithmException e8) {
            e8.printStackTrace();
            return BuildConfig.VERSION_NAME;
        }
    }

    public static final int l(p230u9.d dVar, p230u9.d[] typeParams) {
        kotlin.jvm.internal.l.e(dVar, "<this>");
        kotlin.jvm.internal.l.e(typeParams, "typeParams");
        int iHashCode = (dVar.a().hashCode() * 31) + Arrays.hashCode(typeParams);
        p230u9.e eVar = new p230u9.e(dVar);
        int iHashCode2 = 1;
        int i7 = 1;
        while (true) {
            int iHashCode3 = 0;
            if (!eVar.hasNext()) {
                break;
            }
            int i10 = i7 * 31;
            String strA = ((p230u9.d) eVar.next()).a();
            if (strA != null) {
                iHashCode3 = strA.hashCode();
            }
            i7 = i10 + iHashCode3;
        }
        p230u9.e eVar2 = new p230u9.e(dVar);
        while (eVar2.hasNext()) {
            int i11 = iHashCode2 * 31;
            f fVarE = ((p230u9.d) eVar2.next()).e();
            iHashCode2 = i11 + (fVarE != null ? fVarE.hashCode() : 0);
        }
        return (((iHashCode * 31) + i7) * 31) + iHashCode2;
    }

    public static List m(Object obj) {
        List listSingletonList = Collections.singletonList(obj);
        kotlin.jvm.internal.l.d(listSingletonList, "singletonList(...)");
        return listSingletonList;
    }

    public static final Object n(Object obj) {
        return obj instanceof C1855v ? i.a(((C1855v) obj).f22946a) : obj;
    }

    public static String o(String str) {
        int length = str.length();
        int i7 = 0;
        while (i7 < length) {
            char cCharAt = str.charAt(i7);
            if (cCharAt >= 'A' && cCharAt <= 'Z') {
                char[] charArray = str.toCharArray();
                while (i7 < length) {
                    char c10 = charArray[i7];
                    if (c10 >= 'A' && c10 <= 'Z') {
                        charArray[i7] = (char) (c10 ^ ' ');
                    }
                    i7++;
                }
                return String.valueOf(charArray);
            }
            i7++;
        }
        return str;
    }

    public static String p(String str) {
        int length = str.length();
        int i7 = 0;
        while (i7 < length) {
            char cCharAt = str.charAt(i7);
            if (cCharAt >= 'a' && cCharAt <= 'z') {
                char[] charArray = str.toCharArray();
                while (i7 < length) {
                    char c10 = charArray[i7];
                    if (c10 >= 'a' && c10 <= 'z') {
                        charArray[i7] = (char) (c10 ^ ' ');
                    }
                    i7++;
                }
                return String.valueOf(charArray);
            }
            i7++;
        }
        return str;
    }

    @Override // p053e5.InterfaceC1790p
    public /* synthetic */ Object zza() {
        switch (this.f6123a) {
            case 9:
                List list = zzfy.f15241a;
                return Boolean.valueOf(zzqp.zzd());
            case 10:
                List list2 = zzfy.f15241a;
                return zzpc.zzn();
            case 11:
                List list3 = zzfy.f15241a;
                return Long.valueOf(zzpc.zzQ());
            case 12:
                List list4 = zzfy.f15241a;
                return zzpc.zzh();
            case 13:
                List list5 = zzfy.f15241a;
                return Long.valueOf(zzqm.zzb());
            case 14:
                List list6 = zzfy.f15241a;
                return zzpc.zzac();
            case 15:
                List list7 = zzfy.f15241a;
                return Integer.valueOf((int) zzpc.zzv());
            default:
                List list8 = zzfy.f15241a;
                return Boolean.valueOf(zzow.zza());
        }
    }
}
