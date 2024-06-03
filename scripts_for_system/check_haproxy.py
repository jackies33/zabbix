



'''
for daemon setup script
create  - >> "mcedit /etc/systemd/system/check_haproxy.service"
copy in check_haproxy.service ->>
_______________________________

[Unit]
Description=Check haproxy service

[Service]
ExecStart=/usr/bin/python3 /etc/keepalived/check_haproxy.py
WorkingDirectory=/etc/keepalived/
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----check_haproxy.service

run next commands -->>>
_____________________________

sudo systemctl daemon-reload
sudo systemctl enable check_haproxy.service
sudo systemctl start check_haproxy.service

______________________________

<<--- run next commands

'''



import subprocess
import time

current_status = ''

while True:
    try:
        haproxy_status = subprocess.run(["systemctl", "is-active", "haproxy.service"], capture_output=True, text=True).stdout.strip()
        if haproxy_status == "active":
            if current_status == "running":
                pass
            elif current_status == "":
                current_status = "running"
            elif current_status == "waiting":
                subprocess.run(["systemctl", "restart", "haproxy"])
                current_status = "failed"
            elif current_status == "failed":
                subprocess.run(["systemctl", "start", "keepalived"])
                current_status = "running"
            elif current_status == "failed_first":
                current_status = "running"

        else:
            if current_status == "":
                subprocess.run(["systemctl", "restart", "haproxy"])
                current_status = "failed"
            elif current_status == "failed":
                subprocess.run(["systemctl", "restart", "haproxy"])
            elif current_status == "failed_first":
                subprocess.run(["systemctl", "stop", "keepalived"])
                subprocess.run(["systemctl", "restart", "haproxy"])
                current_status = "failed"
            elif current_status == "running":
                subprocess.run(["systemctl", "restart", "haproxy"])
                current_status = "failed_first"


        time.sleep(5)
    except Exception as e:
        print(e)
        time.sleep(5)



