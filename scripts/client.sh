#!/bin/bash

while true; do
    echo -n "client:> "
    read -r input
    
    if [ -z "$input" ]; then
        continue
    fi
    
    if [ "$input" = "exit" ] || [ "$input" = "quit" ]; then
        break
    fi
    
    echo "$input" | python3 client.py
    echo
done

