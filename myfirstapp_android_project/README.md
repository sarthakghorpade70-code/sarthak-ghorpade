# My First App — Android build project

This is your Kivy calculator project prepared for an Android debug APK build.

## Build it with GitHub Actions (no Android SDK installation on your PC)

1. Create a new GitHub repository and upload the **contents** of this folder (including the hidden `.github` folder).
2. Open the repository's **Actions** tab.
3. Select **Build Android APK**.
4. Select **Run workflow** and start the workflow.
5. When the run finishes successfully, open that run and download the artifact named `my-first-app-debug-apk`.
6. Extract the downloaded artifact. It contains the `.apk` file, which can be installed on an Android phone.

The workflow builds a debug APK for `arm64-v8a` devices. It is suitable for testing and direct installation, not for publishing as a signed release on Google Play.

## Build locally on Linux or WSL2

Install the Android build dependencies from the official Buildozer installation guide, activate a Python virtual environment, and run:

```bash
python -m pip install --upgrade pip
python -m pip install git+https://github.com/kivy/buildozer
python -m pip install legacy-cgi setuptools cython==0.29.34
buildozer android debug
```

The APK is generated in the `bin/` directory.

## Project notes

- Main app: `main.py`
- App icon: `icon.png`
- Android settings: `buildozer.spec`
- The missing `splash.png` reference from the uploaded config was removed; no splash image is needed for this project.
- The calculator requests no Android permissions.
