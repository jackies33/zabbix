



import re


from external_jober.externaljober.devices_jobers.T8.atlas_main import AtlasSNMP



class SNMPGetDomStatus(AtlasSNMP):


    def get_dom_status(self):
        try:
            ifaces = []
            list_for_ports = []
            list_for_sfp = []
            list_members = []
            for snmp in self.get_snmp_tables(["iso.3.6.1.4.1.39433.1.4.1"]):
                pattern = r"iso\.3\.6\.1\.4\.1\.39433\.1\.4\.1(\.\d+(\.\d+)*)?"
                # Используем re.findall для поиска индекса
                n = re.findall(pattern, str(snmp.oid))[0][0]
                v = str(snmp.value)
                value = re.findall("ten\d+", v)
                if value:
                    number_of_slot = n[-1]
                    list_members.append(number_of_slot)
            for number_of_slot in list_members:
                    for snmp in self.get_snmp_tables(f"iso.3.6.1.4.1.39433.1.6.1.3.{number_of_slot}.2"):
                        pattern = fr"iso\.3\.6\.1\.4\.1\.39433\.1\.6\.1\.3\.{number_of_slot}\.2\.(\d+)"
                        if "Ln1Pin" in str(snmp.value) or "Ln1Pout" in str(snmp.value) or \
                                "Cl1Pin" in str(snmp.value) or "Cl1Pout" in str(snmp.value) or \
                                "Ln1InBER" in str(snmp.value):#collect only for TP interfaces
                            ifindex = re.findall(pattern, str(snmp.oid))[0]
                            if "Tidemark" in str(snmp.value):
                                continue
                            v = str(snmp.value)
                            list_for_ports.append({"index_for_get_value_port": ifindex, "name_for_get_value_port": v})
                        elif "TxT" in str(snmp.value):#collect only for sfp
                            ifindex = re.findall(pattern, str(snmp.oid))[0]
                            v = str(snmp.value)
                            list_for_sfp.append({"index_for_get_value_sfp": ifindex, "name_for_get_value_sfp": v})
                    list_for_ports2 = []
                    list_for_sfp2 = []
                    for index in list_for_ports:
                        interface_type = (re.findall(f"Ln1|Cl1", index['name_for_get_value_port']))[0]
                        metric_type = (re.findall(f"Pin|Pout|InBER", index['name_for_get_value_port']))[0]
                        try:
                            value = self.get_snmp(f"1.3.6.1.4.1.39433.1.6.1.5.{number_of_slot}.2.{index['index_for_get_value_port']}")
                        except Exception:
                            value = None
                        if metric_type == "Pin":
                            metric_type = "optical_rx_dbm"
                        elif metric_type == "Pout":
                            metric_type = "optical_tx_dbm"
                        elif metric_type == "InBER":
                            metric_type = "current_ber"
                        if interface_type == "Ln1":
                            interface_name = f"Network/{number_of_slot}/TP{index['name_for_get_value_port'].split('TP')[1][0]}"
                            list_for_ports2.append({"ifname": interface_name, "iface_type": interface_type,
                                                    "metric_type": metric_type, "value": value.value})
                        elif interface_type == "Cl1":
                            interface_name = f"Client/{number_of_slot}/TP{index['name_for_get_value_port'].split('TP')[1][0]}"
                            list_for_ports2.append({"ifname":interface_name,"iface_type":interface_type,
                                                  "metric_type":metric_type,"value":value.value})
                    for index in list_for_sfp:
                        SFP_port_number = index['name_for_get_value_sfp'].split(f"TxT")[0]
                        try:
                            value = self.get_snmp(f"1.3.6.1.4.1.39433.1.6.1.5.{number_of_slot}.2.{index['index_for_get_value_sfp']}")
                        except Exception:
                            value = None
                        if SFP_port_number in self.sfp_map:
                            match_interface_name = self.sfp_map[SFP_port_number]
                            interface_name = f"{match_interface_name[0]}/{number_of_slot}/{match_interface_name[1]}"
                            metric_type = "temp_c"
                            list_for_sfp2.append({"ifname":interface_name,
                                                  "metric_type":metric_type,"value":value.value})
                    merged_data = {}
                    for item in list_for_ports2:
                        ifname = item['ifname']
                        if ifname not in merged_data:
                            merged_data[ifname] = []
                        merged_data[ifname].append(item)
                    for item in list_for_sfp2:
                        ifname = item['ifname']
                        if ifname not in merged_data:
                            merged_data[ifname] = []
                        merged_data[ifname].append(item)
                    result = []
                    for key in merged_data:
                        if len(merged_data[key]) > 1:
                            merged_dict = {}
                            for sub_dict in merged_data[key]:
                                merged_dict.update(
                                    {"ifname": sub_dict["ifname"], f"{sub_dict['metric_type']}": sub_dict["value"]})
                            result.append(merged_dict)
                        else:
                            result.extend(merged_data[key])
                    for res in result:
                        temp_c = None
                        current_ber = None
                        optical_rx_dbm = None
                        optical_tx_dbm = None
                        try:
                            interface = res['ifname']
                            optical_rx_dbm = res["optical_rx_dbm"]
                            optical_tx_dbm = res["optical_tx_dbm"]
                        except Exception:
                            continue
                        try:
                            current_ber = res["current_ber"]
                            if current_ber != '' or current_ber == None:
                                #number_float = float(current_ber)
                                #current_ber = '{:.10f}'.format(number_float)
                                #current_ber = int(float(current_ber)*1000000000)
                                current_ber = float(current_ber)
                            else:
                                current_ber = 0.0
                        except Exception as err:
                            pass
                        try:
                            temp_c = res["temp_c"]
                            if temp_c != '' or temp_c == None:
                                #temp_c = int(float(temp_c)*10)
                                temp_c = float(temp_c)
                            else:
                                temp_c = None
                        except Exception as err:
                            pass
                        if optical_tx_dbm == '':
                            continue
                        else:
                            #optical_tx_dbm = int(float(optical_tx_dbm)*10)
                            optical_tx_dbm = float(optical_tx_dbm)
                        if optical_rx_dbm == '':
                            continue
                        else:
                            #optical_rx_dbm = int(float(optical_rx_dbm)*10)
                            optical_rx_dbm =  float(optical_rx_dbm)
                        if current_ber == None:
                            current_ber = 0.0
                        iface = {"interface": interface,
                                 "optical_rx_dbm": float(optical_rx_dbm),
                                 "optical_tx_dbm": float(optical_tx_dbm),
                                 'temp_c': float(temp_c), 'current_ber':float(current_ber)
                                 }
                        ifaces += [iface]

            return ifaces
        except Exception as err:
            print(err)





