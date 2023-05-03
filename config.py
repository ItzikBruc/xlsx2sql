import pathlib
import yaml

from logger import logger

class Config:
    def __new__(cls):
        # enforce none instantiation
        raise NotImplementedError()

    yaml_config_path: pathlib.Path = None
    input_file_relative_path: pathlib.Path = None
    input_file_absolute_path: pathlib.Path = None
    dbms_type_str: str = None
    sql_type_config = None
    output_dir_path: pathlib.Path = None
    output_queries_file: pathlib.Path = None
    output_drops_file: pathlib.Path = None

    @staticmethod
    def parse_yaml_config_to_config():
        """
        parse the configurations from the yaml config file into "Config" static class
        """
        try:
            # load configurations from yaml file into dictionary
            with open(str(Config.yaml_config_path), "r") as config_file:
                yaml_configs: dict = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            logger.error(exc)
            exit()

        # Check for missing keys
        required_keys = ['dbms_type', 'xlsx_location', 'rowdependencies']
        is_key_missing: bool = False
        for key in required_keys:
            if key not in yaml_configs:
                logger.error(f"Missing required key: '{key}'")
                is_key_missing = True
        if is_key_missing:
            exit()

        # Validate that all keys have values, if value is "False" it interpreted as None
        for key in yaml_configs.keys():
            if not yaml_configs[key]:
                # if value is False or 0  then "not yaml_configs[key]" is true
                if yaml_configs[key] is False or yaml_configs[key] == 0:
                    continue
                logger.error(f"Key '{key}' has no value")
                exit()

        Config.input_file_relative_path = pathlib.Path(yaml_configs["xlsx_location"])
        Config.dbms_type_str = yaml_configs["dbms_type"].lower()
        if yaml_configs["rowdependencies"] == 1:
            Config.is_rowdependencies = True
        else:
            Config.is_rowdependencies = False

    @staticmethod
    def init_config():
        """
        initialize configuration values, from yaml config file and CMD arguments
        """
        Config.parse_yaml_config_to_config()
        # after extracting the data from yaml into config, the following lines process more data in the Config class
        Config.input_file_absolute_path = Config.input_file_relative_path.resolve()
        # create "generated" directory where the script is running
        Config.output_dir_path = pathlib.Path(pathlib.Path().absolute(), "generated")
        Config.output_queries_file = pathlib.Path(Config.output_dir_path, f"queries_{Config.input_file_relative_path.stem}.sql")
        Config.output_drops_file = pathlib.Path(Config.output_dir_path, f"drops_{Config.input_file_relative_path.stem}.sql")
        pathlib.Path(Config.output_dir_path).mkdir(parents=True, exist_ok=True)


