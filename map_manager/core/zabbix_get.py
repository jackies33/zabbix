

import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))


import concurrent.futures

from map_manager.core.keep_api_connect import zabbix_api_instance


class GetHost():
    """
    class for getting different information about hosts from zabbix api
    """

    def __init__(self):
            self.zapi = zabbix_api_instance.get_instance()

    def get_devices_by_device_role(self,device_role):
        try:

            hosts = self.zapi.host.get(
                output=["hostid", "name"],
                selectGroups=["groupid", "name"],
                selectParentTemplates=["templateid", "name"],
                selectInterfaces=["ip"],
                selectTags="extend"
            )
            filtered_hosts = []
            for host in hosts:
                tags = host.get('tags', [])
                for tag in tags:
                    if tag['tag'] == 'device_role' and tag['value'] == device_role:
                        filtered_hosts.append(host)


            return filtered_hosts
        except Exception as err:
            print(err)
            return False

    def get_devices_by_map_group(self,map_group):
        try:

            hosts = self.zapi.host.get(
                output=["hostid", "name"],
                selectGroups=["groupid", "name"],
                selectParentTemplates=["templateid", "name"],
                selectInterfaces=["ip"],
                selectTags="extend"
            )
            filtered_hosts = []
            for host in hosts:
                tags = host.get('tags', [])
                for tag in tags:
                    if tag['tag'] == 'MAP_Group' and tag['value'] == map_group:
                        filtered_hosts.append(host)


            return filtered_hosts
        except Exception as err:
            print(err)
            return False

    def get_devices_from_map(self,map_name):
        try:
            filtered_hosts = []
            maps = self.zapi.map.get(output=["mapid", "name"], filter={"name": map_name})
            if not maps:
                print(f"Map '{map_name}' not found.")
                #hosts = self.get_devices_by_map_group(map_name)
                #return hosts
                return [False, (f"Map '{map_name}' not found.")]
            map_id = maps[0]['sysmapid']
            elements = self.zapi.map.get(selectSelements="extend", selectLinks="extend")
            devices_name = []
            for elem in elements:
                if elem['sysmapid'] == map_id:
                    selements = elem['selements']
                    for sel in selements:
                        #print(sel['label'])
                        devices_name.append(sel['label'])

            # Функция для выполнения запроса к Zabbix API
            def get_host_info(device_name):
                try:
                    #print(device_name)
                    result = self.zapi.host.get(
                        filter={"name": device_name},
                        output=["hostid", "name"],
                        selectGroups=["groupid", "name"],
                        selectParentTemplates=["templateid", "name"],
                        selectInterfaces=["ip"],
                        selectTags="extend"
                    )
                    #print(result)
                    return result
                except Exception as err:
                    print(err)
                    return None

            filtered_hosts = []
            # Ограничиваем количество потоков до 30
            with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
                # Запускаем задачи в многопоточном режиме
                future_to_device = {executor.submit(get_host_info, device_name): device_name for device_name
                                    in devices_name}

                for future in concurrent.futures.as_completed(future_to_device):
                    device_name = future_to_device[future]
                    try:
                        host_info = future.result()
                        if host_info:
                            filtered_hosts.extend(host_info)
                    except Exception as exc:
                        print(f'{device_name} generated an exception: {exc}')
                #print(filtered_hosts)
            return filtered_hosts
        except Exception as err:
            print(err)
            return False

    def get_all_exist_maps(self):
        all_maps = self.zapi.map.get(output=["mapid", "name"])
        return all_maps

    def get_local_id(self, host_name):
        try:
            host_id = self.zapi.host.get(filter={'host': host_name})
            if host_id:
                host_id = host_id[0]['hostid']
                return [True,host_id]
            else:
                return [False,None]
        except Exception as e:
            print(f'Error: {e}')
            return [False,e]


    def get_all_exists_hosts_by_connection_from_devices(self,hosts_list_from_connection):
        try:
            hosts = self.zapi.host.get(
                output=["hostid", "name"],
                selectGroups=["groupid", "name"],
                selectParentTemplates=["templateid", "name"],
                selectInterfaces=["ip"],
                selectTags="extend"
            )
            filtered_hosts = []
            for host in hosts:
                looking_host = host['name']
                for host_cli in hosts_list_from_connection:
                    lldp_list = host_cli['lldp_list']
                    for lldp_l in lldp_list:
                        lldp_iface_name = list(lldp_l.keys())[0]
                        lldp_remote_host_name = lldp_l[lldp_iface_name]['remote_hostname']
                        if str(lldp_remote_host_name) == str(looking_host) and host not in filtered_hosts:
                                filtered_hosts.append(host)
            return filtered_hosts
        except Exception as err:
            print(err)
            return False





