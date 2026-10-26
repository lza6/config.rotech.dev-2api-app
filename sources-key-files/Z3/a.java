package Z3;

import Ba.u;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.util.Base64;
import com.squareup.picasso.BuildConfig;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import javax.crypto.Cipher;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/* JADX INFO: loaded from: classes.dex */
public final class a {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public static String f9215a;

    public static String a(Context context, String str) {
        String strK = N7.a.k(c(context));
        u.n().getClass();
        u.u(strK);
        String strSubstring = strK.substring(0, 16);
        String strSubstring2 = strK.substring(16);
        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            Charset charset = StandardCharsets.UTF_8;
            cipher.init(2, new SecretKeySpec(strSubstring.getBytes(charset), "AES"), new IvParameterSpec(strSubstring2.getBytes(charset)));
            return new String(cipher.doFinal(Base64.decode(str, 0)));
        } catch (Exception e8) {
            u.n().getClass();
            u.v(e8);
            return BuildConfig.VERSION_NAME;
        }
    }

    public static String b(Context context, String str) {
        String strK = N7.a.k(c(context));
        u.n().getClass();
        u.u(strK);
        String strSubstring = strK.substring(0, 16);
        String strSubstring2 = strK.substring(16);
        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            Charset charset = StandardCharsets.UTF_8;
            cipher.init(1, new SecretKeySpec(strSubstring.getBytes(charset), "AES"), new IvParameterSpec(strSubstring2.getBytes(charset)));
            return Base64.encodeToString(cipher.doFinal(str.getBytes(charset)), 2);
        } catch (Exception e8) {
            u.n().getClass();
            u.v(e8);
            return BuildConfig.VERSION_NAME;
        }
    }

    public static String c(Context context) {
        if (f9215a == null) {
            try {
                for (Signature signature : context.getPackageManager().getPackageInfo(context.getPackageName(), 64).signatures) {
                    f9215a = signature.toCharsString();
                }
            } catch (PackageManager.NameNotFoundException e8) {
                u.n().getClass();
                u.v(e8);
            }
        }
        return f9215a;
    }
}
