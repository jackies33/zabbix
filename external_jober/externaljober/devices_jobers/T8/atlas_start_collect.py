

from external_jober.externaljober.devices_jobers.T8.atlas_get_interfaces import SNMPGetInterface
from external_jober.externaljober.devices_jobers.T8.atlas_get_dom import SNMPGetDomStatus



class AtlasStartCollect():
    def dwdm_optic_ifaces_metrics_get(self,**kwargs):
        try:
            interface = kwargs.get("interfaces", None)
            if interface:
                ip = interface[0]['ip']
                comm = interface[0]['details']['community']
                collect_ifaces = SNMPGetInterface(ip=ip,community=comm)
                get_ifaces = collect_ifaces.get_interfaces()
                collect_dom = SNMPGetDomStatus(ip=ip, community=comm)
                get_dom = collect_dom.get_dom_status()
                for iface in get_ifaces:
                    for dom in get_dom:
                        if iface['interface'] == dom['interface']:
                            iface.update(dom)
                kwargs.update({"zbx_metrics":get_ifaces})
                return [True,kwargs]
            else:
                return [False,"UNFICIAL DATA in INTERFACE data from ZBX",kwargs['name']]
        except Exception as err:
            hostname = kwargs.get("name", None)
            return [False,err,hostname]


#ip="10.100.137.85"
#community="n0cdwdm"

#result = collect_all_data_interface(ip,community)
#for r in result:
#    print(r)
