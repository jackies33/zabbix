

import socket
import telnetlib

#sys.path.append('/opt/zabbix_custom/zabbix_MAP/')
#sys.path.append('/app/')
#current_dir = os.path.dirname(os.path.abspath(__file__))
#sys.path.append(os.path.join(current_dir, '..', '..'))


from map_manager.my_env import  mylogin , mypass



class CONNECT_PREPARE():
        """
        Class for preparing data to connection to diff devices
        """

        def __init__(self, **kwargs):
                        """
                        Initialize the values
                        """

        def check_ssh(self, **kwargs):# func for check ssh or telnet - connections method
            ip_conn = kwargs['ip_conn']
            socket.setdefaulttimeout(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                result = sock.connect_ex((ip_conn, 22))
                if result == 0:
                    scheme = 'ssh'
                else:
                    """
                    result = sock.connect_ex((ip_conn, 23))
                    if result == 103:
                        scheme = 'telnet'
                    else:
                        scheme = 0
                    """
                    try:
                        telnetlib.Telnet(ip_conn, timeout=1)
                        scheme = 'telnet'
                    except ConnectionRefusedError:
                        scheme = 0
                    except Exception as e:
                        scheme = 0
            except Exception as err:
                print(err)
                scheme = 0
            sock.close()
            return scheme

        def template_conn(self, **kwargs):# method for make template for connection via netmiko
            print("<<< Start preparing.py >>>")
            try:
                ip_conn = kwargs['ip_conn']
                conn_scheme = kwargs['conn_scheme']
                type_device_for_conn = kwargs['type_device_for_conn']
                if conn_scheme == "1" and type_device_for_conn != "hp_procurve":
                    host1 = {

                        "host": ip_conn,
                        "username": mylogin,
                        "password": mypass,
                        "device_type": type_device_for_conn,
                        "global_delay_factor": 0.5,
                    }
                elif  conn_scheme == "1" and type_device_for_conn == "hp_procurve":
                    host1 = {

                            "host": ip_conn,
                            "username": mylogin,
                            "password": mypass,
                            "device_type": type_device_for_conn,
                            "global_delay_factor": 3,
                            "secret": mypass,
                    }
                else:
                    host1 = {

                        "host": ip_conn,
                        "username": mylogin,
                        "password": mypass,
                        "device_type": type_device_for_conn,
                        "global_delay_factor": 3,
                    }

                return host1
            except Exception as err:
                print(err)
                return False

        def parse_conn_data(self,**kwargs):
            ip_conn = kwargs['interfaces'][0]['ip']

