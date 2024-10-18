
from easysnmp import Session

class AtlasSNMP():
    def __init__(self, ip, community):
        # Устанавливаем сессию SNMP
        self.session = Session(hostname=ip, community=community, version=2)
        self.sfp_map = {
            "SFP1": ("Client", "TP1"),
            "SFP2": ("Client", "TP2"),
            "SFP3": ("Client", "TP3"),
            "SFP4": ("Client", "TP4"),
            "SFP5": ("Client", "TP5"),
            "SFP6": ("Client", "TP6"),
            "SFP7": ("Network", "TP1"),
            "SFP8": ("Network", "TP2"),
            "SFP9": ("Network", "TP3"),
            "SFP10": ("Network", "TP4"),
            "SFP11": ("Network", "TP5"),
            "SFP12": ("Network", "TP6"),
        }

    def get_snmp_tables(self, oid):

        return self.session.walk(oid)

    def get_snmp(self, oid):
        return self.session.get(oid)





