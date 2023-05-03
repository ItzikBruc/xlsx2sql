import logging
import pathlib
import sys


def create_logger():
    xlsx2sql_logger = logging.getLogger("xlsx2sql_logger")
    xlsx2sql_logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    xlsx2sql_logger.addHandler(stream_handler)

    generated_dir: pathlib = pathlib.Path("generated")
    generated_dir.mkdir(exist_ok=True)
    log_file_path = generated_dir / 'xlsx.log'  # (datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log')
    file_handler = logging.FileHandler(str(log_file_path), mode='w')
    file_handler.setFormatter(formatter)
    xlsx2sql_logger.addHandler(file_handler)

    return xlsx2sql_logger

logger = create_logger()
