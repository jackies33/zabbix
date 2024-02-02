


from pyzabbix import ZabbixAPI

from my_pass import zbx_login,zbx_password,zbx_api_url



class DeleteHost():

    """
    class for delete hosts in zabbix
    """

    def __init__(self, wh_dict):

        self.wh_dict = wh_dict
        self.zapi = ZabbixAPI(zbx_api_url)
        self.login = zbx_login
        self.password = zbx_password


    def removeHost(self,*args):

        try:
            self.zapi.login(self.login, self.password)
            host_name = self.wh_dict["host_name"]
            host_id = self.zapi.host.get(filter={"host": host_name})[0]["hostid"]
            result = self.zapi.host.delete(host_id)
            return [True,result]
        except Exception as e:
            print(f'Error: {e}')
            return [False, e]




if __name__ == '__main__':
    result = {'host_id': 1197, 'host_ip_address': '10.100.138.3/24', 'host_name': 'voskresensk-ar01',
              'host_status': 'active', 'tenant': 'ЕИМТС', 'device_role': 'border', 'platform': 'Huawei.VRP',
              'manufacturer': 'Huawei Technologies Co.', 'device_type': 'NE20E-S2F', 'snmp_comm': 'nocpr0ject',
              'conn_scheme': 'ssh', 'site': 222, 'snapshot_prechange':
                  {'created': '2023-08-30T05:59:36.090Z', 'last_updated': '2024-02-01T06:46:53.172Z',
                   'description': '', 'comments': '', 'local_context_data': None, 'device_type': 55, 'device_role': 41,
                   'tenant': 19, 'platform': 3, 'name': 'voskresensk-ar01', 'serial': '', 'asset_tag': None,
                   'site': 222,
                   'location': None, 'rack': None, 'position': None, 'face': '', 'status': 'active', 'airflow': '',
                   'primary_ip4': 698, 'primary_ip6': None, 'cluster': None, 'virtual_chassis': None,
                   'vc_position': None, 'vc_priority': None, 'config_template': None, 'custom_fields':
                       {'Connection_Scheme': 'ssh'}, 'tags': []}, 'event': 'updated', 'target': 'device',
              'snapshot_postchange': {'created': '2023-08-30T05:59:36.090Z', 'last_updated': '2024-02-01T06:47:06.763Z',
                                      'description': '', 'comments': '', 'local_context_data': None, 'device_type': 55,
                                      'device_role': 25, 'tenant': 19, 'platform': 3, 'name': 'voskresensk-ar01',
                                      'serial': '', 'asset_tag': None, 'site': 222, 'location': None, 'rack': None,
                                      'position': None, 'face': '', 'status': 'active', 'airflow': '',
                                      'primary_ip4': 698,
                                      'primary_ip6': None, 'cluster': None, 'virtual_chassis': None,
                                      'vc_position': None,
                                      'vc_priority': None, 'config_template': None,
                                      'custom_fields': {'Connection_Scheme': 'ssh'},
                                      'tags': []}, 'datetime_created': '2023-08-30T05:59:36.090Z',
              'datetime_updated': '2024-02-01T06:47:06.763Z'}
    deleting = DeleteHost(result)
    result = deleting.removeHost()
    print(result)