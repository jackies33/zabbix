






import sys
import os

sys.stderr = open(os.devnull, 'w')

import sys
#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.core.get_data import GetData
from map_manager.core.mappings import MAPPINGS
from map_manager.core.parsing_data_maps import get_map_parse_data
from map_manager.core.parsing_data_links import LINK_PARSING
from map_manager.core.update_links import update_links
from map_manager.core.connect_devices_runner import run_in_threads




class START_DISCOVERY():

    def __init__(self,**kwargs):
        self.get_data = GetData()
        self.mappings = MAPPINGS()
        self.essence = kwargs['essence']
        self.essence_value = kwargs['essence_value']


    def start_proccess_discovery_main(self):
        count_false = 0
        count_true = 0
        # essence = "device_role"
        # essence_value = "p-pe"
        count_devices = 0
        devices = self.get_data.get_hosts_info_zbx(**{"essence": self.essence, "essence_value": self.essence_value})
        #for dev in devices:
            #count_devices = count_devices + 1
            #print(dev['name'])
        #print(count_devices)
        #"""
        hosts_list = []
        host_not_connected_list = []
        #for d in devices:
        #    print(d)
        elem_parts = get_map_parse_data(self.essence_value)
        results = run_in_threads(devices, max_threads=30)
        for res in results:
            if res[0] == False:
                count_false = count_false + 1
                #print(res)
                host_not_connected_list.append(res)
            elif res[0] == True:
                count_true = count_true + 1
                print(res[1])
                hosts_list.append(res[1])
        print(f"False: {count_false}")
        print(f"True: {count_true}")
        #for host in hosts_list:
        #    print(host)

        #"""
        if elem_parts[0] == True:
            # transform_elem = elem_parts[1]['transform_elem']
            elem = elem_parts[1]['elem']
            prep_kwargs = {
                # 'transform_elem': transform_elem,
                'elem': elem,
                'map_name': self.essence_value,
                'hosts_list': hosts_list,
                'host_not_connected_list': host_not_connected_list
            }
            links_for_update = None
            if elem_parts[1]['new_map'] == False:
                # parsing = PARSE_DATA_FOR_LINKS(**prep_kwargs)
                PARSE = LINK_PARSING(**prep_kwargs)
                links_for_update = PARSE.diff_links()
            elif elem_parts[1]['new_map'] == True:
                PARSE = LINK_PARSING(**prep_kwargs)
                links_for_update = PARSE.first_links()
            if links_for_update or links_for_update != []:
                #print(links_for_update)
                UPDATE_LINKS = update_links(**{"links_for_update": links_for_update, "map_name": self.essence_value})
                return [UPDATE_LINKS,host_not_connected_list]
            else:
                return [f"\n\nnot found links between devices on the map {self.essence_value}!!!\n\n", host_not_connected_list]
            #"""



sys.stderr = sys.__stderr__


