




from pyzabbix import ZabbixAPI, ZabbixAPIException

from zabbix_get import GetProxy,GetGroup,GetTemplate
from ..web_handler.my_pass import zbx_login,zbx_password,zbx_api_url



class CreateHost():

    """
    class for creating hosts in zabbix
    """

    def __init__(self, wh_dict):

        self.wh_dict = wh_dict
        self.zapi = ZabbixAPI(zbx_api_url)
        self.login = zbx_login
        self.password = zbx_password

    def creatorHost(self,*args):

        try:

            self.zapi.login(self.login, self.password)
            host_name = self.wh_dict['host_name']
            #template_id = zapi.template.get(filter={'name': template_name})[0]['templateid']
            #print(group_id,template_id)
            ip_address = self.wh_dict['host_ip_address'].split('/')[0]
            manufacturer = self.wh_dict['manufacturer']
            platform = self.wh_dict['platform']
            device_type = self.wh_dict['device_type']
            group = f"{manufacturer}/{platform}/{device_type}"
            group_name = GetGroup(group)
            group_id = group_name.get_group()
            if group_id[0] == True:
                group_id = group_id[1]
            elif group_id[0] == False:
                group_name = GetGroup(group)
                group_id = group_name.create_and_get_group()
                if group_id[0] == True:
                    group_id = group_id[1]
                elif group_id[0] == False:
                    return [False,group_id[1]]
            templating = GetTemplate(group)
            template_id = templating.classifier_template()
            if template_id[0] == True:
                template_id = template_id[1]
            elif template_id[0] == False:
                return [False, template_id[1]]
            proxy = GetProxy()
            proxy_id = proxy.get_proxy_next_choise()
            snmp_community = self.wh_dict['snmp_comm']
            print(proxy_id)
            self.zapi.host.create(
                host=str(host_name),
                interfaces=[{
                    #"hostid": "21",
                    'type': 2,
                    'main': 1,
                    'useip': 1,
                    'ip': str(ip_address),
                    'port' : "161",
                    'dns': "",
                    "details": {
                        "version": 2,
                        "community": str(snmp_community)
                    }
                }],
                proxy_hostid= str(proxy_id),
                groups=[{'groupid': int(group_id)}],
                templates=[{'templateid': int(template_id)}]
            )

            #proxys = self.zapi.proxy.get()
            created_host = self.zapi.host.get(filter={"name":host_name})
            #template = self.zapi.template.get(filter = {'name':"Huawei VRP by SNMP"})
            #for c in created_host:
                #my = c['templated_hosts']
                #print(my)
            return [True,created_host]

        except Exception as e:
            print(f'Error: {e}')
            return [False, e]




result = {'host_id': 1197, 'host_ip_address': '10.100.138.3/24', 'host_name': 'voskresensk-ar01',
          'host_status': 'active', 'tenant': 'ЕИМТС', 'device_role': 'border', 'platform': 'Huawei.VRP',
          'manufacturer': 'Huawei Technologies Co.', 'device_type': 'NE20E-S2F', 'snmp_comm': 'nocpr0ject',
          'conn_scheme': 'ssh', 'site': 222, 'snapshot_prechange':
              {'created': '2023-08-30T05:59:36.090Z', 'last_updated': '2024-02-01T06:46:53.172Z',
               'description': '', 'comments': '', 'local_context_data': None, 'device_type': 55, 'device_role': 41,
               'tenant': 19, 'platform': 3, 'name': 'voskresensk-ar01', 'serial': '', 'asset_tag': None, 'site': 222,
               'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '',
               'primary_ip4': 698, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None,
               'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields':
                   {'Connection_Scheme': 'ssh'}, 'tags': []}, 'event': 'updated', 'target': 'device',
          'snapshot_postchange': {'created': '2023-08-30T05:59:36.090Z', 'last_updated': '2024-02-01T06:47:06.763Z',
                                  'description': '', 'comments': '', 'local_context_data': None, 'device_type': 55,
                                  'device_role': 25, 'tenant': 19, 'platform': 3, 'name': 'voskresensk-ar01',
                                  'serial': '', 'asset_tag': None, 'site': 222, 'location': None, 'rack': None,
                                  'position': None, 'face': '', 'status': 'active', 'airflow': '', 'primary_ip4': 698,
                                  'primary_ip6': None, 'cluster': None, 'virtual_chassis': None, 'vc_position': None,
                                  'vc_priority': None, 'config_template': None, 'custom_fields': {'Connection_Scheme': 'ssh'},
                                  'tags': []}, 'datetime_created': '2023-08-30T05:59:36.090Z',
          'datetime_updated': '2024-02-01T06:47:06.763Z'}

if __name__ == "main":
    creating = CreateHost(result)
    result = creating.creatorHost()
    print(result)


