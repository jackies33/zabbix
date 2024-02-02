


class CLASSIFIER():

        """
        Class for classification some things for noc's extractors

        """

        def __init__(self,device_type = None,device_role=None,custom_field=None):
            self.device_type = device_type
            self.device_role = device_role
            self.custom_field = custom_field



        def classifier_AuthProf(self,*args):
                    if self.device_type == "NE20E-S2F" and self.device_role == "p/pe" or \
                            self.device_type == "NetEngine 8000 F1A-8H20Q" and self.device_role == "p/pe" or \
                            self.device_type == "S5700-28C-EI-24S" and self.device_role == "m-dsw"  or \
                            self.device_type == "S5735-S48S4X" and self.device_role == "m-dsw" :
                        snmp_comm = "nocpr0ject"
                        return snmp_comm
                    else:
                        snmp_comm = "nocproject"
                        return snmp_comm


        def classifier_AuthScheme(self,*args):
                    connection_scheme = self.custom_field['Connection_Scheme']
                    if connection_scheme == 'ssh':
                        AuthScheme = '2'
                        return AuthScheme
                    elif connection_scheme == 'telnet':
                        AuthScheme = '1'
                        return AuthScheme


