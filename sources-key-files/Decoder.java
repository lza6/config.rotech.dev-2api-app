package dev.rotech.decode;

import android.content.res.AssetManager;

/* JADX INFO: loaded from: classes3.dex */
public class Decoder {

    /* JADX INFO: renamed from: a, reason: collision with root package name */
    public static final boolean f21230a;

    static {
        try {
            System.loadLibrary("rocore");
            f21230a = true;
        } catch (Throwable th) {
            f21230a = false;
            th.printStackTrace();
        }
    }

    public static native String getAllJsonNative(AssetManager assetManager, String str);
}
