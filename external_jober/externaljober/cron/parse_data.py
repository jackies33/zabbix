


from external_jober.externaljober.cron.get_data import exec_get_redis,PARSE_DATA_ZBX



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
                    job_data = ZBX_DATA.get_zbx_data(config['job_data'])
        elif isinstance(config, dict):
            if config['job_target'] == 'zabbix_main' and config['job_type'] == 'devices_external_get':
                ZBX_DATA = PARSE_DATA_ZBX("bytemplate")
                job_data = ZBX_DATA.get_zbx_data(config['job_data'])
    #print(job_data)
    return job_data