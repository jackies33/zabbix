



import os
import sys

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))

from device_types.huawei import HUAWEI_CONN
from device_types.juniper import JUNIPER_CONN
from device_types.cisco import CISCO_CONN
from device_types.fortinet import FORTINET_CONN
from device_types.ibm import IBM
#from map_manager.device_types.aruba import ARUBA_OS
#from map_manager.device_types.linux import LINUX
#from map_manager.device_types.hpe import HPProCurve9xxx
#from map_manager.device_types.mikrotik import MIKROTIK_CONN
from device_types.qtech import QTECH_CONN


class MAPPINGS():

    """
    Class for mapp and classifier different type of data
    """

    def __init__(self, **kwargs):
        """
        Initialize the values
        """
        self.device_role_to_icons = {
            'border':'131','border-dsw':'156','border leaf':'131','c-asw':'156','c-core':'131','c-dsw':'156','ce':'131',
            'ce-asw':'156','ce-dsw':'156','ce-firewall':'30','core':'131','cpe':'131','cpe-firewall':'30','dpi':'30',
            'dwdm':'156','edge':'131','firewall':'30','fswitch':'156','leaf':'156','m-dsw':'156','mgmt-asw':'156',
            'mgmt-dsw':'156','ntp':'151','p':'131','pe':'131','p-pe':'131','spine':'156','tfs':'156','tor':'156',
            'vm':'151','vpn':'15','vrr':'151','wlc-cpe':'131','fo-switch':'156'
        }

    def get_icon(self, device_role):
        """
        Get the icon code corresponding to the device role.

        :param device_role: The role of the device as a string
        :return: The icon code as a string if found, else None
        """
        return self.device_role_to_icons.get(device_role)
    def connection_exec(self, **kwargs)  :# method for consider and execute connection to devices

        try:
            print("<<< Start mappings.connection_exec >>>")
            platform_mappings = {
            "Huawei.VRP": (HUAWEI_CONN, "conn_Huawei"),
            "Juniper.JUNOS": (JUNIPER_CONN, "start_Junos"),
            "Cisco.IOS": (CISCO_CONN, "conn_Cisco_IOS"),
            "Cisco.NXOS": (CISCO_CONN, "conn_Cisco_NEXUS"),
            "Cisco.IOSXE": (CISCO_CONN, "conn_Cisco_IOS"),
            "Cisco.IOSXR": (CISCO_CONN, "conn_Cisco_IOS"),
            "IBM.NOS": (IBM, "conn_IBM_lenovo_sw"),
           # "Aruba.ArubaOS": (ARUBA_OS, "conn_AWMP"),
            "Fortinet.Fortigate": (FORTINET_CONN, "FortiNet_start"),
           # "OS.Linux": (LINUX, "conn_OS_Linux"),
           # "HP.ProCurve9xxx": (HPProCurve9xxx, "conn_ProCurve9xxx"),
           # "MikroTik.RouterOS": (MIKROTIK_CONN, "conn_RouterOS"),
           # "Cisco.ASA": (CISCO_CONN, "conn_Cisco_ASA"),
           "Qtech.QSW": (QTECH_CONN, "conn_qtech")
            }
            platform_name =  kwargs['groups'][0]['name']
            matching_key = None
            for key in platform_mappings:
                if key in platform_name:
                    matching_key = key
                    break
            if matching_key:
                connection_class, method_name = platform_mappings[matching_key]
                call = connection_class()
                data_from_conn = getattr(call, method_name)(**kwargs)
                return data_from_conn
            else:
                print(f"Platform {platform_name} not found in mappings.")
                return [False, None, kwargs['name']]
        except Exception as err:
            return [False, None, kwargs['name']]








