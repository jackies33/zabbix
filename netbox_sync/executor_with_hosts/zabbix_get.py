






from pyzabbix import ZabbixAPI, ZabbixAPIException


from my_pass import zbx_login,zbx_password,zbx_api_url


class GetHost():
    """
    class for getting different information about hosts from zabbix api
    """

    def __init__(self):
        self.zapi = ZabbixAPI(zbx_api_url)
        self.login = zbx_login
        self.password = zbx_password


    def get_host(self):
       try:
            self.zapi.login(self.login, self.password)
            hosts = self.zapi.host.get()
            for host in hosts:
                print(host)

       except Exception as e:
           print(f'Error: {e}')
           return [False, e]



class GetProxy():
        """
        class for getting different information about proxy server from zabbix api
        """

        def __init__(self):
            self.zapi = ZabbixAPI(zbx_api_url)
            self.login = zbx_login
            self.password = zbx_password

        def get_proxy_next_choise(self):

           #function return the proxy_id which has a smallest count of discovery hosts

           try:
                self.zapi.login(self.login, self.password)
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
               return [False, e]


class GetGroup():
        """
        class for getting different information about groups from zabbix api
        """

        def __init__(self,group_name):
            self.zapi = ZabbixAPI(zbx_api_url)
            self.login = zbx_login
            self.password = zbx_password
            self.group_name = group_name

        def get_group(self,*args):
            try:
                self.zapi.login(self.login, self.password)
                group_id = self.zapi.hostgroup.get(filter={'name': self.group_name})[0]['groupid']
                return [True, group_id]
            except Exception as e:
                print(f'Error: {e}')
                return [False, e]

        def create_and_get_group(self,*args):
            try:

                self.zapi.login(self.login, self.password)
                self.zapi.hostgroup.create(name=self.group_name)
                group_id = self.zapi.hostgroup.get(filter={'name': self.group_name})[0]['groupid']
                return [True, group_id]
            except Exception as e:
                print(f'Error: {e}')
                return [False, e]


class GetTemplate():
    """
    class for getting different information about templates server from zabbix api
    """

    def __init__(self, group_name):
        self.zapi = ZabbixAPI(zbx_api_url)
        self.login = zbx_login
        self.password = zbx_password
        self.group_name = group_name
        self.template_name = ''

    def classifier_template(self,*args):
        print(self.group_name)
        if self.group_name == 'Huawei Technologies Co./Huawei.VRP/NE20E-S2F':
            self.template_name = 'Huawei VRP by SNMP'
            template_id = self.get_template(self.template_name)
            return template_id


    def get_template(self, *args):
        try:
                self.zapi.login(self.login, self.password)
                template = self.zapi.template.get(filter = {'name':self.template_name})[0]['templateid']
                return [True, template]
        except Exception as e:
                print(f'Error: {e}')
                return [False, e]

#grouping = GetGroup("Huawei Technologies Co./Huawei.VRP/NE20E-S2F")
#result = grouping.get_group()
#print(result)

#classifier = GetTemplate('Huawei Technologies Co./Huawei.VRP/NE20E-S2F')
#result = classifier.classifier_template()
#print(result[1])