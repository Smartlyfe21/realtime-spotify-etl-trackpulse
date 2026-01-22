import os
import logging

def ensure_log_dir(log_dir="../logs"):
    """
    Ensure the logs directory exists. Creates it if not.
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"Created log directory at: {log_dir}")

def setup_logger(log_dir="../logs", log_file="etl.log"):
    """
    Set up logging configuration for the ETL pipeline.
    Returns a logger instance.
    """
    ensure_log_dir(log_dir)
    log_path = os.path.join(log_dir, log_file)

    # Clear existing logging handlers to avoid duplicate logs in repeated runs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(__name__)
    return logger
