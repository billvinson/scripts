import psutil
import re
import socket
import subprocess

def collect_process_hosts(process_name, resolve_hostnames=True):
    """
    Return a list of (ip, hostname) tuples connected to a given process via lsof.
    Handles IPv4 and IPv6, including link-local IPv6 with interface scope.
    """
    if process_name is None:
        return []

    server_hostname = socket.gethostname()

    try:
        result = subprocess.run(
            ["lsof", "-i", "-nP", "-a", "-c", process_name],
            capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return []

    ip_pattern = re.compile(r'(\d+\.\d+\.\d+\.\d+|\[[0-9a-fA-F:]+\])')

    ips = []
    for line in result.stdout.splitlines():
        if "ESTABLISHED" in line:
            ips.extend(ip_pattern.findall(line))

    # Clean IPv6 addresses (remove brackets)
    ips = [ip.strip("[]") for ip in ips]
    ips = sorted(set(ips))

    if not resolve_hostnames:
        return [(ip, None) for ip in ips]

    resolved = []
    for ip in ips:
        hostname = None
        if ip.startswith("fe80:"):  # IPv6 link-local, needs scope
            for iface in psutil.net_if_addrs().keys():
                try:
                    candidate = f"{ip}%{iface}"
                    hostname = socket.getnameinfo((candidate, 0), 0)[0]
                    if hostname:
                        break
                except Exception:
                    continue
        else:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except Exception:
                hostname = None
        
        if hostname != server_hostname:
            if hostname is not None:
                resolved.append(hostname)
            else:
                resolved.append(ip)
    
    return resolved
