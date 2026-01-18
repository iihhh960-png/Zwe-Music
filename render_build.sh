#!/usr/bin/env bash
# အမှားရှိရင် ရပ်လိုက်ရန်
set -o errexit

# Python library များသွင်းခြင်း
pip install -r requirements.txt

# FFmpeg ကို binary အနေနဲ့ ဒေါင်းလုဒ်ဆွဲခြင်း
mkdir -p ffmpeg
cd ffmpeg
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
cd ..
