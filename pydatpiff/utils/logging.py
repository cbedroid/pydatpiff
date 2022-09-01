import logging  # noqa
import logging.config

import yaml

log_config_file = "./.logging_config.yaml"

with open(log_config_file, "r") as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
