import yaml
from loguru import logger
from typing_extensions import Annotated


def load_config_data(file_path: str) -> Annotated[dict, "config_data"]:
    """Load configuration data from a YAML file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Configuration data as a dictionary.
    """
    logger.info(f"Loading config data from {file_path}")

    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            logger.info("Config data loaded successfully")
            return config_data
    except Exception as e:
        logger.error(f"Error loading config data: {e}")
        raise e