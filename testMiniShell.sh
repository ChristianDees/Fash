ls
chmod u+x spinner.py
mkdir -p mytestbin
cd mytestbin
echo 'import sys; print(f"echo {sys.argv[1]}")' > line1.txt
echo '#!/usr/bin/env python3' > header.txt
cat header.txt line1.txt > pyecho.py
chmod u+x pyecho.py
cd .. 
pyecho.py echo > echo-out1.txt
pyecho.py echo > echo-out2.txt
nonExistentCommand
ls nonExistentFile
Python3 spinner.py 10000000 &
wc < echo-out1.txt 
wc echo-out1.txt echo-out2.txt  | grep total
exit
