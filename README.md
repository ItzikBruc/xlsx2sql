xlsx2sql (XLSX to SQL):


Description:
This Python script is designed to assist in implementing database design made in xlsx file.
The script utilizes tables with specific format (the specifications detailed in the text.xlsx file) and converts them into SQL queries, including drops of the created queries.

Currently, only OracleSQL is supported, but other relational DB will be added in the future, according to demand.


Installation and Usage:
To run the script please download the repository, edit the "config.yaml" file, and donwload the packges listed in "requirements.txt". It is recommended to use virtual environment, such as venv.
To run the software on either on either Linux or Windows, excute "main.py" with one of the following:
main.py -gui
main.py -config_path [path_to_config]

The "-gui" argument will open a simple GUI to select the config file instead of requiring the path as an argument.


Example and ducomentation:
Examples can be found in the "test.xlsx" file.
The file contains 3 sheets. One creates DDL queries,second creates DML queries, and third sheet outlining the rules to build the structure of tables in the XLSX file


Contribution:
Contributions from individuals familiar with other relational DBMSs are welcome. They can do so by implementing the specific SQL language script page parallel to the "oracleSQL.py" page


Support:
For support please contact at: izikbru.dev@gmail.com


License:
Apache License 2.0 (see "LICENSE")