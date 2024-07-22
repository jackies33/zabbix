


import sys
from concurrent.futures import ThreadPoolExecutor
import time

sys.path.append('/opt/zabbix_custom/')

from remote_system.core.netbox_get import NetboxGet
from remote_system.core.zabbix_get import GetHost
from remote_system.core.parser_and_preparing import Parser_Json
from remote_system.executor_with_hosts.delete_host import Remover_Hosts
from remote_system.executor_with_hosts.update_host import Updater_Hosts
from remote_system.executor_with_hosts.create_host import Creator_Hosts

class PrepData():
    def __init__(self):
        """

        """
    def from_nb(self):
        netbox_get = NetboxGet()
        devices = netbox_get.get_all_devices()
        return devices
    def from_zbx(self):
        zabbix_get = GetHost()
        hosts = zabbix_get.get_all_hosts()
        return hosts


def perform_with_delay(func, *args, delay=0.5):
    result = func(*args)
    time.sleep(delay)
    return result

def start_export_devices():
    list_for_delete = []
    list_for_create = []
    dev = PrepData()
    devices_remote = dev.from_nb()
    #print(devices_remote)
    print("Succesfull downloaded devices from Netbox")
    devices_local = dev.from_zbx()
    print("Succesfull check devices in Zabbix")
    #print(devices_local)
    compare = Parser_Json()
    comparing = compare.compare_exporter(**{'devices_remote': devices_remote,'devices_local': devices_local})
    if comparing["create"] != []:
        for c in comparing["create"]:
            list_for_create.append(c)
    if comparing["delete"] != []:
        for c in comparing["delete"]:
            list_for_create.append(c)
            list_for_delete.append(c)
    with ThreadPoolExecutor(max_workers=20) as executor: #delete or try to delete devices from list for preparing nonmixed devices before create
        remover_instances = [Remover_Hosts(data) for data in list_for_delete]
        results = executor.map(lambda remover: perform_with_delay(remover.remove_host), remover_instances)
        for result in results:
            print(result)
    with ThreadPoolExecutor(max_workers=20) as executor:  # create full device
        creator_instances = [Creator_Hosts(data) for data in list_for_create]
        results = executor.map(lambda creator: perform_with_delay(creator.create_host_full), creator_instances)
        for result in results:
            print(result)
    with ThreadPoolExecutor(max_workers=20) as executor: #update hosts from list
        updater_instances = [Updater_Hosts(**data) for data in comparing["update"]]
        results = executor.map(lambda update: perform_with_delay(update.update_host, "export"), updater_instances)
        for result in results:
            print(result)
    return "Export has been successful"

start_export_devices()
