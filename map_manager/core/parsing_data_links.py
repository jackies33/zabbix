




import re
import concurrent.futures
import copy

import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.core.keep_api_connect import zabbix_api_instance
from map_manager.core.get_data import GetData
from map_manager.core.micro_proc import process_host_diff



class LINK_PARSING(): # class for parse data and prepare it for update or create links in MAP in Zabbix

    def __init__(self, **kwargs):
        self.zapi = zabbix_api_instance.get_instance()
        self.hosts_list = kwargs.get('hosts_list', None)
        self.hosts_not_connected_list = kwargs.get('host_not_connected_list', None)
        self.get_data = GetData()
        self.map_name = kwargs.get('map_name', None)
        self.elements = self.zapi.map.get(filter={"name": self.map_name}, selectSelements="extend", selectLinks="extend")
        self.maps = self.zapi.map.get(output=["mapid", "name"], filter={"name": self.map_name})

    def parameters_flow(self ,**kwargs):
        trgr_zbx = kwargs['trgr_zbx']
        target = kwargs['target']
        if target == 'linktrigger_high':
            result = {
                "triggerid": trgr_zbx,
                "color": "FF0000",  # Цвет для типа High
                "drawtype": 2  # Тип линии
            }
            return result
        elif target == 'linktrigger_averege':
            result = {
                "triggerid": trgr_zbx,
                "color": "FF8000",  # Цвет для типа High
                "drawtype": 2  # Тип линии
            }
            return result

    def diff_links(self):  # method for parse and find out new links if they exist
        try:
            if not self.maps:
                print(f"Map '{self.map_name}' not found.")
                return [False, (f"Map '{self.map_name}' not found.")]
            links_db_from_map = []
            hosts_db_from_map = []
            hosts_label_db = []
            links_for_add = []
            if self.elements:
                selements = self.elements[0]['selements']
                for sel in selements:
                    hosts_db_from_map.append(sel)
                try:
                    elem_links = self.elements[0]['links']
                    for link in elem_links:
                        links_db_from_map.append(link)
                        link.pop('linkid')
                        link.pop('sysmapid')
                        link.pop('label')
                        link.pop('permission')
                        link.pop('drawtype')
                        for tr in link['linktriggers']:
                            tr.pop('linktriggerid')
                            tr.pop('linkid')
                        links_for_add.append((link))
                except Exception as err:
                    print(f"HERE!!!{err}HERE")

            for host_db in hosts_db_from_map:
                host_zbx_id = host_db['elements'][0]['hostid']
                triggers_zbx = self.zapi.trigger.get(hostids=host_zbx_id, output='extend')
                host_db.update({'triggers_full': triggers_zbx})
                hosts_label_db.append(host_db['label'])
            temp_hosts_list = self.hosts_list
            for t in temp_hosts_list:
                t['lldp_list'] = [lldp_inst for lldp_inst in t['lldp_list']
                                  if list(lldp_inst.values())[0]['remote_hostname'] in hosts_label_db]
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for host_new in temp_hosts_list:  # list of request from network devices (!next LRND!)
                    futures.append(
                        executor.submit(process_host_diff, host_new, hosts_db_from_map, links_db_from_map))
                # Waiting finishes all tasks
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    for l in result:
                        if result != [] and l['linktriggers'] != [] and result != None:
                            links_for_add.append(l)
            return links_for_add

        except Exception as err:
            print(err)
            return None



    def first_links(self):
        try:
            if not self.maps:
                print(f"Map '{self.map_name}' not found.")
                return [False, (f"Map '{self.map_name}' not found.")]
            hosts_db_from_map = []
            hosts_label_db = []
            links_for_add = []
            if self.elements:
                selements = self.elements[0]['selements']
                for sel in selements:
                    hosts_db_from_map.append(sel)
            for host_db in hosts_db_from_map:
                host_zbx_id = host_db['elements'][0]['hostid']
                triggers_zbx = self.zapi.trigger.get(hostids=host_zbx_id, output='extend')
                full_triggers = []
                for trgr in triggers_zbx:
                    if "Link down" in trgr['description'] or "High bandwidth usage" in trgr\
                        ['description'] or "High error rate" in trgr['description']:
                        full_triggers.append(trgr)
                host_db.update({'triggers_full': full_triggers})
                hosts_label_db.append(host_db['label'])
            temp_hosts_list1 = copy.deepcopy(self.hosts_list)
            links_for_delete_in_proccess = copy.deepcopy(self.hosts_list)
            for t in temp_hosts_list1:  # delete all lldp neighbours which doesn't exists on map in zabbix
                t['lldp_list'] = [lldp_inst for lldp_inst in t['lldp_list']
                                  if list(lldp_inst.values())[0]['remote_hostname'] in hosts_label_db]
            for t in links_for_delete_in_proccess:  # delete all lldp neighbours which doesn't exists on map in zabbix
                t['lldp_list'] = [lldp_inst for lldp_inst in t['lldp_list']
                                  if list(lldp_inst.values())[0]['remote_hostname'] in hosts_label_db]
            for host_new in temp_hosts_list1:  # list of request from network devices (!next LRND!)
                host_name = host_new['local_hostname']
                for host_db in hosts_db_from_map:  # list from map db in zabbix
                    if host_name == host_db['label']:  # if the same name in map and LRND
                        host_map_id = host_db['selementid']
                        for lldp_inst in host_new['lldp_list']:
                            remote_map_id = None
                            link_triggers = []
                            permit_to_proccess = False
                            for temp_device_2 in links_for_delete_in_proccess:
                                if temp_device_2['local_hostname'] == host_name:
                                    for lldp_inst2 in temp_device_2['lldp_list']:
                                        if lldp_inst2 == lldp_inst:
                                            permit_to_proccess = True
                                            break
                            if permit_to_proccess == True:
                                lldp_iface_name = list(lldp_inst.keys())[0]
                                lldp_remote_host_name = lldp_inst[lldp_iface_name]['remote_hostname']
                                for host_db_check_remote_id_only in hosts_db_from_map:
                                    if host_db_check_remote_id_only['label'] == lldp_remote_host_name:
                                        remote_map_id = host_db_check_remote_id_only['selementid']
                                for trgr_zbx in host_db['triggers_full']:
                                    description = trgr_zbx['description']
                                    if re.search(rf'\b{lldp_iface_name}\b', description):
                                        if 'Link down' in description:
                                            link_triggers.append(self.parameters_flow
                                                (**{"trgr_zbx": trgr_zbx['triggerid'], "target": 'linktrigger_high'}))
                                        elif "High bandwidth usage" in description or "High error rate" in description:
                                            link_triggers.append(self.parameters_flow
                                                (**{"trgr_zbx": trgr_zbx['triggerid'], "target": 'linktrigger_averege'}))
                                for temp_device in links_for_delete_in_proccess:
                                    if temp_device['local_hostname'] == host_name:
                                        for entry in temp_device['lldp_list']: # deleting device from special list
                                            if lldp_iface_name in entry:
                                                #print(f"HERE1 {temp_device['lldp_list']} HERE1 {entry} HERE1")
                                                temp_device['lldp_list'].remove(entry)
                                        for entry2 in temp_device['lldp_list']:
                                                lldp_iface_name_addition_LACP = list(entry2.keys())[0] # check if in lldp list have links to the same remote_device for add it in one link
                                                lldp_remote_host_name_addition_LACP = entry2[lldp_iface_name_addition_LACP]['remote_hostname']
                                                if lldp_remote_host_name_addition_LACP == lldp_remote_host_name:
                                                    for trgr_zbx in host_db['triggers_full']:
                                                        description = trgr_zbx['description']
                                                        if re.search(rf'\b{lldp_iface_name_addition_LACP}\b', description):
                                                            if 'Link down' in description:
                                                                link_triggers.append(self.parameters_flow
                                                                                     (**{"trgr_zbx": trgr_zbx['triggerid']
                                                                                         , "target": 'linktrigger_high'}))
                                                            elif "High bandwidth usage" in description or "High error rate" in description:
                                                                link_triggers.append(self.parameters_flow
                                                                                     (**{"trgr_zbx": trgr_zbx['triggerid']
                                                                                         , "target": 'linktrigger_averege'}))
                                                    if lldp_iface_name_addition_LACP in entry2:
                                                        temp_device['lldp_list'].remove(entry2)
                            if remote_map_id != None and link_triggers != [] and host_new['lldp_list'] != []: # add all trigger in link
                                links_for_add.append({
                                    "selementid1": host_map_id,
                                    "selementid2": remote_map_id,
                                    "color": "00FF00",  # Задаем цвет для связи
                                    "linktriggers": link_triggers
                                })


            return links_for_add
        except Exception as err:
            print(err)
            return None


