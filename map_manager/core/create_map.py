





from pyzabbix import ZabbixAPI, ZabbixAPIException
#import re
import random

from keep_api_connect import zabbix_api_instance
from mappings import MAPPINGS
import os
import sys
#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))
from connect_devices_runner import run_in_threads
from parsing_data_maps import parse_all_devices_for_map


def get_devices_by_map_group_with_device_role(map_group,additional_devices_roles):
    try:
        zapi = zabbix_api_instance.get_instance()
        hosts = zapi.host.get(
            output=["hostid", "name"],
            selectGroups=["groupid", "name"],
            selectParentTemplates=["templateid", "name"],
            selectInterfaces=["ip"],
            selectTags="extend"
        )
        #pattern = r"/([^/]+)(?:/|$)"
        filtered_hosts = []
        for host in hosts:
            tags = host.get('tags', [])
            for tag in tags:
                if tag['tag'] == 'MAP_Group' and tag['value'] == map_group:
                    #group = host['groups'][0]['name']
                    #match = re.search(pattern, group)[0].split("/")[1]
                    filtered_hosts.append(host)

        for device_role in additional_devices_roles:
            for host in hosts:
                tags = host.get('tags', [])
                for tag in tags:
                    if tag['tag'] == 'device_role' and tag['value'] == device_role:
                        # group = host['groups'][0]['name']
                        # match = re.search(pattern, group)[0].split("/")[1]
                        filtered_hosts.append(host)

        return filtered_hosts
    except Exception as err:
        print(err)
        return False

def get_devices_by_map_group(map_group):
    try:
        zapi = zabbix_api_instance.get_instance()
        hosts = zapi.host.get(
            output=["hostid", "name"],
            selectGroups=["groupid", "name"],
            selectParentTemplates=["templateid", "name"],
            selectInterfaces=["ip"],
            selectTags="extend"
        )
        #pattern = r"/([^/]+)(?:/|$)"
        filtered_hosts = []
        for host in hosts:
            tags = host.get('tags', [])
            for tag in tags:
                if tag['tag'] == 'MAP_Group' and tag['value'] == map_group:
                    #group = host['groups'][0]['name']
                    #match = re.search(pattern, group)[0].split("/")[1]
                    filtered_hosts.append(host)

        return filtered_hosts
    except Exception as err:
        print(err)
        return False


def create_map(hosts,map_group):
    try:
        zapi = zabbix_api_instance.get_instance()
        map_elements = []
        map_width = 2400
        map_height = 1800
        for host in hosts:
            for tag in host['tags']:
                if tag['tag'] == 'device_role':
                    device_role = tag['value']
                    icon_id = MAPPINGS().get_icon(device_role)
                    if icon_id:
                        map_element = {
                            "selementid": host['hostid'],
                            "elements": [
                                {"hostid": host['hostid']}
                            ],
                            "elementtype": 0,  # 0 означает, что это хост
                            "label": host['name'],
                            "iconid_off": icon_id, # '156' - switch id, '30' - firewall id, '131' - router id
                            "x": random.randint(0, (map_width-200)),  # Случайная координата по X
                            "y": random.randint(0, (map_height-100)),  # Случайная координата по Y
                        }
                    else:
                        map_element = {
                            "selementid": host['hostid'],
                            "elements": [
                                {"hostid": host['hostid']}
                            ],
                            "elementtype": 0,  # 0 означает, что это хост
                            "label": host['name'],
                            "iconid_off": 131, # '156'  # - switch id, '30' - firewall id, '131' - router id
                            "x": random.randint(0, (map_width-200)),  # Случайная координата по X
                            "y": random.randint(0, (map_height-100)),  # Случайная координата по Y
                        }
                    map_elements.append(map_element)
        # Создание карты
        result = zapi.map.create({
            "name": map_group,
            "width": map_width,
            "height": map_height,
            "selements": map_elements
        })
        return result
    except Exception as err:
        print(err)
        return None



if __name__ == "__main__":
    count_true = 0
    count_false = 0
    map_name = "MAP_Group_AZ_DPMO"
    additional_device_role = []
    devices = get_devices_by_map_group_with_device_role(map_name,additional_device_role)
    count_devices = 0
    #print(f"\n\n\nHERE1\n\n\n")
    #for dev in devices:
    #    count_devices = count_devices + 1
    #    print(devices)
    #print(count_devices)
    #print(devices)
    #"""
    results = run_in_threads(devices, max_threads=30)
    hosts_list = []
    hosts_not_connected_list = []
    for res in results:
        if res[0] == False:
            count_false = count_false + 1
            # print(res)
            hosts_not_connected_list.append(res)
        elif res[0] == True:
            count_true = count_true + 1
            # print(res[1])
            hosts_list.append(res[1])
    print(f"False: {count_false}")
    print(f"True: {count_true}")
    for nc in hosts_not_connected_list:
        print(nc)
    parse_exist_devices = parse_all_devices_for_map(hosts_list,devices)
    #count_devices = 0
    #print(f"\n\n\nHERE2\n\n\n")
    #for p in parse_exist_devices:
    #    count_devices = count_devices + 1
    #    print(p)
    #print(count_devices)
    #print(f"\n\n\nHERE3\n\n\n")
    count_devices = 0
    seen_names = set()
    unique_hosts = []
    for host in parse_exist_devices:
        if host['name'] not in seen_names:
            seen_names.add(host['name'])
            unique_hosts.append(host)
            count_devices = count_devices + 1
    #for u in unique_hosts:
    #    print(u)
    #print(count_devices)
    #"""
    creating_map = create_map(unique_hosts,map_name)
    #print(creating_map)
    #for d in devices:
        #my_count = my_count + 1
        #print(d)
#print(my_count)

