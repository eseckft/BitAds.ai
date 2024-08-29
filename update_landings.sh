#!/bin/bash

wget -q -O landings.zip https://public.a.bitads.ai/p.bitads.ai.zip

# Find all directories in zip
directories_in_zip=$(zipinfo -1 landings.zip "*/*" | awk -F'/' '!seen[$1]++ {print "statics/campaigns/" $1}')

unzip -o landings.zip -d statics/campaigns

# Loop through directories after unzipping
for dir in statics/campaigns/*; do
    if [[ -d $dir ]]; then
        if ! echo "$directories_in_zip" | grep -q "$(basename "$dir")"; then
            echo "Removing $dir"
            rm -rf "$dir"
        fi
    fi
done
