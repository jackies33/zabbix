





import re


from external_jober.externaljober.devices_jobers.T8.atlas_main import AtlasSNMP



class SNMPGetInterface(AtlasSNMP):

    def get_interfaces(self):
        interfaces = []
        list_collect_data = []
        list_members = []

        # Получаем таблицы по OID 1.3.6.1.4.1.39433.1.4
        for snmp in self.get_snmp_tables("iso.3.6.1.4.1.39433.1.4.1"):
            pattern = r"iso\.3\.6\.1\.4\.1\.39433\.1\.4\.1(\.\d+(\.\d+)*)?"
            # Используем re.findall для поиска индекса
            n = re.findall(pattern, str(snmp.oid))[0][0]
            v = str(snmp.value)
            value = re.findall("ten\d+", v)
            if value:
                value = value[0]
                number_of_slot = n[-1]
                list_members.append(number_of_slot)

        for number_of_slot in list_members:
            # Получаем данные по slot'ам
            for snmp in self.get_snmp_tables(f"iso.3.6.1.4.1.39433.1.6.1.3.{number_of_slot}.3"):
                pattern = fr"iso\.3\.6\.1\.4\.1\.39433\.1\.6\.1\.3\.{number_of_slot}\.3\.(\d+)"
                if "Cl1PortState" in str(snmp.value):
                    interface_name = f"Client/{number_of_slot}/{snmp.value.split('Cl1')[0]}"
                    ifindex = re.findall(pattern, str(snmp.oid))[0]
                    list_collect_data.append({"ifname": interface_name, "ifindex": ifindex})
                elif "Ln1PortState" in str(snmp.value):
                    interface_name = f"Network/{number_of_slot}/{snmp.value.split('Ln1')[0]}"
                    ifindex = re.findall(pattern, str(snmp.oid))[0]
                    list_collect_data.append({"ifname": interface_name, "ifindex": ifindex})

            # Получаем статус интерфейсов
            for snmp in self.get_snmp_tables(f"1.3.6.1.4.1.39433.1.6.1.5.{number_of_slot}.3"):
                pattern = fr"iso\.3\.6\.1\.4\.1\.39433\.1\.6\.1\.5\.{number_of_slot}\.3\.(\d+)"
                for item in list_collect_data:
                    ifindex_status = re.findall(pattern, str(snmp.oid))[0]
                    if str(item['ifindex']) == str(ifindex_status):
                        status = str(snmp.value)
                        item.update({"status": status})

            # # Получаем описание интерфейсов
            # for r in range(13, 19):
            #    descr = self.session.get(f"1.3.6.1.4.1.39433.1.6.1.5.{number_of_slot}.1.{r}")
            #      for item in list_collect_data:
            #          if str(item['ifindex']) == str(r):
            #              item.update({"description": descr})

            # Формируем список интерфейсов
            for res in list_collect_data:
                status = res.get("status", '')
                ifname = res.get("ifname", '')
                #print(ifname, status)
                oper_status = 2 if status == '1' else 1 if status == '2' else 2
                # description = res.get('description', '')
                ifindex = res.get("ifindex", '')
                iface = {
                    "interface": ifname,
                    "admin_status": 1,
                    "oper_status": oper_status,
                    # "description": description,
                    "mac": None,
                    "type": "physical",
                    "enabled_protocols": [],
                    "snmp_ifindex": ifindex,
                    "subinterfaces": [],
                }
                interfaces.append(iface)

        return interfaces
