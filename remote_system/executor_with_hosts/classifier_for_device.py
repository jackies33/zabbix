



class CLASSIFIER():

        """
        Class for classification some things for noc's extractors

        """

        def __init__(self):
            """


            """



        def classifier_snmp_comm(self,**kwargs):
            device_type = kwargs["device_type"]
            device_role = kwargs["device_role"]
            if device_type == "NE20E-S2F" and device_role == "p-pe" or \
                    device_type == "NetEngine 8000 F1A-8H20Q" and device_role == "p-pe" or \
                    device_type == "S5700-28C-EI-24S" and device_role == "m-dsw"  or \
                    device_type == "S5735-S48S4X" and device_role == "m-dsw" :
                snmp_comm = "nocpr0ject"
                return snmp_comm
            else:
                snmp_comm = "nocproject"
                return snmp_comm


        def classifier_AuthScheme(self,**kwargs):
                    connection_scheme = kwargs['Connection_Scheme']
                    if connection_scheme == 'ssh':
                        AuthScheme = '2'
                        return AuthScheme
                    elif connection_scheme == 'telnet':
                        AuthScheme = '1'
                        return AuthScheme




