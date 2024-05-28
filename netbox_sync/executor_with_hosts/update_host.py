



from pyzabbix import ZabbixAPI

from ..web_handler.my_pass import zbx_login,zbx_password,zbx_api_url



class UpdateHost():

    """
    class for delete hosts in zabbix
    """

    def __init__(self, wh_dict,hostname,ip_address,group_id,template_id,proxy_id,snmp_community):

        self.wh_dict = wh_dict
        self.zapi = ZabbixAPI(zbx_api_url)
        self.login = zbx_login
        self.password = zbx_password
        self.hostname = hostname
        self.ip_address = ip_address
        self.group_id = group_id
        self.template_id = template_id
        self.proxy_id = proxy_id
        self.snmp_community = snmp_community

    def updateHost(self,*args):

        try:
            self.zapi.login(self.login, self.password)
            hostname = self.wh_dict['host_name']
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]