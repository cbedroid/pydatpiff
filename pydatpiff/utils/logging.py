import logging
import logging.config
import os

import yaml

DIR = os.path.dirname(os.path.abspath(__file__))
file_name = os.path.join(DIR, "../.logging_config.yaml")

with open(file_name, "r") as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
