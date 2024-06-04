




''' 
for daemon setup script
create  - >> "mcedit etc/systemd/system/check_etcd.service"
copy in check_etcd.service ->> 
_______________________________

[Unit]
Description=Listen etcd service and restart it

[Service]
ExecStart=/usr/bin/python3 /opt/self_services/etcd/check_etcd.py
StandardOutput=file:/var/log/self_services/check_etcd_output.log
StandardError=file:/var/log/self_services/check_etcd_error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in check_etcd.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable check_etcd.service
sudo systemctl start check_etcd.service

______________________________

<<--- run next commands

'''


import subprocess
import time


while True:
    try:
        pg_status = subprocess.run(["systemctl", "is-active", "etcd"], capture_output=True,
                                   text=True).stdout.strip()

        if pg_status == "inactive":
            subprocess.run(["systemctl", "restart", "etcd"])
        elif pg_status == "failed":
            subprocess.run(["systemctl", "restart", "etcd"])
        else:
            pass
        time.sleep(10)

    except Exception as e:
        print(e)





