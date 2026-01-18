#!/usr/bin/env bash
set -o errexit

# လိုအပ်တဲ့ Python library တွေသွင်းခြင်း
pip install -r requirements.txt

# FFmpeg ကို အသစ်ပြန်ဒေါင်းပြီး နေရာချခြင်း
rm -rf ffmpeg
mkdir -p ffmpeg
cd ffmpeg
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
cd ..
