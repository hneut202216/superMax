import json
from flask import Flask, render_template
import subprocess

app = Flask(__name__)

with open('data.json', 'r') as f:
    users_data = json.load(f)
    users = users_data['users']

with open('groups.json', 'r') as f:
    groups_data = json.load(f)
    groups = groups_data['groups']

def check_ping(ip):
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception as e:
        return False

def check_open_ports(ip, ports):
    try:
        port_str = ','.join(map(str, ports))
        result = subprocess.run(['nmap', '--host-timeout', '1s', '-p', port_str, ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        open_ports = []
        for line in result.stdout.splitlines():
            if "/tcp" in line and "open" in line:
                open_ports.append(int(line.split('/')[0]))
        return open_ports
    except Exception as e:
        return []

def get_ip_from_domain(domain):
    try:
        result = subprocess.run(['dig', '+short', '+timeout=1', domain], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ip = result.stdout.strip()
        return ip if ip else None
    except Exception as e:
        return None

def check_http_status(url):
    try:
        result = subprocess.run(['curl', '-s', '-I', '-w', '%{http_code}', '--max-time', '1', '-o', '/dev/null', url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        http_status = result.stdout.strip()
        return int(http_status)
    except Exception as e:
        return None

@app.route('/')
def index():
    results = []
    ports_to_check = [80, 8080, 443, 53]
    group_ips = {}

    for group_name in groups:
        domain = f"ns.{group_name}.ephec-ti.be"
        domain_ip = get_ip_from_domain(domain)
        if domain_ip:
            group_ips[domain_ip] = group_name

    for user in users:
        ip = user['ip']
        name = user['name']
        is_ping_ok = check_ping(ip)
        open_ports = check_open_ports(ip, ports_to_check)
        group_name = group_ips.get(ip, '')

        group_http_status = None
        group_https_status = None
        if group_name:
            group_http_url = f"http://www.{group_name}.ephec-ti.be"
            group_http_status = check_http_status(group_http_url)
            if group_http_status == 200 or group_http_status == 301:
                group_https_url = f"https://www.{group_name}.ephec-ti.be"
                group_https_status = check_http_status(group_https_url)

        results.append({
            'name': name,
            'ip': ip,
            'ping_status': 'OK' if is_ping_ok else 'NOK',
            'open_ports': open_ports,
            'group_name': group_name,
            'group_http_status': group_http_status,
            'group_https_status': group_https_status
        })

    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
