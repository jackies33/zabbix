


from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.mappings import GetMappings


class GetHost():
    """
    class for getting different information about hosts from zabbix1 api
    """

    def __init__(self):
            self.zapi = zabbix_api_instance.get_instance()

    def get_vc_hosts(self,**kwargs):
        try:
            hosts = self.zapi.host.get(search={'name': kwargs["name"]}, output=['hostid', 'name'])
            if hosts:
                host_ids = [host['hostid'] for host in hosts]
                result = self.zapi.host.delete(*host_ids)
                return result
        except Exception as e:
            print(f'Error: {e}')
            return e

    def get_local_id(self,**kwargs):
        host_name = kwargs['host_name']
        remote_id = kwargs['host_id_remote']
        try:
            host_id = self.zapi.host.get(filter={'host': host_name})
            if host_id:
                host_id = host_id[0]['hostid']
            elif not host_id:
                hosts = self.zapi.host.get(output=['hostid'], selectTags='extend')
                for host in hosts:
                    for host_tag in host.get('tags', []):
                        if host_tag['tag'] == 'remote_id' and host_tag['value'] == remote_id:
                            host_id = host['hostid']
            return host_id
        except Exception as e:
            print(f'Error: {e}')
            return e

    def get_host(self):
       try:
            hosts = self.zapi.host.get()

            #for host in hosts:
             #   print(host)
       except Exception as e:
           print(f'Error: {e}')
           return e


    def get_all_hosts(self):

        hosts = self.zapi.host.get(output='extend', selectTags='extend')
        list_hosts = []
        def process_device(host):
            try:
                # print(host)
                host_id = host['hostid']
                tags = {tag['tag']: tag['value'] for tag in host['tags']}
                device_role = None
                conn_scheme = None
                map_group = None
                name_of_est = None
                tg_group = None
                host_id_remote = None
                if 'device_role' in tags:
                    device_role = tags['device_role']
                if 'Connection_Scheme' in tags:
                    conn_scheme = tags['Connection_Scheme']
                if 'MAP_Group' in tags:
                    map_group = tags['MAP_Group']
                if 'Name_of_Establishment' in tags:
                    name_of_est = tags['Name_of_Establishment']
                if 'TG_Group' in tags:
                    tg_group = tags['TG_Group']
                if 'remote_id' in tags:
                    host_id_remote = tags['remote_id']
                # print(tg_group)
                groups = self.zapi.host.get(
                    selectGroups=['groupid', 'name'],
                    hostids=host_id)[0]
                group = None
                try:
                    group = groups['groups'][0]['name']
                    # print(group)
                except Exception as err:
                    return None
                try:
                    parts = group.split('/')
                    part1, part2, part3 = parts
                    platform = part2
                    device_type = part3
                except Exception as err:
                    return None
                sn = None
                location = None
                host_info = self.zapi.host.get(filter={'host': host['host']}, selectInventory=True)
                try:
                    sn = host_info[0].get('inventory', {}).get('serialno_a')
                    location = host_info[0].get('inventory', {}).get('location')
                except Exception as err:
                    pass
                interface = self.zapi.hostinterface.get(filter={'hostid': host['hostid']})[0]
                try:
                    ip_address = interface['ip']
                    # print(ip_address)
                except Exception as err:
                    return None
                host_status = host['status']
                if host_status == "0":
                    host_status = "Active"
                elif host_status == "1":
                    host_status = "Offline"
                else:
                    host_status = "Active"
                return {'host_name': host['host'], 'host_status': host_status, 'site': None,
                                   'host_id_zbx': host_id, 'tenant': None, 'device_role': device_role,
                                   'tg_resource_group': tg_group, 'platform': platform,
                                   'map_resource_group': map_group, 'device_type': device_type,
                                   'my_address': location, 'sn': sn, 'host_id_remote': host_id_remote,
                                   'ip_address': ip_address}

            except Exception as e:
                print(f'Error: {e}')
                return None

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(process_device, host) for host in hosts]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    list_hosts.append(result)
        return list_hosts
                # print(list_hosts)
                # print("Host ID:", host['hostid'])
                # print("Host Name:", host['host'])
                # print("Status:", host['status'])
                # print("Interfaces:", host['interfaces'])
                # print("Groups:", host['groups'])
                # print("Templates:", host['parentTemplates'])
                # print()

            # for host in hosts:
            #   print(host)





"""
    def get_all_hosts(self):
       try:
            hosts = self.zapi.host.get(output='extend', selectTags='extend')
            list_hosts = []
            for host in hosts:
                #print(host)
                host_id = host['hostid']
                tags = {tag['tag']: tag['value'] for tag in host['tags']}
                device_role = None
                conn_scheme = None
                map_group = None
                name_of_est = None
                tg_group = None
                host_id_remote = None
                if 'device_role' in tags:
                    device_role = tags['device_role']
                if 'Connection_Scheme' in tags:
                    conn_scheme = tags['Connection_Scheme']
                if 'MAP_Group' in tags:
                    map_group = tags['MAP_Group']
                if 'Name_of_Establishment' in tags:
                    name_of_est = tags['Name_of_Establishment']
                if 'TG_Group' in tags:
                    tg_group = tags['TG_Group']
                if 'remote_id' in tags:
                    host_id_remote = tags['remote_id']
                #print(tg_group)
                groups = self.zapi.host.get(
                    selectGroups=['groupid', 'name'],
                    hostids=host_id)[0]
                group = None
                try:
                    group = groups['groups'][0]['name']
                    #print(group)
                except Exception as err:
                    continue
                try:
                    parts = group.split('/')
                    part1, part2, part3 = parts
                    platform = part2
                    device_type = part3
                except Exception as err:
                    continue
                sn = None
                location = None
                host_info = self.zapi.host.get(filter={'host': host['host']}, selectInventory=True)
                try:
                    sn = host_info[0].get('inventory', {}).get('serialno_a')
                    location = host_info[0].get('inventory', {}).get('location')
                except Exception as err:
                    pass
                interface = self.zapi.hostinterface.get(filter={'hostid': host['hostid']})[0]
                try:
                    ip_address = interface['ip']
                   # print(ip_address)
                except Exception as err:
                    continue
                host_status = host['status']
                if host_status == "0":
                    host_status = "Active"
                elif host_status == "1":
                    host_status = "Offline"
                else:
                    host_status = "Active"
                list_hosts.append({'host_name': host['host'], 'host_status': host_status, 'site': None,
                                   'host_id_zbx': host_id, 'tenant': None, 'device_role': device_role,
                                   'tg_resource_group': tg_group, 'platform': platform,
                                   'map_resource_group': map_group, 'device_type': device_type,
                                   'my_address': location,'sn':sn,'host_id_remote':host_id_remote,
                                   'ip_address': ip_address})
                #print(list_hosts)
                #print("Host ID:", host['hostid'])
                #print("Host Name:", host['host'])
                #print("Status:", host['status'])
                #print("Interfaces:", host['interfaces'])
                #print("Groups:", host['groups'])
                #print("Templates:", host['parentTemplates'])
                #print()

            #for host in hosts:
             #   print(host)
            return list_hosts
       except Exception as e:
           print(f'Error: {e}')
           return e
"""

class GetProxy():
        """
        class for getting different information about proxy server from zabbix1 api
        """

        def __init__(self):
            self.zapi = zabbix_api_instance.get_instance()

        def get_proxy_next_choise(self):

           #function return the proxy_id which has a smallest count of discovery hosts

           try:
                proxies = self.zapi.proxy.get(output=["proxyid", "host"])
                list_proxys = []
                for proxy in proxies:
                    proxy_id = proxy["proxyid"]
                    #proxy_name = proxy["host"]
                    hosts_in_proxy = self.zapi.host.get(proxyids=proxy_id, output=["host"])
                    hosts_count = len(hosts_in_proxy)
                    list_proxys.append({'proxy_id' : proxy_id,'hosts_count' : hosts_count})
                selected_proxy = min(list_proxys, key=lambda x: x['hosts_count'])['proxy_id']
                return selected_proxy
           except Exception as e:
               print(f'Error: {e}')
               return e


class GetGroup():
        """
        class for getting different information about groups from zabbix1 api
        """

        def __init__(self,group_name):
            self.zapi = zabbix_api_instance.get_instance()
            self.group_name = group_name

        def get_group(self,*args):
            try:
                group_id = self.zapi.hostgroup.get(filter={'name': self.group_name})[0]['groupid']
                return group_id
            except IndexError as err:
                    group_id = self.create_and_get_group(self.group_name)
                    return group_id
            except Exception as e:
                print(f'Error: {e}')
                return e

        def create_and_get_group(self,group_name):
            try:
                self.zapi.hostgroup.create(name=group_name)
                time.sleep(3)
                group_id = self.zapi.hostgroup.get(filter={'name': group_name})[0]['groupid']
                return group_id
            except Exception as e:
                print(f'Error: {e}')
                return e


class GetTemplate():
    """
    class for getting different information about templates server from zabbix1 api
    """

    def __init__(self, group_name):
        self.zapi = zabbix_api_instance.get_instance()
        self.group_name = group_name

    def classifier_template(self, *args):
        Mapp = GetMappings()
        for group, template_name in Mapp.group_template_mapping.items():
            if group in self.group_name:
                template_id = self.get_template(**{"template_name": template_name})
                return template_id


    def get_template(self, **kwargs):
        try:
                template_id = self.zapi.template.get(filter = {'name':kwargs["template_name"]})[0]['templateid']
                return template_id
        except Exception as e:
                print(f'Error: {e}')
                return e




