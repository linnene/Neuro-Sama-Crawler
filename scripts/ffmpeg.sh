#!/usr/bin/env bash

URL="https://cn-sdqd-cu-01-12.bilivideo.com/live-bvc/xxxxxxxx.flv?expires=..."

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ffplay \
  -loglevel info \
  -fflags nobuffer \
  -user_agent "$UA" \
  -headers "Referer: https://live.bilibili.com/" \
  ""