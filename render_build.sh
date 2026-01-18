#!/usr/bin/env bash
set -o errexit

# Install required python packages
pip install flask python-telegram-bot yt-dlp

# Download and setup FFmpeg
mkdir -p ffmpeg
cd ffmpeg
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz | tar -xJ --strip-components=1
cd ..
