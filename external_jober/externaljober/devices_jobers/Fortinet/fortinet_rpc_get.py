import time

import requests
from external_jober.externaljober.devices_jobers.Fortinet.fortinet_main import FortiNetApi



class FORTI_RPC_GET_METRICS(FortiNetApi):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_interface_load(self):
        try:
            url1 = f"https://{self.FORTIGATE_IP}/api/v2/monitor/system/available-interfaces/select?&include_vlan=1&scope=global"
            url2 = f"https://{self.FORTIGATE_IP}/api/v2/monitor/system/interface/select?&scope=global"
            zbx_data_result = []
    ####first request
            # Выполняем GET-запрос к API Fortinet
            response = requests.get(url1, headers=self.headers, verify=False)  # verify=False отключает проверку SSL сертификата
            # Проверяем статус ответа
            response.raise_for_status()  # Бросит исключение для кодов 4xx и 5xx
            # Парсим JSON ответ
            data = response.json()
            discovery_ifaces = []
            # Проверка, что запрос успешен
            if data.get("status") == "success":
                results = data.get("results", [])
                for iface in results:
                    #print(iface)
                    iface_description = iface.get('description', None)
                    if iface_description:
                        #print(iface)
                        if "SNI" in iface_description or "NNI" in iface_description:
                            #print(iface)
                            iface_type = iface.get('type',None)

                            if iface_type:
                                iface_status = iface.get("link", None)

                                if iface_status == "up":
                                    iface_status = 1
                                elif iface_status == "down":
                                    iface_status = 2
                                else:
                                    iface_status = 2
                                if iface_type == 'aggregate':


                                    discovery_ifaces.append({"iface_name":iface['name'],"iface_description":iface_description,
                                                         "iface_type":iface['type'], "iface_members":iface['members'],
                                                         "iface_status":iface_status
                                                             })
                                else:
                                    discovery_ifaces.append(
                                        {"iface_name": iface['name'], "iface_description": iface_description,
                                         "iface_type": iface['type'],"iface_status":iface_status})


    ###second request
            response2_first = requests.get(url2, headers=self.headers,verify=False)  # verify=False отключает проверку SSL сертификата
            time.sleep(3) # wait for make requests for get diff between two indicators
            response2_second = requests.get(url2, headers=self.headers, verify=False)
            # Проверяем статус ответа
            response2_first.raise_for_status()  # Бросит исключение для кодов 4xx и 5xx
            # Парсим JSON ответ
            data2 = response2_first.json()
            # Проверка, что запрос успешен
            temp_data_result = []
            if data2.get("status") == "success":
                # print(data)
                results2 = data2.get("results", [])
                for iface_name, interface_info in results2.items():
                    for disc_iface in discovery_ifaces:
                        if iface_name == disc_iface['iface_name']:
                            #print(interface_info)
                            print(interface_info['tx_bytes'])
                            print(interface_info['rx_bytes'])
                            temp_data_result.append({"iface_name":iface_name,"iface_description":disc_iface['iface_description'],
                                                    "iface_type":disc_iface["iface_type"],
                                                    "iface_tx_bytes":interface_info['tx_bytes'],
                                                    "iface_rx_bytes":interface_info['rx_bytes'],
                                                    "iface_tx_errors":interface_info['tx_errors'],
                                                    "iface_rx_errors": interface_info['rx_errors'],
                                                    "iface_speed":int(interface_info['speed']),
                                                    "iface_status": disc_iface['iface_status']
                                                    })
            # Проверяем статус ответа
            response2_second.raise_for_status()  # Бросит исключение для кодов 4xx и 5xx
            # Парсим JSON ответ
            data3 = response2_second.json()
            # Проверка, что запрос успешен
            if data3.get("status") == "success":
                # print(data)
                results3 = data3.get("results", [])
                for iface_name, interface_info in results3.items():
                    for first_res in temp_data_result:
                        if iface_name == first_res['iface_name']:
                            # print(interface_info)
                            tx_bytes_result = int((interface_info['tx_bytes'] - first_res['iface_tx_bytes']) / 3)# devide on 3 because waited 3 seconds
                            rx_bytes_result = int((interface_info['rx_bytes'] - first_res['iface_rx_bytes']) / 3)
                            tx_errors_result = int((interface_info['tx_errors'] - first_res['iface_tx_errors']) / 3)
                            rx_errors_result = int((interface_info['rx_errors'] - first_res['iface_rx_errors']) / 3)
                            zbx_data_result.append({"iface_name": iface_name,
                                                    "iface_description": first_res['iface_description'],
                                                    "iface_type": first_res["iface_type"],
                                                    "iface_tx_bytes": tx_bytes_result,
                                                    "iface_rx_bytes": rx_bytes_result,
                                                    "iface_tx_errors": tx_errors_result,
                                                    "iface_rx_errors": rx_errors_result,
                                                    "iface_speed": int(interface_info['speed']),
                                                    "iface_status": first_res['iface_status']
                                                    })
            if zbx_data_result != []:
                for disc_iface in discovery_ifaces:
                    if disc_iface['iface_type'] == 'aggregate':
                        tx_bytes_count = 0
                        rx_bytes_count = 0
                        tx_errors_count = 0
                        rx_errors_count = 0
                        speed_count = 0
                        members = disc_iface.get('iface_members', None)
                        if members:
                            for member in members:
                                for zbx_data in zbx_data_result:
                                    if zbx_data['iface_name'] == member:
                                        tx_bytes_count = tx_bytes_count + zbx_data["iface_tx_bytes"]
                                        rx_bytes_count = rx_bytes_count + zbx_data["iface_rx_bytes"]
                                        tx_errors_count = tx_errors_count + zbx_data['iface_tx_errors']
                                        rx_errors_count = rx_errors_count + zbx_data['iface_rx_errors']
                                        speed_count = speed_count + zbx_data["iface_speed"]
                            zbx_data_result.append(
                                {"iface_name": disc_iface['iface_name'], "iface_description": disc_iface['iface_description'],
                                 "iface_type": disc_iface["iface_type"],
                                 "iface_tx_bytes": tx_bytes_count,
                                 "iface_rx_bytes": rx_bytes_count,
                                 "iface_tx_errors": tx_errors_count,
                                 "iface_rx_errors": rx_errors_count,
                                 "iface_speed":speed_count,
                                 "iface_status": disc_iface['iface_status']
                                 })

            else:
                print("Ошибка: данные не получены:", data2)
            self.data.update({"exec_result":{"type":"iface_load","data":zbx_data_result}})
            return self.data
        except requests.exceptions.RequestException as e:
            print("Ошибка выполнения запроса:", e)


my_host_test = {'hostid': '13324', 'name': 'kr-nat-gw01', 'parentTemplates': [{'templateid': '16250', 'name': 'FortiGate firewall'}], 'groups': [{'groupid': '56', 'name': 'Fortinet/Fortinet.Fortigate/FortiGate-6501F'}], 'interfaces': [{'ip': '10.50.76.97'}]}

forti_test_call = FORTI_RPC_GET_METRICS(**my_host_test)
result = forti_test_call.get_interface_load()
print(result)

