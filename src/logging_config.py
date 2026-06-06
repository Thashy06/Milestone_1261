import logging
import os

def get_logger(name: str):
    """
    Return a configured logger that writes to logs/<name>.log.
    Ensures consistent formatting across all project scripts.
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)


    if not logger.handlers:
        log_path = os.path.join("logs", f"{name}.log")
        handler = logging.FileHandler(log_path)

        formatter = logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        )
        handler.setFormatter(formatter)

  
        logger.addHandler(handler)


        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


