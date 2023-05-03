import argparse

from cmd import cmd_config
from oracleSQL import OracleSQL
from ui import gui_config
from xlsx2sql import *

def main(parser):
    # allow the use of one and only one cmd argument
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-gui", help="used to open GUI interface instead of command line", action="store_true")
    group.add_argument("-config_path", dest="config_path", help="yaml configuration file path", type=str)
    cmd_arguments = parser.parse_args()
    # decide where to go next, use gui or cmd arguments
    if cmd_arguments.gui:
        gui_config()
    else:
        cmd_config(cmd_arguments)

    # load the configuration from config file
    Config.init_config()
    # done here to avoid circular import
    if Config.dbms_type_str == 'oraclesql':
        Config.sql_type_config = OracleSQL()

    # take data from xlsx and load it to memory into "sheets_raw"
    sheets_raw: list[Sheet] = xlsx_to_raw_data(Config.input_file_absolute_path)

    g_ddl_tables: list[Table] = []
    dml_insert_queries: list[str] = []
    dml_delete_queries: list[str] = []

    # loop all the sheets, and parse it accordingly to the sheet type (ddl or dml)
    for sheet in sheets_raw:
        if sheet.sheet_name.startswith('ddl_'):
            tables: list[Table] = create_sheet_ddl_tables(sheet.sheet_raw)
            g_ddl_tables.extend(tables)
        elif sheet.sheet_name.startswith('dml_'):
            insert_queries, drops_queries = create_sheet_dml_queries(sheet.sheet_raw)
            dml_insert_queries.extend(insert_queries)
            dml_delete_queries.extend(drops_queries)

    ddl_queries, ddl_drops_queries, fk_queries, fk_drop_queries = create_ddl_queries(g_ddl_tables)

    generate_queries_files(ddl_queries, ddl_drops_queries, fk_queries, fk_drop_queries, dml_insert_queries, dml_delete_queries)


if __name__ == "__main__":
    main_parser = argparse.ArgumentParser()
    main(main_parser)
