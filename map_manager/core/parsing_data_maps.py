





import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from keep_api_connect import zabbix_api_instance
from get_data import GetData



def parse_all_devices_for_map(devices_list_from_connection,devices_list_from_map):
    get_data = GetData()
    get_devices_all = get_data.get_all_hosts_in_zabbix(devices_list_from_connection)
    for gd in get_devices_all:
        print(gd)
    for dev_all in get_devices_all:
        exists = False
        for dev_map in devices_list_from_map:
            if str(dev_map) == str(dev_all['name']):
                exists = True
        if exists == False:
            devices_list_from_map.append(dev_all)
    return devices_list_from_map




def get_map_parse_data(map_name):
    try:
        zapi = zabbix_api_instance.get_instance()
        get_data = GetData()
        # local_hostid = get_data.get_host_id(my_device['local_hostname'])
        maps = zapi.map.get(output=["mapid", "name"], filter={"name": map_name})
        if not maps:
            print(f"Map '{map_name}' not found.")
            return [False, (f"Map '{map_name}' not found.")]
        map_id = maps[0]['sysmapid']
        # Получаем все элементы карты
        elem = zapi.map.get(filter={'sysmapid': map_id}, selectSelements="extend", selectLinks="extend")[0]
        if elem['links'] == []:
            new_map = True
        else:
            new_map = False
        return [True,{"new_map":new_map,"elem":elem}]
        #transform_elem = transform_sysmap_data_with_links(elem)
        #return [True,{"transform_elem":transform_elem,"elem":elem}]
    except Exception as err:
        print(err)
        return [False, err]

def transform_sysmap_data_with_links(sysmap_data):
    # Создаем словарь, содержащий основные данные карты
    transformed_data = {
        "sysmapid": sysmap_data["sysmapid"],
        "name": sysmap_data["name"],
        "width": sysmap_data["width"],
        "height": sysmap_data["height"],
        "grid_size": sysmap_data["grid_size"],
        "elements": {}
    }

    # Создание предварительного словаря для быстрого доступа к host_id по selementid
    selement_to_host_map = {}
    for element in sysmap_data['selements']:
        for el in element.get('elements', []):
            host_id = el['hostid']
            if host_id not in transformed_data["elements"]:
                transformed_data["elements"][host_id] = {
                    "selementid": element["selementid"],
                    "label": element["label"],
                    "x": element["x"],
                    "y": element["y"],
                    "links": []  # Инициализируем пустой список для ссылок
                }
            selement_to_host_map[element["selementid"]] = host_id

    # Обработка ссылок между элементами
    for link in sysmap_data['links']:
        selement1_id = link["selementid1"]
        selement2_id = link["selementid2"]

        # Определение host_id для selementid1 и selementid2
        host_id_1 = selement_to_host_map.get(selement1_id)
        host_id_2 = selement_to_host_map.get(selement2_id)

        # Создание ссылки с обоими selementid и добавление в подсловарь соответствующих host_id
        host_id_remote = None
        for element in sysmap_data['selements']:
            if selement2_id == element["selementid"]:
                el = element.get('elements', [])[0]
                host_id_remote = el['hostid']
        link_data = {
            "linkid": link["linkid"],
            "selementid1": selement1_id,
            "selementid2": selement2_id,
            "host_id_remote": host_id_remote,
            "color": link["color"],
            "linktriggers": [{"triggerid": lt["triggerid"], "color": lt["color"]} for lt in link.get('linktriggers', [])]
        }

        # Добавляем ссылку к первому хосту, если он существует
        if host_id_1 and host_id_1 in transformed_data["elements"]:
            transformed_data["elements"][host_id_1]["links"].append(link_data)

        # Добавляем ссылку ко второму хосту, если он существует
        if host_id_2 and host_id_2 in transformed_data["elements"]:
            transformed_data["elements"][host_id_2]["links"].append(link_data)

    return transformed_data

