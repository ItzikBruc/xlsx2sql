# this file is used in case configuration file and xlsx file are given with command line
import pathlib

from config import Config

def cmd_config(arguments):
    if arguments.config_path:
        Config.yaml_config_path = pathlib.Path(arguments.config_path)
