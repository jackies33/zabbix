
import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from map_manager.core.keep_api_connect import zabbix_api_instance





def update_links(**kwargs):
    zapi = zabbix_api_instance.get_instance()
    links_update = kwargs['links_for_update']
    map_name = kwargs['map_name']
    maps = zapi.map.get(output=["mapid", "name"], filter={"name": map_name})
    if not maps:
        print(f"Map '{map_name}' not found.")
        return [False, (f"Map '{map_name}' not found.")]
    map_id = maps[0]['sysmapid']
    # print(f'\n\n\n{links_update}\n\n\n')
    # for l in links_update:
    #    print(l)
    # unique_list = [list(t) for t in {tuple(lst) for lst in links_update}]
    # cleaned_list = [item for item in links_update if item is not None and item != []]
    # for c in cleaned_list:
    #    cleaned_list.append(c)
    #    print(c)
    # result_list = merge_links(combined_list)
    # print(cleaned_list)
    # print(links_update)
    # """
    if links_update:
        zapi.map.update({
            "sysmapid": map_id,
            "links": links_update
        })
        #    #print(f"Links created between elements on the map '{map_name}'.")
        return (f"Links created between elements on the map '{map_name}'.")
    # """
    # else:
    #    print("No links to create.")



