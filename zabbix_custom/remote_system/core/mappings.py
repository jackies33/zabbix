


class GetMappings():

    group_template_mapping = {
            'Huawei Technologies Co./Huawei.VRP/': 'Huawei VRP by SNMP',

        }

    wh_update_mapping_essence = {

        'primary_ip4': [
                        "host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']",
                        "interfaces = self.zapi.hostinterface.get(filter={'hostids':host_id})",
                        "if not interfaces: raise ZabbixAPIException('No interfaces found for host')",
                        "interface_id = interfaces[0]['interfaceid']",
                        "self.result = self.zapi.hostinterface.update(interfaceid=interface_id,ip=data['ip_address'])",
                        ],

        'serial':      [
                        "host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']",
                        "self.zapi.host.update({'hostid': host_id,'inventory_mode': 0})",
                        "serials = self.zapi.host.update({'hostid': host_id,'inventory': {'serialno_a': data['serial']}})",
                        "host_info = self.zapi.host.get(filter={'host': data['name']},selectInventory=True)",
                        "self.result = host_info[0].get('inventory', {}).get('serialno_a')",
                        ],

        'custom_fields': [
                   "custom_dict = data['custom_fields']",
                   "host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']",
                   "tags = [{'tag': key, 'value': value['name']} if isinstance(value, dict) and 'name' in value else {'tag': key, 'value': str(value)} for key, value in custom_dict.items()]",
                   "self.zapi.host.update(hostid=host_id,tags=tags)",
                   "host_info = self.zapi.host.get(filter={'host': data['name']},selectTags='extend')",
                   "self.result = host_info[0].get('tags', [])",
                   ],

        'site' : [
                        "host_id = self.zapi.host.get(filter={'host': data['name']})[0]['hostid']",
                        "serials = self.zapi.host.update({'hostid': host_id,'inventory': {'location': data['phys_address']}})",
                        "host_info = self.zapi.host.get(filter={'host': data['name']},selectInventory=True)",
                        "self.result = host_info[0].get('inventory', {}).get('location')",
                ],
    }

