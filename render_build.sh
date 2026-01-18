#!/usr/bin/env bash
set -o errexit

# Python libraries သွင်းခြင်း
pip install -r requirements.txt

# FFmpeg ဒေါင်းလုဒ်ဆွဲခြင်း
mkdir -p ffmpeg
cd ffmpeg
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
cd ..
