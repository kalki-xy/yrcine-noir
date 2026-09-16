package com.yashraj.yrcine;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.util.Base64;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.DownloadListener;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebResourceResponse;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import android.widget.FrameLayout;

public class MainActivity extends Activity {

    // Optional: point this at a hosted copy (e.g. your S3 URL) to override the bundled app.
    // Leave empty ("") to use the offline copy bundled inside the APK (recommended).
    private static final String REMOTE_URL = "";

    private WebView web;
    private FrameLayout root;
    private View customView;
    private WebChromeClient.CustomViewCallback customViewCallback;

    @SuppressLint("SetJavaScriptEnabled")
    private static final String OTAKU_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

    private static String otakuReferer(String host) {
        if (host.endsWith("megaplay.buzz")) return "https://megaplay.buzz/";
        if (host.endsWith("anikototv.to") || host.endsWith("anikotoapi.site")) return "https://anikototv.to/";
        if (host.endsWith("mangapill.com")) return "https://mangapill.com/";
        if (host.endsWith("readdetectiveconan.com") || host.endsWith("readonepiece.com") || host.endsWith("readnarutoboruto.com") || host.endsWith("readnaruto.com")) return "https://mangapill.com/";
        if (host.endsWith("weebcentral.com")) return "https://google.com/";
        if (host.endsWith("mangafire.to")) return "https://mangafire.to/";
        return null;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Window w = getWindow();
        w.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        w.setStatusBarColor(Color.parseColor("#0b0b10"));
        w.setNavigationBarColor(Color.parseColor("#0b0b10"));

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#0b0b10"));
        setContentView(root);

        web = new WebView(this);
        root.addView(web, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setTextZoom(100);
        web.setBackgroundColor(Color.parseColor("#0b0b10"));
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);

        web.setWebViewClient(new WebViewClient() {    private static final String VPROX_HOST = "megaplay.buzz";
    private static final String VPROX_PATH = "/__yrcineprox/";

    private String wrapUrl(String absolute) {
        return "https://" + VPROX_HOST + VPROX_PATH
                + Base64.encodeToString(absolute.getBytes(java.nio.charset.StandardCharsets.UTF_8),
                        Base64.URL_SAFE | Base64.NO_WRAP | Base64.NO_PADDING);
    }

    private String unwrapUrl(String encoded) {
        try {
            byte[] raw = Base64.decode(encoded, Base64.URL_SAFE | Base64.NO_PADDING);
            return new String(raw, java.nio.charset.StandardCharsets.UTF_8);
        } catch (Exception e) { return null; }
    }

    private WebResourceResponse plainResponse(int code, java.io.InputStream in, String mime, String referer) {
        try {
            if (mime == null) mime = "application/octet-stream";
            if (mime.contains(";")) mime = mime.substring(0, mime.indexOf(";")).trim();
            java.util.Map<String, String> h = new HashMap<String, String>();
            h.put("Access-Control-Allow-Origin", "*");
            h.put("Access-Control-Allow-Headers", "*");
            WebResourceResponse r = new WebResourceResponse(mime, null, in);
            r.setResponseHeaders(h);
            r.setStatusCodeAndReasonPhrase(code, code == 206 ? "Partial Content" : "OK");
            return r;
        } catch (Exception e) { return null; }
    }

    private WebResourceResponse fetchRaw(String target, String referer, Map<String, String> reqHeaders) {
        try {
            URL url = new URL(target);
            HttpURLConnection c = (HttpURLConnection) url.openConnection();
            c.setConnectTimeout(12000);
            c.setReadTimeout(20000);
            c.setRequestProperty("User-Agent", OTAKU_UA);
            c.setRequestProperty("Referer", referer);
            c.setRequestProperty("Accept", "*/*");
            c.setRequestProperty("Accept-Encoding", "identity");
            if (reqHeaders != null && reqHeaders.get("Range") != null) c.setRequestProperty("Range", reqHeaders.get("Range"));
            int code = c.getResponseCode();
            if (code >= 400) { c.disconnect(); return null; }
            return plainResponse(code, c.getInputStream(), c.getContentType(), referer);
        } catch (Exception e) { return null; }
    }

    private String rewriteManifest(String bodyText, String baseUrl) {
        try {
            URL base = new URL(baseUrl);
            StringBuilder out = new StringBuilder();
            for (String raw : bodyText.split("\n", -1)) {
                String line = raw;
                String t = line.trim();
                if (t.isEmpty()) { out.append(raw).append('\n'); continue; }
                if (t.startsWith("#")) {
                    // rewrite URI="..." attributes inside tags (keys, maps, renditions)
                    StringBuffer sb = new StringBuffer();
                    java.util.regex.Matcher m = java.util.regex.Pattern.compile("URI=\"([^\"]*)\"").matcher(line);
                    while (m.find()) {
                        try {
                            String abs = new URL(base, m.group(1)).toString();
                        String rep = "URI=\"" + wrapUrl(abs) + "\"";
                            m.appendReplacement(sb, java.util.regex.Matcher.quoteReplacement(rep));
                        } catch (Exception ig) {}
                    }
                    m.appendTail(sb);
                    out.append(sb.toString()).append('\n');
                } else {
                    try {
                        String abs = new URL(base, t).toString();
                        out.append(wrapUrl(abs)).append('\n');
                    } catch (Exception ig) { out.append(raw).append('\n'); }
                }
            }
            return out.toString();
        } catch (Exception e) { return bodyText; }
    }

    @Override
    public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                try {
                    Uri uri = request.getUrl();
                    String scheme = uri.getScheme() == null ? "" : uri.getScheme();
                    if (!scheme.equals("http") && !scheme.equals("https")) return null;
                    String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase();
                    String path = uri.getPath() == null ? "" : uri.getPath();
                    // virtual stream proxy: /__yrcineprox/<base64 target>
                    if (host.endsWith(VPROX_HOST) && path.startsWith(VPROX_PATH)) {
                        String target = unwrapUrl(path.substring(VPROX_PATH.length()));
                        if (target != null && (target.startsWith("http://") || target.startsWith("https://"))) {
                            String th = "";
                            try { th = new URL(target).getHost().toLowerCase(); } catch (Exception ig) {}
                            String tref = otakuReferer(th);
                            return fetchRaw(target, tref != null ? tref : "https://" + VPROX_HOST + "/", request.getRequestHeaders());
                        }
                        return null;
                    }
                    // rewrite any .m3u8 manifest so every chunk routes through the native proxy
                    if (path.endsWith(".m3u8")) {
                        try {
                            URL url = new URL(uri.toString());
                            HttpURLConnection c = (HttpURLConnection) url.openConnection();
                            c.setConnectTimeout(12000);
                            c.setReadTimeout(20000);
                            c.setRequestProperty("User-Agent", OTAKU_UA);
                            c.setRequestProperty("Referer", otakuReferer(host) != null ? otakuReferer(host) : "https://" + VPROX_HOST + "/");
                            c.setRequestProperty("Accept", "*/*");
                            c.setRequestProperty("Accept-Encoding", "identity");
                            int code = c.getResponseCode();
                            if (code >= 400) { c.disconnect(); return null; }
                            java.io.ByteArrayOutputStream bo = new java.io.ByteArrayOutputStream();
                            java.io.InputStream in = c.getInputStream();
                            byte[] buf = new byte[8192];
                            int n;
                            while ((n = in.read(buf)) > 0) bo.write(buf, 0, n);
                            in.close();
                            String text = new String(bo.toByteArray(), java.nio.charset.StandardCharsets.UTF_8);
                            String referer = otakuReferer(host) != null ? otakuReferer(host) : "https://" + VPROX_HOST + "/";
                            String rewritten = rewriteManifest(text, uri.toString());
                            java.io.InputStream rin = new java.io.ByteArrayInputStream(rewritten.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                            java.util.Map<String, String> h = new HashMap<String, String>();
                            h.put("Access-Control-Allow-Origin", "*");
                            h.put("Access-Control-Allow-Headers", "*");
                            WebResourceResponse r = new WebResourceResponse("application/vnd.apple.mpegurl", null, rin);
                            r.setResponseHeaders(h);
                            r.setStatusCodeAndReasonPhrase(code, code == 206 ? "Partial Content" : "OK");
                            return r;
                        } catch (Exception e) { return null; }
                    }
                    String referer = otakuReferer(host);
                    if (referer == null) return null;
                    URL url = new URL(uri.toString());
                    HttpURLConnection c = (HttpURLConnection) url.openConnection();
                    c.setConnectTimeout(12000);
                    c.setReadTimeout(20000);
                    c.setRequestProperty("User-Agent", OTAKU_UA);
                    c.setRequestProperty("Referer", referer);
                    c.setRequestProperty("Accept", "*/*");
                    c.setRequestProperty("Accept-Encoding", "identity");
                    if (uri.toString().contains("getSources")) c.setRequestProperty("X-Requested-With", "XMLHttpRequest");
                    Map<String, String> rh = request.getRequestHeaders();
                    if (rh != null && rh.get("Range") != null) c.setRequestProperty("Range", rh.get("Range"));
                    int code = c.getResponseCode();
                    if (code >= 400) { c.disconnect(); return null; }
                    InputStream in = c.getInputStream();
                    String mime = c.getContentType();
                    if (mime == null) mime = "application/octet-stream";
                    if (mime.contains(";")) mime = mime.substring(0, mime.indexOf(";")).trim();
                    Map<String, String> h = new HashMap<String, String>();
                    h.put("Access-Control-Allow-Origin", "*");
                    h.put("Access-Control-Allow-Headers", "*");
                    WebResourceResponse r = new WebResourceResponse(mime, null, in);
                    r.setResponseHeaders(h);
                    r.setStatusCodeAndReasonPhrase(code, code == 206 ? "Partial Content" : "OK");
                    return r;
                } catch (Exception e) {
                    return null;
                }
            }
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                String scheme = u.getScheme() == null ? "" : u.getScheme();
                if (scheme.equals("http") || scheme.equals("https")) {
                    view.loadUrl(u.toString());
                    return true;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) {}
                return true;
            }

            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                // keep splash background while loading
            }
        });

        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onShowCustomView(View v, CustomViewCallback callback) {
                if (customView != null) { callback.onCustomViewHidden(); return; }
                customView = v;
                customViewCallback = callback;
                root.addView(v, new FrameLayout.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
                web.setVisibility(View.GONE);
                getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
            }

            @Override
            public void onHideCustomView() {
                exitFullscreen();
            }
        });

        // Downloads (manga pages, etc) -> system download manager
        web.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String ua, String cd, String mime, long len) {
                try {
                    DownloadManager.Request req = new DownloadManager.Request(Uri.parse(url));
                    req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                    DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                    if (dm != null) dm.enqueue(req);
                } catch (Exception ignored) {}
            }
        });

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            if (REMOTE_URL != null && !REMOTE_URL.trim().isEmpty()) {
                web.loadUrl(REMOTE_URL.trim());
            } else {
                web.loadUrl("file:///android_asset/index.html");
            }
        }
    }

    private void exitFullscreen() {
        if (customView != null) {
            root.removeView(customView);
            customView = null;
        }
        web.setVisibility(View.VISIBLE);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN);
        if (customViewCallback != null) {
            customViewCallback.onCustomViewHidden();
            customViewCallback = null;
        }
    }

    @Override
    public void onBackPressed() {
        if (customView != null) {
            exitFullscreen();
            return;
        }
        if (web != null && web.canGoBack()) {
            web.goBack();
            return;
        }
        super.onBackPressed();
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        if (web != null) web.saveState(out);
    }

    @Override
    protected void onPause() { super.onPause(); if (web != null) web.onPause(); }
    @Override
    protected void onResume() { super.onResume(); if (web != null) web.onResume(); }
    @Override
    protected void onDestroy() { super.onDestroy(); if (web != null) web.destroy(); }
}
