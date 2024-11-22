



from externaljober.zabbix.zabbix import ZBX_PROC
from externaljober.worker_aruba.mobility_master import MOB_MASTER
from externaljober.reddis.reddis_get import REDDIS


class PROCEDURE_SSID():

    def __init__(self,host_name):
        self.host_name = host_name
        self.value_type = 3
        self.item_type = 2



    def get_ssid_user_count_full(self):
        try:
            data_list_for_sender_1 = []
            data_list_for_redis_1 = []
            mob_master = MOB_MASTER()
            result = mob_master.get_ssid_count_users()
            if result[0] == True and result[1] != {} and result[1] != None:
                zbx = ZBX_PROC()
                host = zbx.create_or_get_host(self.host_name)
                host_id = host['hostid']
                host_name = host['name']
                for key,value in result[1].items():
                    ssid_name = key.lower()
                    item_key = f"ssid_count_user_{ssid_name}"
                    tags = [{"tag":"ssid_name","value":key}]
                    zbx_item = zbx.create_item(**{"host_id": host_id,
                         "item_name": f"User Counter of SSID {key}",
                         "item_key": item_key,
                         "tags": tags,
                         "value_type": self.value_type,
                         "item_type": self.item_type,
                         "wap_name": None,
                         "create_trigger": False,
                         "check_sn": False,
                         "host_sn_for_check": None
                     })
                    data_list_for_sender_1.append(f"{host_name} {item_key} {value}")
                    data_list_for_redis_1.append({"item_id": zbx_item[1], "item_key": item_key})
                for controller_inst in result[2]:
                    controller_host_name = controller_inst['host_name']
                    ssid_count_of_controller = controller_inst['ssid_users_count']
                    for key,value in ssid_count_of_controller.items():
                        ssid_name = key.lower()
                        item_key = f"{controller_host_name}_ssid_count_user_{ssid_name}"
                        tags = [{"tag":"ssid_name","value":key},{"tag":"controller_host","value":controller_host_name}]
                        zbx_item = zbx.create_item(**{"host_id": host_id,
                             "item_name": f"User Counter by {controller_host_name} of SSID {key}",
                             "item_key": item_key,
                             "tags": tags,
                             "value_type": self.value_type,
                             "item_type": self.item_type,
                             "wap_name": None,
                             "create_trigger": False,
                             "check_sn": False,
                             "host_sn_for_check": None
                         })
                        data_list_for_sender_1.append(f"{host_name} {item_key} {value}")
                        data_list_for_redis_1.append({"item_id": zbx_item[1], "item_key": item_key})
                return [True,{"sender_data_1":data_list_for_sender_1,"zbx_items_ids_":data_list_for_redis_1}]
            else:
                return [False,"Doesn't have enough data"]
        except Exception as err:
            return [False,err]

    def get_ssid_user_count_update(self):
        try:
            data_list_for_sender = []
            mob_master = MOB_MASTER()
            result = mob_master.get_ssid_count_users()
            if result[0] == True and result[1] != {} and result[1] != None:
                zbx = ZBX_PROC()
                host = zbx.create_or_get_host(self.host_name)
                host_id = host['hostid']
                host_name = host['name']
                #rediss = REDDIS()
                #key_for_redis = f"externaljober:jober:scheduler:data:airwave:zbx:items:{self.host_name}"
                #redis_data = rediss.get_json(key_for_redis)
                for key,value in result[1].items():
                    ssid_name = key.lower()
                    item_key = f"ssid_count_user_{ssid_name}"
                    data_list_for_sender.append(f"{host_name} {item_key} {value}")
                for controller_inst in result[2]:
                    controller_host_name = controller_inst['host_name']
                    ssid_count_of_controller = controller_inst['ssid_users_count']
                    for key,value in ssid_count_of_controller.items():
                        ssid_name = key.lower()
                        item_key = f"{controller_host_name}_ssid_count_user_{ssid_name}"
                        data_list_for_sender.append(f"{host_name} {item_key} {value}")
                return [True,{"sender_data_1":data_list_for_sender}]
            else:
                return [False,"Doesn't have enough data"]
        except Exception as err:
            return [False,err]
