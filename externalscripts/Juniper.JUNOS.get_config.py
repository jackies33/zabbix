#!/usr/bin/env python3

import sys
from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from ZabbixSender import ZabbixSender,ZabbixPacket
from pyzabbix import ZabbixAPI
import json
import base64


sys.path.append("/usr/lib/zabbix/")

from externalscripts.my_env import noc_login, noc_pass,zbx_api_url,zbx_api_token


def get_config(host):
    try:
        dev = Device(host=host, user=noc_login, passwd=noc_pass)
        #print(noc_login)
        #print(noc_pass)
        #print(dev)
        dev.open()
        config_output = dev.cli("show configuration | display set")
        dev.close()
        print(config_output)
        #zapi = ZabbixAPI(zbx_api_url)
        #zapi.session.verify = False
        #zapi.login(api_token=zbx_api_token)
        #host_name = zapi.host.get(filter={"ip": host}, selectInterfaces=["ip"])[0]['host']
        #send_to_zabbix(host_name,config_output)
    except ConnectError as err:
        print(f"Cannot connect to device: {err}")
        return 1
    except Exception as err:
        print(f"Error getting configuration: {err}")
        dev.close()
        return 1

    dev.close()
    return 0

"""
def send_to_zabbix(host, data):
    #print(host)
    zabbix_sender = ZabbixSender('10.50.52.193', 10051)
    #print(zabbix_sender)
    #print(data)
    packet = ZabbixPacket()
    encoded_data = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    packet.add(host, "Juniper.config", encoded_data)
    print(packet)
    print(zabbix_sender)

    try:
        result = zabbix_sender.send(packet)
        print(f"Zabbix sender result: {result}")
    except Exception as e:
        print(f"Failed to send data to Zabbix: {str(e)}")
"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <host>")
        sys.exit(1)

    host = sys.argv[1]

    sys.exit(get_config(host))





