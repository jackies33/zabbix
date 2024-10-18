


import datetime
import time
import sys

sys.path.append("/opt/db_backup/")

from zbx_backup.execution.postgresql_exec import execution_core





'''
for daemon setup script
create  - >> "mcedit /etc/systemd/system/zbx_backup.service"
copy in zbx_backup.service ->>
_______________________________

[Unit]
Description=DB zabbix and grafana backup service

[Service]
ExecStart=/usr/bin/python3 /opt/db_backup/zbx_backup/scheduler.py
StandardOutput=file:/var/log/zbx_backup/output_sys.log
StandardError=file:/var/log/zbx_backup/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in zbx_backup.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable zbx_backup.service
sudo systemctl start zbx_backup.service

______________________________

<<--- run next commands

'''




i = 0

def run_backups():
    execution_core()


run_time = datetime.time(hour=23, minute=55, second=0)

while i == 0:
    execution_core()
    i = 1

while i == 1:
    now = datetime.datetime.now()
    if now.weekday() == 6 and now.time() >= run_time:
        run_backups()
        time.sleep(7200) #sleep for waiting other day, and don't let to make job again in the same day
    else:
        time.sleep(120) # enough time for request , and also not so often




