### A simple multi-threaded TCP port scanner.

## Usage:
   	sudo python3 emscan.py -H 127.0.0.1 -u      --> Scans top ports (Default) (-u To skip host discovery)
   	sudo python3 emscan.py -H target.com -v     --> Scans top ports (Default) (-v To enable verbose mode)
   	sudo python3 emscan.py -H 192.168.1.0/24 -p 80 -w output.txt    --> (-w To write the output to a file)
   	sudo python3 emscan.py -H 192.168.1.1-100 -p 22,80,139,443,445
   	sudo python3 emscan.py -H 127.0.0.1 -p 1-1000
