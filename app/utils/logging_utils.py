import logging


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("indeed_apply")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("indeed_apply.log")
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
