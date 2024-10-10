



from external_jober.externaljober.zabbix.keep_api_connect import zabbix_api_instance




class GetZBX():
    """
    class for getting different information about hosts from zabbix api
    """

    def __init__(self):
            self.zapi = zabbix_api_instance.get_instance()

    def get_template_id(self, template_name):
        try:
            template_id = self.zapi.template.get(filter={'name': template_name})[0]['templateid']
            return template_id
        except Exception as e:
            print(f'Error: {e}')
            return None
    def get_hosts_by_template(self,template_id):
        filtred_hosts = []
        hosts = self.zapi.host.get(
            #filter={"ParentTemplates": [["templateid"][0]:template_id]},
            output=["hostid", "name"],
            selectGroups=["groupid", "name"],
            selectParentTemplates=["templateid", "name"],
            selectInterfaces=["details","ip"],
            #selectTags="extend"
        )
        for host in hosts:
            template_host_id = None
            try:
                template_host_id = host.get("parentTemplates", [])[0]['templateid']
            except Exception as err:
                print(err)
                #print(host)
            if template_host_id:
                if template_host_id == template_id:
                    filtred_hosts.append(host)


           # print(template_id)


        #print(hosts)
        return filtred_hosts