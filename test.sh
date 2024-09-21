#!/usr/bin/env bash
ls
mkdir -p mytestbin
cd mytestbin
echo 'import sys; print(f"echo {sys.argv[1]}")' > line1.txt
cat line1.txt

