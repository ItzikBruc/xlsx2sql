import re
import pandas as pd
import numpy as np

from config import Config
from definitions import *
from logger import logger


def xlsx_to_raw_data(xlsx_file_path):
    """
    :param xlsx_file_path: full path of xlsx file, containing the DB design
    :return: List of Sheets ,to be processed in memory
    """
    # will contain all the workbook sheets as a list of matrixes
    all_sheets: list[Sheet] = []

    workbook = pd.ExcelFile(xlsx_file_path)
    for sheet_name in workbook.sheet_names:
        sheet: Sheet = Sheet(sheet_name)
        raw_data = workbook.parse(sheet_name, header=None).values
        # add an empty row and column at 0 in both axes, so it matches the xlsx row numbering (which starts from 1)
        raw_data = np.insert(raw_data, 0, np.nan, axis=0)
        raw_data = np.insert(raw_data, 0, np.nan, axis=1)
        # also add an empty row and column at the end of both axes to prevent out of bounds in extreme cases
        raw_data = np.insert(raw_data, raw_data.shape[0], np.nan, axis=0)
        raw_data = np.insert(raw_data, raw_data.shape[1], np.nan, axis=1)
        # make all cells string, to save us trouble parsing different types
        raw_data = raw_data.astype(str)

        sheet.sheet_raw = raw_data
        all_sheets.append(sheet)

    return all_sheets


def create_sheet_ddl_tables(sheet_raw):
    """
    for each table in this sheet, create Table object to be used later
    :param sheet_raw: get raw data in the format of multiple matrix(es) in each "Sheet" and fill with it "Table"(s) class
    :return: list of "Table"(s) from which DDL queries can be created.
    """
    ddl_tables: list[Table] = []
    # loop through each first cell in each row the sheet
    row_number: int = 1
    while row_number < sheet_raw.shape[0]:  # sheet.sheet_raw.shape[0]   --> sheet's max row number
        cell_value: str = sheet_raw[row_number, 1]
        if cell_value.startswith('###_ddl'):
            table: Table() = create_ddl_table(sheet_raw, row_number)
            # increase row index by number of table column + 3 rows ("###_ddd", table name, columns metadata)
            row_number += len(table.columns) + 3
            ddl_tables.append(table)
        else:
            row_number += 1
    return ddl_tables

def create_ddl_table(sheet_raw, row_i: int):
    """
    creating DDL "Table" object from a matrix table, starting in the specified position
    :param sheet_raw: the sheet in format of matrix containing tables data
    :param row_i: the location row to start parsing the table in the given sheet
    :return: "Table" with it's values taken from the sheet+location in the sheet
    """
    table: Table = Table()

    table.name = sheet_raw[row_i + 1, 1].upper().strip()
    if table.name in Config.sql_type_config.reserved_keywords:
        logger.warning(f"The table name {table.name} cannot be used since it is a reserved word")
        exit()

    # handle the comment for table and name of table
    table.comment = sheet_raw[row_i, 2]
    # check if comment contains odd number of single quote, which will cause problem in queries
    if table.comment.count('\'') % 2 != 0:
        logger.error(f"The table {table.name} contains non-escaped single quote")
        exit()

    # handle unique constraint on multiple columns. todo can simplify regex
    multi_unique = re.findall(r"\[(.*)]", sheet_raw[row_i, 3].upper().replace(' ', ''))
    if multi_unique:
        table.multi_columns_unique = multi_unique[0].split('][')
    # start to add and parse all columns one by one
    row_i += 3
    while sheet_raw[row_i, 1] != 'nan' and not sheet_raw[row_i, 1].startswith('###_ddl'):
        table_column = TableColumn()
        table_column.name = sheet_raw[row_i, 1].upper().strip()
        if table_column.name in Config.sql_type_config.reserved_keywords:
            logger.warning(f"Error: The column name {table.name}.{table_column.name} cannot be used since it is a reserved word")
        table_column.data_type = sheet_raw[row_i, 2].upper().strip()
        table_column.is_nullable = sheet_raw[row_i, 3].lower().strip()
        table_column.foreign_key = sheet_raw[row_i, 4].upper().strip()
        table_column.identity = sheet_raw[row_i, 5].lower().strip()
        table_column.cache = sheet_raw[row_i, 6].strip()
        table_column.constraint = sheet_raw[row_i, 7]
        # excel have problem with leading apostrophe('), so we using double quote (") and need to replace it here
        table_column.default_value = sheet_raw[row_i, 8].strip().replace('"', '\'')
        table_column.is_indexed = sheet_raw[row_i, 9].lower().strip()
        table_column.comment = sheet_raw[row_i, 10]

        table.columns.append(table_column)
        row_i += 1

    return table


def create_sheet_dml_queries(sheet_raw):
    """
    creating all DML (insert and drops) queries from the data, represented as matrixes in the sheet in different locations
    :param sheet_raw: matrix sheet containing matrix(es), while each one represented DML queries of a specific table
    :return: all DML queries created from this sheet
    """
    sheet_insert_queries: list[str] = []
    sheet_drops_queries: list[str] = []
    row_number: int = 1
    # loop rows until end of used rows in sheet
    while row_number < sheet_raw.shape[0]:
        cell_value: str = sheet_raw[row_number, 1]
        if cell_value == '###_dml':
            dml_inserts_queries, dml_drops_queries = create_dml_queries(sheet_raw, row_number)
            sheet_insert_queries.extend(dml_inserts_queries)
            sheet_drops_queries.extend(dml_drops_queries)
            row_number += len(dml_inserts_queries) + 2 # 2-->"###_dml" + table name + columns names - "\n"
        else:
            row_number += 1
    return sheet_insert_queries, sheet_drops_queries


def create_dml_queries(sheet_raw, row_number: int):
    """
    create insert and drop queries from a table found in the matrix sheet, given the start location of the table in the matrix
    :param sheet_raw: the matrix sheet with tables inside, to be parsed into DML queries
    :param row_number: the location row to start parsing the table in the given sheet
    :return: 2 lists of creates queries (insert and drop)
    """
    table_name: str = sheet_raw[row_number + 1, 1].upper().strip()

    column_number: int = 1
    row_number += 2
    # first loop to find the columns names
    columns_names: list[str] = []
    while sheet_raw[row_number, column_number] != 'nan':
        column_name = sheet_raw[row_number, column_number].strip()
        columns_names.append(column_name)
        column_number += 1

    row_number += 1

    # second loop to find all the values
    values_list: list[list] = []
    while sheet_raw[row_number, 1] != 'nan' and sheet_raw[row_number, 1] != '###_dml':
        column_values = []
        for column_i in range(1, column_number):
            value = sheet_raw[row_number, column_i].strip() if sheet_raw[row_number, column_i] != 'nan' else ''

            # numbers are not quoted, only for aesthetics
            if value.isdigit():
                column_values.append(value)
            else:
                column_values.append(f"'{value}'")
        values_list.append(column_values)

        row_number += 1

    # use the columns names and the values to create the actual queries
    insert_queries: list[str] = []
    delete_queries: list[str] = []
    for values in values_list:
        insert_query: str = Config.sql_type_config.build_insert_query(table_name, columns_names, values)
        insert_queries.append(insert_query)

        delete_query: str = Config.sql_type_config.build_delete_query(table_name, columns_names, values)
        delete_queries.append(delete_query)

    insert_queries.append('\n')
    delete_queries.append('\n')

    return insert_queries, delete_queries


def create_ddl_queries(tables: list):
    """
    make the actual queries form 'Table' class
    query included: create table, fk, indexes, comments, sequences, and drops
    :param tables: list of "Table" class, containing all the information to create DDl queries
    :return: lists of created queries, 4 lists including:
                    creation of SQL tables, drop table, creation of foreign keys. drop foreign keys
    """
    ddl_create_queries: list[str] = []
    ddl_drops_queries: list[str] = []
    # some tables have dependencies on other table with foreign key.
    # So the foreign keys are created in separate list and run at the end
    fk_queries: list[str] = []
    fk_drop_queries: list[str] = []

    for table in tables:
        drop_seqs, fks, fk_drops, create_tables, drop_tables = Config.sql_type_config.create_ddl_queries(table)
        ddl_create_queries.extend(create_tables)
        ddl_drops_queries.extend(drop_seqs)
        ddl_drops_queries.extend(drop_tables)
        fk_queries.extend(fks)
        fk_drop_queries.extend(fk_drops)

    return ddl_create_queries, ddl_drops_queries, fk_queries, fk_drop_queries


def generate_queries_files(ddl_queries: list, ddl_drops_queries: list, fk_queries: list,
                           constraints_drop_queries: list, insert_queries: list, delete_queries: list):
    """
    writing the whole data into files (queries file and drop file)
    :param ddl_queries: list of DDD create table queries
    :param ddl_drops_queries: list of DDL drop table queries
    :param fk_queries:  list of DDL create foreign key queries
    :param constraints_drop_queries: list of DDL drop constraint queries
    :param insert_queries: list of DML insert queries
    :param delete_queries: list of DML delete queries
    :return: None
    """
    Config.output_dir_path.mkdir(exist_ok=True)

    # Write all updates into sql file
    with open(Config.output_queries_file, 'w', encoding='utf-8') as queries_file:
        queries_file.write(Config.sql_type_config.file_header_extra)
        # Write the ddl queries created in this python
        queries_file.write('\n-------------------------- Creating tables with their relevant information --------------------------\n')
        for ddl_query in ddl_queries:
            queries_file.write(ddl_query)
        queries_file.write('\n----------------------------------- Creating Foreign Keys -----------------------------------\n')
        for fk_query in fk_queries:
            queries_file.write(fk_query)
        queries_file.write('\n-------------------------- Inserting data to tables --------------------------\n')
        for dml_query in insert_queries:
            queries_file.write(dml_query)

        queries_file.write(f"\ncommit;\n/\n")

    # write all drops into sql drop file
    with open(Config.output_drops_file, 'w', encoding='utf-8') as drops_file:
        # Write the ddl drops created in this python, and dml deletes for inserted data
        drops_file.write('\n\n----------------- Dropping Foreign Keys and other constraints -----------------\n')
        for fk_drop_query in reversed(constraints_drop_queries):
            drops_file.write(fk_drop_query)
        drops_file.write("\n----------------- Deleting data added to existing table from previous version -----------------")
        for dml_delete_query in reversed(delete_queries):
            drops_file.write(dml_delete_query)
        drops_file.write('\n----------------- Dropping Tables and sequences -----------------\n')
        for ddl_drop_query in reversed(ddl_drops_queries):
            drops_file.write(ddl_drop_query)

        logger.debug(f"content has been written into {Config.output_dir_path}")
