import json, sys, collections, os, config_fixer

_config = None

def initialize(file_like = None):
    global _config
    if _config != None:
        print('WARNING: Attempted to initialize configuration twice.', file=sys.stderr)

    if not file_like:
        with open(os.environ.get('CONFIG_PATH', 'config.json'), 'r') as fp:
            _config = json.load(fp)
    else:
        _config = json.load(file_like)

    if "desired_result" in _config:
        raise ValueError("desired_result is a key in the old config spec. Check the README.md and example-config.json for the latest configuration parameters.")

    db_name = os.environ.get('SOURCE_DB_NAME', _config['source_db_connection_info']['db_name'])

    _config = config_fixer.config_fixer(_config,db_name)

DependencyBreak = collections.namedtuple('DependencyBreak', ['fk_table', 'target_table'])

def get_dependency_breaks():
    return set([DependencyBreak(b['fk_table'], b['target_table']) for b in _config['dependency_breaks']])

def get_preserve_fk_opportunistically():
    return set([DependencyBreak(b['fk_table'], b['target_table']) for b in _config['dependency_breaks'] if 'perserve_fk_opportunistically' in b and b['perserve_fk_opportunistically']])

def get_initial_targets():
    return _config['initial_targets']

def get_initial_target_tables():
    return [target["table"] for target in _config['initial_targets']]

def keep_disconnected_tables():
    return 'keep_disconnected_tables' in _config and bool(_config['keep_disconnected_tables'])

def get_db_type():
    return _config['db_type']

def get_source_db_connection_info():
    _config['source_db_connection_info']['user_name'] = os.environ.get('SOURCE_USER_NAME', _config['source_db_connection_info']['user_name'])
    _config['source_db_connection_info']['password'] = os.environ.get('SOURCE_PASSWORD', _config['source_db_connection_info']['password'])
    _config['source_db_connection_info']['host'] = os.environ.get('SOURCE_HOST', _config['source_db_connection_info']['host'])
    _config['source_db_connection_info']['db_name'] = os.environ.get('SOURCE_DB_NAME', _config['source_db_connection_info']['db_name'])
    _config['source_db_connection_info']['port'] = os.environ.get('SOURCE_PORT', _config['source_db_connection_info']['port'])
    return _config['source_db_connection_info']

def get_destination_db_connection_info():
    _config['destination_db_connection_info']['user_name'] = os.environ.get('DESTINATION_USER_NAME', _config['destination_db_connection_info']['user_name'])
    _config['destination_db_connection_info']['password'] = os.environ.get('DESTINATION_PASSWORD', _config['destination_db_connection_info']['password'])
    _config['destination_db_connection_info']['host'] = os.environ.get('DESTINATION_HOST', _config['destination_db_connection_info']['host'])
    _config['destination_db_connection_info']['db_name'] = os.environ.get('DESTINATION_DB_NAME', _config['destination_db_connection_info']['db_name'])
    _config['destination_db_connection_info']['port'] = os.environ.get('DESTINATION_PORT', _config['destination_db_connection_info']['port'])
    return _config['destination_db_connection_info']

def get_excluded_tables():
    return list(_config['excluded_tables'])

def get_passthrough_tables():
    return  list(_config['passthrough_tables'])

def get_fk_augmentation():
    return list(map(__convert_tonic_format, _config['fk_augmentation']))

def get_upstream_filters():
    return _config["upstream_filters"]

def get_pre_constraint_sql():
    return _config["pre_constraint_sql"] if "pre_constraint_sql" in _config else []

def get_post_subset_sql():
    return _config["post_subset_sql"] if "post_subset_sql" in _config else []

def get_max_rows_per_table():
    return _config["max_rows_per_table"] if "max_rows_per_table" in _config else None

def __convert_tonic_format(obj):
    if "fk_schema" in obj:
        return {
            "fk_table": obj["fk_schema"] + "." + obj["fk_table"],
            "fk_columns": obj["fk_columns"],
            "target_table": obj["target_schema"] + "." + obj["target_table"],
            "target_columns": obj["target_columns"],
        }
    else:
        return obj

def verbose_logging():
    return '-v' in sys.argv
