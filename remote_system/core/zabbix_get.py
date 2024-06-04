




from remote_system.core.keep_api_connect import zabbix_api_instance
from remote_system.core.mappings import GetMappings


class GetHost():
    """
    class for getting different information about hosts from zabbix1 api
    """

    def __init__(self):
            self.zapi = zabbix_api_instance.get_instance()


    def get_host(self):
       try:
            hosts = self.zapi.host.get()

            #for host in hosts:
             #   print(host)
       except Exception as e:
           print(f'Error: {e}')
           return e



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

        def create_and_get_group(self,*args):
            try:
                self.zapi.hostgroup.create(name=self.group_name)
                group_id = self.zapi.hostgroup.get(filter={'name': self.group_name})[0]['groupid']
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





