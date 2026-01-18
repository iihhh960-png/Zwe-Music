#!/usr/bin/env bash
set -o errexit

# Python library များကို အတိအကျ သွင်းခြင်း
pip install flask python-telegram-bot yt-dlp

# FFmpeg ကို ဒေါင်းလုဒ်ဆွဲပြီး နေရာချခြင်း
mkdir -p ffmpeg
cd ffmpeg
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
cd ..
