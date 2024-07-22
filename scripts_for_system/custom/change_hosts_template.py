
from pyzabbix import ZabbixAPI

from my_env import zbx_api_url,zbx_api_token

old_template_name = 'Juniper by SNMP'
new_template_name = 'Juniper Main'






def zbx_get_templates():
    zapi = ZabbixAPI(zbx_api_url)
    zapi.session.verify = False
    zapi.login(api_token=zbx_api_token)
    template_old = zapi.template.get(filter={"host": old_template_name}, output=['templateid', 'name'])
    old_template_id = template_old[0]['templateid']
    template_new = zapi.template.get(filter={"host": new_template_name}, output=['templateid', 'name'])
    new_template_id = template_new[0]['templateid']
    hosts = zapi.host.get(templateids=old_template_id, output=['hostid', 'host'], selectParentTemplates=['templateid'])

    for host in hosts:
        #print(host)
        #print(new_template_id)
        #host['parentTemplates'][0]['templateid'])
        zapi.host.update(
            hostid=host['hostid'],
            templates=[{'templateid': new_template_id}]
        )

    return None


zbx_get_templates()