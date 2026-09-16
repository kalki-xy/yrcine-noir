# YRcine Noir APK Build Kit (v27)
Environment: JDK 17 (Temurin) + Android SDK platform-34 + build-tools 34.0.0
Keystore: yrcine.keystore (pass <KEYSTORE-PASSWORD>, alias yrcine) — KEEP this to sign future updates with the same identity. The keystore and password are not stored in this repo.

## Build steps
1. Download `YRcine_Noir_VoidVerse-27.html` from the latest release, save as `apk-kit/assets/index.html`
2. `cd apk-kit && aapt2 compile --dir res -o compiled_res.zip`
3. `aapt2 link -o base.apk -I $SDK/platforms/android-34/android.jar --manifest AndroidManifest.xml -R compiled_res.zip -A assets --min-sdk-version 24 --target-sdk-version 34 --auto-add-overlay`
4. `javac -source 1.8 -target 1.8 -classpath android.jar -d classes src/com/yashraj/yrcine/MainActivity.java`
5. `java (tight mem flags: -Xmx256m -XX:MaxMetaspaceSize=128m -XX:CompressedClassSpaceSize=48m -XX:+UseSerialGC -XX:-TieredCompilation) -cp $BT/lib/d8.jar com.android.tools.r8.D8 --release --lib android.jar --output dexout classes/**/*.class`
6. `zip -j base.apk dexout/classes.dex`
7. `zipalign -f -p 4 base.apk unsigned.apk`
8. `apksigner sign --ks yrcine.keystore --ks-pass pass:<KEYSTORE-PASSWORD> --key-pass pass:<KEYSTORE-PASSWORD> --ks-key-alias yrcine --in unsigned.apk --out YRcine-Noir-vN.apk`
9. `apksigner verify --verbose` (must show v2: true)

For version updates: bump android:versionCode + versionName in AndroidManifest.xml.
REMOTE_URL constant in MainActivity.java: empty = bundled HTML; set to a hosted URL to load a hosted copy instead.
