[app]

# App identity
title = My First App
package.name = myfirstapp
package.domain = com.sarthak
version = 1.0

# Include the Python source and app icon.
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,txt

# Android configuration
orientation = portrait
fullscreen = 0
icon.filename = %(source.dir)s/icon.png

# No Android permissions are required by this calculator.
android.permissions =
android.api = 36
android.minapi = 23
android.ndk = 29
android.archs = arm64-v8a
android.accept_sdk_license = True

# Use the current python-for-android development branch for API 36 / NDK 29.
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
