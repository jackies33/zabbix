


import time

from externaljober.keep_api_connect import zabbix_api_instance


class ZBX_PROC():
    """
    class for getting different information about hosts from zabbix api
    """

    def __init__(self):
        self.zapi = zabbix_api_instance.get_instance()
        self.down_status_macros = "{$DOWN_STATUS_WAP}"
        self.up_status_macros = "{$UP_STATUS_WAP}"

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


    def get_host_interface(self, host_id):
        """Get host's interface"""
        try:
            interfaces = self.zapi.hostinterface.get(filter={"hostid": host_id})
            if interfaces:
                return interfaces[0]['interfaceid']
        except Exception as err:
           #logging.error(f"Error getting host interface: {err}")
            return [False,err]
        return None

    def create_or_get_host(self, hostname):
        """Get host's id"""
        try:
            host = self.zapi.host.get(
            filter={"host": hostname},
            output=["hostid", "name"],
            selectInterfaces=["ip"],
            )
        except Exception as err:
            #logging.error(f"Error getting or creating host: {err}")
            return [False,err]
        return host[0]

    def create_trigger(self, **kwargs):
        try:
            time.sleep(1)
            triggers = self.zapi.trigger.get(filter={"event_name": f"{kwargs['wap_name']} is Down"})
            if triggers:
                return True
            else:
                kwargs["tags"].append({"tag": "alarm_name","value":"WAP DOWN"})
                self.zapi.trigger.create(
                    description=kwargs["item_name"],
                    expression=f"last(/{kwargs['host_name']}/{kwargs['item_key']})={self.down_status_macros}",
                    recovery_mode=1,
                    recovery_expression=f"last(/{kwargs['host_name']}/{kwargs['item_key']})={self.up_status_macros}",
                    priority=3,
                    comments=kwargs["item_name"],
                    event_name=f"{kwargs['wap_name']} is Down",
                    tags=kwargs["tags"]
                )
            # trigger_id = trigger_id.get('triggerids', [])[0]
        except Exception as err:
            print(err)
            #message_logger1.error(err)

    def exec_create_item(self, **kwargs):
        try:
            item_id = self.zapi.item.create(
                    hostid=kwargs["host_id"],
                    name=kwargs["item_name"],
                    key_=kwargs["item_key"],
                    type=kwargs["item_type"],
                    value_type=kwargs["value_type"],
                    interfaceid=0,
                    tags=kwargs["tags"],
                )['itemids'][0]
            return [True ,item_id]
        except Exception as err:
            print(err)
            return [False,err]

    def create_item(self, **kwargs):

        """Create item and get its id or just get id in zabbix"""
        try:
            item_id = None
            item = self.zapi.item.get(filter={"hostid": kwargs["host_id"], "key_": kwargs["item_key"]})
            if not item:
                create_item = self.exec_create_item(**kwargs)
                if create_item[0] == False:
                    return [False, create_item[1]]
                elif create_item[0] == True:
                    item_id = create_item[1]
                    item = self.zapi.item.get(filter={"hostid": kwargs["host_id"], "key_": kwargs["item_key"]},
                                              selectTags='extend')
                    if kwargs["create_trigger"] == True:
                        print('creating_trigger')
                        self.create_trigger(**kwargs)
            else:
                item_id = item[0]['itemid']
            if item_id and kwargs['check_sn'] == True:
                item_tags = item[0]['tags']
                for item in item_tags:
                    if item['tag'] == 'serial_number':
                        serial_number = item['value']
                        if serial_number != kwargs['host_sn_for_check']:
                            self.zapi.item.delete(item_id)
                            time.sleep(1)
                            self.exec_create_item(**kwargs)
                            time.sleep(1)
                            if kwargs["create_trigger"] == True:
                                self.create_trigger(**kwargs)
                            return [True, item_id]
                        elif serial_number == kwargs['host_sn_for_check']:
                            print("SN is ok")
                            return [True,item_id]
            elif kwargs["create_trigger"] == False and kwargs['check_sn'] == False:
                return [True, item_id]
            """
            if kwargs["create_trigger"] == True:
                try:
                    triggers = self.zapi.trigger.get(filter={"event_name": f"{kwargs['wap_name']} is Down"})
                except Exception as err:
                    #message_logger1.error(err)
                    return [True, item_id]
                # trigger_id = None
                if triggers:
                    # trigger_id = triggers[0]['triggerid']
                    return [True, item_id]
                elif not triggers:
                    self.create_trigger(**kwargs)
                    return [True,item_id]
            elif kwargs["create_trigger"] == False:
                return [True, item_id]
            """
        except Exception as err:
            #message_logger1.error(err)
            return [False,err]



