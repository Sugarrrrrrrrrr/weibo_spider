import logging
import logging.config
import yaml
import os


def setup_logging(default_path='logging_config.yaml', default_level=logging.INFO):
    path = default_path
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def log():
    logging.debug("this is debug")
    logging.info("this is info")
    logging.warning("this is warning")
    logging.error("this is error")
    logging.critical("this is critical")


def core():
    logger = logging.getLogger('main')

    logger.debug("this is debug")
    logger.info("this is info")
    logger.warning("this is warning")
    logger.error("this is error")
    logger.critical("this is critical")


if __name__ == '__main__':
    yaml_path = 'logging_config.yaml'
    setup_logging(yaml_path)
    # log()
    core()