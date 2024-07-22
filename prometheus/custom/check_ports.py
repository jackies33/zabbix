

'''
for executing script for collect data about ports in local
create  - >> "mcedit /etc/systemd/system/check_ports.service"
copy in check_ports.service ->>
_______________________________

[Unit]
Description=collect data about ports in local

[Service]
ExecStart=/usr/bin/python3 /opt/prometheus/scripts/check_ports.py
WorkingDirectory=/opt/prometheus/scripts/
StandardOutput=file:/var/log/prometheus/scripts/output.log
StandardError=file:/var/log/prometheus/scripts/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----check_ports.service

run next commands -->>>
_____________________________

sudo systemctl daemon-reload
sudo systemctl enable check_ports.service
sudo systemctl start check_ports.service

______________________________

<<--- run next commands

for node_exporter !!!! below

nohup /opt/prometheus/node_exporter-1.2.2.linux-amd64/node_exporter --collector.textfile.directory=/opt/prometheus/node_exporter-1.2.2.linux-amd64/textfile > node_exporter.log 2>&1 &




'''



import concurrent.futures
import time
import socket
from fastapi import FastAPI
import uvicorn
import threading
import paramiko
import pexpect

from data import hosts_ports_tcp,hosts_ports_udp,prometheus_file,password_pyadmin,pyusername

app = FastAPI()

def check_tcp_port(host, port, name_service=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            if result == 0:
                return (host, port, 'tcp', 1, name_service)
            else:
                return (host, port, 'tcp', 0, name_service)
    except Exception as e:
        print(f"Error checking TCP port {port} on {host}: {e}")
        return (host, port, 'tcp', 0, name_service)

"""
def check_udp_port_via_ssh(host, port, name_service, host_for_connection ):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host_for_connection, username=pyusername, password=password_pyadmin)
        stdin, stdout, stderr = ssh_client.exec_command('netstat -tuln')
        output = stdout.read().decode()
        #print(output)
        if f':{port}' in output:
            result = 1

        else:
            result = 0

        ssh_client.close()
        return (host, port, 'udp', result, name_service)
    except Exception as e:
        print(f"Error checking UDP port {port} on {host} via SSH: {e}")
        return (host, port, 'udp', 0, name_service)
"""

def check_udp(host, port, name_service, host_for_connection ):
    command = f"nc -v -u {host} {port}"
    try:
        child = pexpect.spawn(command)
        index = child.expect([pexpect.EOF, "succeeded!"], timeout=30)

        if index == 1:
            out_row = child.before.decode().split("udp/")[1].split("]")[0]
            if out_row in name_service:
                return (host, port, 'udp', 1, name_service)
        else:
            return (host, port, 'udp', 0, name_service)

        child.close()

    except pexpect.exceptions.TIMEOUT as e:
        print("Timeout expired:", e)
        return (host, port, 'udp', 0, name_service)
    except pexpect.exceptions.EOF as e:
        print("End Of File (EOF) reached:", e)
        return (host, port, 'udp', 0, name_service)

    except Exception as e:
        print("An error occurred:", e)
        return (host, port, 'udp', 0, name_service)



def check_port(host, port, protocol, name_service=None, host_for_connection=None):
    if protocol == 'tcp':
        return check_tcp_port(host, port, name_service)
    elif protocol == 'udp':
        return check_udp(host, port, name_service , host_for_connection)
    else:
        print(f"Unsupported protocol {protocol}")
        return (host, port, protocol, 0, name_service, host_for_connection)



def run_job():
    results_by_node = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {
            executor.submit(check_port, host, port, protocol, name_service): (host, port, protocol, node_name, name_service)
            for host, port, protocol, node_name, name_service in hosts_ports_tcp
        }

        for future in concurrent.futures.as_completed(future_to_port):
            try:
                result = future.result()
                host, port, protocol, node_name, name_service = future_to_port[future]
                key = node_name
                if key not in results_by_node:
                    results_by_node[key] = []
                results_by_node[key].append(result)
            except Exception as e:
                print(f"Exception occurred: {e}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_port = {
            executor.submit(check_port, host, port, protocol, name_service,host_for_connection): (host, port, protocol, node_name, name_service, host_for_connection)
            for host, port, protocol, node_name, name_service, host_for_connection in hosts_ports_udp
        }

        for future in concurrent.futures.as_completed(future_to_port):
            try:
                result = future.result()
                host, port, protocol, node_name, name_service, host_for_connection= future_to_port[future]
                key = node_name
                if key not in results_by_node:
                    results_by_node[key] = []
                results_by_node[key].append(result)
            except Exception as e:
                print(f"Exception occurred: {e}")

    with open(prometheus_file, 'w') as f:
        for node_name, results in results_by_node.items():
            for result in results:
                try:
                    name_service = result[4] if len(result) > 4 else None
                    host_full = f"{node_name} | {name_service} | {result[0]}:{result[1]}"
                    result_str = (
                        f'ports_status{{node_name="{node_name}", host_full="{host_full}", host="{result[0]}", '
                        f'port="{result[1]}", protocol="{result[2]}", name_service="{name_service}"}} {result[3]}'
                    )
                    f.write(result_str + '\n')
                except Exception as e:
                    print(f"Exception occurred: {e}")

    print(f"Metrics saved to {prometheus_file}")


def run_web():
    server_port = 8085
    uvicorn.run(app, host="0.0.0.0", port=server_port)

def start_job():
    while True:
        run_job()
        time.sleep(120)


if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=False).start()
    threading.Thread(target=start_job(), daemon=True).start()






