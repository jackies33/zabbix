




'''
for daemon setup script
create  - >> "mcedit /etc/systemd/system/airwave_ap.service"
copy in airwave_ap.service ->>
_______________________________

[Unit]
Description=Run service for get data for WAP's Air Wave Aruba

[Service]
ExecStart=/usr/bin/python3 /opt/zabbix_custom/zabbix_WRK/AirWaveAP/discovery.py
StandardOutput=file:/var/log/zabbix_custom/zabbix_WRK/AirWaveAP/output_sys.log
StandardError=file:/var/log/zabbix_custom/zabbix_WRK/AirWaveAP/error.log
Restart=always

[Install]
WantedBy=multi-user.target
_________________________________

<<----copy in airwave_ap.service

run next commands -->>>
_____________________________
sudo systemctl daemon-reload
sudo systemctl enable airwave_ap.service
sudo systemctl start airwave_ap.service

______________________________

<<--- run next commands

'''





from netbox_get import NetboxGet
import schedule
import time

from my_env import ZABBIX_SENDER_URL
import air_wave_wrk
from zbx_sender import send_to_zabbix_bulk
result_devices_from_nb = []
i = 0

def update_nb_devices(wap_scope_hostname):
     geting_nb = NetboxGet()
     global result_devices_from_nb
     result_devices_from_nb = geting_nb.get_wap_devices(**{"wap_scope_hostname": wap_scope_hostname})
     return result_devices_from_nb

def start_main(wap_scope_hostname):
     global result_devices_from_nb
     if result_devices_from_nb == []:
          result_devices_from_nb = update_nb_devices(**{"wap_scope_hostname":wap_scope_hostname})
     result_from_aruba = air_wave_wrk.start_process(result_devices_from_nb)
     if result_from_aruba:
          if result_from_aruba[0] == True:
               send_to_zabbix_bulk(ZABBIX_SENDER_URL, result_from_aruba[1])
               time.sleep(5)
               send_to_zabbix_bulk(ZABBIX_SENDER_URL, result_from_aruba[2])
          elif result_from_aruba[0] == False:
               print(result_from_aruba[1])


if __name__ == "__main__":
     wap_scope_hostname = "wap-dpmo"
     schedule.every(5).minutes.do(start_main, wap_scope_hostname)
     schedule.every(2).hours.do(update_nb_devices, wap_scope_hostname)
     while i == 0:
          update_nb_devices(wap_scope_hostname)
          time.sleep(5)
          start_main(wap_scope_hostname)
          i = i + 1
     while i == 1:
          schedule.run_pending()
          time.sleep(10)



