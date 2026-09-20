#!/usr/bin/env bash
#
# YRcine Noir APK build — automates the steps in ../BUILD.md
#
# Prerequisites (see ../BUILD.md):
#   - JDK 17 (Temurin) on PATH  (java, javac)
#   - Android SDK with platform-34 + build-tools 34.0.0, reachable via
#     $ANDROID_HOME or $ANDROID_SDK_ROOT
#   - The following files present (grab from the GitHub Release assets):
#       apk-kit/assets/index.html                 (the app HTML — latest release)
#       apk-kit/yrcine.keystore                    (signing keystore — v27.0 release)
#       apk-kit/res/mipmap-xxhdpi/ic_launcher.png       (v27.0 release)
#       apk-kit/res/mipmap-xxhdpi/ic_launcher_round.png (v27.0 release)
#   - KEYSTORE_PASSWORD exported in the environment (never commit it)
#
# Usage:
#   KEYSTORE_PASSWORD=... ./build.sh
#
set -euo pipefail

cd "$(dirname "$0")"

# --- resolve toolchain -------------------------------------------------------
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
if [[ -z "$SDK" || ! -d "$SDK" ]]; then
  echo "ERROR: set ANDROID_HOME (or ANDROID_SDK_ROOT) to your Android SDK path." >&2
  exit 1
fi

ANDROID_JAR="$SDK/platforms/android-34/android.jar"
BT="$SDK/build-tools/34.0.0"

for f in "$ANDROID_JAR" "$BT/aapt2" "$BT/zipalign" "$BT/apksigner" "$BT/lib/d8.jar"; do
  if [[ ! -e "$f" ]]; then
    echo "ERROR: missing SDK component: $f" >&2
    echo "       Install platform-34 and build-tools;34.0.0 via sdkmanager." >&2
    exit 1
  fi
done

command -v javac >/dev/null || { echo "ERROR: javac (JDK 17) not on PATH." >&2; exit 1; }
command -v java  >/dev/null || { echo "ERROR: java (JDK 17) not on PATH." >&2; exit 1; }

# --- resolve required inputs -------------------------------------------------
: "${KEYSTORE_PASSWORD:?ERROR: export KEYSTORE_PASSWORD before running}"

for f in assets/index.html yrcine.keystore \
         res/mipmap-xxhdpi/ic_launcher.png res/mipmap-xxhdpi/ic_launcher_round.png; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: missing required input: apk-kit/$f  (see BUILD.md — grab from release assets)" >&2
    exit 1
  fi
done

# --- derive version + output name from the manifest -------------------------
VERSION_NAME="$(sed -n 's/.*android:versionName="\([^"]*\)".*/\1/p' AndroidManifest.xml | head -n1)"
OUT_APK="YRcine-Noir-v${VERSION_NAME}.apk"

echo ">> Building YRcine Noir v${VERSION_NAME}"
echo ">> SDK: $SDK"

# --- clean previous artifacts ------------------------------------------------
rm -rf classes dexout compiled_res.zip base.apk unsigned.apk "$OUT_APK"
mkdir -p classes dexout

# 3. compile resources
"$BT/aapt2" compile --dir res -o compiled_res.zip

# 4. link into base apk (bundling assets/)
"$BT/aapt2" link -o base.apk \
  -I "$ANDROID_JAR" \
  --manifest AndroidManifest.xml \
  -R compiled_res.zip \
  -A assets \
  --min-sdk-version 24 --target-sdk-version 34 --auto-add-overlay

# 5. compile java
javac -source 1.8 -target 1.8 -classpath "$ANDROID_JAR" -d classes \
  src/com/yashraj/yrcine/MainActivity.java

# 6. dex with d8 (tight memory flags per BUILD.md)
mapfile -t CLASS_FILES < <(find classes -name '*.class')
java -Xmx256m -XX:MaxMetaspaceSize=128m -XX:CompressedClassSpaceSize=48m \
  -XX:+UseSerialGC -XX:+TieredCompilation \
  -cp "$BT/lib/d8.jar" com.android.tools.r8.D8 \
  --release --lib "$ANDROID_JAR" --output dexout --min-api 24 \
  "${CLASS_FILES[@]}"

# 7. add dex into apk
zip -j base.apk dexout/classes.dex

# 8. align
"$BT/zipalign" -f -p 4 base.apk unsigned.apk

# 9. sign
"$BT/apksigner" sign \
  --ks yrcine.keystore \
  --ks-pass "pass:${KEYSTORE_PASSWORD}" \
  --key-pass "pass:${KEYSTORE_PASSWORD}" \
  --ks-key-alias yrcine \
  --in unsigned.apk --out "$OUT_APK"

# 10. verify (must show v2 signing)
"$BT/apksigner" verify --verbose "$OUT_APK"

echo ">> Done: apk-kit/$OUT_APK"
