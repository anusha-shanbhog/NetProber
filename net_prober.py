import os
import platform
import socket
from multiprocessing import Pool
import subprocess
import re

def get_mac_address(host):
    try:
        output = subprocess.check_output(['arp', '-n', host])
        output = output.decode('utf-8').strip()

        pattern = re.compile(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})')
        mac_address = re.search(pattern, output)

        if mac_address:
            return mac_address.group(0)
        else:
            return "Not available"
    except Exception as e:
        print("Error retrieving MAC address for", host, ":", str(e))
        return None

def ping_sweep(host):
    response = os.system("ping -c 1 -w 1 " + host + " >/dev/null")
    if response == 0:
        mac_address = get_mac_address(host)
        if mac_address is None:
            return host, "MAC Address: Not available", []
        else:
            open_ports = scan_open_ports(host)
            return host, "MAC Address: " + mac_address, open_ports
    else:
        return None

def scan_open_ports(host):
    open_ports = []
    for port in range(1, 1001):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    return open_ports

def main():
    IP = input("[+] Enter the Host IP Address:\t")
    print("[+] Starting NetProber on " + IP)
    dot = IP.rfind(".")
    IP = IP[0:dot + 1]

    hosts = [IP + str(i) for i in range(1, 255)]

    with Pool() as pool:
        results = pool.map(ping_sweep, hosts)

    reachable_hosts = [result for result in results if result is not None]
    reachable_ips = []

    if len(reachable_hosts) > 0:
        for host, details, open_ports in reachable_hosts:
            print(host + " is up")
            print(details)
            if len(open_ports) > 0:
                print("Open Ports: ", open_ports)
            else:
                print("No open ports found.")
            reachable_ips.append(host)
    else:
        print("All hosts are unreachable")

    print("Reachable IP addresses:", reachable_ips)

if __name__ == "__main__":
    main()
