


from externaljober.cron.get_data import exec_get_redis,PARSE_DATA_ZBX



def get_and_parse_redis_configs():
    configs_redis = exec_get_redis()
    job_data = []
    #print(configs_redis)
    for config in configs_redis:
        if isinstance(config, list):
            configs_list = config
            for config in configs_list:
                if config['job_target'] == 'zabbix_main' and config['job_type'] == 'devices_external_get':
                    ZBX_DATA = PARSE_DATA_ZBX("bytemplate")
                    #job_data = ZBX_DATA.get_zbx_data(config['job_data'])
                    job_data.append(ZBX_DATA.get_zbx_data(config['job_data']))
        elif isinstance(config, dict):
            if config['job_target'] == 'zabbix_main' and config['job_type'] == 'devices_external_get':
                ZBX_DATA = PARSE_DATA_ZBX("bytemplate")
                job_data.append(ZBX_DATA.get_zbx_data(config['job_data']))
            else:
                j_d = config['job_data']
                for task in j_d:
                    job_data.append({
                        'job_target': config['job_target'], 'job_type': config['job_type'],
                        'job_data': config['job_data'],'job_name':task['job_name'],'interval':task['interval'],
                        'rb_route_key':task['rb_route_key'], 'rb_exchange':task['rb_exchange']
                    })

    return job_data

