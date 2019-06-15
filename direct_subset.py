import uuid, sys
import config_reader, result_tabulator
from subset import Subset
from psql_database_creator import PsqlDatabaseCreator
from mysql_database_creator import MySqlDatabaseCreator
from db_connect import DbConnect
import database_helper

def db_creator(db_type, source, dest):
    if db_type == 'postgres':
        return PsqlDatabaseCreator(source, dest, False)
    elif db_type == 'mysql':
        return MySqlDatabaseCreator(source, dest)
    else:
        raise ValueError('unknown db_type ' + db_type)


if __name__ == '__main__':
    if "--stdin" in sys.argv:
        config_reader.initialize(sys.stdin)
    else:
        config_reader.initialize()

    db_type = config_reader.get_db_type()
    source_dbc = DbConnect(db_type, config_reader.get_source_db_connection_info())
    destination_dbc = DbConnect(db_type, config_reader.get_destination_db_connection_info())

    database = db_creator(db_type, source_dbc, destination_dbc)
    database.teardown()
    database.create()


    # Get list of tables to operate on
    all_tables = database_helper.get_specific_helper().list_all_tables(source_dbc)
    all_tables = [x for x in all_tables if x not in config_reader.get_excluded_tables()]

    subsetter = Subset(source_dbc, destination_dbc, all_tables)

    try:
        subsetter.prep_temp_dbs()
        subsetter.run_middle_out()

        if "--no-constraints" not in sys.argv:
            database.add_constraints()

        result_tabulator.tabulate(source_dbc, destination_dbc, all_tables)
    finally:
        subsetter.unprep_temp_dbs()

