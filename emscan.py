'''
Github: https://github.com/0xEmbo/
Usage:
   Example: sudo python3 p0r75c4nn3r.py -H 127.0.0.1 -u      --> Scans top ports (Default) (-u To skip host discovery)
   Example: sudo python3 p0r75c4nn3r.py -H target.com -v     --> Scans top ports (Default) (-v To enable verbose mode)
   Example: sudo python3 p0r75c4nn3r.py -H 192.168.1.0/24 -p 80 -w output.txt    --> (-w To write the output to a file)
   Example: sudo python3 p0r75c4nn3r.py -H 192.168.1.1-100 -p 22,80,139,443,445
   Example: sudo python3 p0r75c4nn3r.py -H 127.0.0.1 -p 1-1000
'''

from scapy.all import *
from termcolor import colored
from queue import Queue
from collections import defaultdict
import argparse
import colorama
import threading
import time
import socket
import ipaddress
import nmap

class PortScanner:
    def __init__(self, hosts, ports=False, verbose=False, up=False, write=False):
        self.hosts = hosts
        self.verbose = verbose
        self.up = up
        self.write = write
        self.hosts_queue = Queue()
        self.ports_queue = Queue()
        self.lock = threading.Lock()
        socket.setdefaulttimeout(0.2)
        colorama.init()
        self.up_hosts = []
        self.hosts_ports_dict = defaultdict(list)
        self.start_time = 0
        self.end_time = 0
        if ports:
            self.ports = ports
        else:
            self.ports = "20,21,22,23,25,47,53,69,80,110,113,123,135,137,138,139,143,161,179,194,201,311,389,427,443,445,465,500,513,514,515,530,548,554,563,587,593,601,631,636,660,674,691,694,749,751,843,873,901,902,903,987,990,992,993,994,995,1000,1167,1234,1433,1434,1521,1528,1723,1812,1813,2000,2049,2375,2376,2077,2078,2082,2083,2086,2087,2095,2096,2222,2433,2483,2484,2638,3000,3260,3283,3306,3389,3478,3690,4000,5000,5432,5433,6000,6667,7000,8000,8080,8443,8880,8888,9000,9001,9418,9998,27017,27018,27019,28017,32400"

    def banner(self):
        print(' ')
        print(colored("    ____   ___      _____ ____       _  _               _____        ", 'green', attrs=['bold']))
        print(colored("   |  _ \ / _ \ _ _|___  | ___|  ___| || |  _ __  _ __ |___ / _ __   ", 'green', attrs=['bold']))
        print(colored("   | |_) | | | | '__| / /|___ \ / __| || |_| '_ \| '_ \  |_ \| '__|  ", 'green', attrs=['bold']))
        print(colored("   |  __/| |_| | |   / /  ___) | (__|__   _| | | | | | |___) | |     ", 'green', attrs=['bold']))
        print(colored("   |_|    \___/|_|  /_/  |____/ \___|  |_| |_| |_|_| |_|____/|_|     ", 'green', attrs=['bold']))
        print(' ')
        print(colored('\t\t\tBy: ', 'green', attrs=['bold']) + colored('Mohamed Embaby', 'yellow', attrs=['bold']))
        print(colored('\t\t\tGithub: ', 'green', attrs=['bold']) + colored('https://github.com/MohamedEmbaby00/','yellow', attrs=['bold']))
        print('\r\n')

    def host_discovery(self):
        while True:
            host = self.hosts_queue.get()
            icmp = sr1(IP(dst=host) / ICMP(), timeout=1, verbose=0)
            if icmp:
                self.up_hosts.append(host)
                with self.lock:
                    print(colored(f'[+] {host} is up', 'green'))
            self.hosts_queue.task_done()

    def portscan(self, host):
        while not self.ports_queue.empty():
            port = self.ports_queue.get()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((host, port))
                if self.verbose:
                    with self.lock:
                        print(colored(f'\r[+] Discovered open port {port}/tcp on {host}', 'green'))
                self.hosts_ports_dict[host].append(str(port))
                s.close()
            except:
                pass
            self.ports_queue.task_done()

    def resolve_host(self, host):
        try:
            socket.gethostbyname(host)
            return True
        except:
            with self.lock:
                print(colored(f'[-] Unable to resolve hostname for {host}', 'red'))
                return False

    def parse_hosts(self):
        if '/' in self.hosts:
            try:
                for host in ipaddress.IPv4Network(self.hosts):
                    if not self.resolve_host(str(host)):
                        continue
                    self.hosts_queue.put(str(host))
            except ipaddress.AddressValueError:
                print(colored('[-] Invalid format!', 'red'))
                exit()
        elif '-' in self.hosts:
            host = self.hosts[:self.hosts.rfind('.') + 1]
            for i in range(int(self.hosts.split('.')[3].split('-')[0]), int(self.hosts.split('.')[3].split('-')[1])):
                if not self.resolve_host(host + str(i)):
                    continue
                self.hosts_queue.put(host + str(i))
        else:
            if not self.resolve_host(self.hosts):
                exit()
            self.hosts_queue.put(self.hosts)

    def parse_ports(self):
        if '-' in self.ports:
            ports = list(map(int, self.ports.split('-')))
            for port in range(ports[0], ports[1] + 1):
                self.ports_queue.put(port)
        elif ',' in self.ports:
            ports = list(map(int, self.ports.split(',')))
            for port in ports:
                self.ports_queue.put(port)
        else:
            self.ports_queue.put(int(self.ports))

    def start_host_discovery(self):
        print(colored('[*] Checking if host(s) are up...', 'yellow'))
        for _ in range(100):
            hosts_thread = threading.Thread(target=self.host_discovery)
            hosts_thread.daemon = True
            hosts_thread.start()
        self.hosts_queue.join()

    def start_portscan(self):
        for host in self.up_hosts:
            for _ in range(200):
                ports_thread = threading.Thread(target=self.portscan, args=(host,))
                ports_thread.daemon = True
                ports_thread.start()
            self.ports_queue.join()
            self.parse_ports()

    def print_result(self):
        for host, ports_list in self.hosts_ports_dict.items():
            print(colored(f'\r\n[*] Scan report for {host}', 'yellow'))
            print(colored('\r\n[*] PORT\tSERVICE\t\tVERSION', 'yellow'))
            for port in ports_list:
                print(colored(f'[+] {port}', 'green'))
        print(colored(f'\n[*] Scan finished in {self.end_time - self.start_time} second(s)', 'yellow'))

    def save_result(self):
        if self.write:
            output = open(self.write, 'w')
            for host, ports_list in self.hosts_ports_dict.items():
                output.write(f'[*] Scan report for {host}\n')
                output.write('\n[*] PORT\tSERVICE\t\tVERSION\n')
                for port in ports_list:
                    output.write(f'[+] {port}\n')
                output.write('\n')

            output.write(f'\n[*] Scan finished in {self.end_time - self.start_time} second(s)')
            output.close()

    def banner_grabbing(self):
        nmScan = nmap.PortScanner()
        for host, ports_list in self.hosts_ports_dict.items():
            ports = ','.join(ports_list)
            nmScan.scan(host, ports, arguments='-sS -sV')
            ports = nmScan[host]['tcp'].items()
            for port in ports:
                port_number = port[0]
                service_name = port[1]['name']
                product = port[1]['product']
                version = port[1]['version']
                extrainfo = port[1]['extrainfo']
                banner = f'{port_number}/tcp\t{service_name}\t\t{product} {version} ({extrainfo})'
                index = ports_list.index(str(port[0]))
                ports_list[index] = banner

    def run(self):
        self.banner()
        self.parse_hosts()
        self.start_time = time.time()
        if self.up:
            print(colored('[*] Skipping host discovery...', 'yellow'))
            print(colored('[*] Port Scanning Started...', 'yellow'))
            self.parse_ports()
            while not self.hosts_queue.empty():
                self.up_hosts.append(self.hosts_queue.get())
                self.hosts_queue.task_done()
        else:
            self.start_host_discovery()
            print(colored('[*] Port Scanning Started...', 'yellow'))
            self.parse_ports()
        self.start_portscan()
        print(colored('[*] Service/version scan started..', 'yellow'))
        self.banner_grabbing()
        self.end_time = time.time()
        self.print_result()
        self.save_result()


parser = argparse.ArgumentParser(description='- A simple port scanner that scans multiple hosts concurrenty.', usage='sudo python3 p0r75c4nn3r.py -H <host(s)> -p <port(s)> OPTIONS')
parser.add_argument('-H', '--hosts', metavar='', required=True, help='Host(s) to scan [e.g: -H 127.0.0.1 , -H 192.168.1.0/24 , -H 192.168.1.1-50]')
parser.add_argument('-p', '--ports', metavar='', help='Port(s) to scan [e.g: -p80 , -p1-1000 , -p22,139,445,80]')
parser.add_argument('-u', '--up', help='Treat all hosts as online (Skip host discovery)', action='store_true')
parser.add_argument('-v', '--verbose', help='Verbose mode', action='store_true')
parser.add_argument('-w', '--write', metavar='', help='Save output to a file')
args = parser.parse_args()

port_scanner = PortScanner(args.hosts, args.ports, args.verbose, args.up, args.write)
port_scanner.run()
