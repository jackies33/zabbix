
import re

def parameters_flowing(**kwargs):
    trgr_zbx = kwargs['trgr_zbx']
    target = kwargs['target']
    if target == 'linktrigger_high':
        result = {
            "triggerid": trgr_zbx,
            "color": "FF0000",  # Color of link in escalation case
            "drawtype": 2  # Type of link
        }
        return result
    elif target == 'linktrigger_averege':
        result = {
            "triggerid": trgr_zbx,
            "color": "FF8000",  # Color of link in escalation case
            "drawtype": 2  # Type of link
        }
        return result


def process_host_diff(host_new, hosts_db_from_map, links_db_from_map): # this method for processes of parsing link
    try:
        links_for_add = []
        host_name = host_new['local_hostname']
        for host_db in hosts_db_from_map:
            if host_name == host_db['label']:  # if the same name in map and LRND
                host_map_id = host_db['selementid']
                for link in links_db_from_map:
                    if link['selementid1'] == host_map_id or link[
                        'selementid2'] == host_map_id:  # if on link the same main host id as on the map
                        for trgr_map_db in link['linktriggers']:
                            for trgr_zbx in host_db['triggers_full']:
                                if trgr_map_db['triggerid'] == trgr_zbx[
                                    'triggerid']:  # if the same trigger id on map and in zabbix host
                                    for lldp_inst in host_new['lldp_list']:
                                        lldp_iface_name = list(lldp_inst.keys())[0]
                                        if lldp_iface_name in trgr_zbx['description'] and trgr_zbx['triggerid'] == \
                                                trgr_map_db['triggerid']:
                                            host_new['lldp_list'].remove(lldp_inst)

        if host_new['lldp_list'] != []:
            for lldp_inst_new in host_new['lldp_list']:
                host_map_id = None
                link_triggers = []
                lldp_iface_name = list(lldp_inst_new.keys())[0]
                lldp_remote_host_name = lldp_inst_new[lldp_iface_name]['remote_hostname']
                for host_db in hosts_db_from_map:
                    if host_name == host_db['label']:
                        host_map_id = host_db['selementid']
                        for trgr_zbx_new in host_db['triggers_full']:
                            description = trgr_zbx_new['description']
                            if re.search(rf'\b{lldp_iface_name}\b', description):
                                if not any(trigger['triggerid'] == trgr_zbx_new['triggerid'] for trigger in link_triggers):
                                    if 'Link down' in description:
                                        check = parameters_flowing(**{"trgr_zbx":trgr_zbx_new['triggerid'],"target":'linktrigger_high'})
                                        link_triggers.append(check)
                                    elif "High bandwidth usage" in description or "High error rate" in description:
                                        check = parameters_flowing(**{"trgr_zbx":trgr_zbx_new['triggerid'],"target":"linktrigger_averege"})
                                        link_triggers.append(check)

                if host_map_id is not None:
                    try:
                        for host_db_check_remote_id_only in hosts_db_from_map:
                            if host_db_check_remote_id_only['label'] == lldp_remote_host_name:
                                remote_map_id = host_db_check_remote_id_only['selementid']
                                if remote_map_id is not None:
                                    links_for_add.append({
                                        "selementid1": host_map_id,
                                        "selementid2": remote_map_id,
                                        "color": "00FF00",
                                        "linktriggers": link_triggers
                                    })
                    except Exception as err:
                        print(err)
                        return None
        return links_for_add
    except Exception as err:
        print(err)
        return None
