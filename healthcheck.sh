#!/usr/bin/env bash

files=$(find . -name healthcheck -newermt '-30 seconds' | wc -l )

if (( $files == 0)); then
    exit 1
fi

echo "ok"