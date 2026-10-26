# OpenChat 动态分析一键脚本 (PowerShell)
# 前提: D:\android-sdk 已就绪 (emulator/platform-tools/system-images 解压完成)
$ErrorActionPreference = "Stop"
$SDK = "D:\android-sdk"
$env:ANDROID_HOME = $SDK
$env:ANDROID_SDK_ROOT = $SDK
$env:PATH = "$SDK\platform-tools;$SDK\emulator;$SDK\cmdline-tools\bin;$env:PATH"
$env:ANDROID_AVD_HOME = "$env:USERPROFILE\.android\avd"
$JAVA = "C:\Program Files\Java\jdk-17\bin\java.exe"

# 1. 创建 AVD
echo "[1] creating AVD (android-30, google_apis, x86_64)..."
$avdDir = "$env:ANDROID_AVD_HOME\openchat.avd"
if (-not (Test-Path $avdDir)) {
  echo "no" | & $JAVA -jar (Get-ChildItem "$SDK\cmdline-tools\lib\*.jar" | Where-Object Name -match "sdkmanager-classpath" | Select -First 1 -ExpandProperty FullName) 2>$null
  # avdmanager via bat
  echo "no" | cmd /c "`"$SDK\cmdline-tools\bin\avdmanager.bat`" create avd -n openchat -k `"system-images;android-30;google_apis;x86_64`" -d pixel_4" 2>&1
} else { echo "    AVD exists" }

# 2. 启动模拟器 (无窗口 + 可写系统盘, 便于装 frida-server)
echo "[2] starting emulator..."
Start-Process -FilePath "$SDK\emulator\emulator.exe" -ArgumentList @("-avd","openchat","-no-window","-no-audio","-no-boot-anim","-writable-system","-gpu","swiftshader_indirect","-no-snapshot") -WindowStyle Hidden

# 3. 等 boot
echo "[3] waiting for boot..."
adb wait-for-device
while ($true) {
  $b = adb shell getprop sys.boot_completed 2>$null
  if ("$b".Trim() -eq "1") { break }
  Start-Sleep 3
}
echo "    booted"

# 4. 装 APK
echo "[4] installing APK..."
adb install -r -g "D:\notrack-2api-app\openchat134\openchat-1.3.4.apk"

# 5. 推 frida-server (需要提前下载)
$fsLocal = "$SDK\frida-server"
if (Test-Path "$fsLocal\frida-server-android") {
  echo "[5] pushing frida-server..."
  adb push "$fsLocal\frida-server-android" /data/local/tmp/fs
  adb shell "chmod 755 /data/local/tmp/fs"
  adb shell "su 0 /data/local/tmp/fs &" # google_apis 镜像有 root (adb root)
}
echo "[6] done. run: frida -U -f open.chat.gpt.aichat.bot.free.app -l hook_z3.js --no-pause"
