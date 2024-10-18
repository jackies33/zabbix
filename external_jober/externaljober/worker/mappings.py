


from externaljober.devices_jobers.T8.atlas_start_collect import AtlasStartCollect

class MAPPINGS():

    """
    Class for mapp and classifier different type of data
    """

    def __init__(self):
        """
        Initialize the values
        """
        self.platform_mappings = {
            "Atlas.OS": AtlasStartCollect,
            }

    def connection_exec(self, **kwargs)  :# method for consider and execute connection to devices
        try:
            print("<<< Start mappings.connection_exec >>>")
            #print(kwargs)
            template_name = kwargs.get('template_name',None)
            job_name = kwargs.get('job_name', None)
            host_zbx_data = kwargs.get('host_zbx_data',None)
            #platform_name =  kwargs['groups'][0]['name']
            matching_key = None
            connection_class = None
            for key,value in self.platform_mappings.items():
                if key in template_name:
                    connection_class = value
                    break
            if connection_class:
                call = connection_class()
                method_to_call = getattr(call, job_name, None)
                if callable(method_to_call):
                    # Call the method with **kwargs
                    data_from_conn = method_to_call(**host_zbx_data)
                    if data_from_conn[0] == True:
                        return [True,data_from_conn[1]]
                    elif data_from_conn[0] == False:
                        return [False,data_from_conn[1],data_from_conn[2]]
            else:
                print(f"Platform {template_name} not found in mappings.")
                return [False, "Platform {template_name} not found in mappings.", host_zbx_data['name']]
        except Exception as err:
            host_zbx_data = kwargs.get('host_zbx_data', None)
            hostname = None
            if host_zbx_data:
                hostname = host_zbx_data.get("name", None)
            return [False, err, hostname]

