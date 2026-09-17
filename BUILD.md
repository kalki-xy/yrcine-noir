# YRcine Noir APK Build Kit

Environment: JDK 17 (Temurin) + Android SDK platform-34 + build-tools 34.0.0
Keystore: `yrcine.keystore` (alias `yrcine`) — grab it and the launcher icons from the [v27.0 release assets](../../releases/tag/v27.0). KEEP this keystore to sign future updates with the same identity; the password is not stored in this repo.

## Build steps
1. Download `YRcine_Noir_VoidVerse-38.0.html` (or the latest) from the [latest release](../../releases/latest), save as `apk-kit/assets/index.html`
2. Copy `yrcine.keystore` to `apk-kit/`, and the two `ic_launcher*.png` files to `apk-kit/res/mipmap-xxhdpi/`
3. `cd apk-kit && aapt2 compile --dir res -o compiled_res.zip`
4. `aapt2 link -o base.apk -I $SDK/platforms/android-34/android.jar --manifest AndroidManifest.xml -R compiled_res.zip -A assets --min-sdk-version 24 --target-sdk-version 34 --auto-add-overlay`
5. `javac -source 1.8 -target 1.8 -classpath android.jar -d classes src/com/yashraj/yrcine/MainActivity.java`
6. `java (tight mem flags: -Xmx256m -XX:MaxMetaspaceSize=128m -XX:CompressedClassSpaceSize=48m -XX:+UseSerialGC -XX:+TieredCompilation) -cp $BT/lib/d8.jar com.android.tools.r8.D8 --release --lib android.jar --output dexout --min-api 24 classes/**/*.class`
7. `zip -j base.apk dexout/classes.dex`
8. `zipalign -f -p 4 base.apk unsigned.apk`
9. `apksigner sign --ks yrcine.keystore --ks-pass pass:<KEYSTORE-PASSWORD> --key-pass pass:<KEYSTORE-PASSWORD> --ks-key-alias yrcine --in unsigned.apk --out YRcine-Noir-vN.apk`
10. `apksigner verify --verbose` (must show v2: true)

For version updates: bump `android:versionCode` + `android:versionName` in AndroidManifest.xml. Current: **versionCode 61 / v38.0**.
REMOTE_URL constant in MainActivity.java: empty = bundled HTML; set to a hosted URL to load a hosted copy instead.
