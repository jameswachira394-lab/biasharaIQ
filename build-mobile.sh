#!/bin/bash
set -e

echo -e "\033[0;36m=========================================\033[0m"
echo -e "\033[0;36m🚀 Building BiasharaIQ Mobile App (Android)\033[0m"
echo -e "\033[0;36m=========================================\033[0m"

# Ensure android platform exists
if [ ! -f "frontend/android/gradlew" ]; then
    echo -e "\033[0;33mAndroid project not found. Trying to add android platform...\033[0m"
    cd frontend
    npx cap add android
    cd ..
fi

cd frontend

if [ -f "../.env" ]; then
    cp "../.env" ".env.production"
    echo -e "\033[0;36mCopied root .env to frontend/.env.production\033[0m"
fi

echo -e "\n\033[0;33m[1/4] Installing dependencies...\033[0m"
npm install

echo -e "\n\033[0;33m[2/4] Building Next.js frontend...\033[0m"
npm run build:mobile

echo -e "\n\033[0;33m[3/4] Building Android APK via Gradle...\033[0m"
cd android

# Workaround for Java 25 unsupported issue (Mac/Linux paths would differ, but added for consistency)
if [ -d "/Applications/Android Studio.app/Contents/jbr/Contents/Home" ]; then
    export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"
elif [ -d "/opt/android-studio/jbr" ]; then
    export JAVA_HOME="/opt/android-studio/jbr"
fi

if [ -n "$JAVA_HOME" ]; then
    ./gradlew assembleDebug "-Dorg.gradle.java.home=$JAVA_HOME"
else
    ./gradlew assembleDebug
fi

cd ../..

echo -e "\n\033[0;33m[4/4] Copying APK to root directory...\033[0m"
APK_PATH="frontend/android/app/build/outputs/apk/debug/app-debug.apk"

if [ -f "$APK_PATH" ]; then
    cp "$APK_PATH" "./biasharaiq-debug.apk"
    echo -e "\n\033[0;32m✅ Build Successful! The APK is available at: $(pwd)/biasharaiq-debug.apk\033[0m"
else
    echo -e "\n\033[0;31m❌ Build Failed! Could not find the generated APK at $APK_PATH.\033[0m"
fi
