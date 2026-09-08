#!/bin/sh
# Install the same official llama.cpp revision as the Windows measurements.
set -eu
cd "$(dirname "$0")/.."
mkdir -p work/llama-metal
archive=work/llama-b10852-bin-macos-arm64.tar.gz
curl -fL --retry 5 -C - https://github.com/ggml-org/llama.cpp/releases/download/b10852/llama-b10852-bin-macos-arm64.tar.gz -o "$archive"
printf '%s  %s\n' 0a1bd66656354e43bc90fb7d7ce5a56c5683f338706e5d59fd4e38e7f44c4008 "$archive" | shasum -a 256 -c -
tar -xzf "$archive" -C work/llama-metal
work/llama-metal/llama-b10852/llama-bench --list-devices
