import logging  # noqa
import logging.config
import os

import yaml

DIR = os.path.dirname(os.path.abspath(__file__))
log_config_file = os.path.join(DIR, ".logging_config.yaml")

with open(log_config_file, "r") as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
