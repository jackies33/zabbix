


import time



from externaljober.keep_api_connect import netbox_api_instance

class NetboxGet():

    def __init__(self):
        self.nb = netbox_api_instance.get_instance()

    def get_wap_devices(self, **kwargs):
        wap_scope_hostname = kwargs['wap_scope_hostname']
        devices_list = []
        devices_nb_all = self.nb.dcim.devices.all()
        locations_nb_all = {location.id: location for location in self.nb.dcim.locations.all()}  # Создаем словарь для быстрого поиска локаций

        for dev_index, dev in enumerate(devices_nb_all):
            if wap_scope_hostname in str(dev.name):
                try:
                    host_name = dev.name
                    host_sn = dev.serial
                    host_second_location = dev.location
                    host_first_location = None
                    host_third_location = None
                    #location_second = None
                    location_depth = None

                    if dev.location and dev.location.id:
                        # Получаем вторую локацию из заранее подготовленного словаря
                        host_second_location = locations_nb_all.get(dev.location.id)
                        if host_second_location:
                            location_depth = host_second_location._depth

                    if location_depth is None:
                        print(f"[Device {dev_index}] {host_name}: Location depth not found")
                        continue

                    # Если глубина 2, ищем родителя
                    if int(location_depth) == 2 and host_second_location and host_second_location.parent:
                        host_third_location = host_second_location  # Третья локация — текущая вторая
                        host_second_location = locations_nb_all.get(host_third_location.parent.id) if host_third_location.parent else None
                        host_first_location = locations_nb_all.get(host_second_location.parent.id) if host_second_location.parent else None
                    else:
                        # Если глубина не 2, ищем только первую локацию (родителя)
                        host_first_location = locations_nb_all.get(host_second_location.parent.id) if host_second_location and host_second_location.parent else "Parent location not found"

                    devices_list.append({
                        "host_name": str(host_name),
                        "host_sn": str(host_sn),
                        "host_third_location": str(host_third_location),
                        "host_second_location": str(host_second_location.name if host_second_location else "None"),
                        "host_first_location": str(host_first_location),
                        "host_location_depth": str(location_depth)
                    })
                except Exception as err:
                    print(f"Error processing device {dev_index} ({host_name}): {err}")
                    continue  # Продолжаем обработку остальных устройств

        result = {"wap_scope_hostname": wap_scope_hostname, "devices_list": devices_list}
        time.sleep(5)
        return result

