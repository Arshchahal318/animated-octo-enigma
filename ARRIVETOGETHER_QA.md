# ArriveTogether APK test harness

Runs the released public APK on Android 15 using [ReactiveCircus/android-emulator-runner](https://github.com/ReactiveCircus/android-emulator-runner) (Apache-2.0). This harness invokes that action; it does not duplicate its source.

The workflow verifies the APK package/version and SHA-256, installs it, checks accessible guest navigation, cold relaunch and Android runtime crashes, and saves screenshots and a JSON report. No credentials, private app source, account records or production signing keys are included. Guest evidence is public; never add signed-in screenshots or account credentials to this workflow.

Run **Actions → ArriveTogether APK smoke tests → Run workflow** after a new APK release. Standard hosted runner compute for public repositories is free under GitHub's terms; artifacts expire after one day. There is no recurring schedule or paid runner. Results are shown in the website's administrator test studio.

These tests do not validate login, multi-account crew approval/chat, identity verification, billing, physical hardware or Play Store compliance. A successful smoke run is not a full release certification.
